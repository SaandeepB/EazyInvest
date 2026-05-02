from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel


AuditStatus = Literal["Pass", "Review Needed", "Fail"]
LogLevel = Literal["info", "warning", "error"]


class AuditControlResult(BaseModel):
    code: str
    title: str
    status: AuditStatus
    detail: str
    evidence: List[str]


class AuditLogEntry(BaseModel):
    step: str
    level: LogLevel
    detail: str


class AuditResult(BaseModel):
    overall_status: AuditStatus
    summary: str
    controls: List[AuditControlResult]
    evidence: Dict[str, Any]
    logs: List[AuditLogEntry]


class AuditEvaluateRequest(BaseModel):
    scenario: Dict[str, Any]
    request_audit: Optional[Dict[str, Any]] = None


class AuditEvaluateResponse(BaseModel):
    audit_result: AuditResult
    audit: Dict[str, Any]


class AuditDemoResultItem(BaseModel):
    case_name: str
    audit_result: AuditResult


class AuditDemoResultsResponse(BaseModel):
    results: List[AuditDemoResultItem]
    audit: Dict[str, Any]


class AuditDemoLogItem(BaseModel):
    case_name: str
    overall_status: AuditStatus
    logs: List[AuditLogEntry]


class AuditDemoLogsResponse(BaseModel):
    logs: List[AuditDemoLogItem]
    audit: Dict[str, Any]
