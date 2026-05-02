CONTROL_TITLES = {
    "C001": "High-risk beginner warning",
    "C002": "Scenario explanation present",
    "C003": "Cost disclosure present",
    "C004": "Tax caution present when selling",
    "C005": "Goal alignment present",
    "C006": "Allocation validity",
    "C007": "Data source/freshness logged",
    "C008": "Holdings coverage check",
    "C009": "Evidence completeness",
    "C010": "Unsupported guarantee check",
    "C011": "Target profile selected",
    "C012": "Recommendation aligned with target profile",
}


def evaluate_controls(evidence: dict) -> list[dict]:
    return [
        _c001(evidence),
        _c002(evidence),
        _c003(evidence),
        _c004(evidence),
        _c005(evidence),
        _c006(evidence),
        _c007(evidence),
        _c008(evidence),
        _c009(evidence),
        _c010(evidence),
        _c011(evidence),
        _c012(evidence),
    ]


def _c001(evidence: dict) -> dict:
    if not evidence["high_risk_beginner"]:
        return _result("C001", "Pass", "High-risk beginner warning was not required for this profile.", ["Profile was not classified as high-risk beginner."])
    if evidence["high_risk_warning_present"]:
        return _result("C001", "Pass", "High-risk warning content was present.", ["Warning language found in profile warnings or explanation."])
    return _result("C001", "Review Needed", "High-risk beginner profile needs clearer warning language.", ["High-risk beginner profile detected without explicit caution text."])


def _c002(evidence: dict) -> dict:
    if evidence["has_summary"] and evidence["has_explanation"] and evidence["has_what_changes"]:
        return _result("C002", "Pass", "Scenario explanation and change summary were present.", ["Summary, why_suggested, and what_changes were populated."])
    return _result("C002", "Fail", "Scenario explanation was incomplete.", ["Missing one or more of summary, why_suggested, or what_changes."])


def _c003(evidence: dict) -> dict:
    text = evidence["cost_disclosure_text"].lower()
    if evidence["has_cost_disclosure"] and any(term in text for term in ("cost", "illustrative", "proxy", "deterministic")):
        return _result("C003", "Pass", "Cost disclosure was present.", [evidence["cost_disclosure_text"]])
    return _result("C003", "Review Needed", "Cost disclosure should be clearer.", ["estimated_cost_note was missing or too vague."])


def _c004(evidence: dict) -> dict:
    if evidence["selling_actions_count"] == 0:
        return _result("C004", "Pass", "No selling actions were modeled, so tax caution was not required.", ["selling_actions_count = 0"])
    if evidence["has_tax_note"] and "tax" in evidence["tax_note_text"].lower():
        return _result("C004", "Pass", "Tax caution was present for selling actions.", [evidence["tax_note_text"]])
    return _result("C004", "Fail", "Selling actions need explicit tax caution.", ["Trim actions were present without an adequate tax note."])


def _c005(evidence: dict) -> dict:
    if evidence["has_goal_alignment"]:
        return _result("C005", "Pass", "Goal alignment explanation was present.", [evidence["goal_alignment_text"]])
    return _result("C005", "Review Needed", "Goal alignment explanation should be present.", ["transparency.goal_alignment was empty."])


def _c006(evidence: dict) -> dict:
    total = evidence["proposed_allocation_total"]
    negatives = evidence["negative_allocations"]
    if negatives:
        return _result("C006", "Fail", f"Proposed allocation contained negative categories: {', '.join(negatives)}.", [f"proposed_total={total:.2f}%"])
    if 99.0 <= total <= 101.0:
        return _result("C006", "Pass", "Proposed allocation summed to a valid total.", [f"proposed_total={total:.2f}%"])
    if 95.0 <= total <= 105.0:
        return _result("C006", "Review Needed", "Proposed allocation was close to valid but needs review.", [f"proposed_total={total:.2f}%"])
    return _result("C006", "Fail", "Proposed allocation total was materially invalid.", [f"proposed_total={total:.2f}%"])


def _c007(evidence: dict) -> dict:
    if evidence["data_source"] != "unknown" and evidence["freshness_note"] and (
        evidence["request_data_sources"] or evidence["data_source"] in {"syndicated_csv", "csv_proxy"}
    ):
        return _result("C007", "Pass", "Data source and freshness were logged.", [evidence["data_source"], evidence["freshness_note"]])
    return _result("C007", "Review Needed", "Data source or freshness logging was incomplete.", ["Missing source or freshness note."])


def _c008(evidence: dict) -> dict:
    coverage_total = evidence["before_allocation_total"] or evidence["current_allocation_total"]
    if evidence["holdings_count"] == 0:
        return _result("C008", "Review Needed", "No holdings were present to validate coverage.", ["holdings_count = 0"])
    if 99.0 <= coverage_total <= 101.0:
        return _result("C008", "Pass", "Holdings coverage looked complete.", [f"coverage_total={coverage_total:.2f}%"])
    return _result("C008", "Review Needed", "Holdings coverage looked incomplete.", [f"coverage_total={coverage_total:.2f}%"])


def _c009(evidence: dict) -> dict:
    missing = []
    for label, present in {
        "profiler_output": evidence["profiler_present"],
        "transparency": evidence["transparency_present"],
        "market_context": evidence["market_context_present"],
        "actions": evidence["actions_present"],
    }.items():
        if not present:
            missing.append(label)
    if not missing:
        return _result("C009", "Pass", "Evidence set was complete.", ["Profiler, transparency, market context, and actions were present."])
    if len(missing) <= 2:
        return _result("C009", "Review Needed", "Evidence set was partially incomplete.", [f"Missing: {', '.join(missing)}"])
    return _result("C009", "Fail", "Evidence set was materially incomplete.", [f"Missing: {', '.join(missing)}"])


def _c010(evidence: dict) -> dict:
    if not evidence["guarantee_hits"]:
        return _result("C010", "Pass", "No unsupported guarantee language was found.", ["guarantee_hits = none"])
    return _result("C010", "Fail", "Unsupported guarantee language was detected.", evidence["guarantee_hits"])


def _c011(evidence: dict) -> dict:
    if evidence["target_profile_name"]:
        return _result("C011", "Pass", "Target profile was selected.", [evidence["target_profile_name"]])
    return _result("C011", "Review Needed", "Target profile selection was missing.", ["profiler_output.target_profile_name was empty."])


def _c012(evidence: dict) -> dict:
    target = evidence["target_allocation"]
    if not target:
        return _result("C012", "Review Needed", "Could not compare recommendation to target profile.", ["No target allocation was present."])
    current_drift = _total_drift(evidence["current_allocation"], target)
    proposed_drift = _total_drift(evidence["proposed_allocation"], target)
    detail = f"Current drift {current_drift:.2f}, proposed drift {proposed_drift:.2f}."
    if proposed_drift <= current_drift + 0.5:
        return _result("C012", "Pass", "Recommendation moved toward or held target-profile alignment.", [detail])
    if proposed_drift <= current_drift + 5.0:
        return _result("C012", "Review Needed", "Recommendation alignment to target profile needs review.", [detail])
    return _result("C012", "Fail", "Recommendation moved materially away from the target profile.", [detail])


def _total_drift(allocation: dict[str, float], target: dict[str, float]) -> float:
    keys = set(allocation.keys()) | set(target.keys())
    return round(sum(abs(allocation.get(key, 0.0) - target.get(key, 0.0)) for key in keys), 2)


def _result(code: str, status: str, detail: str, evidence: list[str]) -> dict:
    return {
        "code": code,
        "title": CONTROL_TITLES[code],
        "status": status,
        "detail": detail,
        "evidence": evidence,
    }
