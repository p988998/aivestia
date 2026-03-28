from typing import Any, Dict

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.messages import ToolMessage
from tools.market_tools import get_market_news, get_market_price, get_stock_price_history
from tools.portfolio_tools import get_portfolio_simulation, get_rule_based_allocation, simulate_holdings
from tools.retrieval_tools import retrieve_context

_model = init_chat_model("gpt-5.4", model_provider="openai")

_SYSTEM_PROMPT = """
You are a portfolio advisor AI that provides personalized investment recommendations.

Tool usage rules:
- For any investment-related claim, you MUST use tools to retrieve supporting data before stating it.
- Use get_market_price and get_market_news for every asset you discuss — including tickers from the rule engine, not only ones the user mentions.
- Use get_stock_price_history for trend or performance claims.
- Use retrieve_context for investment theory, strategy, or principles.
- Use get_portfolio_simulation when giving a concrete recommendation — it returns allocation + historical simulation for the user to see.
- Use get_rule_based_allocation only when you need allocation data internally, without showing a simulation.
- If the user has current holdings, call simulate_holdings(holdings_csv, risk_level) FIRST (format: 'VTI:60,BND:40'), then call get_portfolio_simulation. This generates a side-by-side comparison.

Response requirements:
- After calling tools, explicitly incorporate their outputs in your answer.
- Quote specific headlines, name retrieved principles, cite exact prices and percentages.
- Do not write generic answers that ignore tool results.
- Clearly explain your reasoning.

Behavior:
- If the user provides current holdings, compare their portfolio with the recommended one.
- If not, give a recommendation based on their risk profile and encourage them to share holdings.
- If the recommended portfolio shows lower historical returns than the user's current holdings, acknowledge this honestly and explain the trade-offs: risk alignment, volatility, diversification, or concentration risk. Never hide unfavorable data or recommend a clearly worse portfolio without justification.
- If a tool fails, acknowledge the limitation and proceed with available information.
"""

_agent = create_agent(
    _model,
    tools=[retrieve_context, get_market_price, get_market_news, get_stock_price_history,
           get_rule_based_allocation, get_portfolio_simulation, simulate_holdings],
    system_prompt=_SYSTEM_PROMPT,
)


def run(messages: list, user_profile: dict = {}) -> Dict[str, Any]:
    full_messages = []
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
    response = _agent.invoke({"messages": full_messages})

    answer = response["messages"][-1].content

    context_docs = []
    simulations = []
    for message in response["messages"]:
        if not (isinstance(message, ToolMessage) and hasattr(message, "artifact")):
            continue
        artifact = message.artifact
        if isinstance(artifact, dict) and "performance" in artifact:
            simulations.append(artifact)
        elif isinstance(artifact, list):
            for item in artifact:
                if not isinstance(item, str):
                    context_docs.append(item)

    tool_outputs = [
        message.content
        for message in response["messages"]
        if isinstance(message, ToolMessage)
    ]

    return {"answer": answer, "context": context_docs, "tool_outputs": tool_outputs, "simulations": simulations or None}
