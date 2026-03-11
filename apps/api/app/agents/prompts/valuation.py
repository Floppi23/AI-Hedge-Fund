import json

from app.market_data.models import MarketDataBundle

SYSTEM_PROMPT = """You are a senior valuation analyst performing intrinsic value assessment.

Use multiple valuation methodologies:

1. DCF ANALYSIS: Estimate fair value using discounted cash flow.
   - Use available free cash flow data
   - Apply appropriate discount rate (8-12% for most equities)
   - Use conservative growth assumptions

2. RELATIVE VALUATION: Compare P/E, P/B, EV/EBITDA to sector/historical norms.
   - P/E < 15: potentially undervalued (for mature companies)
   - P/E > 30: potentially overvalued (unless justified by growth)

3. MARGIN OF SAFETY: Calculate % difference between market price and fair value.
   - > 25%: meaningful margin of safety
   - < 0%: potentially overvalued

Assessment rules:
- relative_value must be one of: "undervalued", "fairly_valued", "overvalued"
- score: -1.0 (significantly overvalued) to +1.0 (significantly undervalued)
- signal: "bullish" if undervalued with margin of safety, "bearish" if overvalued, else "neutral"
- confidence: lower when data is limited, when growth is unpredictable, or when quality flags indicate demo data

Be conservative in your estimates. When uncertain, lean toward neutral."""


def build_user_content(ticker: str, data: MarketDataBundle) -> str:
    financials_data = [f.model_dump(mode="json") for f in data.financials]
    for item in financials_data:
        item["period_end"] = str(item["period_end"])

    latest_price = data.prices[-1].close if data.prices else None
    price_str = f"${latest_price:.2f}" if latest_price else "N/A"

    return f"""Ticker: {ticker}
Company: {data.company_info.name}
Current Market Price: {price_str}
Market Cap: ${data.company_info.market_cap:,.0f} if data.company_info.market_cap else 'N/A'

Financial Data ({len(data.financials)} quarters):
{json.dumps(financials_data, indent=2)}

Data Quality Flags: {', '.join(data.quality_flags) if data.quality_flags else 'None'}

Perform your valuation analysis and determine whether this stock is undervalued, fairly valued, or overvalued."""
