from app.audit.audit_schemas import AuditLogEntry


GUARANTEE_TERMS = [
    "guarantee",
    "guaranteed",
    "certain gain",
    "cannot lose",
    "risk free return",
    "will definitely",
]


def collect_audit_evidence(scenario: dict, request_audit: dict | None = None) -> tuple[dict, list[dict]]:
    profiler = scenario.get("profiler_output") or {}
    transparency = scenario.get("transparency") or {}
    market_context = scenario.get("market_context") or {}
    actions = scenario.get("actions") or []
    current_allocation = scenario.get("current_allocation") or {}
    proposed_allocation = scenario.get("proposed_allocation") or {}
    before_allocation = scenario.get("before_allocation") or {}

    current_total = round(sum(current_allocation.values()), 2)
    proposed_total = round(sum(proposed_allocation.values()), 2)
    before_total = round(sum(before_allocation.values()), 2)
    negative_allocations = [key for key, value in proposed_allocation.items() if value < 0]
    selling_actions = [action for action in actions if action.get("action") == "trim"]
    target_profile_name = profiler.get("target_profile_name")
    text_blob = " ".join(
        str(value)
        for value in [
            scenario.get("summary", ""),
            transparency.get("why_suggested", ""),
            transparency.get("what_changes", ""),
            transparency.get("upside", ""),
            transparency.get("downside", ""),
            transparency.get("selling_impact", ""),
            transparency.get("goal_alignment", ""),
            scenario.get("estimated_cost_note", ""),
            scenario.get("estimated_tax_note", ""),
        ]
    ).lower()
    guarantee_hits = [term for term in GUARANTEE_TERMS if term in text_blob]

    warning_text = " ".join(profiler.get("warning_rules", [])) + " " + transparency.get("why_suggested", "")
    warning_text = warning_text.lower()
    high_risk_beginner = profiler.get("risk_profile") == "Growth" and profiler.get("investor_segment") in {
        "High-Risk Watchlist User",
        "Long-Term Growth Investor",
    }
    source = market_context.get("source") or "unknown"
    freshness_note = "Latest available market proxy" if source in {"syndicated_csv", "csv_proxy"} else "Unknown freshness"

    evidence = {
        "scenario_type": scenario.get("scenario_type"),
        "current_allocation_total": current_total,
        "proposed_allocation_total": proposed_total,
        "before_allocation_total": before_total,
        "negative_allocations": negative_allocations,
        "selling_actions_count": len(selling_actions),
        "data_source": source,
        "freshness_note": freshness_note,
        "request_data_sources": (request_audit or {}).get("data_sources", []),
        "request_agents": (request_audit or {}).get("agents", []),
        "request_checks": (request_audit or {}).get("checks", []),
        "holdings_count": len(before_allocation),
        "high_risk_beginner": high_risk_beginner,
        "high_risk_warning_present": any(term in warning_text for term in ("volatility", "concentrat", "downside", "risk")),
        "has_summary": bool(str(scenario.get("summary", "")).strip()),
        "has_explanation": bool(str(transparency.get("why_suggested", "")).strip()),
        "has_what_changes": bool(str(transparency.get("what_changes", "")).strip()),
        "has_cost_disclosure": bool(str(scenario.get("estimated_cost_note", "")).strip()),
        "cost_disclosure_text": str(scenario.get("estimated_cost_note", "")),
        "has_tax_note": bool(str(scenario.get("estimated_tax_note", "")).strip()),
        "tax_note_text": str(scenario.get("estimated_tax_note", "")),
        "has_goal_alignment": bool(str(transparency.get("goal_alignment", "")).strip()),
        "goal_alignment_text": str(transparency.get("goal_alignment", "")),
        "guarantee_hits": guarantee_hits,
        "target_profile_name": target_profile_name,
        "target_allocation": profiler.get("allocation_targets") or {},
        "current_allocation": current_allocation,
        "proposed_allocation": proposed_allocation,
        "market_context_present": bool(market_context),
        "profiler_present": bool(profiler),
        "transparency_present": bool(transparency),
        "actions_present": bool(actions),
    }

    logs = [
        AuditLogEntry(step="collect_scenario", level="info", detail=f"Captured scenario '{scenario.get('scenario_type', 'unknown')}' for audit."),
        AuditLogEntry(step="source_trace", level="info", detail=f"Data source logged as {source} with freshness note '{freshness_note}'."),
        AuditLogEntry(step="allocation_trace", level="info", detail=f"Current allocation total {current_total:.2f}%, proposed allocation total {proposed_total:.2f}%."),
        AuditLogEntry(step="action_trace", level="info", detail=f"Detected {len(actions)} action(s), including {len(selling_actions)} selling action(s)."),
    ]
    if guarantee_hits:
        logs.append(AuditLogEntry(step="guarantee_scan", level="error", detail=f"Unsupported guarantee language found: {', '.join(guarantee_hits)}."))
    return evidence, [log.model_dump() for log in logs]
