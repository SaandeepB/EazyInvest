import { useEffect, useState } from 'react'
import type { AuditPayload, AuditResult } from '../types'

export interface AuditEntry {
  feature: string
  audit: AuditPayload
  receivedAt: string
}

let entries: AuditEntry[] = []
let reviewEntries: AuditReviewEntry[] = []
const listeners = new Set<() => void>()

export interface AuditReviewEntry {
  feature: string
  auditResult: AuditResult
  receivedAt: string
}

export function recordAudit(feature: string, audit: AuditPayload) {
  entries = [{ feature, audit, receivedAt: new Date().toISOString() }, ...entries].slice(0, 50)
  listeners.forEach(listener => listener())
}

export function clearAudits() {
  entries = []
  reviewEntries = []
  listeners.forEach(listener => listener())
}

export function recordAuditReview(feature: string, auditResult: AuditResult) {
  reviewEntries = [{ feature, auditResult, receivedAt: new Date().toISOString() }, ...reviewEntries].slice(0, 25)
  listeners.forEach(listener => listener())
}

export function useAuditEntries() {
  const [state, setState] = useState(entries)
  useEffect(() => {
    const listener = () => setState([...entries])
    listeners.add(listener)
    return () => {
      listeners.delete(listener)
    }
  }, [])
  return state
}

export function useAuditReviews() {
  const [state, setState] = useState(reviewEntries)
  useEffect(() => {
    const listener = () => setState([...reviewEntries])
    listeners.add(listener)
    return () => {
      listeners.delete(listener)
    }
  }, [])
  return state
}
