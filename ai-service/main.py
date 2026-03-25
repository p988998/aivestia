import re

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core import run_llm

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["POST"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]


def _strip_source_suffix(text: str) -> str:
    """Remove 'Source: ...' lines appended by the LLM (inline or trailing)."""
    return re.sub(r"\n?Source:[^\n]*", "", text, flags=re.IGNORECASE).strip()


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    result = run_llm(query=req.message)
    raw_sources = [
        str(doc.metadata.get("source") or "Unknown")
        for doc in (result.get("context") or [])
        if getattr(doc, "metadata", None) is not None
    ] + (result.get("news_urls") or [])
    sources = list(dict.fromkeys(raw_sources))  # deduplicate, preserve order
    answer = _strip_source_suffix(result["answer"])
    return ChatResponse(answer=answer, sources=sources)
