import { Gauge } from 'lucide-react'
import ProgressBar from './ProgressBar'
import StatusPill from './StatusPill'

interface Props {
  level: string
  stockPct: number
}

export default function RiskMeter({ level, stockPct }: Props) {
  const tone = level === 'High' ? 'warning' : level === 'Medium' ? 'blue' : 'success'

  return (
    <section className="card stack-md">
      <div className="panel-head">
        <div>
          <div className="eyebrow">Risk Level</div>
          <div className="section-title">Exposure profile</div>
        </div>
        <div className="panel-head-inline">
          <div className={`icon-chip icon-chip-${tone}`}>
            <Gauge size={18} />
          </div>
          <StatusPill label={level} tone={tone} />
        </div>
      </div>

      <div className="risk-meter-readout">
        <strong>{level}</strong>
        <span className="muted">{stockPct.toFixed(1)}% of value sits in individual stocks.</span>
      </div>

      <ProgressBar label="Individual stock exposure" value={stockPct} tone={tone} suffix="%" />
    </section>
  )
}
