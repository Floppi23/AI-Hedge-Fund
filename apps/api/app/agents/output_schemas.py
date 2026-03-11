"""Pydantic schemas for agent outputs. These define the contract between LLM responses and the DB."""

from typing import Literal

from pydantic import BaseModel, Field


class AgentSignalOutput(BaseModel):
    """Base schema that all signal-producing agents must conform to."""

    signal: Literal["bullish", "bearish", "neutral"]
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence level 0-1")
    score: float = Field(ge=-1.0, le=1.0, description="Directional score, negative=bearish")
    reasoning: str = Field(description="Concise justification for the signal")


class FundamentalsOutput(AgentSignalOutput):
    profitability_assessment: str = Field(description="Assessment of profitability metrics")
    growth_assessment: str = Field(description="Assessment of growth trajectory")
    financial_health_assessment: str = Field(description="Assessment of balance sheet health")
    key_metrics: dict[str, float | None] = Field(
        default_factory=dict, description="Key financial metrics evaluated"
    )


class ValuationOutput(AgentSignalOutput):
    dcf_value: float | None = Field(None, description="Estimated DCF fair value per share")
    relative_value: str = Field(description="undervalued, fairly_valued, or overvalued")
    margin_of_safety: float | None = Field(
        None, description="Margin of safety as percentage (e.g. 0.15 = 15%)"
    )
    valuation_methods_used: list[str] = Field(
        default_factory=list, description="Methods used: dcf, pe_relative, ev_ebitda, etc."
    )


class TechnicalsOutput(AgentSignalOutput):
    trend_direction: str = Field(description="uptrend, downtrend, or sideways")
    momentum_score: float = Field(description="Momentum indicator, -1 to +1")
    volatility_regime: str = Field(description="low, medium, or high")
    key_levels: dict[str, float] = Field(
        default_factory=dict, description="Support/resistance levels"
    )


class SentimentOutput(AgentSignalOutput):
    news_sentiment_score: float = Field(description="Aggregated news sentiment, -1 to +1")
    insider_activity_summary: str = Field(description="Summary of insider trading activity")
    news_count_analyzed: int = Field(description="Number of news items analyzed")


class RiskAssessment(BaseModel):
    """Risk manager output — separate from signal agents, acts as a gate."""

    risk_level: Literal["low", "medium", "high", "critical"]
    should_block: bool = Field(description="Whether to block the final signal from release")
    max_score_allowed: float = Field(
        ge=-1.0, le=1.0, description="Maximum absolute score allowed after risk adjustment"
    )
    force_neutral: bool = Field(
        default=False, description="Whether to override the signal to neutral"
    )
    reasoning: str = Field(description="Explanation of risk assessment")
    risk_factors: list[str] = Field(default_factory=list, description="Identified risk factors")
