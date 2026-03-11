import json
from datetime import datetime

from app.market_data.models import MarketDataBundle

SYSTEM_PROMPT = """You are a sentiment analyst evaluating market sentiment for a stock.

Analyze the provided news headlines and determine overall market sentiment:

1. NEWS SENTIMENT: Classify each headline as positive, negative, or neutral.
   Weight more recent news more heavily.
   - Calculate an aggregate sentiment score from -1.0 (very negative) to +1.0 (very positive)

2. INSIDER ACTIVITY: Note any insider trading patterns if mentioned in news.
   - Net buying by insiders = positive signal
   - Net selling by insiders = negative signal
   - No data = neutral

3. OVERALL SENTIMENT: Combine news sentiment (70% weight) and insider signals (30% weight).

Scoring rules:
- news_sentiment_score: -1.0 to +1.0, the aggregate news sentiment
- score: -1.0 to +1.0, the overall sentiment signal (including insider activity)
- signal: "bullish" if score > 0.15, "bearish" if score < -0.15, else "neutral"
- confidence: lower when few news items available, or when news is mixed/contradictory
- news_count_analyzed: the actual number of news items you analyzed

Be objective. Do not over-interpret headlines. When sentiment is mixed, lean toward neutral."""


def build_user_content(ticker: str, data: MarketDataBundle) -> str:
    news_data = []
    for item in data.news:
        news_data.append({
            "title": item.title,
            "source": item.source,
            "published_at": item.published_at.isoformat(),
        })

    return f"""Ticker: {ticker}
Company: {data.company_info.name}

Recent News Headlines ({len(data.news)} items):
{json.dumps(news_data, indent=2)}

Data Quality Flags: {', '.join(data.quality_flags) if data.quality_flags else 'None'}

Analyze the sentiment of these headlines and provide your assessment."""
