import type { AllocationBarItem } from '../../types'
import AllocationBar from '../ui/AllocationBar'

interface Props {
  items: AllocationBarItem[]
}

export default function AllocationChart({ items }: Props) {
  if (items.length === 0) {
    return <div className="empty-panel">Add holdings to see your allocation bars.</div>
  }

  return (
    <div className="chart-shell">
      <div className="allocation-bars">
        {items.map(item => <AllocationBar key={item.label} label={item.label} value={item.value} weightPct={item.weight_pct} />)}
      </div>
    </div>
  )
}
