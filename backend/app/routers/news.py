from fastapi import APIRouter
from ai.sentiment.pipeline import get_latest_headlines, compute_sentiment_score
from backend.app.schemas.schemas import NewsItem

router = APIRouter(prefix="/news", tags=["News & Sentiment"])

@router.get("/{ticker}", response_model=list[NewsItem])
def get_asset_news(ticker: str):
    """
    Returns latest FinBERT scored news headlines for the given asset.
    """
    headlines = get_latest_headlines(ticker, limit=10)
    return [NewsItem(
        headline=h["headline"],
        source=h.get("source"),
        sentiment_score=h["sentiment_score"],
        finbert_label=h["finbert_label"],
        published_at=h["published_at"],
        hours_ago=h.get("hours_ago")
    ) for h in headlines]
