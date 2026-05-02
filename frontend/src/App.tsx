import { Navigate, Route, Routes } from 'react-router-dom'
import { useState } from 'react'
import Navbar from './components/Navbar'
import AuditLayer from './pages/AuditLayer'
import Dashboard from './pages/Dashboard'
import Holdings from './pages/Holdings'
import Onboarding from './pages/Onboarding'
import ScenarioPlanner from './pages/ScenarioPlanner'
import { clearProfileMeta, EAZYINVEST_ONBOARDED_KEY } from './utils/profileState'

export default function App() {
  const [hasOnboarded, setHasOnboarded] = useState(() => localStorage.getItem(EAZYINVEST_ONBOARDED_KEY) === 'true')

  const handleOnboardingComplete = () => {
    localStorage.setItem(EAZYINVEST_ONBOARDED_KEY, 'true')
    setHasOnboarded(true)
  }

  const handleRestartOnboarding = () => {
    localStorage.removeItem(EAZYINVEST_ONBOARDED_KEY)
    clearProfileMeta()
    setHasOnboarded(false)
  }

  return (
    <div className="app-shell">
      {hasOnboarded && <Navbar onRestartOnboarding={handleRestartOnboarding} />}
      <main className="app-main">
        <Routes>
          <Route path="/onboarding" element={hasOnboarded ? <Navigate to="/dashboard" replace /> : <Onboarding onComplete={handleOnboardingComplete} />} />
          <Route path="/dashboard" element={hasOnboarded ? <Dashboard /> : <Navigate to="/onboarding" replace />} />
          <Route path="/holdings" element={hasOnboarded ? <Holdings /> : <Navigate to="/onboarding" replace />} />
          <Route path="/scenarios" element={hasOnboarded ? <ScenarioPlanner /> : <Navigate to="/onboarding" replace />} />
          <Route path="/audit" element={hasOnboarded ? <AuditLayer /> : <Navigate to="/onboarding" replace />} />
          <Route path="*" element={<Navigate to={hasOnboarded ? '/dashboard' : '/onboarding'} replace />} />
        </Routes>
      </main>
    </div>
  )
}
