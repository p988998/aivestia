import math

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
    try:
        info = yf.Ticker(ticker.upper()).fast_info
        price = info.last_price
        prev_close = info.previous_close
        if price is None or prev_close is None:
            raise ValueError(f"No data available for '{ticker.upper()}'. The ticker may be invalid.")
        return MarketData(
            ticker=ticker.upper(),
            current_price=price,
            previous_close=prev_close,
            day_change_pct=(price - prev_close) / prev_close * 100 if prev_close else 0.0,
            year_high=info.year_high,
            year_low=info.year_low,
        )
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to fetch market data for '{ticker.upper()}': {e}")


def get_price_history(ticker: str, period: str = "1mo", interval: str = "1d") -> list[PricePoint]:
    """
    Fetch historical closing prices for a ticker.

    period:   1d 5d 1mo 3mo 6mo 1y 2y 5y 10y ytd max
    interval: 1m 2m 5m 15m 30m 60m 90m 1h 1d 5d 1wk 1mo 3mo
    """
    try:
        hist = yf.Ticker(ticker.upper()).history(period=period, interval=interval)
        if hist.empty:
            raise ValueError(f"No historical data found for '{ticker.upper()}'.")
        points = [
            PricePoint(date=ts.strftime("%Y-%m-%d"), close=round(float(row["Close"]), 2))
            for ts, row in hist.iterrows()
            if not math.isnan(float(row["Close"]))
        ]
        if not points:
            raise ValueError(f"No valid historical data found for '{ticker.upper()}'.")
        return points
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to fetch price history for '{ticker.upper()}': {e}")


if __name__ == "__main__":
    data = get_market_data("MS")
    print(data)
    
    history = get_price_history("MS", period="1mo")
    for p in history:
        print(p)
