import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../auth'
import { usePromo } from '../promoContext'

const HIDDEN_KEY = 'cc-promo-banner-hidden'

/** After logging in, shows the shopper their own unused promo code. */
export default function PromoBanner() {
  const { user } = useAuth()
  const { promo } = usePromo()
  const [hidden, setHidden] = useState(() => {
    try {
      return sessionStorage.getItem(HIDDEN_KEY) === '1'
    } catch {
      return false
    }
  })

  function hide() {
    setHidden(true)
    try {
      sessionStorage.setItem(HIDDEN_KEY, '1')
    } catch {
      // ignore
    }
  }

  if (!user || !promo || promo.used || hidden) return null

  return (
    <div className="promo-banner" role="status">
      <span>
        Welcome back, {user.first_name}! Your 10% off code: <strong className="promo-banner__code">{promo.code}</strong>
      </span>
      <Link to="/coupon">Use it ›</Link>
      <button onClick={hide} aria-label="Hide promo code banner">×</button>
    </div>
  )
}
