from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from graph.chains.hallucination_grader import hallucination_grader
from graph.state import GraphState

MAX_RETRIES = 2

_compress_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Summarize the following tool output in 2-3 sentences. Preserve all key facts, numbers, prices, and percentages. Be concise.",
        ),
        ("human", "{tool_output}"),
    ]
)
_compressor = _compress_prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0)


def hallucination_check_node(state: GraphState):
    tool_outputs = state.get("tool_outputs", [])
    if not tool_outputs:
        return {"grounded": True}

    compressed_parts = [
        _compressor.invoke({"tool_output": output}).content
        for output in tool_outputs
    ]
    compressed = "\n---\n".join(compressed_parts)

    result = hallucination_grader.invoke(
        {
            "tool_outputs": compressed,
            "generation": state["answer"],
        }
    )
    grounded = result.binary_score == "yes"
    return {
        "grounded": grounded,
        "retry_count": state.get("retry_count", 0) + (0 if grounded else 1),
    }
