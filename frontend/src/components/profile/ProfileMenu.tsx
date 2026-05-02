import { RotateCcw, SlidersHorizontal, UserRound, X } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { api } from '../../services/api'
import type { ProfilerSummary, User, UserUpdatePayload } from '../../types'
import {
  dispatchProfileUpdated,
  loadProfileMeta,
  saveProfileMeta,
} from '../../utils/profileState'

type ExperienceLevel = 'Beginner' | 'Intermediate' | 'Experienced'
type InvestingStyle = 'Passive' | 'Balanced' | 'Active'

interface ProfileEditorForm {
  experienceLevel: ExperienceLevel
  goalOption: string
  customGoal: string
  riskProfile: 'Conservative' | 'Balanced' | 'Growth'
  monthlyContribution: number
  timeHorizon: string
  plannedWithdrawalPct: number
  investingStyle: InvestingStyle
}

const GOAL_OPTIONS = [
  'Build long-term wealth',
  'Save for a major purchase',
  'Prepare for retirement',
  'Preserve capital',
  'Generate income',
  'Other',
]

const TIME_HORIZON_OPTIONS = ['1-3 years', '3-5 years', '5-10 years', '10+ years']

function formatCurrency(value: number | null | undefined) {
  if (value === null || value === undefined) return 'Not set'
  return `$${value.toLocaleString(undefined, { maximumFractionDigits: 0 })}`
}

function formatPercent(value: number | null | undefined) {
  if (value === null || value === undefined) return 'Not set'
  return `${value}%`
}

function formatConfidence(value: number | null | undefined) {
  if (value === null || value === undefined) return 'Not set'
  return `${Math.round(value * 100)}%`
}

function formatTitleCase(value: string | null | undefined) {
  if (!value) return 'Not set'

  if (value.includes('-')) {
    return value
      .split('-')
      .map(part => part.charAt(0).toUpperCase() + part.slice(1))
      .join('-')
  }

  return value
    .split('_')
    .join(' ')
    .split(' ')
    .filter(Boolean)
    .map(part => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
}

function deriveExperienceLevel(user: User, stored?: ExperienceLevel): ExperienceLevel {
  if (stored) return stored
  if (user.ux_mode === 'Control') return 'Experienced'
  if (user.has_external_holdings === 'Yes') return 'Intermediate'
  return 'Beginner'
}

function deriveInvestingStyle(user: User, stored?: InvestingStyle): InvestingStyle {
  if (stored) return stored
  return user.ux_mode === 'Control' ? 'Active' : 'Balanced'
}

function buildForm(user: User): ProfileEditorForm {
  const meta = loadProfileMeta()
  const normalizedGoal = GOAL_OPTIONS.includes(user.goal) ? user.goal : 'Other'
  return {
    experienceLevel: deriveExperienceLevel(user, meta.experienceLevel),
    goalOption: normalizedGoal,
    customGoal: normalizedGoal === 'Other' ? user.goal : '',
    riskProfile: user.risk_profile as 'Conservative' | 'Balanced' | 'Growth',
    monthlyContribution: user.monthly_contribution,
    timeHorizon: TIME_HORIZON_OPTIONS.includes(user.time_horizon) ? user.time_horizon : '10+ years',
    plannedWithdrawalPct: user.planned_withdrawal_pct,
    investingStyle: deriveInvestingStyle(user, meta.investingStyle),
  }
}

function getDisplayGoal(form: ProfileEditorForm) {
  return form.goalOption === 'Other' ? form.customGoal.trim() : form.goalOption
}

export default function ProfileMenu({
  onRestartOnboarding,
}: {
  onRestartOnboarding: () => void
}) {
  const [isOpen, setIsOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [user, setUser] = useState<User | null>(null)
  const [profiler, setProfiler] = useState<ProfilerSummary | null>(null)
  const [form, setForm] = useState<ProfileEditorForm | null>(null)

  const chipLabel = profiler?.investor_segment || user?.risk_profile || 'Profile'

  const loadProfileBundle = async () => {
    setLoading(true)
    setError('')
    try {
      const userResponse = await api.getUser()
      setUser(userResponse.user)
      setForm(buildForm(userResponse.user))

      try {
        const summaryResponse = await api.getPortfolioSummary()
        setProfiler(summaryResponse.profiler)
      } catch {
        setProfiler(null)
      }
    } catch (err: any) {
      setError(err.message || 'Could not load your investor profile.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadProfileBundle()
  }, [])

  useEffect(() => {
    if (!isOpen || user !== null) return
    loadProfileBundle()
  }, [isOpen, user])

  const currentExperience = useMemo(
    () => (user ? deriveExperienceLevel(user, loadProfileMeta().experienceLevel) : 'Not set'),
    [user],
  )

  const currentInvestingStyle = useMemo(
    () => (user ? deriveInvestingStyle(user, loadProfileMeta().investingStyle) : 'Not set'),
    [user],
  )

  const currentLastUpdatedReason = loadProfileMeta().lastUpdatedReason || 'Not set'

  const closeDrawer = () => {
    setIsOpen(false)
    setError('')
    if (user) {
      setForm(buildForm(user))
    }
  }

  const handleSave = async () => {
    if (!user || !form) return

    const resolvedGoal = getDisplayGoal(form)
    if (!resolvedGoal) {
      setError('Please enter a goal before saving your profile.')
      return
    }

    setSaving(true)
    setError('')

    const payload: UserUpdatePayload = {
      risk_profile: form.riskProfile,
      goal: resolvedGoal,
      time_horizon: form.timeHorizon,
      monthly_contribution: Math.max(0, Number(form.monthlyContribution) || 0),
      planned_withdrawal_pct: Math.min(100, Math.max(0, Number(form.plannedWithdrawalPct) || 0)),
      ux_mode: form.investingStyle === 'Active' ? 'Control' : 'Simple',
      has_external_holdings: form.experienceLevel === 'Beginner' ? 'No' : 'Yes',
    }

    try {
      const response = await api.updateProfile(payload)
      const updateTimestamp = `Updated from profile panel on ${new Date().toLocaleString()}`
      saveProfileMeta({
        experienceLevel: form.experienceLevel,
        investingStyle: form.investingStyle,
        lastUpdatedReason: updateTimestamp,
      })
      setUser(response.user)
      setForm(buildForm(response.user))
      try {
        const summaryResponse = await api.getPortfolioSummary()
        setProfiler(summaryResponse.profiler)
      } catch {
        setProfiler(null)
      }
      dispatchProfileUpdated()
      setIsOpen(false)
    } catch (err: any) {
      setError(err.message || 'Could not save your profile. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="profile-menu-shell">
      <button
        type="button"
        className="profile-chip"
        onClick={() => setIsOpen(true)}
        aria-haspopup="dialog"
        aria-expanded={isOpen}
      >
        <div className="profile-chip-icon">
          <UserRound size={16} />
        </div>
        <span className="profile-chip-label">{chipLabel}</span>
        <div className="profile-chip-accent">
          <SlidersHorizontal size={14} />
        </div>
      </button>

      {isOpen && (
        <div className="profile-drawer-backdrop" onClick={closeDrawer}>
          <aside
            className="profile-drawer"
            role="dialog"
            aria-modal="true"
            aria-label="Investor Profile"
            onClick={event => event.stopPropagation()}
          >
            <div className="profile-drawer-head">
              <div className="stack-sm">
                <div className="eyebrow">Investor Profile</div>
                <div className="section-title">Update your preferences anytime.</div>
                <div className="section-description">
                  EazyInvest uses this to personalize scenarios and rebalance guidance.
                </div>
              </div>
              <button type="button" className="profile-close-btn" onClick={closeDrawer} aria-label="Close profile panel">
                <X size={16} />
              </button>
            </div>

            {loading || !user || !form ? (
              <div className="card">Loading profile...</div>
            ) : (
              <div className="profile-drawer-body">
                <section className="card stack-md">
                  <div className="section-title">Current profile</div>
                  <div className="profile-readout-grid">
                    <div className="summary-item profile-readout-item">
                      <span className="muted">Investor segment</span>
                      <strong>{formatTitleCase(profiler?.investor_segment)}</strong>
                    </div>
                    <div className="summary-item profile-readout-item">
                      <span className="muted">Target profile</span>
                      <strong>{formatTitleCase(profiler?.target_profile_name)}</strong>
                    </div>
                    <div className="summary-item profile-readout-item">
                      <span className="muted">Risk profile</span>
                      <strong>{formatTitleCase(user.risk_profile)}</strong>
                    </div>
                    <div className="summary-item profile-readout-item">
                      <span className="muted">Experience level</span>
                      <strong>{currentExperience}</strong>
                    </div>
                    <div className="summary-item profile-readout-item">
                      <span className="muted">Goal</span>
                      <strong>{user.goal || 'Not set'}</strong>
                    </div>
                    <div className="summary-item profile-readout-item">
                      <span className="muted">Time horizon</span>
                      <strong>{user.time_horizon || 'Not set'}</strong>
                    </div>
                    <div className="summary-item profile-readout-item">
                      <span className="muted">Monthly contribution</span>
                      <strong>{formatCurrency(user.monthly_contribution)}</strong>
                    </div>
                    <div className="summary-item profile-readout-item">
                      <span className="muted">Liquidity need</span>
                      <strong>{formatTitleCase(profiler?.liquidity_need)}</strong>
                    </div>
                    <div className="summary-item profile-readout-item">
                      <span className="muted">Planned withdrawal</span>
                      <strong>{formatPercent(user.planned_withdrawal_pct)}</strong>
                    </div>
                    <div className="summary-item profile-readout-item">
                      <span className="muted">Profiler confidence</span>
                      <strong>{formatConfidence(profiler?.confidence)}</strong>
                    </div>
                    <div className="summary-item profile-readout-item">
                      <span className="muted">Investing style</span>
                      <strong>{currentInvestingStyle}</strong>
                    </div>
                    <div className="summary-item profile-readout-item">
                      <span className="muted">Last updated reason</span>
                      <strong>{currentLastUpdatedReason}</strong>
                    </div>
                  </div>
                </section>

                <section className="card stack-md">
                  <div className="section-title">Edit profile</div>
                  <div className="profile-form-grid">
                    <label className="field">
                      <span>Experience level</span>
                      <select value={form.experienceLevel} onChange={event => setForm(current => current ? { ...current, experienceLevel: event.target.value as ExperienceLevel } : current)}>
                        <option>Beginner</option>
                        <option>Intermediate</option>
                        <option>Experienced</option>
                      </select>
                    </label>

                    <label className="field">
                      <span>Goal</span>
                      <select value={form.goalOption} onChange={event => setForm(current => current ? { ...current, goalOption: event.target.value } : current)}>
                        {GOAL_OPTIONS.map(option => (
                          <option key={option}>{option}</option>
                        ))}
                      </select>
                    </label>

                    {form.goalOption === 'Other' && (
                      <label className="field profile-form-full">
                        <span>Custom goal</span>
                        <input
                          value={form.customGoal}
                          onChange={event => setForm(current => current ? { ...current, customGoal: event.target.value } : current)}
                          placeholder="Describe your goal"
                        />
                      </label>
                    )}

                    <label className="field">
                      <span>Risk comfort</span>
                      <select value={form.riskProfile} onChange={event => setForm(current => current ? { ...current, riskProfile: event.target.value as ProfileEditorForm['riskProfile'] } : current)}>
                        <option>Conservative</option>
                        <option>Balanced</option>
                        <option>Growth</option>
                      </select>
                    </label>

                    <label className="field">
                      <span>Monthly contribution</span>
                      <input
                        type="number"
                        min="0"
                        value={form.monthlyContribution}
                        onChange={event => setForm(current => current ? { ...current, monthlyContribution: Number(event.target.value) } : current)}
                      />
                    </label>

                    <label className="field">
                      <span>Time horizon</span>
                      <select value={form.timeHorizon} onChange={event => setForm(current => current ? { ...current, timeHorizon: event.target.value } : current)}>
                        {TIME_HORIZON_OPTIONS.map(option => (
                          <option key={option}>{option}</option>
                        ))}
                      </select>
                    </label>

                    <label className="field">
                      <span>Planned withdrawal %</span>
                      <input
                        type="number"
                        min="0"
                        max="100"
                        value={form.plannedWithdrawalPct}
                        onChange={event => setForm(current => current ? { ...current, plannedWithdrawalPct: Number(event.target.value) } : current)}
                      />
                    </label>

                    <label className="field">
                      <span>Investing style</span>
                      <select value={form.investingStyle} onChange={event => setForm(current => current ? { ...current, investingStyle: event.target.value as InvestingStyle } : current)}>
                        <option>Passive</option>
                        <option>Balanced</option>
                        <option>Active</option>
                      </select>
                    </label>
                  </div>

                  {error && <div className="error-banner">{error}</div>}

                  <div className="profile-drawer-actions">
                    <button type="button" className="btn btn-primary" onClick={handleSave} disabled={saving}>
                      {saving ? 'Saving...' : 'Save Profile'}
                    </button>
                    <button type="button" className="btn btn-secondary" onClick={closeDrawer}>
                      Cancel
                    </button>
                    <button type="button" className="btn btn-secondary profile-reset-btn" onClick={onRestartOnboarding}>
                      <RotateCcw size={15} />
                      <span>Restart Onboarding</span>
                    </button>
                  </div>
                </section>
              </div>
            )}
          </aside>
        </div>
      )}
    </div>
  )
}
