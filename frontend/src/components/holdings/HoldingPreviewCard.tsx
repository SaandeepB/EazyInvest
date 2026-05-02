import { Landmark, Search } from 'lucide-react'
import type { LookupResult } from '../../types'
import InfoCard from '../ui/InfoCard'
import StatusPill from '../ui/StatusPill'

interface Props {
  symbol: string
  selectedLookup?: LookupResult
  showUnknownPreview: boolean
}

function formatCurrency(value: number | null | undefined): string {
  if (value === null || value === undefined) return '--'
  return `$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

export default function HoldingPreviewCard({ symbol, selectedLookup, showUnknownPreview }: Props) {
  if (selectedLookup) {
    return (
      <div className="card stack-sm">
        <div className="section-title">Lookup preview</div>
        <InfoCard
          title={selectedLookup.name}
          description={`${selectedLookup.asset_type} - ${selectedLookup.sector_or_category}`}
          icon={Landmark}
          tone="teal"
        />
        <div className="pill-row">
          <StatusPill label={selectedLookup.symbol} tone="navy" />
          <StatusPill label={formatCurrency(selectedLookup.proxy_price)} tone="success" />
          <StatusPill label={selectedLookup.risk_bucket} tone="blue" />
        </div>
      </div>
    )
  }

  if (showUnknownPreview) {
    return (
      <div className="card stack-sm">
        <div className="section-title">Lookup preview</div>
        <InfoCard
          title={symbol || 'Unknown symbol'}
          description="Market proxy price unavailable. Estimated value will use your purchase price."
          icon={Search}
          tone="warning"
        />
      </div>
    )
  }

  return (
    <div className="card stack-sm">
      <div className="section-title">Lookup preview</div>
      <div className="empty-state">
        <strong>Search a symbol</strong>
        <div className="muted">Preview name, type, sector, and proxy price before you add the holding.</div>
      </div>
    </div>
  )
}
