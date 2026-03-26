from langchain.tools import tool

from services.market_data_service import get_market_data, get_price_history
from services.news_service import get_market_news as _get_market_news


@tool
def get_market_price(ticker: str) -> str:
    """Get real-time price and key metrics for a stock, ETF, or bond by ticker symbol.
    Data is sourced from Yahoo Finance. Use this when the user asks about the current
    price, performance, or market data of a specific security (e.g. VTI, AAPL, BND, SPY).
    """
    data = get_market_data(ticker)
    return (
        f"Ticker: {data.ticker}\n"
        f"Current Price: ${data.current_price:.2f}\n"
        f"Previous Close: ${data.previous_close:.2f}\n"
        f"Day Change: {data.day_change_pct:+.2f}%\n"
        f"52-Week High: ${data.year_high:.2f}\n"
        f"52-Week Low: ${data.year_low:.2f}"
    )

@tool(response_format="content_and_artifact")
def get_market_news(ticker: str):
    """Get recent news articles for a stock, ETF, or bond by ticker symbol.
    Data is sourced from Finnhub. Use this when the user asks about recent news,
    events, or sentiment for a specific security (e.g. VTI, AAPL, BND, SPY).
    """
    articles = _get_market_news(ticker)
    if not articles:
        return f"No recent news found for {ticker.upper()}.", []
    serialized = "\n\n".join(
        f"[{a.published_at}] {a.headline} ({a.source})\n{a.summary}"
        for a in articles
    )
    sources = [a.url for a in articles]
    return serialized, sources


@tool
def get_stock_price_history(ticker: str, period: str = "1mo") -> str:
    """Get historical daily closing prices for a stock, ETF, or bond by ticker symbol.
    Data is sourced from Yahoo Finance. Use this when the user asks about price trends,
    historical performance, or how a security has moved over time (e.g. VTI, AAPL, SPY).
    Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, ytd, max.
    """
    points = get_price_history(ticker, period=period)
    if not points:
        return f"No historical data found for {ticker.upper()}."
    lines = "\n".join(f"{p.date}: ${p.close}" for p in points)
    return f"Historical closing prices for {ticker.upper()} ({period}):\n{lines}"


if __name__ == "__main__":
    result = get_market_price.invoke({"ticker": "MS"})
    print(result)