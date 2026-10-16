import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../auth'
import { popupWasClosed, rememberPopupClosed } from '../promo'
import CoatOfArms from './CoatOfArms'

/** Welcome popup for guests: register for 10% off. Shown once per visit; the Coupon tab keeps the offer. */
export default function PromoPopup() {
  const { user, checking } = useAuth()
  const [open, setOpen] = useState(false)
  const closeRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    if (checking || user || popupWasClosed()) return
    const timer = window.setTimeout(() => setOpen(true), 800)
    return () => window.clearTimeout(timer)
  }, [checking, user])

  useEffect(() => {
    if (!open) return
    closeRef.current?.focus()
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && close()
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open])

  function close() {
    rememberPopupClosed()
    setOpen(false)
  }

  if (!open || user) return null

  return (
    <div className="promo-overlay" onClick={close}>
      <div className="promo-modal" role="dialog" aria-modal="true" aria-labelledby="promo-title" onClick={(e) => e.stopPropagation()}>
        <button ref={closeRef} className="promo-modal__close" onClick={close} aria-label="Close offer">×</button>
        <div className="promo-modal__crest"><CoatOfArms size={56} /></div>
        <p className="promo-modal__eyebrow">Welcome to Campus Customs</p>
        <h2 id="promo-title">Register and get 10% off.</h2>
        <p>Create a free account and we'll give you a personal promo code for 10% off your order.</p>
        <div className="promo-modal__actions">
          <Link to="/create-account" className="button" onClick={close}>Create account</Link>
          <button className="promo-modal__later" onClick={close}>Maybe later</button>
        </div>
        <p className="promo-modal__fine">One code per account, good for one use. Find it any time under Coupon.</p>
      </div>
    </div>
  )
}
