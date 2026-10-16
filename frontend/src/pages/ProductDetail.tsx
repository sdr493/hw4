import { Link, useParams } from 'react-router-dom'
import Price from '../components/Price'
import { useCatalog } from '../catalog'
import ErrorMessage from '../components/ErrorMessage'
import Loading from '../components/Loading'

export default function ProductDetail() {
  const { productId = '' } = useParams()
  const catalog = useCatalog()
  const { loading } = catalog
  const product = catalog.getProduct(productId)
  const error = catalog.error ?? (!loading && !product ? 'not-found' : null)

  if (loading) return <Loading label="Fetching this item" />
  if (error === 'not-found') {
    return (
      <section className="section">
        <h1>We couldn't find that item</h1>
        <Link to="/products">Back to all products</Link>
      </section>
    )
  }
  if (error || !product) return <section className="section"><ErrorMessage message={error ?? 'Unknown error'} /></section>

  const inStock = product.total_stock > 0

  return (
    <section className="section">
      <Link to="/products" className="back">‹ All products</Link>
      <div className="detail">
        <div className="detail__img">
          <img src={product.image_url} alt={product.name} />
        </div>
        <div className="detail__info">
          <h1>{product.name}</h1>
          <p className="detail__desc">{product.description}</p>
          <p className="detail__price"><Price amount={product.price} /></p>
          <p className={inStock ? 'stock stock--in' : 'stock stock--out'}>
            {inStock ? 'In stock' : 'Out of stock'}
          </p>
          <h2>Sizes</h2>
          <ul className="sizes">
            {product.inventory.map((s) => (
              <li key={s.size} className={s.quantity > 0 ? 'size' : 'size size--out'}>
                <strong>{s.size}</strong>
                {s.quantity > 0 ? <span>{s.quantity} in stock</span> : <span className="oos">Out of stock</span>}
              </li>
            ))}
          </ul>
          <p className="detail__colors">Colors: {product.colors.join(', ')}</p>
        </div>
      </div>
    </section>
  )
}
