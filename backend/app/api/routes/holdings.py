from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.schemas import HoldingCreate, HoldingMutationResponse, HoldingsResponse, HoldingUpdate, LookupResponse
from app.services.audit_guardrail_agent import enforce_no_live_sources, validate_holdings
from app.services.audit_service import finalize_audit, start_audit
from app.services.holdings_service import create_holding, delete_holding, list_holdings, update_holding
from app.services.market_dataset_service import search_symbols
from app.services.portfolio_math_service import enrich_holdings


router = APIRouter(prefix="/holdings", tags=["holdings"])


@router.get("/", response_model=HoldingsResponse)
def get_holdings(db: Session = Depends(get_db)):
    audit = start_audit("holdings.list")
    enriched = enrich_holdings(list_holdings(db), audit)
    enforce_no_live_sources(audit)
    validate_holdings(enriched, audit)
    return {"holdings": enriched, "audit": finalize_audit(audit)}


@router.get("/lookup", response_model=LookupResponse)
def lookup_holdings(q: str = Query("", min_length=0), db: Session = Depends(get_db)):
    audit = start_audit("holdings.lookup")
    _ = db  # keeps route signature consistent
    results = search_symbols(q, audit=audit)
    enforce_no_live_sources(audit)
    return {"results": results, "audit": finalize_audit(audit)}


@router.post("/", response_model=HoldingMutationResponse, status_code=201)
def add_holding(payload: HoldingCreate, db: Session = Depends(get_db)):
    audit = start_audit("holdings.create")
    try:
        holding = create_holding(db, payload.symbol, payload.quantity, payload.avg_cost, audit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    enriched = enrich_holdings([holding], audit)
    enforce_no_live_sources(audit)
    return {"holding": enriched[0], "audit": finalize_audit(audit)}


@router.put("/{holding_id}", response_model=HoldingMutationResponse)
def edit_holding(holding_id: int, payload: HoldingUpdate, db: Session = Depends(get_db)):
    audit = start_audit("holdings.update")
    holding = update_holding(db, holding_id, payload.quantity, payload.avg_cost, audit)
    if holding is None:
        raise HTTPException(status_code=404, detail="Holding not found")
    enriched = enrich_holdings([holding], audit)
    enforce_no_live_sources(audit)
    return {"holding": enriched[0], "audit": finalize_audit(audit)}


@router.delete("/{holding_id}", response_model=HoldingMutationResponse)
def remove_holding(holding_id: int, db: Session = Depends(get_db)):
    audit = start_audit("holdings.delete")
    deleted = delete_holding(db, holding_id, audit)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Holding not found")
    enforce_no_live_sources(audit)
    return {"deleted_id": holding_id, "audit": finalize_audit(audit)}
