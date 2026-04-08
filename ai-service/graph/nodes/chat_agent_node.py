from agents.chat_agent import run as chat_agent_run
from graph.state import GraphState
from langchain_core.runnables import RunnableConfig


def _build_profile_message(user_profile: dict) -> dict | None:
    if not user_profile:
        return None
    interests = user_profile.get("interests") or []
    interests_text = f", interests: {', '.join(interests)}" if interests else ""
    profile_text = (
        f"User profile: age={user_profile.get('age')}, "
        f"risk tolerance={user_profile.get('riskLevel')}, "
        f"investment horizon={user_profile.get('horizon')} years"
        f"{interests_text}."
    )
    return {"role": "system", "content": profile_text}


def chat_agent_node(state: GraphState, config: RunnableConfig) -> GraphState:
    history = state.get("history", [])
    profile_msg = _build_profile_message(state.get("user_profile", {}))
    messages = ([profile_msg] if profile_msg else []) + history + [{"role": "user", "content": state["question"]}]
    result = chat_agent_run(messages, config=config)
    return {
        "answer":       result["answer"],
        "context":      result.get("context", []),
        "news_urls":    result.get("news_urls", []),
        "tool_outputs": result.get("tool_outputs", []),
        "simulations":  result.get("simulations"),
        "retry_count":  0,
        "history":      [
            {"role": "user",      "content": state["question"]},
            {"role": "assistant", "content": result["answer"]},
        ],
    }
