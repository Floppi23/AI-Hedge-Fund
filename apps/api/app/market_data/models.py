from datetime import date, datetime

from pydantic import BaseModel, Field


class PriceBar(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int


class FinancialPeriod(BaseModel):
    period_end: date
    revenue: float | None = None
    net_income: float | None = None
    total_assets: float | None = None
    total_liabilities: float | None = None
    free_cash_flow: float | None = None
    eps: float | None = None
    pe_ratio: float | None = None
    debt_to_equity: float | None = None
    roe: float | None = None
    current_ratio: float | None = None
    gross_margin: float | None = None
    operating_margin: float | None = None
    net_margin: float | None = None
    revenue_growth: float | None = None
    earnings_growth: float | None = None


class CompanyInfo(BaseModel):
    ticker: str
    name: str
    sector: str | None = None
    industry: str | None = None
    market_cap: float | None = None
    currency: str = "USD"


class NewsItem(BaseModel):
    title: str
    source: str
    published_at: datetime
    url: str
    snippet: str | None = None


class MarketDataBundle(BaseModel):
    """Everything an agent needs for analysis — fetched once per run."""

    ticker: str
    prices: list[PriceBar]
    financials: list[FinancialPeriod]
    company_info: CompanyInfo
    news: list[NewsItem]
    quality_flags: list[str] = Field(default_factory=list)
