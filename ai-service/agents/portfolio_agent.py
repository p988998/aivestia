from typing import Any, Dict

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.messages import ToolMessage

from langchain.messages import ToolMessage

from tools.market_tools import get_market_news, get_market_price, get_stock_price_history
from tools.portfolio_tools import get_rule_based_allocation
from tools.retrieval_tools import retrieve_context

_model = init_chat_model("gpt-5.4", model_provider="openai")

_SYSTEM_PROMPT = (
    "You are a portfolio advisor AI. The user will describe their current holdings. "
    "Your job is to analyze their portfolio, assess whether the allocation matches their "
    "risk profile and investment horizon, and suggest rebalancing if needed. "
    "You have access to a rule engine that provides baseline allocation recommendations "
    "based on risk level. Call get_rule_based_allocation with the user's risk level "
    "before or during your analysis to use it as a reference point. "
    "You also have access to real-time market prices and historical price data. "
    "Use these tools to look up the current price and recent performance of the assets "
    "the user mentions before giving your analysis. "
    "Be specific: reference actual prices, percentage changes, and allocation percentages. "
    "Always explain your reasoning clearly."
)

_agent = create_agent(
    _model,
    tools=[retrieve_context, get_market_price, get_market_news, get_stock_price_history, get_rule_based_allocation],
    system_prompt=_SYSTEM_PROMPT,
)


def run(messages: list, user_profile: dict = {}) -> Dict[str, Any]:
    full_messages = []
    if user_profile:
        interests = user_profile.get("interests") or []
        interests_text = f", interests: {', '.join(interests)}" if interests else ""
        profile_text = (
            f"User profile: age={user_profile.get('age')}, "
            f"risk tolerance={user_profile.get('riskLevel')}, "
            f"investment horizon={user_profile.get('horizon')} years"
            f"{interests_text}."
        )
        full_messages.append({"role": "system", "content": profile_text})
    full_messages += messages
    response = _agent.invoke({"messages": full_messages})

    answer = response["messages"][-1].content

    context_docs = []
    for message in response["messages"]:
        if isinstance(message, ToolMessage) and hasattr(message, "artifact"):
            if not isinstance(message.artifact, list):
                continue
            for item in message.artifact:
                if not isinstance(item, str):
                    context_docs.append(item)

    return {"answer": answer, "context": context_docs}
