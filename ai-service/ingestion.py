import asyncio
import hashlib
import os
import ssl
from typing import Any, Dict, List

import certifi
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_tavily import TavilyCrawl
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
tavily_crawl = TavilyCrawl(max_depth=1, max_breadth=10)

SOURCES = [
    "https://www.investopedia.com/etfs-4427784",
    "https://www.investopedia.com/investing-4427685",
    "https://www.investopedia.com/stocks-4427785",
    "https://www.investopedia.com/bonds-4689778",
    "https://www.investopedia.com/portfolio-management-4689748",
    "https://www.investopedia.com/terms/m/modernportfoliotheory.asp",
    # Asset Allocation
    "https://www.investopedia.com/terms/a/assetallocation.asp",
    "https://investor.vanguard.com/investor-resources-education/how-to-invest/asset-allocation",
    ## **Diversification
    "https://www.investopedia.com/terms/d/diversification.asp",
    # **Strategic Asset Allocation
    "https://www.vanguard.co.uk/professional/vanguard-365/investment-knowledge/portfolio-construction/strategic-asset-allocation",
    # classic allocation-strategies
    "https://www.investopedia.com/investing/6-asset-allocation-strategies-work/",
    # Buffett 90/10 Strategy
    "https://www.investopedia.com/how-warren-buffett-s-90-10-rule-can-transform-your-investment-strategy-in-simple-steps-11919302",
    # Age-based Allocation
    "https://www.investor.gov/additional-resources/general-resources/publications-research/info-sheets/beginners-guide-asset",
    # Portfolio Construction
    "https://www.investopedia.com/financial-advisor/steps-building-profitable-portfolio",
    # Rebalancing
    "https://smartasset.com/investing/asset-allocation-calculator",
]


async def index_documents_async(documents: List[Document], batch_size: int = 50):
    """Process documents in batches asynchronously."""
    log_header("VECTOR STORAGE PHASE")
    log_info(
        f"📚 VectorStore Indexing: Preparing to add {len(documents)} documents to vector store",
        Colors.DARKCYAN,
    )

    # Generate deterministic IDs based on source URL + chunk index to prevent duplicates on re-run
    ids = [
        hashlib.md5(f"{doc.metadata['source']}_{i}".encode()).hexdigest()
        for i, doc in enumerate(documents)
    ]

    # Create batches
    batches = [
        documents[i : i + batch_size] for i in range(0, len(documents), batch_size)
    ]
    id_batches = [ids[i : i + batch_size] for i in range(0, len(ids), batch_size)]

    log_info(
        f"📦 VectorStore Indexing: Split into {len(batches)} batches of {batch_size} documents each"
    )

    # Process all batches concurrently
    async def add_batch(batch: List[Document], id_batch: List[str], batch_num: int):
        try:
            await vectorstore.aadd_documents(batch, ids=id_batch)
            log_success(
                f"VectorStore Indexing: Successfully added batch {batch_num}/{len(batches)} ({len(batch)} documents)"
            )
        except Exception as e:
            log_error(f"VectorStore Indexing: Failed to add batch {batch_num} - {e}")
            return False
        return True

    # Process batches sequentially to avoid shared session conflicts
    results = []
    for i, batch in enumerate(batches):
        result = await add_batch(batch, id_batches[i], i + 1)
        results.append(result)

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

    # Phase 1: Crawl content from all source URLs
    log_header("CRAWL PHASE")
    all_docs: List[Document] = []
    seen_urls: set[str] = set()

    for source_url in SOURCES:
        log_info(f"🕷️  TavilyCrawl: Crawling {source_url}", Colors.PURPLE)
        try:
            crawl_result = tavily_crawl.invoke({"url": source_url})
            if isinstance(crawl_result, list):
                results = crawl_result
            elif isinstance(crawl_result, dict):
                results = crawl_result.get("results", [])
            else:
                results = []
            new_count = 0
            for item in results:
                url = item.get("url", "")
                content = item.get("raw_content") or item.get("content", "")
                if content and url and url not in seen_urls:
                    seen_urls.add(url)
                    all_docs.append(Document(page_content=content, metadata={"source": url}))
                    new_count += 1
            log_success(f"TavilyCrawl: {source_url} → {new_count} new pages")
        except Exception as e:
            log_error(f"TavilyCrawl: Failed for {source_url} - {e}")

    log_info(f"📚 Total documents crawled: {len(all_docs)}", Colors.BOLD)

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
    log_info(f"   • Source URLs crawled: {len(SOURCES)}")
    log_info(f"   • Unique pages collected: {len(seen_urls)}")
    log_info(f"   • Documents extracted: {len(all_docs)}")
    log_info(f"   • Chunks indexed: {len(splitted_docs)}")


if __name__ == "__main__":
    asyncio.run(main())