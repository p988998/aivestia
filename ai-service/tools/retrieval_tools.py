from langchain.tools import tool

from services.retrieval_service import get_relevant_docs


@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve relevant documentation to help answer user queries about investing."""
    docs = get_relevant_docs(query)
    serialized = "\n\n".join(
        f"Source: {doc.metadata.get('source', 'Unknown')}\n\nContent: {doc.page_content}"
        for doc in docs
    )
    return serialized, docs
