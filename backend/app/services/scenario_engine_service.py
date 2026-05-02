from app.services.audit_guardrail_agent import validate_scenario_projection
from app.services.audit_service import add_event
from app.services.market_dataset_service import get_default_recommendation
from app.services.portfolio_math_service import build_simulated_holdings, compute_health, compute_portfolio_payload, enrich_holdings
from app.services.rebalancing_agent import order_actions
from app.services.scenario_agent import validate_scenario_request
from app.services.transparency_agent import build_transparency
from app.utils.defaults import DEFAULT_DIVERSIFIERS


def analyze_scenario(holdings, user, scenario_type: str, custom_params: dict | None, audit: dict) -> dict:
    scenario_meta = validate_scenario_request(scenario_type, custom_params, audit)
    enriched = enrich_holdings(holdings, audit)
    current_portfolio = compute_portfolio_payload(enriched, user)
    current_health = current_portfolio["health"]
    before_allocation = {item["symbol"]: round(item["weight_pct"], 2) for item in enriched}

    if not enriched:
        empty = {
            "scenario_type": scenario_type,
            "scenario_label": scenario_meta["label"],
            "summary": "No holdings found. Add holdings in My Holdings before running a scenario.",
            "profiler_output": None,
            "current_health": current_health,
            "projected_health": current_health,
            "current_allocation": {},
            "proposed_allocation": {},
            "before_allocation": {},
            "after_allocation": {},
            "actions": [],
            "transparency": build_transparency(scenario_type, [], audit=audit),
            "market_context": {"source": "syndicated_csv", "supported_symbol_count": 0, "top_sectors": [], "diversified_weight_pct": 0.0, "narrative": ""},
            "estimated_cost_note": "No trades suggested because the portfolio is empty.",
            "estimated_tax_note": "No tax impact because no trades were modeled.",
        }
        validate_scenario_projection({}, audit)
        return empty

    handlers = {
        "market_drop": _market_drop,
        "inflation": _inflation,
        "withdrawal": _withdrawal,
        "reduce_risk": _reduce_risk,
        "concentration": _concentration,
    }
    actions, summary = handlers[scenario_type](enriched, user, custom_params or {}, audit)
    actions = order_actions(actions, audit)
    after_allocation = _compute_after_allocation(before_allocation, actions)
    simulated = build_simulated_holdings(after_allocation, current_portfolio["total_value"], audit)
    projected_health = compute_health(simulated, user)
    validate_scenario_projection(after_allocation, audit)
    add_event(audit, "scenario_engine_service", "analyze", f"Generated {len(actions)} actions for {scenario_type}.")
    return {
        "scenario_type": scenario_type,
        "scenario_label": scenario_meta["label"],
        "summary": summary,
        "current_health": current_health,
        "projected_health": projected_health,
        "current_allocation": {},
        "proposed_allocation": {},
        "before_allocation": before_allocation,
        "after_allocation": after_allocation,
        "actions": actions,
        "transparency": build_transparency(scenario_type, actions, audit=audit),
        "market_context": {"source": "syndicated_csv", "supported_symbol_count": 0, "top_sectors": [], "diversified_weight_pct": 0.0, "narrative": ""},
        "estimated_cost_note": "Costs are illustrative only. EazyInvest modeled weight changes with deterministic CSV proxy prices.",
        "estimated_tax_note": "Tax notes are generic educational guidance. EazyInvest did not run tax-lot analysis.",
    }


def _market_drop(enriched: list[dict], user, params: dict, audit: dict) -> tuple[list[dict], str]:
    drop_pct = float(params.get("drop_pct", 20))
    stock_pct = sum(item["weight_pct"] for item in enriched if item["asset_type"] == "stock")
    stock_value = sum(item["effective_value"] for item in enriched if item["asset_type"] == "stock")
    simulated_loss = round(stock_value * drop_pct / 100, 2)
    trims = []
    adds = []
    largest_stocks = [item for item in enriched if item["asset_type"] == "stock"][:2]
    trim_total = 0.0
    for item in largest_stocks:
        if stock_pct <= 55:
            break
        trim_amt = min(6.0, max(item["weight_pct"] - 10.0, 0.0))
        if trim_amt > 0:
            trim_total += trim_amt
            trims.append(_build_action(item, "trim", item["weight_pct"] - trim_amt, True, "Reduce downside if a broad equity drawdown hits concentrated stock exposure."))

    if trim_total > 0:
        candidate = get_default_recommendation(DEFAULT_DIVERSIFIERS["defensive"], exclude={item["symbol"] for item in enriched}, audit=audit)
        adds.append(_build_new_action(candidate, trim_total, "Redirect a slice of risk toward a more defensive, diversified instrument."))
    if not trims and not adds:
        trims = [_build_action(item, "hold", item["weight_pct"], True, "Current weights already look manageable for a market-drop stress test.") for item in enriched[:3]]

    summary = f"A modeled {drop_pct:.0f}% market drop would reduce current stock value by about ${simulated_loss:,.0f}. The planner focuses on trimming concentrated stock risk rather than reacting after a selloff."
    return trims + adds, summary


def _inflation(enriched: list[dict], user, params: dict, audit: dict) -> tuple[list[dict], str]:
    tech_holdings = [item for item in enriched if item["sector_or_category"] in {"Technology", "Communication Services"}]
    tech_pct = round(sum(item["weight_pct"] for item in tech_holdings), 2)
    actions = []
    if tech_holdings and tech_pct > 35:
        top = tech_holdings[0]
        trim_amt = min(8.0, max(top["weight_pct"] - 8.0, 0.0))
        if trim_amt > 0:
            actions.append(_build_action(top, "trim", top["weight_pct"] - trim_amt, True, "High inflation can hit rate-sensitive growth concentration harder than a balanced mix."))
            candidate = get_default_recommendation(DEFAULT_DIVERSIFIERS["inflation"], exclude={item["symbol"] for item in enriched}, audit=audit)
            actions.append(_build_new_action(candidate, trim_amt, "Add broader or inflation-aware diversification to reduce single-sector dependence."))
    else:
        actions = [_build_action(item, "hold", item["weight_pct"], True, "Sector mix already looks reasonably spread for this inflation scenario.") for item in enriched[:3]]
    summary = f"Technology and adjacent growth exposure is about {tech_pct:.1f}% of the portfolio. The inflation scenario checks whether that concentration should be spread out."
    return actions, summary


def _withdrawal(enriched: list[dict], user, params: dict, audit: dict) -> tuple[list[dict], str]:
    withdrawal_pct = float(params.get("withdrawal_pct", getattr(user, "planned_withdrawal_pct", 0.0) or 20.0))
    remaining = withdrawal_pct
    actions = []
    for item in [row for row in enriched if row["asset_type"] == "stock"]:
        if remaining <= 0:
            break
        trim_amt = min(item["weight_pct"] - 5.0, remaining)
        if trim_amt > 0:
            actions.append(_build_action(item, "trim", item["weight_pct"] - trim_amt, True, "Create a more stable near-term spending sleeve by trimming stock exposure."))
            remaining -= trim_amt
    candidate = get_default_recommendation(DEFAULT_DIVERSIFIERS["defensive"], exclude={item["symbol"] for item in enriched}, audit=audit)
    shifted = round(withdrawal_pct - remaining, 2)
    if shifted > 0:
        actions.append(_build_new_action(candidate, shifted, "Use a defensive instrument as a placeholder for near-term liquidity needs."))
    summary = f"This scenario reserves about {withdrawal_pct:.1f}% of the portfolio for a possible near-term withdrawal while keeping the rest invested."
    return actions, summary


def _reduce_risk(enriched: list[dict], user, params: dict, audit: dict) -> tuple[list[dict], str]:
    stock_pct = sum(item["weight_pct"] for item in enriched if item["asset_type"] == "stock")
    target_stock = {"Conservative": 35.0, "Balanced": 55.0, "Growth": 75.0}.get(getattr(user, "risk_profile", "Balanced"), 55.0)
    excess = max(0.0, stock_pct - target_stock)
    actions = []
    if excess > 0:
        stock_positions = [item for item in enriched if item["asset_type"] == "stock"]
        per_trim = round(excess / max(len(stock_positions), 1), 2)
        for item in stock_positions:
            trim_amt = min(per_trim, max(item["weight_pct"] - 3.0, 0.0))
            if trim_amt > 0:
                actions.append(_build_action(item, "trim", item["weight_pct"] - trim_amt, True, "Move the portfolio closer to the user's target risk mix."))
        candidate = get_default_recommendation(DEFAULT_DIVERSIFIERS["defensive"], exclude={item["symbol"] for item in enriched}, audit=audit)
        actions.append(_build_new_action(candidate, round(sum(abs(a["change_pct"]) for a in actions if a["action"] == "trim"), 2), "Offset reduced stock exposure with a steadier diversified allocation."))
    else:
        actions = [_build_action(item, "hold", item["weight_pct"], True, "Current stock weight already aligns with the stored risk profile.") for item in enriched[:3]]
    summary = f"Current stock weight is {stock_pct:.1f}% versus a {target_stock:.1f}% target for the user's {user.risk_profile} profile."
    return actions, summary


def _concentration(enriched: list[dict], user, params: dict, audit: dict) -> tuple[list[dict], str]:
    threshold = float(params.get("threshold", 30.0))
    actions = []
    trimmed_total = 0.0
    for item in enriched:
        if item["weight_pct"] > threshold:
            target = threshold - 2.0
            trimmed_total += item["weight_pct"] - target
            actions.append(_build_action(item, "trim", target, True, "Trim an overweight position so one name does not dominate portfolio outcomes."))
    if trimmed_total > 0:
        candidate = get_default_recommendation(DEFAULT_DIVERSIFIERS["equity"], exclude={item["symbol"] for item in enriched}, audit=audit)
        actions.append(_build_new_action(candidate, round(trimmed_total, 2), "Spread freed capital across a diversified holding."))
    if not actions:
        actions = [_build_action(item, "hold", item["weight_pct"], True, "No holding currently breaches the concentration threshold.") for item in enriched[:3]]
    summary = f"The concentration scan looked for holdings above {threshold:.1f}% of portfolio weight."
    return actions, summary


def _compute_after_allocation(before_allocation: dict[str, float], actions: list[dict]) -> dict[str, float]:
    after = {symbol: round(weight, 2) for symbol, weight in before_allocation.items()}
    for action in actions:
        after[action["symbol"]] = round(action["target_weight_pct"], 2)
    total = sum(after.values())
    if after and total:
        adjustment = round(100.0 - total, 2)
        if adjustment != 0:
            first_key = next(iter(after))
            after[first_key] = round(after[first_key] + adjustment, 2)
    return after


def _build_action(item: dict, action: str, target_weight_pct: float, owned_holding: bool, reason: str) -> dict:
    current_weight = round(item["weight_pct"], 2)
    target = round(max(target_weight_pct, 0.0), 2)
    return {
        "symbol": item["symbol"],
        "name": item["name"],
        "action": action,
        "owned_holding": owned_holding,
        "current_weight_pct": current_weight,
        "target_weight_pct": target,
        "change_pct": round(target - current_weight, 2),
        "reason": reason,
    }


def _build_new_action(record, target_weight_pct: float, reason: str) -> dict:
    target = round(max(target_weight_pct, 0.0), 2)
    return {
        "symbol": record.symbol,
        "name": record.name,
        "action": "add",
        "owned_holding": False,
        "current_weight_pct": 0.0,
        "target_weight_pct": target,
        "change_pct": target,
        "reason": reason,
    }
