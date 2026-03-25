import yfinance as yf
from pydantic import BaseModel


class MarketData(BaseModel):
    ticker: str
    current_price: float
    previous_close: float
    day_change_pct: float
    year_high: float
    year_low: float

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


if __name__ == "__main__":
    data = get_market_data("MS")
    print(data)
