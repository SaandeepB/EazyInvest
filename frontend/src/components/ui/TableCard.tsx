import type { ReactNode } from 'react'
import SectionHeader from './SectionHeader'

interface Props {
  title: string
  description?: string
  action?: ReactNode
  children: ReactNode
}

export default function TableCard({ title, description, action, children }: Props) {
  return (
    <section className="card stack-sm">
      <SectionHeader title={title} description={description} action={action} />
      {children}
    </section>
  )
}
