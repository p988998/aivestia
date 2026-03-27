import os
from datetime import date, datetime, timedelta, timezone

import finnhub
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

finnhub_client = finnhub.Client(api_key=os.environ["FINNHUB_API_KEY"])


class NewsArticle(BaseModel):
    headline: str
    summary: str
    source: str
    url: str
    published_at: str


def get_market_news(ticker: str, days: int = 7, limit: int = 5) -> list[NewsArticle]:
    try:
        to_date = date.today()
        from_date = to_date - timedelta(days=days)
        raw = finnhub_client.company_news(
            ticker.upper(),
            _from=from_date.isoformat(),
            to=to_date.isoformat(),
        )
        return [
            NewsArticle(
                headline=item.get("headline", ""),
                summary=item.get("summary", ""),
                source=item.get("source", ""),
                url=item.get("url", ""),
                published_at=datetime.fromtimestamp(item["datetime"], tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            )
            for item in raw[:limit]
        ]
    except Exception as e:
        raise ValueError(f"Failed to fetch news for '{ticker.upper()}': {e}")


if __name__ == "__main__":
    articles = get_market_news("AAPL")
    for a in articles:
        print(a)
