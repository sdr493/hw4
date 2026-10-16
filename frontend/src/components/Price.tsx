import { formatPrice } from '../api'
import { usePromo } from '../promoContext'

/** A price that shows the shopper's applied discount: list price struck through, then their price. */
export default function Price({ amount, className }: { amount: number; className?: string }) {
  const { discountPercent } = usePromo()
  if (!discountPercent) return <span className={className}>{formatPrice(amount)}</span>

  const discounted = Math.round(amount * (100 - discountPercent)) / 100
  return (
    <span className={`price price--discounted ${className ?? ''}`}>
      <s className="price__was" aria-label={`Was ${formatPrice(amount)}`}>{formatPrice(amount)}</s>{' '}
      <span className="price__now" aria-label={`Now ${formatPrice(discounted)}`}>{formatPrice(discounted)}</span>
      <span className="price__tag">{discountPercent}% off</span>
    </span>
  )
}
