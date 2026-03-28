import re

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core import run_llm
from services.performance_service import PerformanceResult, period_for_risk, simulate_portfolio
from services.portfolio_service import Allocation, apply_interest_tilts, get_allocations
from utils.logger import log_info, log_success

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["POST"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: str
    user_profile: dict = {}


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    simulations: list | None = None


class PortfolioRequest(BaseModel):
    age: int
    riskLevel: str
    horizon: int
    interests: list[str] = []


class PortfolioResponse(BaseModel):
    allocations: list[Allocation]
    age: int
    riskLevel: str
    horizon: int


class PerformanceRequest(BaseModel):
    allocations: list[dict]  # [{"ticker": str, "weight": int}]
    riskLevel: str


def _strip_source_suffix(text: str) -> str:
    """Remove 'Source: ...' lines appended by the LLM (inline or trailing)."""
    return re.sub(r"\n?Source:[^\n]*", "", text, flags=re.IGNORECASE).strip()


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    log_info(f"[/chat] session={req.session_id} message: {req.message}")
    result = run_llm(query=req.message, session_id=req.session_id, user_profile=req.user_profile)
    raw_sources = [
        str(doc.metadata.get("source") or "Unknown")
        for doc in (result.get("context") or [])
        if getattr(doc, "metadata", None) is not None
    ] + (result.get("news_urls") or [])
    sources = list(dict.fromkeys(raw_sources))  # deduplicate, preserve order
    answer = _strip_source_suffix(result["answer"])
    simulations = result.get("simulations") or None
    log_success(f"[/chat] answer: {answer[:120]}{'...' if len(answer) > 120 else ''} | sources: {len(sources)} | simulations: {len(simulations) if simulations else 0}")
    return ChatResponse(answer=answer, sources=sources, simulations=simulations)


@app.post("/portfolio", response_model=PortfolioResponse)
def portfolio(req: PortfolioRequest):
    log_info(f"[/portfolio] age={req.age}, riskLevel={req.riskLevel}, horizon={req.horizon}")
    allocations = apply_interest_tilts(get_allocations(req.riskLevel), req.interests)
    response = PortfolioResponse(
        allocations=allocations,
        age=req.age,
        riskLevel=req.riskLevel,
        horizon=req.horizon,
    )
    log_success(f"[/portfolio] allocations: {[f'{a.ticker} {a.weight}%' for a in allocations]}")
    return response


@app.post("/portfolio/performance", response_model=PerformanceResult)
def portfolio_performance(req: PerformanceRequest):
    log_info(f"[/portfolio/performance] riskLevel={req.riskLevel}, tickers={[a['ticker'] for a in req.allocations]}")
    try:
        period = period_for_risk(req.riskLevel)
        result = simulate_portfolio(req.allocations, period)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    log_success(f"[/portfolio/performance] period={result.period}, total_return={result.total_return_pct}%, points={len(result.data_points)}")
    return result
