import type { ReactNode } from 'react'
import SectionHeader from './SectionHeader'

interface Props {
  title: string
  description?: string
  children: ReactNode
}

export default function InputCard({ title, description, children }: Props) {
  return (
    <section className="card stack-sm">
      <SectionHeader title={title} description={description} />
      {children}
    </section>
  )
}
