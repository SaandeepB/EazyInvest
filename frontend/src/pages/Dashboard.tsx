import { useEffect, useState } from 'react'
import AllocationChart from '../components/charts/AllocationChart'
import PageShell from '../components/layout/PageShell'
import MetricCard from '../components/ui/MetricCard'
import DataSourceBadge from '../components/ui/DataSourceBadge'
import HealthScoreCard from '../components/ui/HealthScoreCard'
import MarketContextCard from '../components/ui/MarketContextCard'
import RiskMeter from '../components/ui/RiskMeter'
import StatusPill from '../components/ui/StatusPill'
import { api } from '../services/api'
import type { PortfolioSummaryResponse } from '../types'

function formatCurrency(value: number): string {
  return `$${value.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`
}

export default function Dashboard() {
  const [data, setData] = useState<PortfolioSummaryResponse | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.getPortfolioSummary().then(setData).catch(err => setError(err.message))
  }, [])

  if (error) return <div className="card error-banner">{error}</div>
  if (!data) return <div className="card">Loading dashboard...</div>

  const { portfolio, market_context, profiler } = data

  return (
    <PageShell
      eyebrow="Dashboard"
      title="EazyInvest overview"
      description={`${profiler.explanation} ${portfolio.data_source_note}`}
      aside={<DataSourceBadge source={portfolio.price_source} />}
    >
      <section className="metric-grid">
        <MetricCard label="Total Portfolio Value" value={formatCurrency(portfolio.total_value)} tone="navy" />
        <MetricCard
          label="Gain / Loss"
          value={`${portfolio.total_gain_loss >= 0 ? '+' : '-'}${formatCurrency(Math.abs(portfolio.total_gain_loss))}`}
          detail={`${portfolio.total_gain_loss >= 0 ? '+' : ''}${portfolio.total_gain_loss_pct.toFixed(2)}%`}
          tone={portfolio.total_gain_loss >= 0 ? 'success' : 'warning'}
        />
        <MetricCard label="Health Score" value={portfolio.health.overall.toFixed(0)} detail={portfolio.health.label} tone="blue" />
        <MetricCard label="Risk Level" value={portfolio.risk_level} detail={`${portfolio.holdings_count} holdings`} tone="teal" />
      </section>

      <section className="content-grid">
        <div className="stack-lg">
          <div className="card stack-sm">
            <div className="panel-head">
              <div className="section-title">Allocation by portfolio bucket</div>
              <StatusPill label={`${portfolio.allocation_bars.length} buckets`} tone="navy" />
            </div>
            <AllocationChart items={portfolio.allocation_bars} />
          </div>

          <div className="card stack-sm">
            <div className="panel-head">
              <div className="section-title">Top Holdings</div>
              <StatusPill label={portfolio.top_holding_symbol || 'None'} tone="blue" />
            </div>
            {portfolio.top_holdings.length === 0 ? (
              <div className="empty-panel">My Holdings is empty. Add your first position to activate the dashboard math.</div>
            ) : (
              <table className="summary-table">
                <thead>
                  <tr>
                    <th>Symbol</th>
                    <th>Name</th>
                    <th>Value</th>
                    <th>Weight</th>
                    <th>Gain / Loss</th>
                  </tr>
                </thead>
                <tbody>
                  {portfolio.top_holdings.map(holding => (
                    <tr key={holding.symbol}>
                      <td><strong>{holding.symbol}</strong></td>
                      <td>{holding.name}</td>
                      <td>{formatCurrency(holding.current_value)}</td>
                      <td>{holding.weight_pct.toFixed(1)}%</td>
                      <td>{holding.gain_loss >= 0 ? '+' : '-'}{formatCurrency(Math.abs(holding.gain_loss))}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        <div className="stack-lg">
          <HealthScoreCard health={portfolio.health} />
          <RiskMeter level={portfolio.risk_level} stockPct={portfolio.stock_allocation_pct} />

          <div className="card stack-sm">
            <div className="panel-head">
              <div>
                <div className="eyebrow">Concentration Warning</div>
                <div className="section-title">{portfolio.concentration_warning ? 'Review suggested' : 'Within range'}</div>
              </div>
              <StatusPill label={portfolio.concentration_warning ? 'Watch' : 'Stable'} tone={portfolio.concentration_warning ? 'warning' : 'success'} />
            </div>
            <div className="muted">
              {portfolio.top_holding_symbol
                ? `${portfolio.top_holding_symbol} is ${portfolio.top_holding_pct.toFixed(1)}% of portfolio value.`
                : 'Add holdings to evaluate concentration.'}
            </div>
          </div>

          <MarketContextCard context={market_context} />

          <div className="card stack-sm">
            <div className="panel-head">
              <div>
                <div className="eyebrow">Profiler Agent</div>
                <div className="section-title">{profiler.target_profile_name}</div>
              </div>
              <StatusPill label={profiler.risk_profile} tone="blue" />
            </div>
            <div className="muted">Target stock weight: {profiler.target_stock_pct.toFixed(0)}%</div>
            <div className="pill-row">
              {profiler.tags.map(tag => <StatusPill key={tag} label={tag.split('_').join(' ')} tone="neutral" />)}
            </div>
          </div>
        </div>
      </section>
    </PageShell>
  )
}
