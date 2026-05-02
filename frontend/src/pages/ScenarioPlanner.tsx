import { ArrowRightLeft, BadgeDollarSign, Goal, Lightbulb, ShieldAlert } from 'lucide-react'
import { useEffect, useState } from 'react'
import ScenarioCard from '../components/scenario/ScenarioCard'
import PageShell from '../components/layout/PageShell'
import AllocationBar from '../components/ui/AllocationBar'
import EmptyState from '../components/ui/EmptyState'
import InfoCard from '../components/ui/InfoCard'
import InputCard from '../components/ui/InputCard'
import MetricCard from '../components/ui/MetricCard'
import StatusPill from '../components/ui/StatusPill'
import TableCard from '../components/ui/TableCard'
import { api } from '../services/api'
import type { ScenarioCatalogItem, ScenarioPayload } from '../types'

function formatAllocation(allocation: Record<string, number>) {
  return Object.entries(allocation).filter(([, value]) => value > 0)
}

export default function ScenarioPlanner() {
  const [scenarios, setScenarios] = useState<ScenarioCatalogItem[]>([])
  const [result, setResult] = useState<ScenarioPayload | null>(null)
  const [loadingType, setLoadingType] = useState<string | null>(null)
  const [customScenarioText, setCustomScenarioText] = useState('')
  const [selectedScenario, setSelectedScenario] = useState<string | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.listScenarios().then(response => setScenarios(response.scenarios)).catch(() => setScenarios([]))
  }, [])

  const actionTone: 'navy' | 'success' | 'warning' =
    !result
      ? 'navy'
      : result.projected_health.overall > result.current_health.overall
        ? 'success'
        : result.projected_health.overall < result.current_health.overall
          ? 'warning'
          : 'navy'

  const runScenario = async (payload: { scenario_type?: string; custom_scenario_text?: string }) => {
    setLoadingType(payload.scenario_type ?? 'custom')
    setSelectedScenario(payload.scenario_type ?? 'custom')
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
      title="Explore what-if paths before you make a move."
      description="Suggested scenario cards and custom input both route into the same deterministic portfolio math, with plain-English reasoning layered on top."
      aside={<StatusPill label={result ? result.scenario_label : 'Ready to analyze'} tone="navy" />}
    >
      <section className="scenario-top-grid">
        <TableCard
          title="Suggested scenarios"
          description="Start with a guided stress test, then compare the recommendation structure with your current allocation."
          action={<StatusPill label={`${scenarios.length} cards`} tone="blue" />}
        >
          <div className="scenario-grid">
            {scenarios.map(scenario => (
              <ScenarioCard
                key={scenario.type}
                title={scenario.label}
                description={scenario.description}
                tag={loadingType === scenario.type ? 'Running' : 'Suggested'}
                selected={selectedScenario === scenario.type}
                disabled={loadingType !== null}
                onClick={() => runScenario({ scenario_type: scenario.type })}
              />
            ))}
          </div>
        </TableCard>

        <InputCard
          title="Describe your own concern"
          description="Custom input is classified by the profiler and scenario agents, then mapped into deterministic allocation logic."
        >
          <div className="stack-md">
            <textarea
              className="scenario-textarea"
              value={customScenarioText}
              onChange={event => setCustomScenarioText(event.target.value)}
              placeholder="I might need 20% of my money next year and I am worried the market may drop."
              rows={5}
            />
            <div className="button-row">
              <button
                className="btn btn-primary"
                onClick={() => runScenario({ custom_scenario_text: customScenarioText })}
                disabled={!customScenarioText.trim() || loadingType !== null}
              >
                {loadingType === 'custom' ? 'Analyzing...' : 'Analyze custom scenario'}
              </button>
            </div>
            {error && <div className="error-banner">{error}</div>}
          </div>
        </InputCard>
      </section>

      {result ? (
        <section className="stack-lg">
          <section className="scenario-summary-hero">
            <div className="scenario-summary-copy">
              <div className="eyebrow">Scenario Summary</div>
              <h2>{result.scenario_label}</h2>
              <p>{result.summary}</p>
            </div>
            <div className="scenario-summary-stats">
              <MetricCard label="Current Health" value={result.current_health.overall.toFixed(0)} tone="navy" icon={ShieldAlert} />
              <MetricCard label="Projected Health" value={result.projected_health.overall.toFixed(0)} tone={actionTone} icon={ArrowRightLeft} />
              <MetricCard label="Recommended actions" value={String(result.actions.length)} tone="blue" icon={Lightbulb} />
              {result.profiler_output && (
                <MetricCard label="Profiler confidence" value={`${Math.round(result.profiler_output.confidence * 100)}%`} tone="teal" icon={Goal} />
              )}
            </div>
          </section>

          <section className="scenario-results-layout">
            <div className="stack-lg">
              {result.profiler_output && (
                <section className="card stack-md">
                  <div className="section-header">
                    <div className="section-header-copy">
                      <div className="eyebrow">Profiler Summary</div>
                      <div className="section-title">{result.profiler_output.investor_segment}</div>
                      <div className="section-description">{result.profiler_output.reasoning}</div>
                    </div>
                    <StatusPill label={result.profiler_output.risk_profile} tone="blue" />
                  </div>

                  <div className="summary-grid">
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
                    <div className="summary-item">
                      <span className="muted">Target profile</span>
                      <strong>{result.profiler_output.target_profile_name}</strong>
                    </div>
                  </div>
                </section>
              )}

              <TableCard
                title="Rebalancing output"
                description="Ordered actions based on current allocation versus the selected target profile."
                action={<StatusPill label={`${result.actions.length} actions`} tone="navy" />}
              >
                {result.actions.length === 0 ? (
                  <EmptyState title="No action needed" description="The current mix is already close to the recommended profile for this scenario." />
                ) : (
                  <div className="stack-sm">
                    {result.actions.map(action => (
                      <div key={`${action.symbol}-${action.action}`} className="rebalance-card">
                        <div className="rebalance-card-main">
                          <div>
                            <strong>{action.symbol}</strong>
                            <div className="muted">{action.name}</div>
                          </div>
                          <StatusPill
                            label={action.action}
                            tone={action.action === 'trim' ? 'warning' : action.action === 'add' ? 'success' : 'neutral'}
                          />
                        </div>
                        <div className="rebalance-stats">
                          <span>Current {action.current_weight_pct.toFixed(1)}%</span>
                          <span>Target {action.target_weight_pct.toFixed(1)}%</span>
                          <span>{action.change_pct > 0 ? '+' : ''}{action.change_pct.toFixed(1)}%</span>
                        </div>
                        <div className="muted">{action.reason}</div>
                      </div>
                    ))}
                  </div>
                )}
              </TableCard>
            </div>

            <div className="stack-lg">
              <div className="scenario-allocation-grid">
                <section className="card stack-md">
                  <div className="section-title">Current allocation</div>
                  {formatAllocation(result.current_allocation).length === 0 ? (
                    <EmptyState title="No current allocation" description="Add holdings first to see the starting point for a scenario." />
                  ) : (
                    formatAllocation(result.current_allocation).map(([label, value]) => (
                      <AllocationBar key={label} label={label} value={value} weightPct={value} valueLabel={`${value.toFixed(1)}%`} />
                    ))
                  )}
                </section>

                <section className="card stack-md">
                  <div className="section-title">Recommended allocation</div>
                  {formatAllocation(result.proposed_allocation).map(([label, value]) => (
                    <AllocationBar key={label} label={label} value={value} weightPct={value} valueLabel={`${value.toFixed(1)}%`} />
                  ))}
                </section>
              </div>

              <section className="card stack-md">
                <div className="section-header">
                  <div className="section-header-copy">
                    <div className="eyebrow">Transparency</div>
                    <div className="section-title">Why this recommendation</div>
                    <div className="section-description">Structured explanations without changing the underlying deterministic math.</div>
                  </div>
                  <div className="icon-chip icon-chip-teal">
                    <BadgeDollarSign size={18} />
                  </div>
                </div>

                <div className="info-card-grid">
                  <InfoCard title="Why this recommendation" description={result.transparency.why_suggested} tone="teal" />
                  <InfoCard title="Estimated cost note" description={result.estimated_cost_note} tone="warning" />
                  <InfoCard title="Tax caution" description={result.estimated_tax_note || result.transparency.selling_impact} tone="warning" />
                  <InfoCard title="Goal alignment" description={result.transparency.goal_alignment} tone="success" />
                  <InfoCard title="Upside" description={result.transparency.upside} tone="blue" />
                  <InfoCard title="Downside tradeoff" description={result.transparency.downside} tone="navy" />
                </div>
              </section>

              <section className="card stack-md">
                <div className="section-title">Market context</div>
                <div className="muted">{result.market_context.narrative}</div>
              </section>
            </div>
          </section>
        </section>
      ) : (
        <section className="card">
          <EmptyState title="Pick a scenario to begin" description="Suggested cards and custom input both feed the same centralized scenario engine. Results will appear here once you run an analysis." />
        </section>
      )}
    </PageShell>
  )
}
