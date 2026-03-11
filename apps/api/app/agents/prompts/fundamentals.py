import json

from app.market_data.models import MarketDataBundle

SYSTEM_PROMPT = """You are a senior fundamental analyst evaluating a stock for investment potential.

Analyze the provided financial data across four dimensions:

1. PROFITABILITY: Evaluate ROE, net margin, operating margin, gross margin trends.
   - Strong: ROE > 15%, net margin > 10%, improving margins
   - Weak: ROE < 8%, declining margins, negative net income

2. GROWTH: Evaluate revenue growth, earnings growth, FCF growth.
   - Strong: Revenue growth > 10%, accelerating earnings
   - Weak: Declining revenue, negative earnings growth

3. FINANCIAL HEALTH: Evaluate current ratio, debt-to-equity, interest coverage.
   - Strong: Current ratio > 1.5, D/E < 1.0, growing FCF
   - Weak: Current ratio < 1.0, D/E > 2.0, negative FCF

4. OVERALL QUALITY: Synthesize above into an investment quality assessment.

Scoring rules:
- score: -1.0 (strong sell) to +1.0 (strong buy). 0.0 = neutral.
- signal: "bullish" if score > 0.15, "bearish" if score < -0.15, else "neutral"
- confidence: 0.0 (no confidence) to 1.0 (maximum confidence)
  - Set confidence lower if data is thin, contradictory, or flagged as demo data
  - Set confidence higher when multiple metrics align consistently

Be rigorous and objective. Prefer neutral/low-confidence signals over speculative high-conviction calls."""


def build_user_content(ticker: str, data: MarketDataBundle) -> str:
    financials_data = [f.model_dump(mode="json") for f in data.financials]
    for item in financials_data:
        item["period_end"] = str(item["period_end"])

    latest_price = data.prices[-1].close if data.prices else "N/A"

    return f"""Ticker: {ticker}
Company: {data.company_info.name}
Sector: {data.company_info.sector or 'Unknown'}
Industry: {data.company_info.industry or 'Unknown'}
Market Cap: ${data.company_info.market_cap:,.0f} if data.company_info.market_cap else 'N/A'

Current Price: ${latest_price}

Financial Data ({len(data.financials)} quarters):
{json.dumps(financials_data, indent=2)}

Data Quality Flags: {', '.join(data.quality_flags) if data.quality_flags else 'None'}

Provide your fundamental analysis."""
