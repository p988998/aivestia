from collections import defaultdict
from dataclasses import dataclass

from pydantic import BaseModel


class Allocation(BaseModel):
    ticker: str
    name: str
    weight: int
    color: str


@dataclass
class TiltRule:
    add_ticker: str
    add_name: str
    add_color: str
    reduce_tickers: list[str]  # priority order — only baseline tickers (VTI/VXUS/BND)


# Metadata for tickers that may be introduced by tilts (not in baseline)
_TICKER_META: dict[str, tuple[str, str]] = {
    "VUG":  ("Growth",        "#4f46e5"),
    "VYM":  ("Dividend",      "#06b6d4"),
    "VNQ":  ("Real Estate",   "#10b981"),
    "VTV":  ("Value",         "#f59e0b"),
    "VB":   ("Small & Mid",   "#f97316"),
    "ESGV": ("ESG",           "#22c55e"),
    # baseline tickers also listed for completeness
    "VTI":  ("US Total Market", "#6366f1"),
    "VXUS": ("International",   "#8b5cf6"),
    "BND":  ("US Bonds",        "#a78bfa"),
}

_TILT_RULES: dict[str, TiltRule] = {
    "Tech & Growth":         TiltRule("VUG",  "Growth",      "#4f46e5", ["BND",  "VXUS"]),
    "International Markets": TiltRule("VXUS", "International","#8b5cf6", ["VTI",  "BND"]),
    "Bonds & Fixed Income":  TiltRule("BND",  "US Bonds",    "#a78bfa", ["VTI",  "VXUS"]),
    "Dividend Income":       TiltRule("VYM",  "Dividend",    "#06b6d4", ["VTI",  "BND"]),
    "REITs / Real Estate":   TiltRule("VNQ",  "Real Estate", "#10b981", ["VTI",  "BND"]),
    "Value Investing":       TiltRule("VTV",  "Value",       "#f59e0b", ["VTI",  "BND"]),
    "Small & Mid Cap":       TiltRule("VB",   "Small & Mid", "#f97316", ["VTI",  "VXUS"]),
    "ESG / Sustainable":     TiltRule("ESGV", "ESG",         "#22c55e", ["BND",  "VTI"]),
}

_PRIMARY_SHIFT   = 10.0
_SECONDARY_SHIFT =  5.0
_MAX_TOTAL_SHIFT = 20.0

_ALLOCATIONS: dict[str, list[Allocation]] = {
    "low": [
        Allocation(ticker="VTI",  name="US Total Market", weight=30, color="#6366f1"),
        Allocation(ticker="VXUS", name="International",   weight=20, color="#8b5cf6"),
        Allocation(ticker="BND",  name="US Bonds",        weight=50, color="#a78bfa"),
    ],
    "medium": [
        Allocation(ticker="VTI",  name="US Total Market", weight=60, color="#6366f1"),
        Allocation(ticker="VXUS", name="International",   weight=30, color="#8b5cf6"),
        Allocation(ticker="BND",  name="US Bonds",        weight=10, color="#a78bfa"),
    ],
    "high": [
        Allocation(ticker="VTI",  name="US Total Market", weight=80, color="#6366f1"),
        Allocation(ticker="VXUS", name="International",   weight=20, color="#8b5cf6"),
    ],
}


def get_allocations(risk_level: str) -> list[Allocation]:
    key = risk_level.lower()
    if key not in _ALLOCATIONS:
        raise ValueError(f"Unknown risk level: {risk_level!r}. Must be low, medium, or high.")
    return _ALLOCATIONS[key]


def apply_interest_tilts(
    base_allocations: list[Allocation],
    interests: list[str],
) -> list[Allocation]:
    """Apply interest-based tilts on top of the baseline allocation.

    Algorithm:
    1. Assign shifts: primary=10%, secondary=5%, total capped at 20%
       (primary preserved, secondary scaled down proportionally if cap exceeded)
    2. available_capacity tracks how much each baseline ticker can still be reduced
       (prevents over-committing the same source asset across multiple interests)
    3. For each interest, build a reduce_pool from the priority list
       (all tickers with available_capacity > 0); fall back to top-2 largest holders
    4. actual_shift = min(shift, total_capacity) — prevents shift from being "lost"
    5. Distribute actual_shift proportionally across reduce_pool by capacity
    6. Aggregate all adjustments, apply, clamp ≥ 0, normalize to 100%, round
    """
    if not interests:
        return base_allocations

    interests = interests[:3]  # safety cap

    # Working portfolio: ticker → {weight (float), name, color}
    portfolio: dict[str, dict] = {
        a.ticker: {"weight": float(a.weight), "name": a.name, "color": a.color}
        for a in base_allocations
    }

    # available_capacity is a separate budget tracker — baseline weights only
    available_capacity: dict[str, float] = {
        t: v["weight"] for t, v in portfolio.items()
    }

    # ── Assign planned shifts ─────────────────────────────────────────────────
    planned_shifts = [_PRIMARY_SHIFT if i == 0 else _SECONDARY_SHIFT for i in range(len(interests))]

    total_planned = sum(planned_shifts)
    if total_planned > _MAX_TOTAL_SHIFT:
        primary = planned_shifts[0]
        remaining_budget = _MAX_TOTAL_SHIFT - primary
        secondary_total = sum(planned_shifts[1:])
        if secondary_total > 0:
            scale = remaining_budget / secondary_total
            planned_shifts = [primary] + [s * scale for s in planned_shifts[1:]]

    # ── Build and apply adjustments ───────────────────────────────────────────
    adjustments: dict[str, float] = defaultdict(float)

    for interest, shift in zip(interests, planned_shifts):
        rule = _TILT_RULES.get(interest)
        if not rule:
            continue

        add_ticker = rule.add_ticker

        # reduce_pool: priority list filtered to tickers with available capacity
        reduce_pool = [t for t in rule.reduce_tickers if available_capacity.get(t, 0) > 0]

        # fallback: top-2 largest available holdings (excluding add_ticker)
        if not reduce_pool:
            candidates = sorted(
                [(t, available_capacity[t]) for t in portfolio
                 if t != add_ticker and available_capacity.get(t, 0) > 0],
                key=lambda x: x[1],
                reverse=True,
            )
            reduce_pool = [t for t, _ in candidates[:2]]

        total_capacity = sum(available_capacity[t] for t in reduce_pool)
        if total_capacity <= 1e-6:
            continue  # nothing left to reduce — skip this interest

        # Cap shift at available capacity (prevents budget from being "lost")
        # Since actual_shift ≤ total_capacity, each portion ≤ capacity[t] — no min() needed
        actual_shift = min(shift, total_capacity)

        for t in reduce_pool:
            portion = available_capacity[t] / total_capacity * actual_shift
            available_capacity[t]   -= portion
            adjustments[add_ticker] += portion
            adjustments[t]          -= portion

    # ── Apply aggregated adjustments ─────────────────────────────────────────
    for ticker, delta in adjustments.items():
        if ticker not in portfolio:
            name, color = _TICKER_META.get(ticker, (ticker, "#94a3b8"))
            portfolio[ticker] = {"weight": 0.0, "name": name, "color": color}
        portfolio[ticker]["weight"] += delta

    # ── Clamp, normalize, round ───────────────────────────────────────────────
    for v in portfolio.values():
        v["weight"] = max(v["weight"], 0.0)

    total = sum(v["weight"] for v in portfolio.values())
    if total <= 0:
        return base_allocations  # degenerate — return unchanged

    for v in portfolio.values():
        v["weight"] = v["weight"] / total * 100

    result = [
        Allocation(ticker=t, name=v["name"], weight=round(v["weight"]), color=v["color"])
        for t, v in portfolio.items()
        if round(v["weight"]) > 0
    ]

    # Fix rounding drift: ensure sum == 100 exactly
    total_rounded = sum(a.weight for a in result)
    if total_rounded != 100 and result:
        diff = 100 - total_rounded
        largest_idx = max(range(len(result)), key=lambda i: result[i].weight)
        result[largest_idx] = result[largest_idx].model_copy(
            update={"weight": result[largest_idx].weight + diff}
        )

    return result
