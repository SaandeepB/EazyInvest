from app.audit.audit_payload_builder import build_audit_result
from app.agents.market_context_agent import build_scenario_market_context
from app.agents.profiler_agent import build_profiler_summary
from app.agents.rebalancing_agent import build_allocation_view, compare_to_target_profile
from app.agents.scenario_agent import list_scenarios, resolve_scenario_request
from app.agents.transparency_agent import build_transparency
from app.services.audit_service import add_event
from app.services.portfolio_math_service import build_simulated_holdings, enrich_holdings
from app.services.scenario_engine_service import analyze_scenario as run_scenario_engine


def analyze_scenario_request(holdings, user, payload, audit: dict) -> dict:
    custom_text = getattr(payload, "custom_scenario_text", None)
    profiler_output = build_profiler_summary(user, len(holdings), audit, custom_scenario_text=custom_text)
    resolved = resolve_scenario_request(
        scenario_type=getattr(payload, "scenario_type", None),
        custom_scenario_text=custom_text,
        custom_params=getattr(payload, "custom_params", None),
        profiler_output=profiler_output,
        audit=audit,
    )

    scenario = run_scenario_engine(holdings, user, resolved["scenario_type"], resolved["custom_params"], audit)
    enriched = enrich_holdings(holdings, audit)
    simulated = build_simulated_holdings(scenario["after_allocation"], sum(item["effective_value"] for item in enriched), audit) if enriched else []
    current_allocation = build_allocation_view(enriched, audit)
    proposed_allocation = build_allocation_view(simulated, audit) if simulated else build_allocation_view([], audit)
    target_profile = profiler_output["allocation_targets"] if profiler_output else {}
    drift = compare_to_target_profile(current_allocation, target_profile, audit) if target_profile else []

    scenario["profiler_output"] = profiler_output
    scenario["current_allocation"] = current_allocation
    scenario["proposed_allocation"] = proposed_allocation
    scenario["market_context"] = build_scenario_market_context(enriched, resolved["scenario_type"], profiler_output, audit)
    scenario["transparency"] = build_transparency(
        scenario_type=resolved["scenario_type"],
        actions=scenario["actions"],
        current_allocation=current_allocation,
        proposed_allocation=proposed_allocation,
        profiler_output=profiler_output,
        custom_scenario_text=custom_text,
        audit=audit,
    )

    if resolved["concerns"] and len(resolved["concerns"]) > 1:
        scenario["summary"] += f" Custom input also signaled: {', '.join(resolved['concerns'][1:])}."
    if drift:
        top_gap = drift[0]
        scenario["summary"] += (
            f" Largest target-profile drift is {top_gap['category']} at {top_gap['drift_pct']:+.1f}% versus target."
        )
    scenario["audit_result"] = build_audit_result(scenario, request_audit=audit)
    add_event(audit, "scenario_service", "assemble_response", f"Built scenario response for {resolved['scenario_type']}.")
    return scenario
