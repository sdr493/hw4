import { Link } from 'react-router-dom'
import type { Product, ProductCardData } from '../api'
import Price from './Price'

/** Works for catalogue products and for structured matches from the chat agent. */
type CardProduct = Pick<Product, 'product_id' | 'name' | 'price' | 'image_url' | 'description'> &
  Partial<Pick<Product, 'total_stock'>> &
  Partial<Pick<ProductCardData, 'in_stock'>>

export default function ProductCard({ product }: { product: CardProduct }) {
  const inStock = product.in_stock ?? (product.total_stock ?? 0) > 0
  return (
    <Link to={`/products/${product.product_id}`} className="card">
      <div className="card__img">
        <img src={product.image_url} alt={product.name} loading="lazy" />
      </div>
      <div className="card__body">
        <h3>{product.name}</h3>
        <p className="card__price"><Price amount={product.price} /></p>
        <p className="card__desc">{product.description}</p>
        {!inStock && <p className="card__oos oos">Out of stock</p>}
      </div>
    </Link>
  )
}
