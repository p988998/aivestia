from typing import Any, Dict

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.messages import ToolMessage
from langchain_core.runnables import RunnableConfig

from tools.market_tools import get_market_news, get_market_price, get_stock_price_history
from tools.portfolio_tools import get_portfolio_simulation, simulate_holdings
from tools.retrieval_tools import retrieve_context

_model = init_chat_model("gpt-5.4", model_provider="openai")

_SYSTEM_PROMPT = (
    "You are a financial chat agent focused on retrieving information, "

    "## Role (CRITICAL)\n"
    "- You are NOT the final answer generator.\n"
    "- Your job is to gather data, reason carefully, and produce a structured draft.\n"
    "- Your output will be consumed by another model that generates the final user response.\n\n"

    "## Scope\n"
    "- You provide factual market information and explanations.\n"
    "- You MUST NOT provide portfolio recommendations or personalized investment advice.\n"
    "- If the user asks for investment decisions, indicate this requires portfolio analysis.\n\n"

    "## Tool Usage Rules\n"
    "- Use retrieve_context ONLY for conceptual questions.\n"
    "- Use get_market_price for current price questions.\n"
    "- Use get_market_news for market events.\n"
    "- Use get_stock_price_history ONLY for trend analysis.\n"
    "- Use get_portfolio_simulation ONLY when the user explicitly asks to see a historical simulation or backtest for a specific risk level.\n"
    "- Use simulate_holdings ONLY when the user explicitly asks to simulate or backtest their current holdings (resolve company names to tickers, e.g. 'Apple' → 'AAPL').\n"
    "- Do NOT call tools unnecessarily.\n\n"

    "## Grounding Rules (CRITICAL)\n"
    "- ALL factual claims must come from tool outputs.\n"
    "- If data is missing, say so explicitly.\n"
    "- NEVER guess.\n\n"

    "## Output Format\n"
    "Write a complete factual draft in natural language.\n"
    "- Include ALL key numbers, prices, percentages from tool outputs.\n"
    "- Prioritize completeness over presentation.\n"
    "- This draft will be validated and rewritten by another model.\n\n"

    "## Behavior\n"
    "- Focus on correctness and completeness, NOT presentation.\n"
    "- Keep reasoning explicit but concise.\n"
)

_agent = create_agent(
    _model,
    tools=[retrieve_context, get_market_price, get_market_news, get_stock_price_history,
           get_portfolio_simulation, simulate_holdings],
    system_prompt=_SYSTEM_PROMPT,
)


def run(messages: list, config: RunnableConfig = None) -> Dict[str, Any]:
    response = _agent.invoke({"messages": messages}, config=config)

    answer = response["messages"][-1].content

    context_docs = []
    news_urls = []
    simulations = []
    for message in response["messages"]:
        if not (isinstance(message, ToolMessage) and hasattr(message, "artifact")):
            continue
        artifact = message.artifact
        if isinstance(artifact, dict) and "performance" in artifact:
            simulations.append(artifact)
        elif isinstance(artifact, list):
            for item in artifact:
                if isinstance(item, str):
                    news_urls.append(item)
                else:
                    context_docs.append(item)

    tool_outputs = [
        message.content
        for message in response["messages"]
        if isinstance(message, ToolMessage)
    ]

    return {"answer": answer, "context": context_docs, "news_urls": news_urls,
            "tool_outputs": tool_outputs, "simulations": simulations or None}
