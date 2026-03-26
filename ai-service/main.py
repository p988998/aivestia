import re

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core import run_llm
from services.portfolio_service import Allocation, get_allocations
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


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]


class PortfolioRequest(BaseModel):
    age: int
    riskLevel: str
    horizon: int


class PortfolioResponse(BaseModel):
    allocations: list[Allocation]
    age: int
    riskLevel: str
    horizon: int


def _strip_source_suffix(text: str) -> str:
    """Remove 'Source: ...' lines appended by the LLM (inline or trailing)."""
    return re.sub(r"\n?Source:[^\n]*", "", text, flags=re.IGNORECASE).strip()


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    log_info(f"[/chat] session={req.session_id} message: {req.message}")
    result = run_llm(query=req.message, session_id=req.session_id)
    raw_sources = [
        str(doc.metadata.get("source") or "Unknown")
        for doc in (result.get("context") or [])
        if getattr(doc, "metadata", None) is not None
    ] + (result.get("news_urls") or [])
    sources = list(dict.fromkeys(raw_sources))  # deduplicate, preserve order
    answer = _strip_source_suffix(result["answer"])
    log_success(f"[/chat] answer: {answer[:120]}{'...' if len(answer) > 120 else ''} | sources: {len(sources)}")
    return ChatResponse(answer=answer, sources=sources)


@app.post("/portfolio", response_model=PortfolioResponse)
def portfolio(req: PortfolioRequest):
    log_info(f"[/portfolio] age={req.age}, riskLevel={req.riskLevel}, horizon={req.horizon}")
    allocations = get_allocations(req.riskLevel)
    response = PortfolioResponse(
        allocations=allocations,
        age=req.age,
        riskLevel=req.riskLevel,
        horizon=req.horizon,
    )
    log_success(f"[/portfolio] allocations: {[f'{a.ticker} {a.weight}%' for a in allocations]}")
    return response
