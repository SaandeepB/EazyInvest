import { Navigate, Route, Routes } from 'react-router-dom'
import { useState } from 'react'
import Navbar from './components/Navbar'
import AuditLayer from './pages/AuditLayer'
import Dashboard from './pages/Dashboard'
import Holdings from './pages/Holdings'
import Onboarding from './pages/Onboarding'
import ScenarioPlanner from './pages/ScenarioPlanner'

export default function App() {
  const [hasOnboarded, setHasOnboarded] = useState(() => localStorage.getItem('eazyinvest_onboarded') === 'true')

  const handleOnboardingComplete = () => {
    localStorage.setItem('eazyinvest_onboarded', 'true')
    setHasOnboarded(true)
  }

  return (
    <div className="app-shell">
      {hasOnboarded && <Navbar />}
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
