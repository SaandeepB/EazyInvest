export const EAZYINVEST_ONBOARDED_KEY = 'eazyinvest_onboarded'
export const EAZYINVEST_PROFILE_META_KEY = 'eazyinvest_profile_meta'
export const EAZYINVEST_PROFILE_UPDATED_EVENT = 'eazyinvest-profile-updated'

export interface ProfileMetaState {
  experienceLevel?: 'Beginner' | 'Intermediate' | 'Experienced'
  investingStyle?: 'Passive' | 'Balanced' | 'Active'
  lastUpdatedReason?: string
}

export function loadProfileMeta(): ProfileMetaState {
  try {
    const raw = localStorage.getItem(EAZYINVEST_PROFILE_META_KEY)
    if (!raw) return {}
    const parsed = JSON.parse(raw) as ProfileMetaState
    return parsed ?? {}
  } catch {
    return {}
  }
}

export function saveProfileMeta(meta: ProfileMetaState) {
  localStorage.setItem(EAZYINVEST_PROFILE_META_KEY, JSON.stringify(meta))
}

export function clearProfileMeta() {
  localStorage.removeItem(EAZYINVEST_PROFILE_META_KEY)
}

export function dispatchProfileUpdated() {
  window.dispatchEvent(new CustomEvent(EAZYINVEST_PROFILE_UPDATED_EVENT))
}
