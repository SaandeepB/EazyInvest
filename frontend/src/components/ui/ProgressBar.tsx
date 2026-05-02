interface Props {
  label: string
  value: number
  max?: number
  tone?: 'navy' | 'blue' | 'teal' | 'success' | 'warning' | 'error'
  suffix?: string
}

export default function ProgressBar({ label, value, max = 100, tone = 'blue', suffix = '' }: Props) {
  const pct = Math.min(Math.max((value / max) * 100, 0), 100)
  return (
    <div className="progress-block">
      <div className="progress-head">
        <span>{label}</span>
        <strong>{value.toFixed(0)}{suffix}</strong>
      </div>
      <div className="progress-track">
        <div className={`progress-fill progress-fill-${tone}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}
