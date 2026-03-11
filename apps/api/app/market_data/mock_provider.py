"""Mock market data provider with realistic synthetic data for development."""

import hashlib
import math
from datetime import date, datetime, timedelta, timezone

from app.market_data.models import (
    CompanyInfo,
    FinancialPeriod,
    MarketDataBundle,
    NewsItem,
    PriceBar,
)
from app.market_data.provider import MarketDataProvider

# Realistic base data for common tickers
COMPANY_DATA: dict[str, dict] = {
    "AAPL": {
        "name": "Apple Inc.",
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "market_cap": 3_200_000_000_000,
        "base_price": 195.0,
        "revenue": 383_000_000_000,
        "net_income": 97_000_000_000,
        "eps": 6.42,
        "pe_ratio": 30.4,
        "roe": 1.60,
        "debt_to_equity": 1.76,
        "current_ratio": 0.99,
        "gross_margin": 0.458,
        "operating_margin": 0.302,
        "net_margin": 0.253,
        "revenue_growth": 0.02,
    },
    "MSFT": {
        "name": "Microsoft Corporation",
        "sector": "Technology",
        "industry": "Software - Infrastructure",
        "market_cap": 3_100_000_000_000,
        "base_price": 420.0,
        "revenue": 227_000_000_000,
        "net_income": 86_000_000_000,
        "eps": 11.53,
        "pe_ratio": 36.4,
        "roe": 0.39,
        "debt_to_equity": 0.42,
        "current_ratio": 1.77,
        "gross_margin": 0.695,
        "operating_margin": 0.445,
        "net_margin": 0.379,
        "revenue_growth": 0.16,
    },
    "NVDA": {
        "name": "NVIDIA Corporation",
        "sector": "Technology",
        "industry": "Semiconductors",
        "market_cap": 2_800_000_000_000,
        "base_price": 880.0,
        "revenue": 79_000_000_000,
        "net_income": 43_000_000_000,
        "eps": 1.74,
        "pe_ratio": 65.0,
        "roe": 1.15,
        "debt_to_equity": 0.41,
        "current_ratio": 4.17,
        "gross_margin": 0.738,
        "operating_margin": 0.621,
        "net_margin": 0.544,
        "revenue_growth": 1.22,
    },
    "TSLA": {
        "name": "Tesla, Inc.",
        "sector": "Consumer Cyclical",
        "industry": "Auto Manufacturers",
        "market_cap": 780_000_000_000,
        "base_price": 245.0,
        "revenue": 97_000_000_000,
        "net_income": 7_900_000_000,
        "eps": 2.49,
        "pe_ratio": 98.4,
        "roe": 0.20,
        "debt_to_equity": 0.11,
        "current_ratio": 1.73,
        "gross_margin": 0.182,
        "operating_margin": 0.082,
        "net_margin": 0.081,
        "revenue_growth": 0.19,
    },
    "GOOGL": {
        "name": "Alphabet Inc.",
        "sector": "Communication Services",
        "industry": "Internet Content & Information",
        "market_cap": 2_100_000_000_000,
        "base_price": 172.0,
        "revenue": 340_000_000_000,
        "net_income": 85_000_000_000,
        "eps": 6.89,
        "pe_ratio": 24.9,
        "roe": 0.31,
        "debt_to_equity": 0.05,
        "current_ratio": 2.10,
        "gross_margin": 0.574,
        "operating_margin": 0.322,
        "net_margin": 0.250,
        "revenue_growth": 0.13,
    },
}

NEWS_TEMPLATES = [
    "{company} reports strong quarterly earnings, beating analyst estimates",
    "Analysts upgrade {company} citing growth in AI segment",
    "{company} announces strategic partnership to expand market presence",
    "Institutional investors increase positions in {company}",
    "{company} faces regulatory scrutiny over market practices",
    "Supply chain concerns weigh on {company} outlook",
    "{company} CEO discusses innovation roadmap at industry conference",
    "Market volatility impacts {company} as sector rotates",
]


def _deterministic_random(seed: str, index: int) -> float:
    """Generate a deterministic pseudo-random float in [0, 1) from a seed string."""
    h = hashlib.md5(f"{seed}:{index}".encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


class MockMarketDataProvider(MarketDataProvider):
    async def get_bundle(self, ticker: str) -> MarketDataBundle:
        data = COMPANY_DATA.get(ticker.upper())
        if data is None:
            # Generate generic data for unknown tickers
            data = {
                "name": f"{ticker.upper()} Corp",
                "sector": "Unknown",
                "industry": "Unknown",
                "market_cap": 50_000_000_000,
                "base_price": 100.0,
                "revenue": 10_000_000_000,
                "net_income": 1_000_000_000,
                "eps": 3.50,
                "pe_ratio": 28.6,
                "roe": 0.15,
                "debt_to_equity": 0.50,
                "current_ratio": 1.50,
                "gross_margin": 0.40,
                "operating_margin": 0.15,
                "net_margin": 0.10,
                "revenue_growth": 0.05,
            }

        prices = self._generate_prices(ticker, data["base_price"])
        financials = self._generate_financials(ticker, data)
        company_info = CompanyInfo(
            ticker=ticker.upper(),
            name=data["name"],
            sector=data.get("sector"),
            industry=data.get("industry"),
            market_cap=data.get("market_cap"),
        )
        news = self._generate_news(ticker, data["name"])

        return MarketDataBundle(
            ticker=ticker.upper(),
            prices=prices,
            financials=financials,
            company_info=company_info,
            news=news,
            quality_flags=["demo_data"],
        )

    def _generate_prices(self, ticker: str, base_price: float, days: int = 252) -> list[PriceBar]:
        """Generate realistic price data using seeded random walk."""
        prices = []
        price = base_price
        today = date.today()

        for i in range(days, 0, -1):
            d = today - timedelta(days=i)
            # Skip weekends
            if d.weekday() >= 5:
                continue

            r = _deterministic_random(ticker, i)
            # Daily return: slight upward drift + noise
            daily_return = 0.0003 + (r - 0.5) * 0.04
            price = price * (1 + daily_return)

            # Generate OHLV from close
            r2 = _deterministic_random(ticker, i + 10000)
            r3 = _deterministic_random(ticker, i + 20000)
            spread = price * 0.015
            high = price + spread * r2
            low = price - spread * r3
            open_price = price + (r2 - 0.5) * spread * 0.5

            volume = int(30_000_000 + (r - 0.5) * 20_000_000)

            prices.append(
                PriceBar(
                    date=d,
                    open=round(open_price, 2),
                    high=round(high, 2),
                    low=round(low, 2),
                    close=round(price, 2),
                    volume=max(volume, 1_000_000),
                )
            )

        return prices

    def _generate_financials(self, ticker: str, data: dict) -> list[FinancialPeriod]:
        """Generate 4 quarters of financial data with slight variation."""
        periods = []
        today = date.today()
        base_revenue = data["revenue"]

        for q in range(4):
            period_end = today - timedelta(days=90 * q + 30)
            r = _deterministic_random(ticker, 5000 + q)
            growth_factor = 1 + (r - 0.4) * 0.08  # ±4% variation

            quarterly_revenue = (base_revenue / 4) * growth_factor
            quarterly_ni = quarterly_revenue * data["net_margin"]

            periods.append(
                FinancialPeriod(
                    period_end=period_end,
                    revenue=round(quarterly_revenue),
                    net_income=round(quarterly_ni),
                    total_assets=round(base_revenue * 1.2),
                    total_liabilities=round(base_revenue * 0.6),
                    free_cash_flow=round(quarterly_ni * 0.85),
                    eps=round(data["eps"] * growth_factor / 4, 2),
                    pe_ratio=round(data["pe_ratio"] * (1 + (r - 0.5) * 0.1), 1),
                    debt_to_equity=data["debt_to_equity"],
                    roe=data["roe"],
                    current_ratio=data["current_ratio"],
                    gross_margin=data["gross_margin"],
                    operating_margin=data["operating_margin"],
                    net_margin=data["net_margin"],
                    revenue_growth=data["revenue_growth"],
                    earnings_growth=round(data["revenue_growth"] * 1.1, 3),
                )
            )

        return periods

    def _generate_news(self, ticker: str, company_name: str) -> list[NewsItem]:
        """Generate sample news items."""
        news = []
        today = datetime.now(timezone.utc)

        for i, template in enumerate(NEWS_TEMPLATES[:6]):
            r = _deterministic_random(ticker, 8000 + i)
            published = today - timedelta(hours=int(r * 72) + 1)
            sentiment_idx = i % 3  # rotate positive/neutral/negative

            news.append(
                NewsItem(
                    title=template.format(company=company_name),
                    source=["Reuters", "Bloomberg", "CNBC", "WSJ", "MarketWatch", "Barrons"][i],
                    published_at=published,
                    url=f"https://example.com/news/{ticker.lower()}-{i}",
                )
            )

        return news
