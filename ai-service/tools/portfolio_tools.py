from langchain.tools import tool

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
