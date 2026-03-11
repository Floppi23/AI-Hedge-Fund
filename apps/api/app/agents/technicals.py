"""Technicals agent — 100% deterministic, no LLM calls.

Uses a 5-strategy ensemble adapted from the reference repo:
- Trend following (EMA crossover): 25%
- Mean reversion (Bollinger Bands): 20%
- Momentum (rate of change + volume): 25%
- Volatility regime: 15%
- Statistical (Hurst exponent approximation): 15%
"""

import math

from app.agents.base import BaseAgent
from app.agents.output_schemas import TechnicalsOutput
from app.llm.client import LLMClient
from app.market_data.models import MarketDataBundle, PriceBar

# Strategy weights
WEIGHTS = {
    "trend": 0.25,
    "mean_reversion": 0.20,
    "momentum": 0.25,
    "volatility": 0.15,
    "statistical": 0.15,
}

MIN_PRICE_BARS = 60


def _safe_float(val: float) -> float:
    """Clamp to [-1, 1], handle NaN/Inf."""
    if math.isnan(val) or math.isinf(val):
        return 0.0
    return max(-1.0, min(1.0, val))


def _ema(prices: list[float], period: int) -> list[float]:
    """Exponential moving average."""
    if not prices:
        return []
    k = 2.0 / (period + 1)
    result = [prices[0]]
    for p in prices[1:]:
        result.append(p * k + result[-1] * (1 - k))
    return result


def _sma(prices: list[float], period: int) -> float:
    """Simple moving average of last `period` values."""
    if len(prices) < period:
        return sum(prices) / len(prices) if prices else 0
    return sum(prices[-period:]) / period


def _std(prices: list[float], period: int) -> float:
    """Standard deviation of last `period` values."""
    if len(prices) < 2:
        return 0.0
    data = prices[-period:]
    mean = sum(data) / len(data)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    return math.sqrt(variance)


def _trend_signal(closes: list[float]) -> float:
    """EMA crossover strategy: short EMA vs long EMA."""
    if len(closes) < 50:
        return 0.0
    ema_short = _ema(closes, 12)
    ema_long = _ema(closes, 26)
    # Normalized difference
    diff = (ema_short[-1] - ema_long[-1]) / ema_long[-1]
    return _safe_float(diff * 10)  # Scale to [-1, 1] range


def _mean_reversion_signal(closes: list[float]) -> float:
    """Bollinger Band position — price relative to bands."""
    period = 20
    if len(closes) < period:
        return 0.0
    sma_val = _sma(closes, period)
    std_val = _std(closes, period)
    if std_val == 0:
        return 0.0
    # Z-score: negative = below mean (potential buy), positive = above mean (potential sell)
    z = (closes[-1] - sma_val) / (2 * std_val)
    # Invert: below band = bullish signal
    return _safe_float(-z)


def _momentum_signal(closes: list[float], volumes: list[int]) -> float:
    """Rate of change + volume-weighted momentum."""
    if len(closes) < 20:
        return 0.0
    # 14-day rate of change
    roc = (closes[-1] - closes[-14]) / closes[-14]
    # Volume trend: recent vs average
    avg_vol = sum(volumes[-20:]) / 20
    recent_vol = sum(volumes[-5:]) / 5
    vol_factor = min(recent_vol / avg_vol, 2.0) if avg_vol > 0 else 1.0
    # Momentum weighted by volume
    return _safe_float(roc * vol_factor * 5)


def _volatility_signal(closes: list[float]) -> tuple[float, str]:
    """Volatility regime detection and signal."""
    if len(closes) < 20:
        return 0.0, "medium"
    # Annualized volatility
    returns = [(closes[i] / closes[i - 1]) - 1 for i in range(1, len(closes[-30:]))]
    if not returns:
        return 0.0, "medium"
    std_ret = _std(returns, len(returns))
    ann_vol = std_ret * math.sqrt(252)
    # Classify regime
    if ann_vol < 0.15:
        regime = "low"
        signal = 0.2  # Low vol = slight bullish
    elif ann_vol < 0.30:
        regime = "medium"
        signal = 0.0
    elif ann_vol < 0.50:
        regime = "high"
        signal = -0.2
    else:
        regime = "high"
        signal = -0.5  # Very high vol = bearish
    return _safe_float(signal), regime


def _statistical_signal(closes: list[float]) -> float:
    """Simplified Hurst exponent approximation for trend persistence."""
    if len(closes) < 60:
        return 0.0
    # R/S analysis (simplified)
    returns = [(closes[i] / closes[i - 1]) - 1 for i in range(1, len(closes))]
    n = len(returns)
    if n < 20:
        return 0.0
    mean_r = sum(returns) / n
    deviations = [r - mean_r for r in returns]
    cumulative = []
    s = 0
    for d in deviations:
        s += d
        cumulative.append(s)
    r_range = max(cumulative) - min(cumulative) if cumulative else 0
    std_ret = _std(returns, n)
    if std_ret == 0:
        return 0.0
    rs = r_range / std_ret
    hurst = math.log(rs) / math.log(n) if rs > 0 and n > 1 else 0.5
    # H > 0.5 = trending, H < 0.5 = mean reverting
    # Scale: use current trend direction * hurst deviation from 0.5
    trend = 1.0 if closes[-1] > closes[-20] else -1.0
    return _safe_float((hurst - 0.5) * trend * 3)


class TechnicalsAgent(BaseAgent):
    name = "technicals"
    prompt_version = "v1"

    def analyze(
        self,
        ticker: str,
        market_data: MarketDataBundle,
        llm: LLMClient,  # Not used — purely deterministic
    ) -> TechnicalsOutput:
        prices = market_data.prices
        if len(prices) < MIN_PRICE_BARS:
            return TechnicalsOutput(
                signal="neutral",
                confidence=0.1,
                score=0.0,
                reasoning=f"Insufficient price data ({len(prices)} bars, need {MIN_PRICE_BARS})",
                trend_direction="sideways",
                momentum_score=0.0,
                volatility_regime="medium",
                key_levels={},
            )

        closes = [p.close for p in prices]
        volumes = [p.volume for p in prices]

        # Run each strategy
        trend = _trend_signal(closes)
        mean_rev = _mean_reversion_signal(closes)
        momentum = _momentum_signal(closes, volumes)
        vol_signal, vol_regime = _volatility_signal(closes)
        stat = _statistical_signal(closes)

        # Weighted ensemble
        raw_score = (
            trend * WEIGHTS["trend"]
            + mean_rev * WEIGHTS["mean_reversion"]
            + momentum * WEIGHTS["momentum"]
            + vol_signal * WEIGHTS["volatility"]
            + stat * WEIGHTS["statistical"]
        )
        score = _safe_float(raw_score)

        # Determine signal
        if score > 0.15:
            signal = "bullish"
        elif score < -0.15:
            signal = "bearish"
        else:
            signal = "neutral"

        # Confidence based on agreement between strategies
        signals_list = [trend, mean_rev, momentum, vol_signal, stat]
        same_direction = sum(1 for s in signals_list if (s > 0) == (score > 0) and s != 0)
        confidence = min(0.3 + same_direction * 0.12, 0.85)
        if "demo_data" in market_data.quality_flags:
            confidence *= 0.7

        # Key levels
        recent_highs = closes[-20:]
        recent_lows = closes[-20:]
        key_levels = {
            "resistance": round(max(recent_highs), 2),
            "support": round(min(recent_lows), 2),
            "current": round(closes[-1], 2),
            "sma_20": round(_sma(closes, 20), 2),
            "sma_50": round(_sma(closes, 50), 2),
        }

        # Trend direction
        sma_20 = _sma(closes, 20)
        sma_50 = _sma(closes, 50)
        if sma_20 > sma_50 * 1.01:
            trend_dir = "uptrend"
        elif sma_20 < sma_50 * 0.99:
            trend_dir = "downtrend"
        else:
            trend_dir = "sideways"

        reasoning = (
            f"5-strategy ensemble: trend={trend:.2f}, mean_rev={mean_rev:.2f}, "
            f"momentum={momentum:.2f}, volatility={vol_signal:.2f}, "
            f"statistical={stat:.2f}. "
            f"Weighted score={score:.3f}. "
            f"{same_direction}/5 strategies agree on direction."
        )

        return TechnicalsOutput(
            signal=signal,
            confidence=round(confidence, 3),
            score=round(score, 4),
            reasoning=reasoning,
            trend_direction=trend_dir,
            momentum_score=round(momentum, 3),
            volatility_regime=vol_regime,
            key_levels=key_levels,
        )
