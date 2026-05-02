import type { ReactNode } from 'react'

interface Props {
  eyebrow?: string
  title: string
  description?: string
  action?: ReactNode
}

export default function SectionHeader({ eyebrow, title, description, action }: Props) {
  return (
    <div className="section-header">
      <div className="section-header-copy">
        {eyebrow && <div className="eyebrow">{eyebrow}</div>}
        <div className="section-title">{title}</div>
        {description && <div className="muted section-description">{description}</div>}
      </div>
      {action && <div className="section-header-action">{action}</div>}
    </div>
  )
}
