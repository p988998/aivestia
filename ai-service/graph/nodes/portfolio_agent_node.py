from agents.portfolio_agent import run as portfolio_agent_run
from graph.state import GraphState
from langchain_core.runnables import RunnableConfig


def portfolio_agent_node(state: GraphState, config: RunnableConfig) -> GraphState:
    history = state.get("history", [])
    messages = history + [{"role": "user", "content": state["question"]}]
    result = portfolio_agent_run(messages, state.get("user_profile", {}), config=config)
    return {
        "answer":       result["answer"],
        "context":      result.get("context", []),
        "news_urls":    [],
        "tool_outputs": result.get("tool_outputs", []),
        "simulations":  result.get("simulations"),
        "retry_count":  0,
        "history":      [
            {"role": "user",      "content": state["question"]},
            {"role": "assistant", "content": result["answer"]},
        ],
    }
