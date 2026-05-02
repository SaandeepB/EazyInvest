export interface AuditCheck {
  name: string
  status: 'passed' | 'warning' | 'failed'
  detail: string
}

export interface AuditEvent {
  agent: string
  action: string
  detail: string
}

export interface AuditPayload {
  request_id: string
  feature: string
  timestamp: string
  agents: string[]
  checks: AuditCheck[]
  events: AuditEvent[]
  data_sources: string[]
}

export interface AuditControlResult {
  code: string
  title: string
  status: 'Pass' | 'Review Needed' | 'Fail'
  detail: string
  evidence: string[]
}

export interface AuditLogEntry {
  step: string
  level: 'info' | 'warning' | 'error'
  detail: string
}

export interface AuditResult {
  overall_status: 'Pass' | 'Review Needed' | 'Fail'
  summary: string
  controls: AuditControlResult[]
  evidence: Record<string, unknown>
  logs: AuditLogEntry[]
}

export interface User {
  id: number
  name: string
  risk_profile: 'Conservative' | 'Balanced' | 'Growth'
  goal: string
  time_horizon: string
  planned_withdrawal_pct: number
  starting_amount: number
  monthly_contribution: number
  contribution_stability: string
  behavioral_risk: string
  has_emergency_fund: string
  account_type: string
  has_external_holdings: string
  ux_mode: string
  created_at: string
}

export interface UserResponse {
  user: User
  audit: AuditPayload
}

export interface UserUpdatePayload {
  name?: string
  risk_profile?: string
  goal?: string
  time_horizon?: string
  planned_withdrawal_pct?: number
  starting_amount?: number
  monthly_contribution?: number
  contribution_stability?: string
  behavioral_risk?: string
  has_emergency_fund?: string
  account_type?: string
  has_external_holdings?: string
  ux_mode?: string
}

export interface OnboardingAnswers {
  goal: string
  time_horizon: string
  starting_amount: number
  monthly_contribution: number
  contribution_stability: string
  loss_comfort: string
  behavioral_risk: string
  near_term_withdrawal: boolean
  withdrawal_pct: number
  has_emergency_fund: string
  account_type: string
  has_external_holdings: string
  ux_mode: string
}

export interface Holding {
  id: number
  symbol: string
  name: string
  asset_type: string
  portfolio_bucket: string
  sector_or_category: string
  risk_bucket: string
  is_diversified: boolean
  quantity: number
  avg_cost: number
  cost_basis: number
  current_price: number | null
  current_value: number | null
  estimated_value: number | null
  price_source: string
  price_freshness: string
  as_of_date: string | null
  gain_loss: number
  gain_loss_pct: number
  weight_pct: number
  updated_at: string
}

export interface HoldingsResponse {
  holdings: Holding[]
  audit: AuditPayload
}

export interface HoldingMutationResponse {
  holding?: Holding
  deleted_id?: number
  audit: AuditPayload
}

export interface HoldingCreate {
  symbol: string
  quantity: number
  avg_cost: number
}

export interface LookupResult {
  symbol: string
  name: string
  asset_type: string
  sector_or_category: string
  proxy_price: number
  risk_bucket: string
  is_diversified: boolean
}

export interface LookupResponse {
  results: LookupResult[]
  audit: AuditPayload
}

export interface HealthScores {
  overall: number
  diversification: number
  concentration: number
  risk_alignment: number
  liquidity_readiness: number
  label: string
}

export interface AllocationItem {
  symbol: string
  name: string
  asset_type: string
  sector_or_category: string
  current_value: number
  weight_pct: number
  gain_loss: number
  gain_loss_pct: number
}

export interface AllocationBarItem {
  label: string
  value: number
  weight_pct: number
}

export interface PortfolioPayload {
  total_value: number
  total_cost: number
  total_gain_loss: number
  total_gain_loss_pct: number
  stock_value: number
  etf_value: number
  stock_allocation_pct: number
  etf_allocation_pct: number
  holdings_count: number
  top_holding_symbol: string
  top_holding_pct: number
  concentration_warning: boolean
  health: HealthScores
  risk_level: string
  price_source: string
  data_source_note: string
  allocation_bars: AllocationBarItem[]
  top_holdings: AllocationItem[]
  holdings: AllocationItem[]
}

export interface MarketContextSummary {
  source: string
  supported_symbol_count: number
  top_sectors: string[]
  diversified_weight_pct: number
  narrative: string
}

export interface ProfilerSummary {
  investor_segment: string
  risk_profile: string
  liquidity_need: string
  time_horizon_bucket: string
  recommended_scenario_type: string
  confidence: number
  reasoning: string
  target_profile_name: string
  allocation_targets: Record<string, number>
  max_single_holding_pct: number
  max_sector_pct: number
  rebalance_trigger_pct: number
  warning_rules: string[]
  target_stock_pct: number
  planning_style: string
  tags: string[]
  explanation: string
}

export interface PortfolioSummaryResponse {
  portfolio: PortfolioPayload
  market_context: MarketContextSummary
  profiler: ProfilerSummary
  audit: AuditPayload
}

export type ScenarioType = 'market_drop' | 'inflation' | 'withdrawal' | 'reduce_risk' | 'concentration'

export interface ScenarioCatalogItem {
  type: ScenarioType
  label: string
  description: string
}

export interface ScenarioCatalogResponse {
  scenarios: ScenarioCatalogItem[]
  audit: AuditPayload
}

export interface RebalanceAction {
  symbol: string
  name: string
  action: 'trim' | 'add' | 'hold'
  owned_holding: boolean
  current_weight_pct: number
  target_weight_pct: number
  change_pct: number
  reason: string
}

export interface TransparencyDetail {
  why_suggested: string
  what_changes: string
  upside: string
  downside: string
  selling_impact: string
  guardrail_note: string
  goal_alignment: string
}

export interface ScenarioPayload {
  scenario_type: ScenarioType
  scenario_label: string
  summary: string
  profiler_output?: ProfilerSummary | null
  current_health: HealthScores
  projected_health: HealthScores
  current_allocation: Record<string, number>
  proposed_allocation: Record<string, number>
  before_allocation: Record<string, number>
  after_allocation: Record<string, number>
  actions: RebalanceAction[]
  transparency: TransparencyDetail
  market_context: MarketContextSummary
  estimated_cost_note: string
  estimated_tax_note: string
  audit_result?: AuditResult | null
}

export interface ScenarioAnalyzeRequest {
  scenario_type?: string
  custom_params?: Record<string, unknown>
  custom_scenario_text?: string
}

export interface ScenarioAnalyzeResponse {
  scenario: ScenarioPayload
  audit: AuditPayload
}

export interface AuditEvaluateResponse {
  audit_result: AuditResult
  audit: AuditPayload
}

export interface AuditDemoResultItem {
  case_name: string
  audit_result: AuditResult
}

export interface AuditDemoResultsResponse {
  results: AuditDemoResultItem[]
  audit: AuditPayload
}

export interface AuditDemoLogItem {
  case_name: string
  overall_status: 'Pass' | 'Review Needed' | 'Fail'
  logs: AuditLogEntry[]
}

export interface AuditDemoLogsResponse {
  logs: AuditDemoLogItem[]
  audit: AuditPayload
}
