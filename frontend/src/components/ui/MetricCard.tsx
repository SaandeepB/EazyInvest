import type { ReactNode } from 'react'
import StatusPill from './StatusPill'

interface Props {
  label: string
  value: string
  detail?: string
  tone?: 'navy' | 'blue' | 'teal' | 'success' | 'warning' | 'error' | 'neutral'
  badge?: string
  children?: ReactNode
}

export default function MetricCard({ label, value, detail, tone = 'neutral', badge, children }: Props) {
  return (
    <div className={`metric-card metric-card-${tone}`}>
      <div className="metric-card-header">
        <span className="metric-label">{label}</span>
        {badge && <StatusPill label={badge} tone={tone} />}
      </div>
      <strong className="metric-value">{value}</strong>
      {detail && <span className="metric-detail">{detail}</span>}
      {children}
    </div>
  )
}
