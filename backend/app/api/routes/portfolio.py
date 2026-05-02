from app.agents.profiler_agent import build_profiler_summary
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.schemas import PortfolioSummaryResponse
from app.services.audit_guardrail_agent import enforce_no_live_sources, validate_holdings
from app.services.audit_service import finalize_audit, start_audit
from app.services.holdings_service import get_or_create_user, list_holdings
from app.services.market_context_agent import build_market_context
from app.services.portfolio_math_service import enrich_holdings
from app.services.portfolio_service import build_portfolio_summary


router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/summary", response_model=PortfolioSummaryResponse)
def get_portfolio_summary(db: Session = Depends(get_db)):
    audit = start_audit("portfolio.summary")
    user = get_or_create_user(db)
    holdings = list_holdings(db)
    enriched = enrich_holdings(holdings, audit)
    portfolio = build_portfolio_summary(holdings, user, audit)
    market_context = build_market_context(enriched, audit)
    profiler = build_profiler_summary(user, len(enriched), audit)
    enforce_no_live_sources(audit)
    validate_holdings(enriched, audit)
    return {
        "portfolio": portfolio,
        "market_context": market_context,
        "profiler": profiler,
        "audit": finalize_audit(audit),
    }
