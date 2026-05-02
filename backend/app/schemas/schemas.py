from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field
from app.audit.audit_schemas import AuditResult


class AuditCheck(BaseModel):
    name: str
    status: Literal["passed", "warning", "failed"]
    detail: str


class AuditEvent(BaseModel):
    agent: str
    action: str
    detail: str


class AuditPayload(BaseModel):
    request_id: str
    feature: str
    timestamp: str
    agents: List[str]
    checks: List[AuditCheck]
    events: List[AuditEvent]
    data_sources: List[str]


class UserBase(BaseModel):
    name: str = "EazyInvest User"
    risk_profile: str = "Balanced"
    goal: str = "Long-term growth"
    time_horizon: str = "10+ years"
    planned_withdrawal_pct: float = 0.0
    starting_amount: float = 0.0
    monthly_contribution: float = 0.0
    contribution_stability: str = "Stable"
    behavioral_risk: str = "Hold"
    has_emergency_fund: str = "Yes"
    account_type: str = "Taxable"
    has_external_holdings: str = "No"
    ux_mode: str = "Simple"


class UserUpdate(BaseModel):
    name: Optional[str] = None
    risk_profile: Optional[str] = None
    goal: Optional[str] = None
    time_horizon: Optional[str] = None
    planned_withdrawal_pct: Optional[float] = None
    starting_amount: Optional[float] = None
    monthly_contribution: Optional[float] = None
    contribution_stability: Optional[str] = None
    behavioral_risk: Optional[str] = None
    has_emergency_fund: Optional[str] = None
    account_type: Optional[str] = None
    has_external_holdings: Optional[str] = None
    ux_mode: Optional[str] = None


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class UserResponse(BaseModel):
    user: UserOut
    audit: AuditPayload


class OnboardingAnswers(BaseModel):
    goal: str
    time_horizon: str
    starting_amount: float = 0.0
    monthly_contribution: float = 0.0
    contribution_stability: str = "Stable"
    loss_comfort: str
    behavioral_risk: str = "Hold"
    near_term_withdrawal: bool = False
    withdrawal_pct: float = 0.0
    has_emergency_fund: str = "Yes"
    account_type: str = "Taxable"
    has_external_holdings: str = "No"
    ux_mode: str = "Simple"


class HoldingCreate(BaseModel):
    symbol: str
    quantity: float = Field(..., gt=0)
    avg_cost: float = Field(..., gt=0)


class HoldingUpdate(BaseModel):
    quantity: Optional[float] = Field(None, gt=0)
    avg_cost: Optional[float] = Field(None, gt=0)


class HoldingView(BaseModel):
    id: int
    symbol: str
    name: str
    asset_type: str
    portfolio_bucket: str
    sector_or_category: str
    risk_bucket: str
    is_diversified: bool
    quantity: float
    avg_cost: float
    cost_basis: float
    current_price: Optional[float]
    current_value: Optional[float]
    estimated_value: Optional[float]
    price_source: str
    price_freshness: str
    as_of_date: Optional[str]
    gain_loss: float
    gain_loss_pct: float
    weight_pct: float
    updated_at: datetime


class HoldingsResponse(BaseModel):
    holdings: List[HoldingView]
    audit: AuditPayload


class HoldingMutationResponse(BaseModel):
    holding: Optional[HoldingView] = None
    deleted_id: Optional[int] = None
    audit: AuditPayload


class LookupResult(BaseModel):
    symbol: str
    name: str
    asset_type: str
    sector_or_category: str
    proxy_price: float
    risk_bucket: str
    is_diversified: bool


class LookupResponse(BaseModel):
    results: List[LookupResult]
    audit: AuditPayload


class HealthScores(BaseModel):
    overall: float
    diversification: float
    concentration: float
    risk_alignment: float
    liquidity_readiness: float
    label: str


class AllocationItem(BaseModel):
    symbol: str
    name: str
    asset_type: str
    sector_or_category: str
    current_value: float
    weight_pct: float
    gain_loss: float
    gain_loss_pct: float


class AllocationBarItem(BaseModel):
    label: str
    value: float
    weight_pct: float


class PortfolioPayload(BaseModel):
    total_value: float
    total_cost: float
    total_gain_loss: float
    total_gain_loss_pct: float
    stock_value: float
    etf_value: float
    stock_allocation_pct: float
    etf_allocation_pct: float
    holdings_count: int
    top_holding_symbol: str
    top_holding_pct: float
    concentration_warning: bool
    health: HealthScores
    risk_level: str
    price_source: str
    data_source_note: str
    allocation_bars: List[AllocationBarItem]
    top_holdings: List[AllocationItem]
    holdings: List[AllocationItem]


class MarketContextSummary(BaseModel):
    source: str
    supported_symbol_count: int
    top_sectors: List[str]
    diversified_weight_pct: float
    narrative: str


class TargetProfileConfig(BaseModel):
    allocation_targets: Dict[str, float]
    max_single_holding_pct: float
    max_sector_pct: float
    rebalance_trigger_pct: float
    warning_rules: List[str]


class ProfilerSummary(BaseModel):
    investor_segment: str
    risk_profile: str
    liquidity_need: str
    time_horizon_bucket: str
    recommended_scenario_type: str
    confidence: float
    reasoning: str
    target_profile_name: str
    allocation_targets: Dict[str, float]
    max_single_holding_pct: float
    max_sector_pct: float
    rebalance_trigger_pct: float
    warning_rules: List[str]
    target_stock_pct: float
    planning_style: str
    tags: List[str]
    explanation: str


class PortfolioSummaryResponse(BaseModel):
    portfolio: PortfolioPayload
    market_context: MarketContextSummary
    profiler: ProfilerSummary
    audit: AuditPayload


class ScenarioCatalogItem(BaseModel):
    type: str
    label: str
    description: str


class ScenarioCatalogResponse(BaseModel):
    scenarios: List[ScenarioCatalogItem]
    audit: AuditPayload


class ScenarioRequest(BaseModel):
    scenario_type: Optional[str] = None
    custom_params: Optional[Dict[str, Any]] = None
    custom_scenario_text: Optional[str] = None


class RebalanceAction(BaseModel):
    symbol: str
    name: str
    action: Literal["trim", "add", "hold"]
    owned_holding: bool
    current_weight_pct: float
    target_weight_pct: float
    change_pct: float
    reason: str


class TransparencyDetail(BaseModel):
    why_suggested: str
    what_changes: str
    upside: str
    downside: str
    selling_impact: str
    guardrail_note: str
    goal_alignment: str


class ScenarioPayload(BaseModel):
    scenario_type: str
    scenario_label: str
    summary: str
    profiler_output: Optional[ProfilerSummary] = None
    current_health: HealthScores
    projected_health: HealthScores
    current_allocation: Dict[str, float]
    proposed_allocation: Dict[str, float]
    before_allocation: Dict[str, float]
    after_allocation: Dict[str, float]
    actions: List[RebalanceAction]
    transparency: TransparencyDetail
    market_context: MarketContextSummary
    estimated_cost_note: str
    estimated_tax_note: str
    audit_result: Optional[AuditResult] = None


class ScenarioAnalyzeResponse(BaseModel):
    scenario: ScenarioPayload
    audit: AuditPayload
