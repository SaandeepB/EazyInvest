import { ShieldCheck } from 'lucide-react'
import type { HealthScores } from '../../types'
import ProgressBar from './ProgressBar'
import StatusPill from './StatusPill'

interface Props {
  health: HealthScores
}

export default function HealthScoreCard({ health }: Props) {
  const tone = health.label === 'Good' ? 'success' : health.label === 'Fair' ? 'warning' : 'error'

  return (
    <section className="card stack-md">
      <div className="panel-head">
        <div>
          <div className="eyebrow">Portfolio Health</div>
          <div className="section-title">Diversification and fit</div>
        </div>
        <div className="panel-head-inline">
          <div className={`icon-chip icon-chip-${tone}`}>
            <ShieldCheck size={18} />
          </div>
          <StatusPill label={health.label} tone={tone} />
        </div>
      </div>

      <div className="score-block">
        <div className="score-value">{health.overall.toFixed(0)}</div>
        <div className="muted">A blended score across diversification, concentration, risk fit, and liquidity readiness.</div>
      </div>

      <div className="stack-sm">
        <ProgressBar label="Diversification" value={health.diversification} tone="teal" />
        <ProgressBar label="Concentration" value={health.concentration} tone="navy" />
        <ProgressBar label="Risk Alignment" value={health.risk_alignment} tone="blue" />
        <ProgressBar label="Liquidity" value={health.liquidity_readiness} tone="success" />
      </div>
    </section>
  )
}
