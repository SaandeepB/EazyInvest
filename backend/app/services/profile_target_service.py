from types import SimpleNamespace

from app.config.target_profiles import TARGET_PROFILES


DEFAULT_PROFILE = "Balanced Builder"


def derive_risk_profile(answers) -> str:
    risk_score = 0
    if answers.time_horizon in ("5-10 years", "10+ years"):
        risk_score += 2
    if answers.loss_comfort == "Fine with it":
        risk_score += 2
    elif answers.loss_comfort == "Cautious":
        risk_score += 1
    if answers.behavioral_risk == "Buy more":
        risk_score += 2
    elif answers.behavioral_risk == "Hold":
        risk_score += 1
    if answers.near_term_withdrawal:
        risk_score -= 2
    if answers.has_emergency_fund == "No":
        risk_score -= 1

    if risk_score <= 1:
        return "Conservative"
    if risk_score >= 5:
        return "Growth"
    return "Balanced"


def build_profile_attributes(answers, risk_profile: str) -> dict:
    return {
        "name": "EazyInvest User",
        "risk_profile": risk_profile,
        "goal": answers.goal,
        "time_horizon": answers.time_horizon,
        "planned_withdrawal_pct": answers.withdrawal_pct if answers.near_term_withdrawal else 0.0,
        "starting_amount": answers.starting_amount,
        "monthly_contribution": answers.monthly_contribution,
        "contribution_stability": answers.contribution_stability,
        "behavioral_risk": answers.behavioral_risk,
        "has_emergency_fund": answers.has_emergency_fund,
        "account_type": answers.account_type,
        "has_external_holdings": answers.has_external_holdings,
        "ux_mode": answers.ux_mode,
    }


def build_profiler_output(user, custom_scenario_text: str | None = None, holdings_count: int = 0) -> dict:
    scenario_text = (custom_scenario_text or "").strip().lower()
    risk_profile = getattr(user, "risk_profile", "Balanced")
    scenario_context = parse_scenario_context(scenario_text)
    time_horizon_bucket = scenario_context.get("time_horizon_bucket") or bucket_time_horizon(getattr(user, "time_horizon", "10+ years"))
    liquidity_need = infer_liquidity_need(
        planned_withdrawal_pct=getattr(user, "planned_withdrawal_pct", 0.0),
        time_horizon_bucket=time_horizon_bucket,
        has_emergency_fund=getattr(user, "has_emergency_fund", "Yes"),
    )
    if scenario_context.get("liquidity_need") == "high":
        liquidity_need = "high"
    elif scenario_context.get("liquidity_need") == "medium" and liquidity_need == "low":
        liquidity_need = "medium"

    investor_segment = choose_investor_segment(
        risk_profile=risk_profile,
        time_horizon_bucket=time_horizon_bucket,
        liquidity_need=liquidity_need,
        ux_mode=getattr(user, "ux_mode", "Simple"),
        has_external_holdings=getattr(user, "has_external_holdings", "No"),
        contribution_stability=getattr(user, "contribution_stability", "Stable"),
        behavioral_risk=getattr(user, "behavioral_risk", "Hold"),
        holdings_count=holdings_count,
    )
    profile_config = get_target_profile(investor_segment)
    recommended_scenario_type = recommend_scenario_type(user, scenario_text, investor_segment, liquidity_need)
    confidence = round(score_confidence(user, scenario_text, investor_segment, holdings_count), 2)
    reasoning = build_reasoning(
        user=user,
        investor_segment=investor_segment,
        time_horizon_bucket=time_horizon_bucket,
        liquidity_need=liquidity_need,
        recommended_scenario_type=recommended_scenario_type,
        scenario_text=scenario_text,
    )

    target_stock_pct = round(
        profile_config["allocation_targets"]["Individual Stocks"]
        + profile_config["allocation_targets"]["Broad Market Funds"]
        + profile_config["allocation_targets"]["International Funds"]
        + profile_config["allocation_targets"]["Dividend / Income Funds"]
        + profile_config["allocation_targets"]["Thematic / Sector Exposure"],
        1,
    )
    tags = build_tags(user, investor_segment, holdings_count, liquidity_need)
    explanation = (
        f"{investor_segment} mapped to a {risk_profile} risk profile with a "
        f"{profile_config['rebalance_trigger_pct']:.0f}% rebalance band."
    )

    return {
        "investor_segment": investor_segment,
        "risk_profile": risk_profile,
        "liquidity_need": liquidity_need,
        "time_horizon_bucket": time_horizon_bucket,
        "recommended_scenario_type": recommended_scenario_type,
        "confidence": confidence,
        "reasoning": reasoning,
        "target_profile_name": investor_segment,
        "allocation_targets": profile_config["allocation_targets"],
        "max_single_holding_pct": profile_config["max_single_holding_pct"],
        "max_sector_pct": profile_config["max_sector_pct"],
        "rebalance_trigger_pct": profile_config["rebalance_trigger_pct"],
        "warning_rules": profile_config["warning_rules"],
        "target_stock_pct": target_stock_pct,
        "planning_style": getattr(user, "ux_mode", "Simple"),
        "tags": tags,
        "explanation": explanation,
    }


def get_target_profile(name: str) -> dict:
    return TARGET_PROFILES.get(name, TARGET_PROFILES[DEFAULT_PROFILE])


def bucket_time_horizon(time_horizon: str) -> str:
    normalized = time_horizon.strip().lower()
    if normalized in {"1-2 years", "1 year", "2 years"} or "next year" in normalized:
        return "near_term"
    if normalized in {"3-5 years", "5-10 years"}:
        return "medium_term"
    return "long_term"


def infer_liquidity_need(planned_withdrawal_pct: float, time_horizon_bucket: str, has_emergency_fund: str) -> str:
    if planned_withdrawal_pct >= 15 or time_horizon_bucket == "near_term":
        return "high"
    if planned_withdrawal_pct > 0 or has_emergency_fund == "No":
        return "medium"
    return "low"


def choose_investor_segment(
    risk_profile: str,
    time_horizon_bucket: str,
    liquidity_need: str,
    ux_mode: str,
    has_external_holdings: str,
    contribution_stability: str,
    behavioral_risk: str,
    holdings_count: int,
) -> str:
    if liquidity_need == "high":
        return "Goal-Focused Planner"
    if risk_profile == "Conservative":
        return "Cautious Starter"
    if risk_profile == "Growth" and ux_mode.lower() == "control" and behavioral_risk == "Buy more":
        return "High-Risk Watchlist User"
    if ux_mode.lower() == "control" and (has_external_holdings == "Yes" or holdings_count >= 5):
        return "Active Portfolio Tweaker"
    if risk_profile == "Growth" and time_horizon_bucket == "long_term":
        return "Long-Term Growth Investor"
    if risk_profile == "Balanced" and contribution_stability == "Stable":
        return "Balanced Builder"
    return DEFAULT_PROFILE


def recommend_scenario_type(user, scenario_text: str, investor_segment: str, liquidity_need: str) -> str:
    if scenario_text:
        if any(keyword in scenario_text for keyword in ("cash", "withdraw", "next year", "liquidity", "need money")):
            return "withdrawal"
        if any(keyword in scenario_text for keyword in ("inflation", "prices", "rates", "cost of living")):
            return "inflation"
        if any(keyword in scenario_text for keyword in ("concentrat", "too big", "overweight", "single stock")):
            return "concentration"
        if any(keyword in scenario_text for keyword in ("less risk", "safer", "de-risk", "reduce risk")):
            return "reduce_risk"
        if any(keyword in scenario_text for keyword in ("drop", "crash", "drawdown", "bear market")):
            return "market_drop"

    if liquidity_need == "high":
        return "withdrawal"
    if investor_segment in {"High-Risk Watchlist User", "Long-Term Growth Investor"}:
        return "market_drop"
    if investor_segment == "Active Portfolio Tweaker":
        return "concentration"
    if investor_segment == "Cautious Starter":
        return "reduce_risk"
    return "inflation"


def score_confidence(user, scenario_text: str, investor_segment: str, holdings_count: int) -> float:
    score = 0.62
    if getattr(user, "risk_profile", "Balanced") in {"Conservative", "Balanced", "Growth"}:
        score += 0.08
    if getattr(user, "time_horizon", ""):
        score += 0.08
    if getattr(user, "goal", ""):
        score += 0.06
    if scenario_text:
        score += 0.08
    if holdings_count > 0:
        score += 0.04
    if investor_segment in TARGET_PROFILES:
        score += 0.04
    return min(0.95, score)


def build_tags(user, investor_segment: str, holdings_count: int, liquidity_need: str) -> list[str]:
    tags: list[str] = [investor_segment.lower().replace(" ", "_")]
    if getattr(user, "monthly_contribution", 0.0) > 0:
        tags.append("active_contributor")
    if getattr(user, "has_emergency_fund", "Yes") == "Yes":
        tags.append("liquidity_buffer")
    if holdings_count >= 5:
        tags.append("building_diversification")
    if getattr(user, "ux_mode", "Simple").lower() == "control":
        tags.append("detail_oriented")
    else:
        tags.append("simple_planner")
    if liquidity_need == "high":
        tags.append("near_term_cash_need")
    return tags


def build_reasoning(
    user,
    investor_segment: str,
    time_horizon_bucket: str,
    liquidity_need: str,
    recommended_scenario_type: str,
    scenario_text: str,
) -> str:
    reasons = [
        f"Segmented as {investor_segment} from {getattr(user, 'risk_profile', 'Balanced').lower()} risk preferences",
        f"time horizon bucket {time_horizon_bucket}",
        f"liquidity need {liquidity_need}",
    ]
    if scenario_text:
        reasons.append("custom scenario text influenced the scenario recommendation")
    reasons.append(f"recommended scenario {recommended_scenario_type}")
    return "; ".join(reasons) + "."


def profiler_output_from_answers(answers, custom_scenario_text: str | None = None) -> dict:
    risk_profile = derive_risk_profile(answers)
    user_like = SimpleNamespace(**build_profile_attributes(answers, risk_profile))
    return build_profiler_output(user_like, custom_scenario_text=custom_scenario_text, holdings_count=0)


def parse_scenario_context(scenario_text: str) -> dict[str, str]:
    context: dict[str, str] = {}
    if any(keyword in scenario_text for keyword in ("cash", "withdraw", "need money", "next year", "liquidity", "spending")):
        context["liquidity_need"] = "high"
        context["time_horizon_bucket"] = "near_term"
    elif any(keyword in scenario_text for keyword in ("soon", "retire", "retirement")):
        context["liquidity_need"] = "medium"
    return context
