import asyncio
import os
import ssl
from typing import Any, Dict, List

import certifi
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_tavily import TavilyCrawl, TavilyExtract, TavilyMap
from utils.logger import (Colors, log_error, log_header, log_info, log_success, log_warning)

load_dotenv()

# Configure SSL context to use certifi certificates
ssl_context = ssl.create_default_context(cafile=certifi.where())
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()


embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    show_progress_bar=False,
    chunk_size=50,
    retry_min_seconds=10,
)
# vectorstore = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
vectorstore = PineconeVectorStore(
    index_name=os.environ["INDEX_NAME"] , embedding=embeddings
)
tavily_extract = TavilyExtract()
tavily_map = TavilyMap(max_depth=3, max_breadth=50, max_pages=200)

SOURCES = [
    "https://www.investopedia.com/etfs-4427784",
    "https://www.investopedia.com/investing-4427685",
    "https://www.investopedia.com/stocks-4427785",
    "https://www.investopedia.com/bonds-4689778",
    "https://www.investopedia.com/portfolio-management-4689748",
]


async def index_documents_async(documents: List[Document], batch_size: int = 50):
    """Process documents in batches asynchronously."""
    log_header("VECTOR STORAGE PHASE")
    log_info(
        f"📚 VectorStore Indexing: Preparing to add {len(documents)} documents to vector store",
        Colors.DARKCYAN,
    )

    # Create batches
    batches = [
        documents[i : i + batch_size] for i in range(0, len(documents), batch_size)
    ]

    log_info(
        f"📦 VectorStore Indexing: Split into {len(batches)} batches of {batch_size} documents each"
    )

    # Process all batches concurrently
    async def add_batch(batch: List[Document], batch_num: int):
        try:
            await vectorstore.aadd_documents(batch)
            log_success(
                f"VectorStore Indexing: Successfully added batch {batch_num}/{len(batches)} ({len(batch)} documents)"
            )
        except Exception as e:
            log_error(f"VectorStore Indexing: Failed to add batch {batch_num} - {e}")
            return False
        return True

    # Process batches concurrently
    tasks = [add_batch(batch, i + 1) for i, batch in enumerate(batches)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Count successful batches
    successful = sum(1 for result in results if result is True)

    if successful == len(batches):
        log_success(
            f"VectorStore Indexing: All batches processed successfully! ({successful}/{len(batches)})"
        )
    else:
        log_warning(
            f"VectorStore Indexing: Processed {successful}/{len(batches)} batches successfully"
        )


async def main():
    """Main async function to orchestrate the entire process."""
    log_header("DOCUMENTATION INGESTION PIPELINE")

    # Phase 1: Discover URLs from all category pages via TavilyMap
    log_header("URL DISCOVERY PHASE")
    discovered_urls: set[str] = set()

    for source_url in SOURCES:
        log_info(f"🗺️  TavilyMap: Mapping {source_url}", Colors.PURPLE)
        try:
            map_result = tavily_map.invoke({"url": source_url})
            urls = map_result if isinstance(map_result, list) else map_result.get("urls", [])
            before = len(discovered_urls)
            discovered_urls.update(u for u in urls if "investopedia.com" in u)
            log_success(f"TavilyMap: Found {len(discovered_urls) - before} new URLs from {source_url}")
        except Exception as e:
            log_error(f"TavilyMap: Failed for {source_url} - {e}")

    log_info(f"📋 Total unique URLs discovered: {len(discovered_urls)}", Colors.BOLD)

    # Phase 2: Extract content from discovered URLs in batches
    log_header("CONTENT EXTRACTION PHASE")
    all_docs: List[Document] = []
    url_list = list(discovered_urls)
    batch_size = 20

    for i in range(0, len(url_list), batch_size):
        batch_urls = url_list[i:i + batch_size]
        batch_num = i // batch_size + 1
        log_info(f"📄 TavilyExtract: Extracting batch {batch_num} ({len(batch_urls)} URLs)", Colors.DARKCYAN)
        try:
            extract_result = tavily_extract.invoke({"urls": batch_urls})
            results = extract_result if isinstance(extract_result, list) else extract_result.get("results", [])
            for item in results:
                content = item.get("raw_content") or item.get("content", "")
                url = item.get("url", "")
                if content and url:
                    all_docs.append(Document(page_content=content, metadata={"source": url}))
            log_success(f"TavilyExtract: Batch {batch_num} — extracted {len(results)} pages")
        except Exception as e:
            log_error(f"TavilyExtract: Batch {batch_num} failed - {e}")

    log_info(f"📚 Total documents extracted: {len(all_docs)}", Colors.BOLD)

    # Phase 3: Chunk documents
    log_header("DOCUMENT CHUNKING PHASE")
    log_info(
        f"✂️  Text Splitter: Processing {len(all_docs)} documents (chunk_size=2000, overlap=200)",
        Colors.YELLOW,
    )
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    splitted_docs = text_splitter.split_documents(all_docs)
    log_success(f"Text Splitter: Created {len(splitted_docs)} chunks from {len(all_docs)} documents")

    # Phase 4: Store in Pinecone
    await index_documents_async(splitted_docs, batch_size=50)

    log_header("PIPELINE COMPLETE")
    log_success("🎉 Documentation ingestion pipeline finished successfully!")
    log_info("📊 Summary:", Colors.BOLD)
    log_info(f"   • Category URLs crawled: {len(SOURCES)}")
    log_info(f"   • Unique pages discovered: {len(discovered_urls)}")
    log_info(f"   • Documents extracted: {len(all_docs)}")
    log_info(f"   • Chunks indexed: {len(splitted_docs)}")


if __name__ == "__main__":
    asyncio.run(main())