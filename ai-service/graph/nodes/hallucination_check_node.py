import asyncio

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from graph.chains.hallucination_grader import hallucination_grader
from graph.state import GraphState

MAX_RETRIES = 2
_COMPRESS_THRESHOLD = 300

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


async def _compress_one(output: str) -> str:
    if len(output) <= _COMPRESS_THRESHOLD:
        return output
    result = await _compressor.ainvoke({"tool_output": output})
    return result.content


async def _compress_all(tool_outputs: list[str]) -> str:
    parts = await asyncio.gather(*(_compress_one(o) for o in tool_outputs))
    return "\n---\n".join(parts)


def hallucination_check_node(state: GraphState):
    tool_outputs = state.get("tool_outputs", [])
    if not tool_outputs:
        return {"grounded": True}

    compressed = asyncio.run(_compress_all(tool_outputs))

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
