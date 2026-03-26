from langchain.tools import tool

from services.portfolio_service import get_allocations


@tool
def get_rule_based_allocation(risk_level: str) -> str:
    """Get the baseline portfolio allocation from the rule engine for a given risk level.
    Valid risk levels: low, medium, high.
    Use this to retrieve the recommended baseline allocation before analyzing the user's
    actual holdings or suggesting rebalancing.
    """
    try:
        allocations = get_allocations(risk_level)
    except ValueError as e:
        return str(e)
    lines = "\n".join(f"  {a.ticker} ({a.name}): {a.weight}%" for a in allocations)
    return f"Rule-based baseline allocation for '{risk_level}' risk:\n{lines}"
