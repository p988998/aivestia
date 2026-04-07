from typing import Any, Dict

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.messages import ToolMessage
from langchain_core.runnables import RunnableConfig
from tools.market_tools import get_market_news, get_market_price, get_stock_price_history
from tools.portfolio_tools import get_portfolio_simulation, get_rule_based_allocation, simulate_holdings
from tools.retrieval_tools import retrieve_context

_model = init_chat_model("gpt-5.4", model_provider="openai")

_SYSTEM_PROMPT = (
    "You are a portfolio reasoning agent.\n\n"

    "## Role (CRITICAL)\n"
    "- You are NOT the final answer generator.\n"
    "- Your job is to construct a data-backed investment analysis and draft recommendation.\n"
    "- Another model will generate the final user-facing answer.\n\n"

    "## Responsibilities\n"
    "- Analyze user risk profile and preferences.\n"
    "- Generate allocation and reasoning.\n"
    "- Compare current holdings if provided.\n"
    "- Identify trade-offs (return vs risk vs diversification).\n\n"

    "## Tool Usage Rules\n"
    "- ALWAYS use get_portfolio_simulation for recommendations.\n"
    "- Use simulate_holdings FIRST if user provides current portfolio.\n"
    "- Use get_market_price and get_market_news for discussed assets.\n"
    "- Use get_stock_price_history for performance claims.\n"
    "- Use retrieve_context for investment principles.\n\n"

    "## Grounding Rules (CRITICAL)\n"
    "- ALL claims must be backed by tool outputs.\n"
    "- NEVER invent returns, prices, or results.\n\n"

    "## Output Format\n"
    "Write a complete factual draft in natural language.\n"
    "- Include ALL key numbers, prices, percentages from tool outputs.\n"
    "- Prioritize completeness over presentation.\n"
    "- This draft will be validated and rewritten by another model.\n\n"

    "## Behavior\n"
    "- Be precise, data-driven, and explicit.\n"
    "- Do NOT optimize for user readability — optimize for correctness.\n"
    "- If the recommended portfolio shows lower returns than user's holdings, include this honestly.\n"
)

_agent = create_agent(
    _model,
    tools=[retrieve_context, get_market_price, get_market_news, get_stock_price_history,
           get_rule_based_allocation, get_portfolio_simulation, simulate_holdings],
    system_prompt=_SYSTEM_PROMPT,
)


def run(messages: list, user_profile: dict = {}, config: RunnableConfig = None) -> Dict[str, Any]:
    full_messages = []
    valid_holdings = []

    if user_profile:
        interests = user_profile.get("interests") or []
        interests_text = f", interests: {', '.join(interests)}" if interests else ""
        holdings = user_profile.get("holdings") or []
        valid_holdings = [h for h in holdings if h.get("ticker") and h.get("weight")]
        holdings_text = (
            " Current holdings: " + ", ".join(f"{h['ticker']} {h['weight']}%" for h in valid_holdings) + "."
            if valid_holdings else ""
        )
        profile_text = (
            f"User profile: age={user_profile.get('age')}, "
            f"risk tolerance={user_profile.get('riskLevel')}, "
            f"investment horizon={user_profile.get('horizon')} years"
            f"{interests_text}.{holdings_text}"
        )
        full_messages.append({"role": "system", "content": profile_text})

    full_messages += messages
    response = _agent.invoke({"messages": full_messages}, config=config)

    answer = response["messages"][-1].content

    context_docs = []
    agent_simulations = []
    for message in response["messages"]:
        if not (isinstance(message, ToolMessage) and hasattr(message, "artifact")):
            continue
        artifact = message.artifact
        if isinstance(artifact, dict) and "performance" in artifact:
            agent_simulations.append(artifact)
        elif isinstance(artifact, list):
            for item in artifact:
                if not isinstance(item, str):
                    context_docs.append(item)

    tool_outputs = [
        message.content
        for message in response["messages"]
        if isinstance(message, ToolMessage)
    ]

    # Only simulate current holdings when agent produced a recommendation
    simulations = []
    has_recommendation = any(s.get("label") == "Recommended Portfolio" for s in agent_simulations)
    if has_recommendation and valid_holdings:
        holdings_csv = ",".join(f"{h['ticker']}:{h['weight']}" for h in valid_holdings)
        risk_level = user_profile.get("riskLevel", "medium")
        result = simulate_holdings.invoke(
            {"holdings_csv": holdings_csv, "risk_level": risk_level}
        )
        holdings_artifact = getattr(result, "artifact", {})
        if isinstance(holdings_artifact, dict) and "performance" in holdings_artifact:
            simulations.append(holdings_artifact)  # current holdings first (left card)

    simulations.extend(agent_simulations)  # recommended portfolio second (right card)

    return {"answer": answer, "context": context_docs, "tool_outputs": tool_outputs, "simulations": simulations or None}
