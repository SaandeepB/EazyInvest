import type { ReactNode } from 'react'

interface Props {
  eyebrow: string
  title: string
  description: string
  aside?: ReactNode
  actions?: ReactNode
  children: ReactNode
}

export default function PageShell({ eyebrow, title, description, aside, actions, children }: Props) {
  return (
    <div className="page-grid">
      <section className="page-hero">
        <div className="page-hero-copy">
          <div className="eyebrow">{eyebrow}</div>
          <h1 className="page-title">{title}</h1>
          <p className="page-description">{description}</p>
        </div>
        {(aside || actions) && (
          <div className="page-hero-aside">
            {aside && <div className="page-hero-note">{aside}</div>}
            {actions && <div className="page-hero-actions">{actions}</div>}
          </div>
        )}
      </section>
      {children}
    </div>
  )
}
