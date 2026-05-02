import type { MarketContextSummary } from '../../types'

interface Props {
  context: MarketContextSummary
}

export default function MarketContextCard({ context }: Props) {
  return (
    <div className="card stack-sm">
      <div className="eyebrow">Market Context Agent</div>
      <div className="section-title">CSV proxy market context</div>
      <div className="muted">{context.narrative}</div>
      <div className="pill-row">
        <span className="badge">{context.supported_symbol_count} supported symbols</span>
        <span className="badge">{context.diversified_weight_pct.toFixed(1)}% diversified</span>
      </div>
      <div className="list-panel">
        {context.top_sectors.map(sector => (
          <div key={sector} className="list-row">
            <span>{sector}</span>
            <span>{context.source}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
