from app.audit.audit_evidence_agent import collect_audit_evidence
from app.audit.guardrail_agent import evaluate_recommendation_guardrails


def build_audit_result(scenario: dict, request_audit: dict | None = None) -> dict:
    request_audit = normalize_request_audit(request_audit)
    evidence, logs = collect_audit_evidence(scenario, request_audit=request_audit)
    controls, logs = evaluate_recommendation_guardrails(evidence, logs, request_audit=request_audit)
    overall_status = derive_overall_status(controls)
    counts = {
        "pass": sum(1 for item in controls if item["status"] == "Pass"),
        "review_needed": sum(1 for item in controls if item["status"] == "Review Needed"),
        "fail": sum(1 for item in controls if item["status"] == "Fail"),
    }
    summary = (
        f"{overall_status}: {counts['pass']} controls passed, "
        f"{counts['review_needed']} need review, {counts['fail']} failed."
    )
    return {
        "overall_status": overall_status,
        "summary": summary,
        "controls": controls,
        "evidence": evidence,
        "logs": logs,
    }


def derive_overall_status(controls: list[dict]) -> str:
    if any(item["status"] == "Fail" for item in controls):
        return "Fail"
    if any(item["status"] == "Review Needed" for item in controls):
        return "Review Needed"
    return "Pass"


def normalize_request_audit(request_audit: dict | None) -> dict:
    payload = dict(request_audit or {})
    payload.setdefault("agents", [])
    payload.setdefault("checks", [])
    payload.setdefault("events", [])
    payload.setdefault("data_sources", [])
    return payload
