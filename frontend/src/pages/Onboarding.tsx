import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../services/api'
import type { OnboardingAnswers } from '../types'

const DEFAULT_FORM: OnboardingAnswers = {
  goal: 'Retirement savings',
  time_horizon: '10+ years',
  starting_amount: 0,
  monthly_contribution: 0,
  contribution_stability: 'Stable',
  loss_comfort: 'Cautious',
  behavioral_risk: 'Hold',
  near_term_withdrawal: false,
  withdrawal_pct: 20,
  has_emergency_fund: 'Yes',
  account_type: 'Taxable',
  has_external_holdings: 'No',
  ux_mode: 'Simple',
}

export default function Onboarding({ onComplete }: { onComplete: () => void }) {
  const [form, setForm] = useState<OnboardingAnswers>(DEFAULT_FORM)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const update = <K extends keyof OnboardingAnswers>(key: K, value: OnboardingAnswers[K]) => {
    setForm(current => ({ ...current, [key]: value }))
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setSaving(true)
    setError('')
    try {
      await api.completeOnboarding(form)
      onComplete()
      navigate('/dashboard')
    } catch (err: any) {
      setError(err.message || 'Could not save onboarding answers.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="centered-page">
      <form className="card onboarding-card" onSubmit={handleSubmit}>
        <div className="eyebrow">Profiler Agent Intake</div>
        <h1 className="page-title">Set up EazyInvest</h1>
        <p className="muted">This onboarding stays lightweight but still feeds the profiler, scenario routing, and audit trail.</p>

        <div className="form-grid">
          <label className="field">
            <span>Goal</span>
            <select value={form.goal} onChange={e => update('goal', e.target.value)}>
              <option>Retirement savings</option>
              <option>Emergency fund growth</option>
              <option>Wealth growth</option>
              <option>Education savings</option>
              <option>Home purchase</option>
            </select>
          </label>
          <label className="field">
            <span>Time horizon</span>
            <select value={form.time_horizon} onChange={e => update('time_horizon', e.target.value)}>
              <option>1-3 years</option>
              <option>3-5 years</option>
              <option>5-10 years</option>
              <option>10+ years</option>
            </select>
          </label>
          <label className="field">
            <span>Starting amount</span>
            <input type="number" min="0" value={form.starting_amount} onChange={e => update('starting_amount', Number(e.target.value))} />
          </label>
          <label className="field">
            <span>Monthly contribution</span>
            <input type="number" min="0" value={form.monthly_contribution} onChange={e => update('monthly_contribution', Number(e.target.value))} />
          </label>
          <label className="field">
            <span>Contribution stability</span>
            <select value={form.contribution_stability} onChange={e => update('contribution_stability', e.target.value)}>
              <option>Stable</option>
              <option>Variable</option>
              <option>Unsure</option>
            </select>
          </label>
          <label className="field">
            <span>Loss comfort</span>
            <select value={form.loss_comfort} onChange={e => update('loss_comfort', e.target.value)}>
              <option>Stressed</option>
              <option>Cautious</option>
              <option>Fine with it</option>
            </select>
          </label>
          <label className="field">
            <span>Crash behavior</span>
            <select value={form.behavioral_risk} onChange={e => update('behavioral_risk', e.target.value)}>
              <option>Sell all</option>
              <option>Sell some</option>
              <option>Hold</option>
              <option>Buy more</option>
            </select>
          </label>
          <label className="field">
            <span>Account type</span>
            <select value={form.account_type} onChange={e => update('account_type', e.target.value)}>
              <option>Taxable</option>
              <option>IRA</option>
              <option>Roth IRA</option>
              <option>401(k)</option>
              <option>Mixed</option>
            </select>
          </label>
        </div>

        <div className="inline-toggle">
          <label><input type="checkbox" checked={form.near_term_withdrawal} onChange={e => update('near_term_withdrawal', e.target.checked)} /> I may need part of this money in the next 1-3 years</label>
          {form.near_term_withdrawal && (
            <label className="field compact-field">
              <span>Withdrawal %</span>
              <input type="number" min="1" max="100" value={form.withdrawal_pct} onChange={e => update('withdrawal_pct', Number(e.target.value))} />
            </label>
          )}
        </div>

        <div className="form-grid">
          <label className="field">
            <span>Emergency fund</span>
            <select value={form.has_emergency_fund} onChange={e => update('has_emergency_fund', e.target.value)}>
              <option>Yes</option>
              <option>Building</option>
              <option>No</option>
            </select>
          </label>
          <label className="field">
            <span>Outside holdings</span>
            <select value={form.has_external_holdings} onChange={e => update('has_external_holdings', e.target.value)}>
              <option>No</option>
              <option>Yes</option>
            </select>
          </label>
          <label className="field">
            <span>Interface style</span>
            <select value={form.ux_mode} onChange={e => update('ux_mode', e.target.value)}>
              <option>Simple</option>
              <option>Control</option>
            </select>
          </label>
        </div>

        {error && <div className="error-banner">{error}</div>}
        <button className="btn btn-primary" type="submit" disabled={saving}>
          {saving ? 'Saving...' : 'Enter EazyInvest'}
        </button>
      </form>
    </div>
  )
}
