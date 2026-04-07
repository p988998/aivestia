from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

from graph.state import GraphState

_SYSTEM_PROMPT = (
    "You are the final response generator for an investment AI assistant.\n\n"

    "## Inputs You Receive\n"
    "- Verified Draft: a factual summary produced by a research agent.\n"
    "- Raw Tool Data: the full outputs of every tool the agent called — "
    "this includes retrieved investment knowledge, market prices, news, and simulations.\n\n"

    "## Your Job\n"
    "- Write the final user-facing answer using the Draft as your factual backbone "
    "and the Raw Tool Data as your evidence and explanation source.\n"
    "- Pull investment theories, strategies, and principles directly from Raw Tool Data "
    "to explain and support the answer.\n"
    "- NEVER invent numbers, prices, or returns not present in the provided data.\n\n"

    "## Style\n"
    "- Clear, well-structured, and substantive.\n"
    "- Include key numbers from the draft.\n"
    "- Use investment reasoning from the tool data as evidence.\n"
    "- Professional tone. Use bullets or headers where helpful.\n"
)

_prompt = ChatPromptTemplate.from_messages([
    ("system", _SYSTEM_PROMPT),
    ("human",
     "Question: {question}\n\n"
     "Verified Draft:\n{draft}\n\n"
     "Raw Tool Data:\n{tool_outputs}"),
])

_llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
_chain = _prompt | _llm


def final_llm_node(state: GraphState, config: RunnableConfig) -> GraphState:
    tool_outputs_str = "\n---\n".join(state.get("tool_outputs", []))
    result = _chain.invoke(
        {
            "question": state["question"],
            "draft": state["answer"],
            "tool_outputs": tool_outputs_str,
        },
        config=config,
    )
    return {"answer": result.content}
