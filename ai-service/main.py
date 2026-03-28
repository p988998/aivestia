import json
import re
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core import run_llm, set_langgraph_app
from database import DATABASE_URL, get_conn, init_db
from graph.graph import build_graph
from services.performance_service import PerformanceResult, period_for_risk, simulate_portfolio
from services.portfolio_service import Allocation, apply_interest_tilts, get_allocations
from utils.logger import log_info, log_success


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    from langgraph.checkpoint.postgres import PostgresSaver
    with PostgresSaver.from_conn_string(DATABASE_URL) as checkpointer:
        checkpointer.setup()
        set_langgraph_app(build_graph(checkpointer))
        yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)


# ---------- Pydantic models ----------

class ChatRequest(BaseModel):
    message: str
    chat_id: str
    user_id: str
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
    allocations: list[dict]
    riskLevel: str


class ChatMeta(BaseModel):
    id: str
    title: str
    updated_at: str


class MessageOut(BaseModel):
    role: str
    content: str
    sources: list[str] = []
    simulations: list | None = None


# ---------- Helpers ----------

def _strip_source_suffix(text: str) -> str:
    return re.sub(r"\n?Source:[^\n]*", "", text, flags=re.IGNORECASE).strip()


# ---------- User endpoints ----------

@app.post("/users", status_code=201)
def create_user(user_id: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO users (id) VALUES (%s) ON CONFLICT DO NOTHING",
            (user_id,),
        )
    return {"user_id": user_id}


# ---------- Chat endpoints ----------

@app.get("/users/{user_id}/chats", response_model=list[ChatMeta])
def list_chats(user_id: str):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, title, updated_at FROM chats WHERE user_id = %s ORDER BY updated_at DESC",
            (user_id,),
        ).fetchall()
    return [{"id": str(r["id"]), "title": r["title"], "updated_at": str(r["updated_at"])} for r in rows]


@app.post("/users/{user_id}/chats", status_code=201, response_model=ChatMeta)
def create_chat(user_id: str):
    chat_id = str(uuid.uuid4())
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO chats (id, user_id) VALUES (%s, %s)",
            (chat_id, user_id),
        )
    return {"id": chat_id, "title": "New Chat", "updated_at": ""}


@app.patch("/chats/{chat_id}/title", status_code=204)
def update_chat_title(chat_id: str, title: str):
    with get_conn() as conn:
        conn.execute("UPDATE chats SET title = %s WHERE id = %s", (title[:60], chat_id))


@app.delete("/chats/{chat_id}", status_code=204)
def delete_chat(chat_id: str):
    with get_conn() as conn:
        conn.execute("DELETE FROM chats WHERE id = %s", (chat_id,))


@app.get("/chats/{chat_id}/messages", response_model=list[MessageOut])
def get_messages(chat_id: str):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT role, content, sources, simulations FROM messages WHERE chat_id = %s ORDER BY created_at",
            (chat_id,),
        ).fetchall()
    return [
        {
            "role": r["role"],
            "content": r["content"],
            "sources": r["sources"] or [],
            "simulations": r["simulations"],
        }
        for r in rows
    ]


# ---------- Chat (LLM) endpoint ----------

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    log_info(f"[/chat] chat={req.chat_id} message: {req.message}")
    result = run_llm(query=req.message, session_id=req.chat_id, user_profile=req.user_profile)
    raw_sources = [
        str(doc.metadata.get("source") or "Unknown")
        for doc in (result.get("context") or [])
        if getattr(doc, "metadata", None) is not None
    ] + (result.get("news_urls") or [])
    sources = list(dict.fromkeys(raw_sources))
    answer = _strip_source_suffix(result["answer"])
    simulations = result.get("simulations") or None

    with get_conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS cnt FROM messages WHERE chat_id = %s", (req.chat_id,)
        ).fetchone()
        is_first = row["cnt"] == 0

        conn.execute(
            "INSERT INTO messages (chat_id, role, content, sources, simulations) VALUES (%s, %s, %s, %s, %s)",
            (req.chat_id, "user", req.message, json.dumps([]), None),
        )
        conn.execute(
            "INSERT INTO messages (chat_id, role, content, sources, simulations) VALUES (%s, %s, %s, %s, %s)",
            (req.chat_id, "assistant", answer, json.dumps(sources), json.dumps(simulations) if simulations else None),
        )

        if is_first:
            conn.execute(
                "UPDATE chats SET title = %s, updated_at = NOW() WHERE id = %s",
                (req.message[:40], req.chat_id),
            )
        else:
            conn.execute(
                "UPDATE chats SET updated_at = NOW() WHERE id = %s",
                (req.chat_id,),
            )

    log_success(f"[/chat] answer: {answer[:120]}{'...' if len(answer) > 120 else ''} | sources: {len(sources)} | simulations: {len(simulations) if simulations else 0}")
    return ChatResponse(answer=answer, sources=sources, simulations=simulations)


# ---------- Portfolio endpoints ----------

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
