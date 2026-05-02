interface EvidenceRow {
  label: string
  value: string
}

interface Props {
  title: string
  rows: EvidenceRow[]
}

export default function EvidencePanel({ title, rows }: Props) {
  return (
    <section className="card stack-sm">
      <div className="section-title">{title}</div>
      <div className="evidence-panel">
        {rows.map(row => (
          <div key={row.label} className="evidence-row">
            <span className="evidence-label">{row.label}</span>
            <span className="evidence-value">{row.value}</span>
          </div>
        ))}
      </div>
    </section>
  )
}
