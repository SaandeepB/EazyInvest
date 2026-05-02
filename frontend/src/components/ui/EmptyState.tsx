interface Props {
  title: string
  description: string
}

export default function EmptyState({ title, description }: Props) {
  return (
    <div className="empty-state">
      <strong>{title}</strong>
      <div className="muted">{description}</div>
    </div>
  )
}
