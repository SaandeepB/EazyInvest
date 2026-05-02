import type { AuditControlResult } from '../../types'
import StatusPill from '../ui/StatusPill'

interface Props {
  controls: AuditControlResult[]
}

function toneForStatus(status: AuditControlResult['status']) {
  if (status === 'Pass') return 'success'
  if (status === 'Review Needed') return 'warning'
  return 'error'
}

export default function ControlMatrix({ controls }: Props) {
  return (
    <section className="card stack-sm">
      <div className="section-title">Control Matrix</div>
      <div className="control-matrix">
        <div className="control-matrix-head">
          <span>Control</span>
          <span>Status</span>
          <span>Detail</span>
        </div>
        {controls.map(control => (
          <div key={control.code} className="control-row">
            <div>
              <strong>{control.code}</strong>
              <div className="muted">{control.title}</div>
            </div>
            <StatusPill label={control.status} tone={toneForStatus(control.status)} />
            <div className="muted">{control.detail}</div>
          </div>
        ))}
      </div>
    </section>
  )
}
