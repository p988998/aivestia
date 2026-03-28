from pydantic import BaseModel

from services.market_data_service import get_price_history

_RISK_PERIOD = {
    "low": "5y",
    "medium": "2y",
    "high": "1y",
}

_PERIOD_YEARS = {
    "5y": 5,
    "2y": 2,
    "1y": 1,
}


class PerfPoint(BaseModel):
    date: str
    value: float  # normalized index, starts at 100


class PerformanceResult(BaseModel):
    period: str
    data_points: list[PerfPoint]
    total_return_pct: float
    annualized_return_pct: float
    start_value: float
    end_value: float


def period_for_risk(risk_level: str) -> str:
    period = _RISK_PERIOD.get(risk_level.lower())
    if period is None:
        raise ValueError(f"Invalid risk level: '{risk_level}'. Must be low, medium, or high.")
    return period


def simulate_portfolio(allocations: list[dict], period: str) -> PerformanceResult:
    """
    Simulate historical portfolio performance.

    allocations: list of {"ticker": str, "weight": int}  (weights must sum to 100)
    period: yfinance period string, e.g. "2y"

    Returns a PerformanceResult with a normalized time series (start = 100)
    and summary statistics.
    """
    # Fetch price history for each ticker
    ticker_series: dict[str, dict[str, float]] = {}  # ticker -> {date -> close}
    for alloc in allocations:
        ticker = alloc["ticker"]
        points = get_price_history(ticker, period=period)
        ticker_series[ticker] = {p.date: p.close for p in points}

    # Inner join on common dates
    date_sets = [set(series.keys()) for series in ticker_series.values()]
    common_dates = sorted(date_sets[0].intersection(*date_sets[1:]))

    if len(common_dates) < 2:
        raise ValueError("Not enough overlapping price data across tickers to simulate performance.")

    first_date = common_dates[0]
    base_prices = {ticker: series[first_date] for ticker, series in ticker_series.items()}

    # Build normalized portfolio value series
    data_points: list[PerfPoint] = []
    for date in common_dates:
        value = sum(
            (alloc["weight"] / 100) * (ticker_series[alloc["ticker"]][date] / base_prices[alloc["ticker"]])
            for alloc in allocations
        ) * 100  # scale to 100-based index
        data_points.append(PerfPoint(date=date, value=round(value, 2)))

    end_value = data_points[-1].value
    total_return = end_value - 100
    total_return_pct = round(total_return, 2)

    years = _PERIOD_YEARS.get(period, 1)
    annualized = ((end_value / 100) ** (1 / years) - 1) * 100
    annualized_return_pct = round(annualized, 2)

    return PerformanceResult(
        period=period,
        data_points=data_points,
        total_return_pct=total_return_pct,
        annualized_return_pct=annualized_return_pct,
        start_value=100.0,
        end_value=round(end_value, 2),
    )
