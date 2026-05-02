from app.services.audit_service import add_event


TRANSPARENCY_TEXT = {
    "market_drop": {
        "why_suggested": "A drawdown stress test checks whether a stock-heavy mix could become emotionally or financially hard to hold.",
        "upside": "Lower downside concentration if markets correct.",
        "downside": "A calmer allocation may trail a sharp rebound.",
        "selling_impact": "Partial trims lower exposure without forcing a full exit from long-term ideas.",
        "goal_alignment": "The plan is meant to keep the portfolio investable through volatility.",
    },
    "inflation": {
        "why_suggested": "Inflationary periods often expose sector concentration and valuation sensitivity.",
        "upside": "Less dependence on one sector driving outcomes.",
        "downside": "If the concentrated sector keeps outperforming, upside may be smaller.",
        "selling_impact": "The result is a modest spread of exposure rather than a wholesale portfolio rewrite.",
        "goal_alignment": "Diversification supports steadier progress toward long-term goals.",
    },
    "withdrawal": {
        "why_suggested": "Money needed soon should not depend on a strong stock market right before withdrawal.",
        "upside": "Improves liquidity readiness for planned withdrawals.",
        "downside": "The safer sleeve may earn less if markets rally.",
        "selling_impact": "Trims are sized to create a spending buffer instead of liquidating everything.",
        "goal_alignment": "Protects near-term goals while keeping the rest of the portfolio invested.",
    },
    "reduce_risk": {
        "why_suggested": "This compares current stock weight with the user's stated risk comfort and time horizon.",
        "upside": "Potentially smoother portfolio swings.",
        "downside": "Lower volatility usually means somewhat lower upside participation too.",
        "selling_impact": "Risk is reduced through partial trims rather than forcing binary decisions.",
        "goal_alignment": "Staying aligned with stated risk preferences makes the plan easier to follow.",
    },
    "concentration": {
        "why_suggested": "Single-name concentration can dominate total portfolio outcomes.",
        "upside": "Reduces dependence on one position working perfectly.",
        "downside": "A trimmed winner contributes less if it keeps outperforming.",
        "selling_impact": "The emphasis is on measured partial trims rather than panic selling.",
        "goal_alignment": "Concentration control supports a more durable long-term portfolio.",
    },
}


def build_transparency(
    scenario_type: str,
    actions: list[dict],
    current_allocation: dict[str, float] | None = None,
    proposed_allocation: dict[str, float] | None = None,
    profiler_output: dict | None = None,
    custom_scenario_text: str | None = None,
    audit: dict | None = None,
) -> dict:
    content = TRANSPARENCY_TEXT.get(scenario_type, TRANSPARENCY_TEXT["reduce_risk"]).copy()
    content["what_changes"] = _describe_allocation_shift(current_allocation or {}, proposed_allocation or {})

    if profiler_output:
      content["why_suggested"] += f" The current user profile maps to {profiler_output['target_profile_name']}."
    if custom_scenario_text:
      content["goal_alignment"] += " Custom scenario text was classified deterministically before the math ran."

    content["guardrail_note"] = (
        "AI-style agents only classified, routed, explained, and validated. "
        "All portfolio math stayed deterministic in backend services, and no returns were guaranteed."
    )
    if audit is not None:
        add_event(audit, "transparency_agent", "explain", f"Built transparency summary for {scenario_type} with {len(actions)} actions.")
    return content


def _describe_allocation_shift(current_allocation: dict[str, float], proposed_allocation: dict[str, float]) -> str:
    deltas = []
    for category, current in current_allocation.items():
        proposed = proposed_allocation.get(category, 0.0)
        change = round(proposed - current, 2)
        if abs(change) >= 0.5:
            direction = "increase" if change > 0 else "reduce"
            deltas.append(f"{direction} {category} by {abs(change):.1f}%")

    if not deltas:
        return "The proposed scenario keeps the high-level allocation close to the current mix."
    return "The proposal would " + ", then ".join(deltas[:3]) + "."
