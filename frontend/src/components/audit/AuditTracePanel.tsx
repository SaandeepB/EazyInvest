import type { AuditPayload } from '../../types'
import StatusPill from '../ui/StatusPill'

interface Props {
  audit: AuditPayload
  title?: string
}

export default function AuditTracePanel({ audit, title }: Props) {
  return (
    <div className="card stack-sm">
      <div className="panel-head">
        <div>
          <div className="section-title">{title ?? audit.feature}</div>
          <div className="muted">Request {audit.request_id.slice(0, 8)} | {audit.timestamp}</div>
        </div>
        <StatusPill label={`${audit.checks.length} checks`} tone="navy" />
      </div>

      <div className="pill-row">
        {audit.data_sources.map(source => (
          <StatusPill key={source} label={source} tone="teal" />
        ))}
      </div>

      <div className="subsection-title">Checks</div>
      <div className="list-panel">
        {audit.checks.map(check => (
          <div key={`${check.name}-${check.detail}`} className="list-row">
            <span>{check.name}</span>
            <StatusPill
              label={check.status}
              tone={check.status === 'passed' ? 'success' : check.status === 'warning' ? 'warning' : 'error'}
            />
          </div>
        ))}
      </div>

      <div className="subsection-title">Events</div>
      <div className="timeline">
        {audit.events.map((event, index) => (
          <div key={`${event.agent}-${index}`} className="timeline-item">
            <strong>{event.agent}</strong>
            <span>{event.action}</span>
            <p>{event.detail}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
