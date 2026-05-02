import type { HealthScores } from '../../types'
import ProgressBar from './ProgressBar'
import StatusPill from './StatusPill'

interface Props {
  health: HealthScores
}

export default function HealthScoreCard({ health }: Props) {
  const tone = health.label === 'Good' ? 'success' : health.label === 'Fair' ? 'warning' : 'error'
  return (
    <div className="card stack-sm">
      <div className="panel-head">
        <div>
          <div className="eyebrow">Portfolio Health</div>
          <div className="section-title">Health Score</div>
        </div>
        <StatusPill label={health.label} tone={tone} />
      </div>
      <div className="score-row">
        <div className="score-value">{health.overall.toFixed(0)}</div>
        <div>
          <div className="muted">Diversification, concentration, risk fit, and liquidity readiness.</div>
        </div>
      </div>
      <div className="stack-sm">
        <ProgressBar label="Diversification" value={health.diversification} tone="blue" />
        <ProgressBar label="Concentration" value={health.concentration} tone="teal" />
        <ProgressBar label="Risk Alignment" value={health.risk_alignment} tone="navy" />
        <ProgressBar label="Liquidity" value={health.liquidity_readiness} tone="success" />
      </div>
    </div>
  )
}
