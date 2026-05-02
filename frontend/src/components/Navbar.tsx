import { NavLink } from 'react-router-dom'

const links = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/holdings', label: 'My Holdings' },
  { to: '/scenarios', label: 'Scenario Planner' },
  { to: '/audit', label: 'Audit Layer' },
]

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <div className="brand-mark">EI</div>
        <div>
          <div className="brand-name">EazyInvest</div>
          <div className="brand-subtitle">Deterministic portfolio planning</div>
        </div>
      </div>
      <div className="nav-links">
        {links.map(({ to, label }) => (
          <NavLink key={to} to={to} className={({ isActive }) => `nav-link ${isActive ? 'nav-link-active' : ''}`}>
            {label}
          </NavLink>
        ))}
      </div>
    </nav>
  )
}
