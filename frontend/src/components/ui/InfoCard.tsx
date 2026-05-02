import type { LucideIcon } from 'lucide-react'

interface Props {
  title: string
  description: string
  icon?: LucideIcon
  tone?: 'navy' | 'blue' | 'teal' | 'success' | 'warning' | 'error' | 'neutral'
}

export default function InfoCard({ title, description, icon: Icon, tone = 'neutral' }: Props) {
  return (
    <div className={`info-card info-card-${tone}`}>
      {Icon && (
        <div className={`info-card-icon info-card-icon-${tone}`}>
          <Icon size={18} />
        </div>
      )}
      <div className="info-card-body">
        <strong>{title}</strong>
        <div className="muted">{description}</div>
      </div>
    </div>
  )
}
