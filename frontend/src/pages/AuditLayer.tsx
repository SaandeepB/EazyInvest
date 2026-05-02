import { useEffect, useMemo, useState } from 'react'
import AuditTracePanel from '../components/audit/AuditTracePanel'
import ControlMatrix from '../components/audit/ControlMatrix'
import EvidencePanel from '../components/audit/EvidencePanel'
import PageShell from '../components/layout/PageShell'
import MetricCard from '../components/ui/MetricCard'
import StatusPill from '../components/ui/StatusPill'
import TableCard from '../components/ui/TableCard'
import { api } from '../services/api'
import { clearAudits, useAuditEntries, useAuditReviews } from '../state/auditStore'
import type { AuditDemoLogItem, AuditDemoResultItem, AuditResult } from '../types'

interface ReviewRow {
  key: string
  title: string
  source: string
  auditResult: AuditResult
  logCount: number
}

function toneForStatus(status: AuditResult['overall_status']): 'success' | 'warning' | 'error' {
  if (status === 'Pass') return 'success'
  if (status === 'Review Needed') return 'warning'
  return 'error'
}

function stringifyEvidence(value: unknown): string {
  if (Array.isArray(value)) return value.join(', ') || 'None'
  if (value && typeof value === 'object') return JSON.stringify(value)
  if (value === null || value === undefined || value === '') return 'Not provided'
  return String(value)
}

export default function AuditLayer() {
  const entries = useAuditEntries()
  const reviews = useAuditReviews()
  const [demoResults, setDemoResults] = useState<AuditDemoResultItem[]>([])
  const [demoLogs, setDemoLogs] = useState<AuditDemoLogItem[]>([])
  const [selectedKey, setSelectedKey] = useState('')

  useEffect(() => {
    api.getAuditDemoResults().then(response => setDemoResults(response.results)).catch(() => setDemoResults([]))
    api.getAuditDemoLogs().then(response => setDemoLogs(response.logs)).catch(() => setDemoLogs([]))
  }, [])

  const reviewRows = useMemo(() => {
    const demoLogMap = new Map(demoLogs.map(item => [item.case_name, item]))
    const sessionRows: ReviewRow[] = reviews.map((entry, index) => ({
      key: `session-${index}-${entry.receivedAt}`,
      title: entry.feature,
      source: 'Session review',
      auditResult: entry.auditResult,
      logCount: entry.auditResult.logs.length,
    }))
    const demoRows: ReviewRow[] = demoResults.map(item => ({
      key: `demo-${item.case_name}`,
      title: item.case_name.split('_').join(' '),
      source: 'Demo case',
      auditResult: item.audit_result,
      logCount: demoLogMap.get(item.case_name)?.logs.length ?? item.audit_result.logs.length,
    }))
    return [...sessionRows, ...demoRows]
  }, [demoLogs, demoResults, reviews])

  useEffect(() => {
    if (reviewRows.length > 0 && !reviewRows.some(item => item.key === selectedKey)) {
      setSelectedKey(reviewRows[0].key)
    }
  }, [reviewRows, selectedKey])

  const selectedReview = reviewRows.find(item => item.key === selectedKey) ?? null
  const exceptions = selectedReview?.auditResult.controls.filter(control => control.status !== 'Pass') ?? []
  const evidenceRows = selectedReview
    ? Object.entries(selectedReview.auditResult.evidence).slice(0, 10).map(([label, value]) => ({
        label: label.split('_').join(' '),
        value: stringifyEvidence(value),
      }))
    : []

  const kpis = {
    total: reviewRows.length,
    pass: reviewRows.filter(item => item.auditResult.overall_status === 'Pass').length,
    review: reviewRows.filter(item => item.auditResult.overall_status === 'Review Needed').length,
    fail: reviewRows.filter(item => item.auditResult.overall_status === 'Fail').length,
  }

  return (
    <PageShell
      eyebrow="Audit Layer"
      title="Operational review of recommendation outputs."
      description="This is the only page where audit controls, evidence packets, review statuses, and request traces are surfaced in the UI."
      actions={<button className="btn btn-secondary" onClick={() => clearAudits()}>Clear session traces</button>}
    >
      <section className="metric-grid">
        <MetricCard label="Reviews" value={String(kpis.total)} detail="Session plus demo cases" tone="navy" />
        <MetricCard label="Pass" value={String(kpis.pass)} detail="Controls satisfied" tone="success" />
        <MetricCard label="Review Needed" value={String(kpis.review)} detail="Requires analyst attention" tone="warning" />
        <MetricCard label="Fail" value={String(kpis.fail)} detail="High-priority exception" tone="error" />
      </section>

      {selectedReview ? (
        <ControlMatrix controls={selectedReview.auditResult.controls} />
      ) : (
        <section className="card">
          <div className="empty-state">
            <strong>No review packets yet</strong>
            <div className="muted">Run a scenario or use the demo endpoints to populate the review queue.</div>
          </div>
        </section>
      )}

      <section className="audit-board">
        <div className="audit-board-main">
          <TableCard title="Recent reviews" description="Session reviews appear alongside the seeded demo cases so you can inspect both live and sample packets.">
            {reviewRows.length === 0 ? (
              <div className="empty-state">
                <strong>No audit reviews yet</strong>
                <div className="muted">Scenario analyses with audit results will land here automatically.</div>
              </div>
            ) : (
              <div className="review-list">
                {reviewRows.map(item => (
                  <button
                    key={item.key}
                    className={`review-item ${selectedKey === item.key ? 'review-item-active' : ''}`}
                    onClick={() => setSelectedKey(item.key)}
                  >
                    <div>
                      <strong>{item.title}</strong>
                      <div className="muted">{item.source}</div>
                    </div>
                    <div className="review-item-meta">
                      <StatusPill label={item.auditResult.overall_status} tone={toneForStatus(item.auditResult.overall_status)} />
                      <span className="muted">{item.logCount} logs</span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </TableCard>

          {entries.length > 0 && (
            <section className="stack-sm">
              <div className="section-title">Recent request traces</div>
              {entries.slice(0, 2).map(entry => (
                <AuditTracePanel key={`${entry.feature}-${entry.receivedAt}`} audit={entry.audit} title={entry.feature} />
              ))}
            </section>
          )}
        </div>

        <div className="audit-board-side">
          {selectedReview && <EvidencePanel title="Evidence packet" rows={evidenceRows} />}

          <section className="card stack-md">
            <div className="section-title">Exceptions</div>
            {exceptions.length === 0 ? (
              <div className="empty-state">
                <strong>No exceptions</strong>
                <div className="muted">The selected review did not produce review-needed or fail controls.</div>
              </div>
            ) : (
              <div className="stack-sm">
                {exceptions.map(control => (
                  <div key={control.code} className="exception-card">
                    <div className="panel-head">
                      <div>
                        <strong>{control.code}</strong>
                        <div className="muted">{control.title}</div>
                      </div>
                      <StatusPill label={control.status} tone={toneForStatus(control.status)} />
                    </div>
                    <div className="muted">{control.detail}</div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>
      </section>
    </PageShell>
  )
}
