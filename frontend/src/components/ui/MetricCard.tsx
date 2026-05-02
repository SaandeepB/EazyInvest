import type { LucideIcon } from 'lucide-react'
import StatusPill from './StatusPill'

interface Props {
  label: string
  value: string
  detail?: string
  icon?: LucideIcon
  tone?: 'navy' | 'blue' | 'teal' | 'success' | 'warning' | 'error' | 'neutral'
  badge?: string
}

export default function MetricCard({
  label,
  value,
  detail,
  icon: Icon,
  tone = 'neutral',
  badge,
}: Props) {
  return (
    <div className={`metric-card metric-card-${tone}`}>
      <div className="metric-card-head">
        <div className="metric-card-label">
          {Icon && (
            <span className={`metric-card-icon metric-card-icon-${tone}`}>
              <Icon size={18} />
            </span>
          )}
          <span>{label}</span>
        </div>
        {badge && <StatusPill label={badge} tone={tone} />}
      </div>
      <div className="metric-card-value">{value}</div>
      {detail && <div className="metric-card-detail">{detail}</div>}
    </div>
  )
}
