import { Link, NavLink } from 'react-router-dom'
import { useAuth } from '../auth'
import HandsomeDan from './HandsomeDan'

const LINKS = [
  { to: '/', label: 'Home', end: true },
  { to: '/products', label: 'Products' },
  { to: '/about', label: 'About Us' },
  { to: '/coupon', label: 'Coupon' },
]

const GUEST_LINKS = [
  { to: '/login', label: 'Log in' },
  { to: '/create-account', label: 'Create account', cta: true },
]

export default function NavBar() {
  const { user, logout } = useAuth()

  return (
    <header className="site-header">
      <nav className="nav" aria-label="Main">
        <Link to="/" className="brand" aria-label="Campus Customs home">
          <HandsomeDan size={76} chews />
          <span className="brand__text">
            <strong>Campus Customs</strong>
          </span>
        </Link>
        <ul className="nav__links">
          {LINKS.map((l) => (
            <li key={l.to}>
              <NavLink to={l.to} end={l.end}>
                {l.label}
              </NavLink>
            </li>
          ))}
          {user ? (
            <>
              <li className="nav__greeting">Hi, {user.first_name}</li>
              <li><button className="nav__logout" onClick={() => logout()}>Log out</button></li>
            </>
          ) : (
            GUEST_LINKS.map((l) => (
              <li key={l.to}>
                <NavLink to={l.to} className={l.cta ? 'nav__cta' : undefined}>{l.label}</NavLink>
              </li>
            ))
          )}
        </ul>
      </nav>
    </header>
  )
}
