import ProgressBar from './ProgressBar'
import StatusPill from './StatusPill'

interface Props {
  level: string
  stockPct: number
}

export default function RiskMeter({ level, stockPct }: Props) {
  const tone = level === 'High' ? 'warning' : level === 'Medium' ? 'blue' : 'success'
  return (
    <div className="card stack-sm">
      <div className="panel-head">
        <div>
          <div className="eyebrow">Risk Level</div>
          <div className="section-title">{level}</div>
        </div>
        <StatusPill label={level} tone={tone} />
      </div>
      <ProgressBar label="Individual stock exposure" value={stockPct} tone={tone} suffix="%" />
      <div className="muted">{stockPct.toFixed(1)}% of portfolio value is in individual stocks.</div>
    </div>
  )
}
