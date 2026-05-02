interface Props {
  label: string
  value: number
  weightPct: number
  valueLabel?: string
}

export default function AllocationBar({ label, value, weightPct, valueLabel }: Props) {
  return (
    <div className="allocation-bar-row">
      <div className="allocation-bar-label">
        <strong>{label}</strong>
        <span className="muted">{weightPct.toFixed(1)}%</span>
      </div>
      <div className="allocation-bar-track">
        <div className="allocation-bar-fill" style={{ width: `${Math.min(Math.max(weightPct, 0), 100)}%` }} />
      </div>
      <div className="allocation-bar-value">{valueLabel ?? `$${value.toLocaleString(undefined, { maximumFractionDigits: 0 })}`}</div>
    </div>
  )
}
