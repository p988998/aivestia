from agents.portfolio_agent import run as portfolio_agent_run
from graph.state import GraphState


def portfolio_agent_node(state: GraphState) -> GraphState:
    result = portfolio_agent_run(state["question"])
    return {
        "answer":    result["answer"],
        "context":   [],
        "news_urls": [],
    }
