import { BarChart3, ClipboardCheck, LayoutGrid, Wallet } from 'lucide-react'
import { NavLink } from 'react-router-dom'

const links = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutGrid },
  { to: '/holdings', label: 'My Holdings', icon: Wallet },
  { to: '/scenarios', label: 'Scenario Planner', icon: BarChart3 },
  { to: '/audit', label: 'Audit Layer', icon: ClipboardCheck },
]

export default function Navbar() {
  return (
    <header className="navbar-shell">
      <nav className="navbar">
        <div className="navbar-brand">
          <div className="brand-mark">
            <span className="brand-mark-core">E</span>
          </div>
          <div className="brand-copy">
            <div className="brand-name">EazyInvest</div>
            <div className="brand-subtitle">Simple planning with deterministic market proxies.</div>
          </div>
        </div>

        <div className="nav-links">
          {links.map(({ to, label, icon: Icon }) => (
            <NavLink key={to} to={to} className={({ isActive }) => `nav-link ${isActive ? 'nav-link-active' : ''}`}>
              <Icon size={16} />
              <span>{label}</span>
            </NavLink>
          ))}
        </div>
      </nav>
    </header>
  )
}
