from langgraph.graph import END, StateGraph

from graph.consts import CHAT_AGENT, HALLUCINATION_CHECK, PORTFOLIO_AGENT, ROUTER
from graph.nodes.chat_agent_node import chat_agent_node
from graph.nodes.hallucination_check_node import MAX_RETRIES, hallucination_check_node
from graph.nodes.portfolio_agent_node import portfolio_agent_node
from graph.nodes.router_node import router_node
from graph.state import GraphState


def _route(state: GraphState) -> str:
    return state["datasource"]


def _after_check(state: GraphState) -> str:
    if state.get("grounded", True) or state.get("retry_count", 0) >= MAX_RETRIES:
        return END
    return state["datasource"]


def build_graph(checkpointer):
    workflow = StateGraph(GraphState)

    workflow.add_node(ROUTER, router_node)
    workflow.add_node(CHAT_AGENT, chat_agent_node)
    workflow.add_node(PORTFOLIO_AGENT, portfolio_agent_node)
    workflow.add_node(HALLUCINATION_CHECK, hallucination_check_node)

    workflow.set_entry_point(ROUTER)

    workflow.add_conditional_edges(
        ROUTER,
        _route,
        {
            CHAT_AGENT: CHAT_AGENT,
            PORTFOLIO_AGENT: PORTFOLIO_AGENT,
        },
    )

    workflow.add_edge(CHAT_AGENT, HALLUCINATION_CHECK)
    workflow.add_edge(PORTFOLIO_AGENT, HALLUCINATION_CHECK)

    workflow.add_conditional_edges(
        HALLUCINATION_CHECK,
        _after_check,
        {CHAT_AGENT: CHAT_AGENT, PORTFOLIO_AGENT: PORTFOLIO_AGENT, END: END},
    )

    return workflow.compile(checkpointer=checkpointer)
