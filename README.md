# Aivestia — AI Investment Advisor

[中文](README.zh.md)

> An educational demo of an AI-driven investment advisor. Not a licensed financial product.

**Live Demo:** https://www.aivestia.xyz

---

## Features

| | |
|---|---|
| 🤖 **Conversational AI Advisor** | Ask anything about ETFs, risk levels, market trends, or portfolio strategies via a streaming chat interface |
| 🎯 **Personalized Portfolio Recommendations** | Rule-based allocation engine adjusted by user age, risk tolerance, investment horizon, and interests |
| 🔀 **Dual-Agent Architecture** | LangGraph routes queries to a Chat Agent (market info) or Portfolio Agent (personalized recommendations) based on intent |
| 🛡️ **Hallucination Detection** | A dedicated verification node validates all answers against tool outputs before the final response is generated |
| 📈 **Historical Portfolio Simulation** | Compare your current holdings vs. the recommended portfolio with real historical performance data |
| 📡 **Real-Time Market Data** | Live stock prices, 52-week highs/lows, and recent news via Yahoo Finance and Finnhub |
| 🧠 **RAG Investment Knowledge Base** | Pinecone vector store with 60+ pages of investment concepts (ETFs, asset allocation, Modern Portfolio Theory) |
| 💬 **Persistent Chat History** | Full conversation history stored in PostgreSQL with LangGraph checkpoint support |

---

## Architecture

### LangGraph Agent Flow

![LangGraph Architecture](ai-service/graph.png)

```
User Message
     │
     ▼
  ┌──────┐
  │Router│  (gpt-4o-mini — classifies intent)
  └──┬───┘
     │
     ├─────────────────────┐
     ▼                     ▼
┌──────────┐        ┌───────────────┐
│Chat Agent│        │Portfolio Agent│
│ gpt-5.4  │        │   gpt-5.4     │
│          │        │               │
│ Tools:   │        │ Tools:        │
│ · price  │        │ · allocation  │
│ · news   │        │ · simulation  │
│ · RAG    │        │ · holdings    │
│ · sim*   │        │ · price/news  │
└────┬─────┘        └──────┬────────┘
     │                     │
     └──────────┬──────────┘
                ▼
     ┌──────────────────┐
     │Hallucination Check│  (gpt-4o-mini — binary grounding score)
     └────────┬─────────┘
              │
        ┌─────┴──────┐
        │ grounded?  │
        │  yes → FinalLLM
        │  no  → retry (max 2)
        └────────────┘
                ▼
          ┌──────────┐
          │ Final LLM│  (gpt-4o — polished user-facing response)
          └──────────┘
```

\* Chat Agent can also run simulations when explicitly requested.

### Deployment

```
Browser → Vercel (React SPA)
              │
              ▼ HTTPS
         Nginx (rate limiting + reverse proxy)
              │
              ▼
         AWS EC2 (FastAPI + uvicorn)
              │
    ┌─────────┼──────────┬────────────┐
    ▼         ▼          ▼            ▼
 AWS RDS   Pinecone  Yahoo Finance  Finnhub
(PostgreSQL) (vectors)  (prices)    (news)
```

---

## Tech Stack

### Backend
| | |
|---|---|
| **FastAPI** | REST API + SSE streaming |
| **LangGraph** | Multi-agent orchestration with PostgreSQL checkpointer |
| **LangChain** | Agent framework, tool integration, RAG pipeline |
| **OpenAI** | GPT-5.4 (agents) · GPT-4o (final LLM) · text-embedding-3-small (RAG) |
| **PostgreSQL** | Chat history · user data · LangGraph state persistence |
| **Pinecone** | Vector store for investment knowledge retrieval |
| **yfinance** | Historical and real-time market data |
| **Finnhub** | Company news API |

### Frontend
| | |
|---|---|
| **React 19** | UI framework |
| **Vite** | Build tool |
| **Recharts** | Portfolio performance charts |
| **SSE** | Real-time streaming responses |

### Infrastructure
| | |
|---|---|
| **AWS EC2** | Backend hosting |
| **AWS RDS** | Managed PostgreSQL |
| **Nginx** | Reverse proxy · rate limiting |
| **Vercel** | Frontend deployment |

---

## Project Structure

```
aivestia/
├── ai-service/
│   ├── main.py                  # FastAPI app — all REST endpoints
│   ├── core.py                  # LangGraph stream/invoke wrappers
│   ├── database.py              # PostgreSQL connection + schema init
│   ├── ingestion.py             # RAG pipeline: crawl → chunk → embed → Pinecone
│   ├── graph/
│   │   ├── graph.py             # LangGraph workflow definition
│   │   ├── state.py             # GraphState TypedDict
│   │   └── nodes/               # Router, Chat Agent, Portfolio Agent, Hallucination Check, Final LLM
│   ├── agents/
│   │   ├── chat_agent.py        # General-purpose market info agent
│   │   └── portfolio_agent.py   # Personalized portfolio recommendation agent
│   ├── services/
│   │   ├── portfolio_service.py # Rule-based allocation engine + interest tilts
│   │   ├── performance_service.py # Historical simulation
│   │   └── market_data_service.py # yfinance wrapper
│   └── tools/                   # LangChain tool definitions
│
└── frontend/
    └── src/
        ├── pages/               # HomePage, ChatPage, HowItWorksPage, AboutPage
        └── components/          # SimulationCard, PortfolioForm, SuggestionBar, ...
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/users` | Create or update user (records IP) |
| `GET` | `/users/{user_id}/chats` | List user's chat sessions |
| `POST` | `/users/{user_id}/chats` | Create a new chat session |
| `PATCH` | `/chats/{chat_id}/title` | Rename a chat |
| `DELETE` | `/chats/{chat_id}` | Delete a chat and its messages |
| `GET` | `/chats/{chat_id}/messages` | Fetch chat message history |
| `POST` | `/chat/stream` | **Streaming chat via SSE** (main endpoint) |
| `POST` | `/portfolio` | Get rule-based portfolio allocation |
| `POST` | `/portfolio/performance` | Run historical portfolio simulation |
| `POST` | `/suggestions` | Generate 3 follow-up question suggestions |

API docs available at `/docs` when `ENV=dev`.

---

## Portfolio Allocation Logic

Portfolio allocation is fully **deterministic** — no AI involved in investment decisions.

**Baseline allocations by risk level:**

| Risk | VTI | VXUS | BND |
|------|-----|------|-----|
| Low | 30% | 20% | 50% |
| Medium | 60% | 30% | 10% |
| High | 80% | 20% | — |

**Interest tilts** adjust the baseline by adding exposure to:
`Tech & Growth` · `Dividend Income` · `ESG` · `International` · `REITs` · `Bonds` · `Value` · `Small & Mid Cap`

Up to 3 interests are applied (primary +10%, secondary +5%), capped at a 20% total shift.

---

## Disclaimer

Aivestia is an **educational demo** and is not a licensed financial advisor, broker, or investment product. All portfolio suggestions are for demonstration purposes only and do not constitute investment advice. Always consult a qualified financial professional before making investment decisions.

---

## Contact

aivestia.ai@gmail.com
