from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.schemas import ScenarioAnalyzeResponse, ScenarioCatalogResponse, ScenarioRequest
from app.services.audit_guardrail_agent import enforce_no_live_sources
from app.services.audit_service import finalize_audit, start_audit
from app.services.holdings_service import get_or_create_user, list_holdings
from app.services.scenario_service import analyze_scenario_request, list_scenarios


router = APIRouter(prefix="/scenarios", tags=["scenarios"])


@router.get("/", response_model=ScenarioCatalogResponse)
def get_scenario_catalog(db: Session = Depends(get_db)):
    audit = start_audit("scenarios.catalog")
    _ = db
    scenarios = list_scenarios(audit)
    enforce_no_live_sources(audit)
    return {"scenarios": scenarios, "audit": finalize_audit(audit)}


@router.post("/analyze", response_model=ScenarioAnalyzeResponse)
def run_scenario(payload: ScenarioRequest, db: Session = Depends(get_db)):
    audit = start_audit("scenarios.analyze")
    user = get_or_create_user(db)
    holdings = list_holdings(db)
    try:
        scenario = analyze_scenario_request(holdings, user, payload, audit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    enforce_no_live_sources(audit)
    return {"scenario": scenario, "audit": finalize_audit(audit)}
