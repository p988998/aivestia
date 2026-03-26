from agents.portfolio_agent import run as portfolio_agent_run
from graph.state import GraphState


def portfolio_agent_node(state: GraphState) -> GraphState:
    history = state.get("history", [])
    messages = history + [{"role": "user", "content": state["question"]}]
    result = portfolio_agent_run(messages, state.get("user_profile", {}))
    return {
        "answer":    result["answer"],
        "context":   result.get("context", []),
        "news_urls": [],
        "history":   [
            {"role": "user",      "content": state["question"]},
            {"role": "assistant", "content": result["answer"]},
        ],
    }
