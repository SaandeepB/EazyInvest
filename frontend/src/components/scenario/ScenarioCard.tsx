import { ArrowRight } from 'lucide-react'
import StatusPill from '../ui/StatusPill'

interface Props {
  title: string
  description: string
  tag?: string
  selected?: boolean
  disabled?: boolean
  onClick: () => void
}

export default function ScenarioCard({ title, description, tag, selected = false, disabled = false, onClick }: Props) {
  return (
    <button
      className={`scenario-card ${selected ? 'scenario-card-selected' : ''}`}
      onClick={onClick}
      disabled={disabled}
    >
      <div className="scenario-card-head">
        <strong>{title}</strong>
        <ArrowRight size={16} />
      </div>
      <div className="muted">{description}</div>
      {tag && <StatusPill label={tag} tone={selected ? 'teal' : 'blue'} />}
    </button>
  )
}
