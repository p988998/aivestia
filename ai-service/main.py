import json
import os
import re
import uuid
import warnings
from contextlib import asynccontextmanager

warnings.filterwarnings("ignore", message="Pydantic serializer warnings", category=UserWarning)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from core import run_llm, set_langgraph_app, stream_llm
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


ENV = os.getenv("ENV")

app = FastAPI(
    lifespan=lifespan,
    docs_url="/docs" if ENV == "dev" else None,
    redoc_url="/redoc" if ENV == "dev" else None,
)

_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,https://aivestia.vercel.app,https://www.aivestia.xyz").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
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


class SuggestionsRequest(BaseModel):
    last_message: str


class SuggestionsResponse(BaseModel):
    suggestions: list[str]


class SuggestionsRequest(BaseModel):
    last_message: str


class SuggestionsResponse(BaseModel):
    suggestions: list[str]


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


# ---------- Suggestions endpoint ----------

@app.post("/suggestions", response_model=SuggestionsResponse)
def get_suggestions(req: SuggestionsRequest):
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    prompt = f"""
You are a financial assistant.

Based on the following response, generate exactly 3 follow-up questions.

Requirements:
- 5-10 words each
- Specific and actionable
- Investment-related

Return JSON:
{{
  "questions": ["...", "...", "..."]
}}

Response:
{req.last_message[:800]}
"""
    fallback = [
        "Compare with S&P 500?",
        "What are the risks here?",
        "How can I improve this portfolio?",
    ]
    try:
        result = llm.invoke(prompt)
        data = json.loads(result.content)
        questions = data.get("questions", [])
        seen = set()
        clean_q = []
        for q in questions:
            q = q.strip()
            if not q.endswith("?"):
                q += "?"
            if 5 <= len(q.split()) <= 10 and q not in seen:
                seen.add(q)
                clean_q.append(q)
        return SuggestionsResponse(suggestions=clean_q[:3] if len(clean_q) >= 3 else fallback)
    except Exception:
        return SuggestionsResponse(suggestions=fallback)


# ---------- Chat (LLM) endpoints ----------

@app.post("/chat/stream")
def chat_stream(req: ChatRequest):
    def generate():
        final_vals = {}
        try:
            for event_type, data in stream_llm(req.message, req.chat_id, req.user_profile):
                if event_type == "status":
                    yield f"event: status\ndata: {json.dumps({'message': data})}\n\n"
                elif event_type == "retry":
                    yield f"event: retry\ndata: {json.dumps({'reason': data})}\n\n"
                elif event_type == "token":
                    yield f"event: token\ndata: {json.dumps(data)}\n\n"
                elif event_type == "done":
                    final_vals = data
        except Exception:
            yield f"event: token\ndata: {json.dumps('Sorry, the AI service is unavailable.')}\n\n"

        answer = _strip_source_suffix(final_vals.get("answer", ""))
        raw_sources = [
            str(doc.metadata.get("source") or "Unknown")
            for doc in (final_vals.get("context") or [])
            if getattr(doc, "metadata", None) is not None
        ] + (final_vals.get("news_urls") or [])
        sources = list(dict.fromkeys(raw_sources))
        simulations = final_vals.get("simulations") or None

        with get_conn() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS cnt FROM messages WHERE chat_id = %s", (req.chat_id,)
            ).fetchone()
            is_first = row["cnt"] == 0
            conn.execute(
                "INSERT INTO messages (chat_id, role, content, sources, simulations) VALUES (%s,%s,%s,%s,%s)",
                (req.chat_id, "user", req.message, json.dumps([]), None),
            )
            conn.execute(
                "INSERT INTO messages (chat_id, role, content, sources, simulations) VALUES (%s,%s,%s,%s,%s)",
                (req.chat_id, "assistant", answer, json.dumps(sources), json.dumps(simulations) if simulations else None),
            )
            if is_first:
                conn.execute(
                    "UPDATE chats SET title = %s, updated_at = NOW() WHERE id = %s",
                    (req.message[:40], req.chat_id),
                )
            else:
                conn.execute("UPDATE chats SET updated_at = NOW() WHERE id = %s", (req.chat_id,))

        yield f"event: done\ndata: {json.dumps({'sources': sources, 'simulations': simulations, 'answer': answer})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


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
