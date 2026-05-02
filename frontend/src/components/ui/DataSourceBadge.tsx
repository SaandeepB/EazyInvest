import StatusPill from './StatusPill'

interface Props {
  source: string
}

export default function DataSourceBadge({ source }: Props) {
  return <StatusPill label={source.split('_').join(' ').toUpperCase()} tone="teal" />
}
