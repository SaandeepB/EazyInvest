import { Globe2 } from 'lucide-react'
import type { MarketContextSummary } from '../../types'
import StatusPill from './StatusPill'

interface Props {
  context: MarketContextSummary
}

export default function MarketContextCard({ context }: Props) {
  return (
    <section className="card stack-md">
      <div className="panel-head">
        <div>
          <div className="eyebrow">Market Context</div>
          <div className="section-title">Proxy dataset backdrop</div>
        </div>
        <div className="icon-chip icon-chip-teal">
          <Globe2 size={18} />
        </div>
      </div>

      <p className="muted">{context.narrative}</p>

      <div className="pill-row">
        <StatusPill label={`${context.supported_symbol_count} supported symbols`} tone="navy" />
        <StatusPill label={`${context.diversified_weight_pct.toFixed(1)}% diversified`} tone="success" />
      </div>

      <div className="list-panel">
        {context.top_sectors.map(sector => (
          <div key={sector} className="list-row">
            <span>{sector}</span>
            <span className="list-value">{context.source}</span>
          </div>
        ))}
      </div>
    </section>
  )
}
