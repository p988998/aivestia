from graph.chains.router import question_router
from graph.state import GraphState


def router_node(state: GraphState) -> GraphState:
    history = state.get("history", [])
    recent = history[-4:]  # last 2 turns (user + assistant each)
    if recent:
        context = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in recent)
        question = f"Recent conversation:\n{context}\n\nNew question: {state['question']}"
    else:
        question = state["question"]

    result = question_router.invoke({"question": question})
    return {"datasource": result.datasource}
