import StatusPill from './StatusPill'

interface Props {
  source: string
}

function formatSource(source: string): string {
  if (source === 'syndicated_csv') return 'Latest market proxy'
  if (source === 'csv_proxy') return 'CSV proxy data'
  return source.split('_').join(' ')
}

export default function DataSourceBadge({ source }: Props) {
  return <StatusPill label={formatSource(source)} tone="teal" />
}
