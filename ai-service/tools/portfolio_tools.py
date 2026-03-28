from langchain.tools import tool

from services.performance_service import period_for_risk, simulate_portfolio
from services.portfolio_service import apply_interest_tilts, get_allocations


@tool
def get_rule_based_allocation(risk_level: str, interests: str = "") -> str:
    """Get the portfolio allocation from the rule engine for a given risk level.
    Optionally pass a comma-separated list of user interests to get a
    personalized interest-adjusted allocation instead of the plain baseline.
    Valid risk levels: low, medium, high.
    Example: get_rule_based_allocation("medium", "Tech & Growth, Dividend Income")
    """
    try:
        base = get_allocations(risk_level)
    except ValueError as e:
        return str(e)

    parsed_interests = [i.strip() for i in interests.split(",") if i.strip()] if interests else []

    if parsed_interests:
        allocations = apply_interest_tilts(base, parsed_interests)
        header = f"Interest-adjusted allocation for '{risk_level}' risk ({', '.join(parsed_interests)}):"
    else:
        allocations = base
        header = f"Baseline allocation for '{risk_level}' risk:"

    lines = "\n".join(f"  {a.ticker} ({a.name}): {a.weight}%" for a in allocations)
    return f"{header}\n{lines}"


@tool(response_format="content_and_artifact")
def get_portfolio_simulation(risk_level: str, interests: str = "") -> tuple:
    """Generate a portfolio allocation AND run a historical performance simulation.
    Call this when giving the user a concrete portfolio recommendation so they can
    see how this allocation would have performed historically.
    Valid risk levels: low, medium, high.
    Example: get_portfolio_simulation("medium", "Tech & Growth, Dividend Income")
    """
    try:
        base = get_allocations(risk_level)
    except ValueError as e:
        return str(e), {}

    parsed_interests = [i.strip() for i in interests.split(",") if i.strip()] if interests else []
    allocations = apply_interest_tilts(base, parsed_interests) if parsed_interests else base

    alloc_lines = "\n".join(f"  {a.ticker} ({a.name}): {a.weight}%" for a in allocations)
    period = period_for_risk(risk_level)

    try:
        perf = simulate_portfolio(
            [{"ticker": a.ticker, "weight": a.weight} for a in allocations],
            period,
        )
        sign = "+" if perf.total_return_pct >= 0 else ""
        sign_ann = "+" if perf.annualized_return_pct >= 0 else ""
        text = (
            f"Portfolio simulation for '{risk_level}' risk ({period}):\n{alloc_lines}\n"
            f"Historical ({period}): {sign}{perf.total_return_pct:.1f}% total, "
            f"{sign_ann}{perf.annualized_return_pct:.1f}%/yr annualized"
        )
        artifact = {
            "label": "Recommended Portfolio",
            "allocations": [
                {"ticker": a.ticker, "name": a.name, "weight": a.weight, "color": a.color}
                for a in allocations
            ],
            "performance": perf.model_dump(),
        }
    except Exception as e:
        text = f"Portfolio allocation for '{risk_level}' risk:\n{alloc_lines}\n(Simulation unavailable: {e})"
        artifact = {}

    return text, artifact


@tool(response_format="content_and_artifact")
def simulate_holdings(holdings_csv: str, risk_level: str = "medium") -> tuple:
    """Simulate historical performance of the user's CURRENT portfolio holdings.
    Call this FIRST when the user has existing holdings, before get_portfolio_simulation,
    so both current and recommended portfolios can be compared side by side.
    holdings_csv: comma-separated TICKER:WEIGHT pairs, e.g. 'VTI:60,BND:40'
    risk_level: determines simulation period (low=5y, medium=2y, high=1y)
    """
    try:
        allocations = []
        for pair in [p.strip() for p in holdings_csv.split(",") if p.strip()]:
            parts = pair.split(":")
            if len(parts) != 2:
                continue
            ticker, weight = parts[0].strip().upper(), parts[1].strip()
            allocations.append({"ticker": ticker, "weight": int(float(weight))})

        if not allocations:
            return "No valid holdings provided.", {}

        period = period_for_risk(risk_level)
        perf = simulate_portfolio(allocations, period)

        alloc_lines = "\n".join(f"  {a['ticker']}: {a['weight']}%" for a in allocations)
        sign = "+" if perf.total_return_pct >= 0 else ""
        sign_ann = "+" if perf.annualized_return_pct >= 0 else ""
        text = (
            f"Current holdings simulation ({period}):\n{alloc_lines}\n"
            f"Historical ({period}): {sign}{perf.total_return_pct:.1f}% total, "
            f"{sign_ann}{perf.annualized_return_pct:.1f}%/yr annualized"
        )
        artifact = {
            "label": "Your Current Portfolio",
            "allocations": allocations,
            "performance": perf.model_dump(),
        }
        return text, artifact
    except Exception as e:
        return f"Holdings simulation failed: {e}", {}
