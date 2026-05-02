import { AlertTriangle, BadgeDollarSign, BarChart3, Layers3, ShieldCheck, Sparkles, Wallet } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import AllocationChart from '../components/charts/AllocationChart'
import PageShell from '../components/layout/PageShell'
import DataSourceBadge from '../components/ui/DataSourceBadge'
import HealthScoreCard from '../components/ui/HealthScoreCard'
import InfoCard from '../components/ui/InfoCard'
import MarketContextCard from '../components/ui/MarketContextCard'
import MetricCard from '../components/ui/MetricCard'
import RiskMeter from '../components/ui/RiskMeter'
import StatusPill from '../components/ui/StatusPill'
import TableCard from '../components/ui/TableCard'
import { api } from '../services/api'
import type { PortfolioSummaryResponse } from '../types'
import { EAZYINVEST_PROFILE_UPDATED_EVENT } from '../utils/profileState'

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
    const loadSummary = () => {
      setError('')
      api.getPortfolioSummary().then(setData).catch(err => setError(err.message))
    }

    loadSummary()
    window.addEventListener(EAZYINVEST_PROFILE_UPDATED_EVENT, loadSummary)
    return () => window.removeEventListener(EAZYINVEST_PROFILE_UPDATED_EVENT, loadSummary)
  }, [])

  const coverageLabel = useMemo(() => {
    if (!data) return 'Waiting for holdings'
    return data.portfolio.holdings_count > 0 ? `${data.portfolio.holdings_count} holdings mapped` : 'No holdings added yet'
  }, [data])

  if (error) return <div className="card error-banner">{error}</div>
  if (!data) return <div className="card">Loading dashboard...</div>

  const { portfolio, market_context, profiler } = data
  const gainTone = portfolio.total_gain_loss >= 0 ? 'success' : 'warning'
  const concentrationTone = portfolio.concentration_warning ? 'warning' : 'success'

  return (
    <PageShell
      eyebrow="Dashboard"
      title="A calm snapshot of your portfolio."
      description={`${profiler.explanation} ${portfolio.data_source_note}`}
      aside={<DataSourceBadge source={portfolio.price_source} />}
    >
      <section className="metric-grid">
        <MetricCard label="Total Portfolio Value" value={formatCurrency(portfolio.total_value)} detail="Latest available market proxy" tone="navy" icon={Wallet} />
        <MetricCard
          label="Gain / Loss"
          value={`${portfolio.total_gain_loss >= 0 ? '+' : '-'}${formatCurrency(Math.abs(portfolio.total_gain_loss))}`}
          detail={`${portfolio.total_gain_loss >= 0 ? '+' : ''}${portfolio.total_gain_loss_pct.toFixed(2)}% vs. cost basis`}
          tone={gainTone}
          icon={BadgeDollarSign}
        />
        <MetricCard label="Portfolio Health" value={portfolio.health.overall.toFixed(0)} detail={portfolio.health.label} tone="blue" icon={ShieldCheck} />
        <MetricCard label="Risk Level" value={portfolio.risk_level} detail={coverageLabel} tone="teal" icon={BarChart3} />
      </section>

      <section className="dashboard-hero-grid">
        <div className="dashboard-hero-main">
          <TableCard
            title="Allocation overview"
            description="Horizontal allocation bars keep the distribution easy to compare at a glance."
            action={<StatusPill label={`${portfolio.allocation_bars.length} buckets`} tone="navy" />}
          >
            <AllocationChart items={portfolio.allocation_bars} />
          </TableCard>
        </div>

        <div className="dashboard-hero-side">
          <HealthScoreCard health={portfolio.health} />
          <RiskMeter level={portfolio.risk_level} stockPct={portfolio.stock_allocation_pct} />
        </div>
      </section>

      <section className="dashboard-detail-grid">
        <div className="dashboard-detail-main">
          <TableCard
            title="Top holdings"
            description="Your largest positions by current market proxy value."
            action={<StatusPill label={portfolio.top_holding_symbol || 'No leader yet'} tone="blue" />}
          >
            {portfolio.top_holdings.length === 0 ? (
              <div className="empty-state">
                <strong>No holdings yet</strong>
                <div className="muted">Add your first position in My Holdings to activate the dashboard view.</div>
              </div>
            ) : (
              <div className="table-wrap">
                <table className="summary-table">
                  <thead>
                    <tr>
                      <th>Symbol</th>
                      <th>Name</th>
                      <th>Market Value</th>
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
                        <td className={holding.gain_loss >= 0 ? 'text-success' : 'text-warning'}>
                          {holding.gain_loss >= 0 ? '+' : '-'}{formatCurrency(Math.abs(holding.gain_loss))}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </TableCard>
        </div>

        <div className="dashboard-detail-side">
          <section className="card stack-md dashboard-source-card">
            <div className="section-header">
              <div className="section-header-copy">
                <div className="eyebrow">Source Note</div>
                <div className="section-title">Latest available market proxy</div>
                <div className="section-description">Valuations on this dashboard come from the syndicated CSV proxy dataset rather than live market feeds.</div>
              </div>
              <div className="icon-chip icon-chip-navy">
                <Layers3 size={18} />
              </div>
            </div>
          </section>
          <MarketContextCard context={market_context} />
        </div>
      </section>

      <section className="dashboard-insights-grid">
        <InfoCard
          title="Diversification"
          description={portfolio.health.diversification >= 70 ? 'Mix across buckets is in a healthy range.' : 'Current mix is narrow enough to deserve a second look.'}
          icon={Sparkles}
          tone={portfolio.health.diversification >= 70 ? 'success' : 'warning'}
        />
        <InfoCard
          title="Concentration"
          description={portfolio.top_holding_symbol ? `${portfolio.top_holding_symbol} is ${portfolio.top_holding_pct.toFixed(1)}% of total value.` : 'Add holdings to evaluate position concentration.'}
          icon={AlertTriangle}
          tone={concentrationTone}
        />
        <InfoCard
          title="Coverage"
          description={portfolio.holdings_count > 0 ? `${portfolio.holdings_count} user-added holdings are included in the centralized valuation summary.` : 'No user-added holdings are in the portfolio summary yet.'}
          icon={Layers3}
          tone="blue"
        />
      </section>
    </PageShell>
  )
}
