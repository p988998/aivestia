from typing import Any, Dict

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.messages import ToolMessage

from tools.market_tools import get_market_news, get_market_price, get_stock_price_history
from tools.retrieval_tools import retrieve_context

_model = init_chat_model("gpt-5.4", model_provider="openai")

_SYSTEM_PROMPT = (
    "You are a financial information assistant focused on providing accurate, data-backed answers.\n\n"

    "## Scope (CRITICAL)\n"
    "- You provide market information, explanations, and factual insights.\n"
    "- You MUST NOT provide portfolio recommendations, asset allocation, or personalized investment advice.\n"
    "- If the user asks for portfolio construction, allocation, or investment decisions,\n"
    "  you MUST indicate that this requires portfolio analysis and should be handled by the portfolio advisor.\n\n"

    "## Tool Usage Rules\n"
    "- Use retrieve_context ONLY for conceptual or educational questions (e.g., 'what is ETF', 'what is diversification').\n"
    "- Use get_market_price when the question involves current prices or tickers.\n"
    "- Use get_market_news when discussing recent market events or sentiment.\n"
    "- Use get_stock_price_history ONLY when analyzing trends or historical performance.\n"
    "- Do NOT call tools unnecessarily.\n\n"

    "## Grounding Rules (CRITICAL)\n"
    "- You MUST NOT state any factual claim (prices, returns, trends, news) unless it comes from tool output.\n"
    "- If tool data is unavailable, say: 'I don't have enough data to answer this precisely.'\n"
    "- Do NOT guess or hallucinate.\n\n"

    "## Tool Integration Rules\n"
    "- After calling tools, you MUST explicitly reference the returned data.\n"
    "- Include concrete numbers such as prices, percentage changes, and time ranges.\n"
    "- Do NOT ignore or vaguely summarize tool outputs.\n\n"

    "## Answering Style\n"
    "- Be concise and clear by default.\n"
    "- Use structured formatting when helpful (bullet points, short paragraphs).\n"
    "- Explain reasoning only when needed.\n\n"

    "## Error Handling\n"
    "- If a tool fails, acknowledge the limitation and proceed with available information.\n"
)

_agent = create_agent(
    _model,
    tools=[retrieve_context, get_market_price, get_market_news, get_stock_price_history],
    system_prompt=_SYSTEM_PROMPT,
)


def run(messages: list) -> Dict[str, Any]:
    response = _agent.invoke({"messages": messages})

    answer = response["messages"][-1].content

    context_docs = []
    news_urls = []
    for message in response["messages"]:
        if isinstance(message, ToolMessage) and hasattr(message, "artifact"):
            if not isinstance(message.artifact, list):
                continue
            for item in message.artifact:
                if isinstance(item, str):
                    news_urls.append(item)
                else:
                    context_docs.append(item)

    tool_outputs = [
        message.content
        for message in response["messages"]
        if isinstance(message, ToolMessage)
    ]

    return {"answer": answer, "context": context_docs, "news_urls": news_urls, "tool_outputs": tool_outputs}
