import os

from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = PineconeVectorStore(
    index_name=os.environ["INDEX_NAME"], embedding=embeddings
)


def get_relevant_docs(query: str, k: int = 4) -> list[Document]:
    try:
        return vectorstore.as_retriever().invoke(query, k=k)
    except Exception as e:
        raise ValueError(f"Failed to retrieve documents from vector store: {e}")
