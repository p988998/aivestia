from pydantic import BaseModel


class Allocation(BaseModel):
    ticker: str
    name: str
    weight: int
    color: str


_ALLOCATIONS: dict[str, list[Allocation]] = {
    "low": [
        Allocation(ticker="VTI", name="US Total Market", weight=30, color="#6366f1"),
        Allocation(ticker="VXUS", name="International", weight=20, color="#8b5cf6"),
        Allocation(ticker="BND", name="US Bonds", weight=50, color="#a78bfa"),
    ],
    "medium": [
        Allocation(ticker="VTI", name="US Total Market", weight=60, color="#6366f1"),
        Allocation(ticker="VXUS", name="International", weight=30, color="#8b5cf6"),
        Allocation(ticker="BND", name="US Bonds", weight=10, color="#a78bfa"),
    ],
    "high": [
        Allocation(ticker="VTI", name="US Total Market", weight=80, color="#6366f1"),
        Allocation(ticker="VXUS", name="International", weight=20, color="#8b5cf6"),
    ],
}


def get_allocations(risk_level: str) -> list[Allocation]:
    key = risk_level.lower()
    if key not in _ALLOCATIONS:
        raise ValueError(f"Unknown risk level: {risk_level!r}. Must be low, medium, or high.")
    return _ALLOCATIONS[key]
