from typing import Any, Dict

from dotenv import load_dotenv

load_dotenv()

_app = None


def set_langgraph_app(app) -> None:
    global _app
    _app = app


def run_llm(query: str, session_id: str, user_profile: dict = {}) -> Dict[str, Any]:
    return _app.invoke(
        {"question": query, "user_profile": user_profile},
        config={"configurable": {"thread_id": session_id}},
    )
