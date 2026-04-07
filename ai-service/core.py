from typing import Any, Dict

from dotenv import load_dotenv
from langchain_core.messages import AIMessageChunk

from graph.consts import CHAT_AGENT, FINAL_LLM, HALLUCINATION_CHECK, PORTFOLIO_AGENT, ROUTER

load_dotenv()

_app = None


def set_langgraph_app(app) -> None:
    global _app
    _app = app


def run_llm(query: str, session_id: str, user_profile: dict = {}) -> Dict[str, Any]:
    return _app.invoke(
        {"question": query, "user_profile": user_profile},
        config={"configurable": {"thread_id": session_id}},
    )


def stream_llm(query: str, session_id: str, user_profile: dict = {}):
    config = {"configurable": {"thread_id": session_id}}

    for mode, chunk in _app.stream(
        {"question": query, "user_profile": user_profile},
        config=config,
        stream_mode=["messages", "updates"],
    ):
        if mode == "updates":
            node_name = list(chunk.keys())[0]
            state_update = chunk[node_name]
            if node_name == ROUTER:
                datasource = state_update.get("datasource", "")
                if datasource == PORTFOLIO_AGENT:
                    yield ("status", "Analyzing your portfolio...")
                else:
                    yield ("status", "Researching your question...")
            elif node_name in (CHAT_AGENT, PORTFOLIO_AGENT):
                yield ("status", "Checking accuracy...")
            elif node_name == HALLUCINATION_CHECK:
                if not state_update.get("grounded", True):
                    yield ("retry", "hallucination_check_failed")

        elif mode == "messages":
            msg_chunk, metadata = chunk
            if (
                isinstance(msg_chunk, AIMessageChunk)
                and metadata.get("langgraph_node") == FINAL_LLM
                and msg_chunk.content
            ):
                yield ("token", msg_chunk.content)

    snapshot = _app.get_state(config)
    yield ("done", snapshot.values)
