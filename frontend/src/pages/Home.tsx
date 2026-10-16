import { Link } from 'react-router-dom'
import { useCatalog } from '../catalog'
import CoatOfArms from '../components/CoatOfArms'
import ErrorMessage from '../components/ErrorMessage'
import Loading from '../components/Loading'
import ProductCard from '../components/ProductCard'

export default function Home() {
  const catalog = useCatalog()

  return (
    <>
      <section className="hero">
        <CoatOfArms size={96} />
        <div className="hero__copy">
          <h1>Wear Yale for less.</h1>
          <p>
            Yale gear for every college, team and school, priced so you can rep the Bulldogs without blowing your budget.
          </p>
          <Link to="/products" className="button button--light">Shop now</Link>
        </div>
      </section>

      <section className="section">
        <div className="section__head">
          <h2>Popular right now.</h2>
          <Link to="/products">See all ›</Link>
        </div>
        {catalog.loading && <Loading label="Fetching popular picks" />}
        {catalog.error && <ErrorMessage message={catalog.error} />}
        {!catalog.loading && !catalog.error && (
          <div className="grid grid--five">
            {catalog.popular.map((p) => <ProductCard key={p.product_id} product={p} />)}
          </div>
        )}
      </section>

      <section className="section perks">
        <div><h3>Every corner of campus</h3><p>Residential colleges, varsity teams and graduate schools all in one place.</p></div>
        <div><h3>Real prices, real stock</h3><p>What you see is pulled straight from our inventory, size by size.</p></div>
        <div><h3>Ask Dan's helper</h3><p>Not sure what fits? Tap the chat bubble and ask about any item.</p></div>
      </section>
    </>
  )
}
