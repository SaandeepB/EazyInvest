interface Props {
  label: string
  tone?: 'navy' | 'blue' | 'teal' | 'success' | 'warning' | 'error' | 'neutral'
}

export default function StatusPill({ label, tone = 'neutral' }: Props) {
  return <span className={`status-pill status-pill-${tone}`}>{label}</span>
}
