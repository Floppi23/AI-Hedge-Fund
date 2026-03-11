"""Aggregation logic: combine agent outputs into a final signal with reliability gates."""

from app.agents.output_schemas import RiskAssessment

# Agent weights from spec
AGENT_WEIGHTS = {
    "fundamentals": 0.30,
    "valuation": 0.25,
    "technicals": 0.20,
    "sentiment": 0.15,
}

MIN_VALID_AGENTS = 3
MIN_CONFIDENCE = 0.55


def aggregate_signals(
    agent_results: list[dict],
    risk_assessment: RiskAssessment,
) -> dict:
    """Compute final signal from validated agent outputs + risk assessment.

    Returns a dict matching the FinalSignal model fields.
    """
    valid_results = [r for r in agent_results if r.get("is_valid", False)]
    contributing_agents = [r["agent_name"] for r in valid_results]

    blocked_reasons = []

    # Check minimum valid agents
    if len(valid_results) < MIN_VALID_AGENTS:
        blocked_reasons.append(
            f"Insufficient valid agents: {len(valid_results)}/{MIN_VALID_AGENTS} required"
        )

    # Weighted aggregation
    total_weight = 0.0
    weighted_score = 0.0
    weighted_confidence = 0.0

    for result in valid_results:
        name = result["agent_name"]
        base_weight = AGENT_WEIGHTS.get(name, 0.10)
        confidence = result.get("confidence", 0.0)
        score = result.get("score", 0.0)

        # Weight adjusted by confidence
        effective_weight = base_weight * confidence
        weighted_score += score * effective_weight
        weighted_confidence += confidence * base_weight
        total_weight += effective_weight

    if total_weight > 0:
        final_score = weighted_score / total_weight
        final_confidence = weighted_confidence / sum(
            AGENT_WEIGHTS.get(r["agent_name"], 0.10) for r in valid_results
        )
    else:
        final_score = 0.0
        final_confidence = 0.0

    # Apply risk manager decisions
    risk_override = False
    if risk_assessment.force_neutral:
        final_score = 0.0
        risk_override = True
        blocked_reasons.append("Risk manager forced neutral signal")

    if abs(final_score) > risk_assessment.max_score_allowed:
        original = final_score
        final_score = (
            risk_assessment.max_score_allowed
            if final_score > 0
            else -risk_assessment.max_score_allowed
        )
        risk_override = True
        blocked_reasons.append(
            f"Score capped from {original:.3f} to {final_score:.3f} by risk manager"
        )

    if risk_assessment.should_block:
        blocked_reasons.append(f"Risk manager blocked: {risk_assessment.reasoning}")

    # Determine stance
    if final_score > 0.15:
        final_stance = "bullish"
    elif final_score < -0.15:
        final_stance = "bearish"
    else:
        final_stance = "neutral"

    # Determine release status
    if risk_assessment.should_block:
        release_status = "blocked"
    elif len(valid_results) < MIN_VALID_AGENTS:
        release_status = "blocked"
    elif final_confidence < MIN_CONFIDENCE:
        release_status = "needs_review"
    elif risk_assessment.risk_level in ("high", "critical"):
        release_status = "needs_review"
    else:
        release_status = "approved"

    # Build summary
    summary_parts = [f"Final signal: {final_stance} (score={final_score:.3f}, confidence={final_confidence:.3f})"]
    for r in valid_results:
        summary_parts.append(
            f"  {r['agent_name']}: {r.get('stance', '?')} "
            f"(score={r.get('score', 0):.3f}, conf={r.get('confidence', 0):.3f})"
        )
    if risk_override:
        summary_parts.append(f"  Risk override active: {risk_assessment.risk_level}")

    return {
        "final_stance": final_stance,
        "final_score": round(final_score, 4),
        "final_confidence": round(final_confidence, 4),
        "risk_override": risk_override,
        "release_status": release_status,
        "summary": "\n".join(summary_parts),
        "contributing_agents": contributing_agents,
        "blocked_reasons": blocked_reasons if blocked_reasons else None,
    }
