from agents.chat_agent import run as chat_agent_run
from graph.state import GraphState


def chat_agent_node(state: GraphState) -> GraphState:
    history = state.get("history", [])
    messages = history + [{"role": "user", "content": state["question"]}]
    result = chat_agent_run(messages)
    return {
        "answer":    result["answer"],
        "context":   result.get("context", []),
        "news_urls": result.get("news_urls", []),
        "history":   [
            {"role": "user",      "content": state["question"]},
            {"role": "assistant", "content": result["answer"]},
        ],
    }
