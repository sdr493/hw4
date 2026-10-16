import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'
import { useAuth } from './auth'
import { fetchMyPromo, type PromoCode } from './promo'

interface PromoState {
  promo: PromoCode | null
  /** Percent off shown on every price: set once the shopper has applied their code, otherwise 0. */
  discountPercent: number
  refresh: () => Promise<void>
}

const PromoContext = createContext<PromoState | null>(null)

/** The logged-in shopper's promo code, shared by the banner, the Coupon tab and every price on the site. */
export function PromoProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth()
  const [promo, setPromo] = useState<PromoCode | null>(null)

  const refresh = useCallback(async () => {
    if (!user) {
      setPromo(null)
      return
    }
    setPromo(await fetchMyPromo().catch(() => null))
  }, [user])

  useEffect(() => {
    setPromo(null)
    refresh()
  }, [refresh])

  const discountPercent = user && promo?.used ? promo.discount_percent : 0
  return <PromoContext.Provider value={{ promo, discountPercent, refresh }}>{children}</PromoContext.Provider>
}

export function usePromo(): PromoState {
  const ctx = useContext(PromoContext)
  if (!ctx) throw new Error('usePromo must be used inside PromoProvider')
  return ctx
}
