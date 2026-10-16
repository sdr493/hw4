export interface PromoCode {
  code: string
  discount_percent: number
  created_at: string
  used: boolean
  used_at: string | null
}

export interface PromoRedeemResult {
  ok: boolean
  message: string
  discount_percent: number | null
}

/** The logged-in shopper's own code. The backend generates it the first time it's asked for. */
export async function fetchMyPromo(): Promise<PromoCode> {
  const res = await fetch('/api/promo', { credentials: 'same-origin' })
  if (!res.ok) throw new Error(res.status === 401 ? 'Log in to see your promo code' : `Request failed (${res.status})`)
  return res.json()
}

export async function redeemPromo(code: string): Promise<PromoRedeemResult> {
  const res = await fetch('/api/promo/redeem', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'same-origin',
    body: JSON.stringify({ code }),
  })
  if (!res.ok) throw new Error(`Request failed (${res.status})`)
  return res.json()
}

const POPUP_KEY = 'cc-promo-popup-closed'

export function popupWasClosed(): boolean {
  try {
    return sessionStorage.getItem(POPUP_KEY) === '1'
  } catch {
    return false
  }
}

export function rememberPopupClosed() {
  try {
    sessionStorage.setItem(POPUP_KEY, '1')
  } catch {
    // Storage unavailable: the popup may show again on the next visit.
  }
}
