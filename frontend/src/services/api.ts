import { recordAudit, recordAuditReview } from '../state/auditStore'
import type {
  AuditDemoLogsResponse,
  AuditDemoResultsResponse,
  AuditEvaluateResponse,
  HoldingCreate,
  HoldingMutationResponse,
  HoldingsResponse,
  LookupResponse,
  OnboardingAnswers,
  PortfolioSummaryResponse,
  ScenarioAnalyzeRequest,
  ScenarioAnalyzeResponse,
  ScenarioCatalogResponse,
  UserResponse,
} from '../types'

const BASE = '/api'

async function request<T>(path: string, feature: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || `Request failed: ${response.status}`)
  }

  const payload = await response.json() as T & { audit?: unknown }
  if (payload && typeof payload === 'object' && 'audit' in payload && payload.audit) {
    recordAudit(feature, payload.audit as any)
  }
  if (
    payload &&
    typeof payload === 'object' &&
    'scenario' in payload &&
    payload.scenario &&
    typeof payload.scenario === 'object' &&
    'audit_result' in payload.scenario &&
    payload.scenario.audit_result
  ) {
    recordAuditReview(feature, payload.scenario.audit_result as any)
  }
  return payload as T
}

export const api = {
  getUser: () => request<UserResponse>('/users/profile', 'users.profile'),
  completeOnboarding: (answers: OnboardingAnswers) =>
    request<UserResponse>('/users/onboarding', 'users.onboarding', {
      method: 'POST',
      body: JSON.stringify(answers),
    }),
  getPortfolioSummary: () => request<PortfolioSummaryResponse>('/portfolio/summary', 'portfolio.summary'),
  getHoldings: () => request<HoldingsResponse>('/holdings/', 'holdings.list'),
  lookupSymbols: (query: string) => request<LookupResponse>(`/holdings/lookup?q=${encodeURIComponent(query)}`, 'holdings.lookup'),
  addHolding: (payload: HoldingCreate) =>
    request<HoldingMutationResponse>('/holdings/', 'holdings.create', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  updateHolding: (id: number, payload: Partial<HoldingCreate>) =>
    request<HoldingMutationResponse>(`/holdings/${id}`, 'holdings.update', {
      method: 'PUT',
      body: JSON.stringify(payload),
    }),
  deleteHolding: (id: number) =>
    request<HoldingMutationResponse>(`/holdings/${id}`, 'holdings.delete', {
      method: 'DELETE',
    }),
  listScenarios: () => request<ScenarioCatalogResponse>('/scenarios/', 'scenarios.catalog'),
  analyzeScenario: (payload: ScenarioAnalyzeRequest) =>
    request<ScenarioAnalyzeResponse>('/scenarios/analyze', 'scenarios.analyze', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  getAuditDemoResults: () => request<AuditDemoResultsResponse>('/audit/demo-results', 'audit.demo-results'),
  getAuditDemoLogs: () => request<AuditDemoLogsResponse>('/audit/demo-logs', 'audit.demo-logs'),
  evaluateAudit: (scenario: Record<string, unknown>, request_audit?: Record<string, unknown>) =>
    request<AuditEvaluateResponse>('/audit/evaluate', 'audit.evaluate', {
      method: 'POST',
      body: JSON.stringify({ scenario, request_audit }),
    }),
}
