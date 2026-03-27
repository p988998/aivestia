from typing import Any, Dict

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.messages import ToolMessage

from tools.market_tools import get_market_news, get_market_price, get_stock_price_history
from tools.retrieval_tools import retrieve_context

_model = init_chat_model("gpt-5.4", model_provider="openai")

_SYSTEM_PROMPT = (
    "You are a helpful AI assistant that answers questions about investing. "
    "You have access to a tool that retrieves relevant documentation. "
    "You also have access to a tool that fetches real-time market prices for stocks, ETFs, and bonds by ticker symbol. "
    "You also have access to a tool that fetches real-time market news. "
    "You also have access to a tool that fetches historical daily closing prices for stocks, ETFs, and bonds. "
    "Use the tools to find relevant information before answering questions. "
    "Always fetch recent market news for any ticker or asset mentioned in the question, "
    "unless the question is purely conceptual or definitional (e.g. 'what is an ETF?'). "
    "Always cite the sources you use in your answers. "
    "If you cannot find the answer in the retrieved documentation, say so. "
    "If a tool returns an error, acknowledge the limitation to the user and "
    "answer based on available information rather than guessing."
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
