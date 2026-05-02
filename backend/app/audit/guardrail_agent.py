from app.audit.audit_rules import evaluate_controls
from app.services.audit_service import add_event


def evaluate_recommendation_guardrails(evidence: dict, logs: list[dict], request_audit: dict | None = None) -> tuple[list[dict], list[dict]]:
    controls = evaluate_controls(evidence)
    if request_audit is not None:
        add_event(request_audit, "guardrail_agent", "evaluate_controls", f"Evaluated {len(controls)} recommendation audit controls.")
    if any(control["status"] == "Fail" for control in controls):
        logs.append({"step": "guardrail_summary", "level": "error", "detail": "One or more hard-fail controls were triggered."})
    elif any(control["status"] == "Review Needed" for control in controls):
        logs.append({"step": "guardrail_summary", "level": "warning", "detail": "Recommendation passed basic checks but needs review on one or more controls."})
    else:
        logs.append({"step": "guardrail_summary", "level": "info", "detail": "All recommendation audit controls passed."})
    return controls, logs
