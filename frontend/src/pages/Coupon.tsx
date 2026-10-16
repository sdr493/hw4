import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../auth'
import ErrorMessage from '../components/ErrorMessage'
import Loading from '../components/Loading'
import { redeemPromo } from '../promo'
import { usePromo } from '../promoContext'

export default function Coupon() {
  const { user, checking } = useAuth()
  const { promo, refresh } = usePromo()
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<{ ok: boolean; message: string } | null>(null)
  const [busy, setBusy] = useState(false)

  async function apply() {
    if (!promo) return
    setBusy(true)
    try {
      const r = await redeemPromo(promo.code)
      setResult(r)
      await refresh() // turns on the discounted prices across the site
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setBusy(false)
    }
  }

  if (checking) return <Loading label="Checking your account" />

  if (!user) {
    return (
      <section className="section coupon">
        <p className="coupon__eyebrow">Coupon</p>
        <h1>10% off when you register.</h1>
        <p className="coupon__lead">
          Create a free Campus Customs account and you'll get your own promo code for 10% off your order.
          It's yours alone and works once.
        </p>
        <div className="coupon__actions">
          <Link to="/create-account" className="button">Create account</Link>
          <Link to="/login">Already registered? Log in ›</Link>
        </div>
      </section>
    )
  }

  return (
    <section className="section coupon">
      <p className="coupon__eyebrow">Coupon</p>
      <h1>Your 10% off code, {user.first_name}.</h1>
      {error && <ErrorMessage message={error} />}
      {!promo && !error && <Loading label="Fetching your code" />}
      {promo && (
        <div className={`coupon__card${promo.used ? ' coupon__card--used' : ''}`}>
          <span className="coupon__code" aria-label="Your promo code">{promo.code}</span>
          <span className="coupon__status">
            {promo.used
              ? <strong className="coupon__ready">Applied on {promo.used_at?.slice(0, 10)} · {promo.discount_percent}% off is showing on every price</strong>
              : <strong className="coupon__ready">Ready to use · {promo.discount_percent}% off</strong>}
          </span>
          {promo.used ? (
            <button className="button" onClick={apply} disabled={busy}>Try to use it again</button>
          ) : (
            <button className="button" onClick={apply} disabled={busy}>{busy ? 'Applying…' : 'Use my code'}</button>
          )}
        </div>
      )}
      {result && (
        <p className={result.ok ? 'notice' : 'error'} role="status">{result.message}</p>
      )}
      <p className="coupon__fine">One unique code per account. It can only be used once and only on your account.</p>
    </section>
  )
}
