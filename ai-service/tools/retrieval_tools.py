from langchain.tools import tool

from graph.chains.retrieval_grader import retrieval_grader
from services.retrieval_service import get_relevant_docs


@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve relevant documentation to help answer user queries about investing."""
    try:
        docs = get_relevant_docs(query)
        filtered_docs = [
            doc for doc in docs
            if retrieval_grader.invoke({"question": query, "document": doc.page_content}).binary_score == "yes"
        ]
        relevant_docs = filtered_docs if filtered_docs else docs[:1]
        serialized = "\n\n".join(
            f"Source: {doc.metadata.get('source', 'Unknown')}\n\nContent: {doc.page_content}"
            for doc in relevant_docs
        )
        return serialized, relevant_docs
    except Exception as e:
        return f"Could not retrieve documentation: {e}", []
