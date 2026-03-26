from typing import Any, Dict

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.messages import ToolMessage

from tools.market_tools import get_market_price, get_stock_price_history

_model = init_chat_model("gpt-4o", model_provider="openai")

_SYSTEM_PROMPT = (
    "You are a portfolio advisor AI. The user will describe their current holdings. "
    "Your job is to analyze their portfolio, assess whether the allocation matches their "
    "risk profile and investment horizon, and suggest rebalancing if needed. "
    "You have access to real-time market prices and historical price data. "
    "Use these tools to look up the current price and recent performance of the assets "
    "the user mentions before giving your analysis. "
    "Be specific: reference actual prices, percentage changes, and allocation percentages. "
    "Always explain your reasoning clearly."
)

_agent = create_agent(
    _model,
    tools=[get_market_price, get_stock_price_history],
    system_prompt=_SYSTEM_PROMPT,
)


def run(question: str) -> Dict[str, Any]:
    messages = [{"role": "user", "content": question}]
    response = _agent.invoke({"messages": messages})

    answer = response["messages"][-1].content

    return {"answer": answer}
