from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from graph.consts import CHAT_AGENT, PORTFOLIO_AGENT, ROUTER
from graph.nodes.chat_agent_node import chat_agent_node
from graph.nodes.portfolio_agent_node import portfolio_agent_node
from graph.nodes.router_node import router_node
from graph.state import GraphState


def _route(state: GraphState) -> str:
    return state["datasource"]


workflow = StateGraph(GraphState)

workflow.add_node(ROUTER, router_node)
workflow.add_node(CHAT_AGENT, chat_agent_node)
workflow.add_node(PORTFOLIO_AGENT, portfolio_agent_node)

workflow.set_entry_point(ROUTER)

workflow.add_conditional_edges(
    ROUTER,
    _route,
    {
        CHAT_AGENT: CHAT_AGENT,
        PORTFOLIO_AGENT: PORTFOLIO_AGENT,
    },
)

workflow.add_edge(CHAT_AGENT, END)
workflow.add_edge(PORTFOLIO_AGENT, END)

app = workflow.compile(checkpointer=MemorySaver())



if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    app.get_graph().draw_mermaid_png(output_file_path="graph.png")

    result = app.invoke({"question": "I have VTI and BND in my portfolio, should I rebalance?"})
    print(result["answer"])
