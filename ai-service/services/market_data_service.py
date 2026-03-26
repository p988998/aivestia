import yfinance as yf
from pydantic import BaseModel


class MarketData(BaseModel):
    ticker: str
    current_price: float
    previous_close: float
    day_change_pct: float
    year_high: float
    year_low: float


class PricePoint(BaseModel):
    date: str
    close: float


def get_market_data(ticker: str) -> MarketData:
    info = yf.Ticker(ticker.upper()).fast_info
    price = info.last_price
    prev_close = info.previous_close
    return MarketData(
        ticker=ticker.upper(),
        current_price=price,
        previous_close=prev_close,
        day_change_pct=(price - prev_close) / prev_close * 100,
        year_high=info.year_high,
        year_low=info.year_low,
    )


def get_price_history(ticker: str, period: str = "1mo", interval: str = "1d") -> list[PricePoint]:
    """
    Fetch historical closing prices for a ticker.

    period:   1d 5d 1mo 3mo 6mo 1y 2y 5y 10y ytd max
    interval: 1m 2m 5m 15m 30m 60m 90m 1h 1d 5d 1wk 1mo 3mo
    """
    hist = yf.Ticker(ticker.upper()).history(period=period, interval=interval)
    return [
        PricePoint(date=ts.strftime("%Y-%m-%d"), close=round(row["Close"], 2))
        for ts, row in hist.iterrows()
    ]


if __name__ == "__main__":
    data = get_market_data("MS")
    print(data)
    
    history = get_price_history("MS", period="1mo")
    for p in history:
        print(p)
