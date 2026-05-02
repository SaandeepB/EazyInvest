from fastapi import APIRouter

from app.audit.audit_payload_builder import build_audit_result
from app.audit.audit_schemas import (
    AuditDemoLogsResponse,
    AuditDemoResultsResponse,
    AuditEvaluateRequest,
    AuditEvaluateResponse,
)
from app.audit.mock_audit_payloads import get_demo_cases
from app.services.audit_service import finalize_audit, start_audit


router = APIRouter(prefix="/audit", tags=["audit"])


@router.post("/evaluate", response_model=AuditEvaluateResponse)
def evaluate_audit(payload: AuditEvaluateRequest):
    audit = start_audit("audit.evaluate")
    audit_result = build_audit_result(payload.scenario, request_audit=payload.request_audit)
    return {"audit_result": audit_result, "audit": finalize_audit(audit)}


@router.get("/demo-results", response_model=AuditDemoResultsResponse)
def get_demo_results():
    audit = start_audit("audit.demo_results")
    results = []
    for case in get_demo_cases():
        results.append(
            {
                "case_name": case["case_name"],
                "audit_result": build_audit_result(case["scenario"], request_audit=case["request_audit"]),
            }
        )
    return {"results": results, "audit": finalize_audit(audit)}


@router.get("/demo-logs", response_model=AuditDemoLogsResponse)
def get_demo_logs():
    audit = start_audit("audit.demo_logs")
    logs = []
    for case in get_demo_cases():
        audit_result = build_audit_result(case["scenario"], request_audit=case["request_audit"])
        logs.append(
            {
                "case_name": case["case_name"],
                "overall_status": audit_result["overall_status"],
                "logs": audit_result["logs"],
            }
        )
    return {"logs": logs, "audit": finalize_audit(audit)}
