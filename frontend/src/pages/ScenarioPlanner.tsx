import { useEffect, useMemo, useState } from 'react'
import ControlMatrix from '../components/audit/ControlMatrix'
import PageShell from '../components/layout/PageShell'
import AllocationBar from '../components/ui/AllocationBar'
import MetricCard from '../components/ui/MetricCard'
import StatusPill from '../components/ui/StatusPill'
import { api } from '../services/api'
import type { ScenarioCatalogItem, ScenarioPayload } from '../types'

function formatAllocation(allocation: Record<string, number>) {
  return Object.entries(allocation).filter(([, value]) => value > 0)
}

function statusTone(status?: string): 'success' | 'warning' | 'error' | 'neutral' {
  if (status === 'Pass') return 'success'
  if (status === 'Review Needed') return 'warning'
  if (status === 'Fail') return 'error'
  return 'neutral'
}

export default function ScenarioPlanner() {
  const [scenarios, setScenarios] = useState<ScenarioCatalogItem[]>([])
  const [result, setResult] = useState<ScenarioPayload | null>(null)
  const [loadingType, setLoadingType] = useState<string | null>(null)
  const [customScenarioText, setCustomScenarioText] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    api.listScenarios().then(response => setScenarios(response.scenarios)).catch(() => setScenarios([]))
  }, [])

  const trustSummary = useMemo(() => {
    if (!result?.audit_result) return null
    const controls = result.audit_result.controls
    return {
      pass: controls.filter(control => control.status === 'Pass').length,
      review: controls.filter(control => control.status === 'Review Needed').length,
      fail: controls.filter(control => control.status === 'Fail').length,
    }
  }, [result])

  const runScenario = async (payload: { scenario_type?: string; custom_scenario_text?: string }) => {
    setLoadingType(payload.scenario_type ?? 'custom')
    setError('')
    try {
      const response = await api.analyzeScenario(payload)
      setResult(response.scenario)
    } catch (err: any) {
      setError(err.message || 'Could not analyze scenario.')
    } finally {
      setLoadingType(null)
    }
  }

  return (
    <PageShell
      eyebrow="Scenario Planner"
      title="Deterministic scenario testing"
      description="Use guided cards or enter a custom concern. Agents classify, route, explain, and validate, while the portfolio math stays deterministic."
      aside={result?.audit_result ? <StatusPill label={result.audit_result.overall_status} tone={statusTone(result.audit_result.overall_status)} /> : undefined}
    >
      <section className="card stack-sm">
        <div className="panel-head">
          <div className="section-title">Suggested scenarios</div>
          <StatusPill label={`${scenarios.length} available`} tone="navy" />
        </div>
        <div className="scenario-grid">
          {scenarios.map(scenario => (
            <button
              key={scenario.type}
              className="scenario-card"
              onClick={() => runScenario({ scenario_type: scenario.type })}
              disabled={loadingType !== null}
            >
              <strong>{scenario.label}</strong>
              <span>{scenario.description}</span>
              <StatusPill label={loadingType === scenario.type ? 'Running' : 'Analyze'} tone="blue" />
            </button>
          ))}
        </div>
      </section>

      <section className="card stack-sm">
        <div className="section-title">Custom scenario input</div>
        <textarea
          className="scenario-textarea"
          value={customScenarioText}
          onChange={event => setCustomScenarioText(event.target.value)}
          placeholder="I might need 20% of my money next year and I am worried the market may drop."
          rows={4}
        />
        <div className="button-row">
          <button
            className="btn btn-primary"
            onClick={() => runScenario({ custom_scenario_text: customScenarioText })}
            disabled={!customScenarioText.trim() || loadingType !== null}
          >
            {loadingType === 'custom' ? 'Running...' : 'Analyze custom scenario'}
          </button>
        </div>
        {error && <div className="error-banner">{error}</div>}
      </section>

      {result && (
        <section className="stack-lg">
          <section className="card stack-sm">
            <div className="panel-head">
              <div>
                <div className="section-title">{result.scenario_label}</div>
                <p className="muted">{result.summary}</p>
              </div>
              {result.audit_result && <StatusPill label={result.audit_result.overall_status} tone={statusTone(result.audit_result.overall_status)} />}
            </div>

            <div className="metric-grid">
              <MetricCard label="Current Health" value={result.current_health.overall.toFixed(0)} tone="navy" />
              <MetricCard label="Projected Health" value={result.projected_health.overall.toFixed(0)} tone="teal" />
              <MetricCard label="Actions" value={String(result.actions.length)} tone="blue" />
              {trustSummary && (
                <MetricCard
                  label="Trust Check"
                  value={`${trustSummary.pass}/${result.audit_result?.controls.length ?? 0}`}
                  detail={`${trustSummary.review} review | ${trustSummary.fail} fail`}
                  tone={trustSummary.fail ? 'error' : trustSummary.review ? 'warning' : 'success'}
                />
              )}
            </div>
          </section>

          <section className="content-grid">
            <div className="stack-lg">
              {result.profiler_output && (
                <section className="card stack-sm">
                  <div className="panel-head">
                    <div className="section-title">Profiler summary</div>
                    <StatusPill label={result.profiler_output.investor_segment} tone="blue" />
                  </div>
                  <div className="summary-grid">
                    <div className="summary-item">
                      <span className="muted">Risk profile</span>
                      <strong>{result.profiler_output.risk_profile}</strong>
                    </div>
                    <div className="summary-item">
                      <span className="muted">Liquidity need</span>
                      <strong>{result.profiler_output.liquidity_need}</strong>
                    </div>
                    <div className="summary-item">
                      <span className="muted">Time horizon</span>
                      <strong>{result.profiler_output.time_horizon_bucket}</strong>
                    </div>
                    <div className="summary-item">
                      <span className="muted">Recommended route</span>
                      <strong>{result.profiler_output.recommended_scenario_type}</strong>
                    </div>
                  </div>
                  <div className="muted">{result.profiler_output.reasoning}</div>
                </section>
              )}

              <section className="card stack-sm">
                <div className="panel-head">
                  <div className="section-title">Strategist / rebalancing output</div>
                  <StatusPill label={`${result.actions.length} actions`} tone="navy" />
                </div>
                <div className="stack-sm">
                  {result.actions.map(action => (
                    <div key={`${action.symbol}-${action.action}`} className="action-card">
                      <div className="panel-head">
                        <div>
                          <strong>{action.symbol}</strong>
                          <div className="muted">{action.owned_holding ? 'Owned holding' : 'Suggested instrument'}</div>
                        </div>
                        <StatusPill label={action.action} tone={action.action === 'trim' ? 'warning' : action.action === 'add' ? 'success' : 'neutral'} />
                      </div>
                      <div className="action-metrics">
                        <span>{action.current_weight_pct.toFixed(1)}%</span>
                        <span>{action.target_weight_pct.toFixed(1)}%</span>
                        <span>{action.change_pct > 0 ? '+' : ''}{action.change_pct.toFixed(1)}%</span>
                      </div>
                      <div className="muted">{action.reason}</div>
                    </div>
                  ))}
                </div>
              </section>

              {result.audit_result && <ControlMatrix controls={result.audit_result.controls.slice(0, 6)} />}
            </div>

            <div className="stack-lg">
              <section className="card stack-sm">
                <div className="section-title">Current allocation</div>
                {formatAllocation(result.current_allocation).map(([label, value]) => (
                  <AllocationBar key={label} label={label} value={value} weightPct={value} valueLabel={`${value.toFixed(1)}%`} />
                ))}
              </section>

              <section className="card stack-sm">
                <div className="section-title">Proposed allocation</div>
                {formatAllocation(result.proposed_allocation).map(([label, value]) => (
                  <AllocationBar key={label} label={label} value={value} weightPct={value} valueLabel={`${value.toFixed(1)}%`} />
                ))}
              </section>

              <section className="card stack-sm">
                <div className="section-title">Transparency panel</div>
                <div className="stack-sm">
                  <div className="info-box">
                    <strong>Why suggested</strong>
                    <span>{result.transparency.why_suggested}</span>
                  </div>
                  <div className="info-box">
                    <strong>What changes</strong>
                    <span>{result.transparency.what_changes}</span>
                  </div>
                  <div className="info-box">
                    <strong>Trust note</strong>
                    <span>{result.transparency.guardrail_note}</span>
                  </div>
                </div>
              </section>

              <section className="card stack-sm">
                <div className="panel-head">
                  <div className="section-title">Compact trust check</div>
                  {result.audit_result && <StatusPill label={result.audit_result.overall_status} tone={statusTone(result.audit_result.overall_status)} />}
                </div>
                <div className="muted">{result.market_context.narrative}</div>
                {trustSummary && (
                  <div className="pill-row">
                    <StatusPill label={`${trustSummary.pass} pass`} tone="success" />
                    <StatusPill label={`${trustSummary.review} review`} tone="warning" />
                    <StatusPill label={`${trustSummary.fail} fail`} tone="error" />
                  </div>
                )}
              </section>
            </div>
          </section>
        </section>
      )}
    </PageShell>
  )
}
