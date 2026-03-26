from typing import Any, Dict

from dotenv import load_dotenv

load_dotenv()

from graph.graph import app


def run_llm(query: str, session_id: str) -> Dict[str, Any]:
    return app.invoke(
        {"question": query},
        config={"configurable": {"thread_id": session_id}},
    )


if __name__ == "__main__":
    result = run_llm(query="What's the difference between trading and investing?")
    print(result)
