from typing import Any, Dict

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.messages import ToolMessage
from tools.market_tools import get_market_news, get_market_price, get_stock_price_history
from tools.portfolio_tools import get_rule_based_allocation
from tools.retrieval_tools import retrieve_context

_model = init_chat_model("gpt-5.4", model_provider="openai")

_SYSTEM_PROMPT = (
    "You are a portfolio advisor AI that provides personalized investment recommendations. "
    "Your job is to help users with portfolio analysis, rebalancing, and investment advice. "
    "You have access to a rule engine that provides baseline allocation recommendations "
    "based on risk level. Call get_rule_based_allocation with the user's risk level "
    "before or during your analysis to use it as a reference point. "
    "You also have access to real-time market prices, historical price data, market news, "
    "and relevant investment documentation. "
    "Use these tools to look up the current price, recent performance, and news of any "
    "assets the user mentions before giving your analysis. "
    "Be specific: reference actual prices, percentage changes, and allocation percentages. "
    "Always support your recommendations with evidence — cite relevant market news, "
    "investment principles, or financial theory to justify your suggestions. "
    "Always explain your reasoning clearly. "
    "If a tool returns an error, acknowledge the limitation to the user and "
    "answer based on available information rather than guessing."
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

    tool_outputs = [
        message.content
        for message in response["messages"]
        if isinstance(message, ToolMessage)
    ]

    return {"answer": answer, "context": context_docs, "tool_outputs": tool_outputs}
