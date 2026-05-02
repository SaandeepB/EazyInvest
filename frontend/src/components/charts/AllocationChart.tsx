import type { AllocationBarItem } from '../../types'
import EmptyState from '../ui/EmptyState'
import AllocationBar from '../ui/AllocationBar'

interface Props {
  items: AllocationBarItem[]
}

export default function AllocationChart({ items }: Props) {
  if (items.length === 0) {
    return <EmptyState title="No allocation yet" description="Add holdings to see how value is distributed across your portfolio buckets." />
  }

  return (
    <div className="chart-shell">
      <div className="allocation-bars">
        {items.map(item => (
          <AllocationBar
            key={item.label}
            label={item.label}
            value={item.value}
            weightPct={item.weight_pct}
            valueLabel={`${item.weight_pct.toFixed(1)}%`}
          />
        ))}
      </div>
    </div>
  )
}
