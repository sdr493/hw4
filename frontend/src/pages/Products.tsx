import { useSearchParams } from 'react-router-dom'
import { useCatalog } from '../catalog'
import ErrorMessage from '../components/ErrorMessage'
import Loading from '../components/Loading'
import ProductCard from '../components/ProductCard'

const SORTS = [
  { key: 'popular', label: 'Most popular' },
  { key: 'price_asc', label: 'Price: low to high' },
  { key: 'price_desc', label: 'Price: high to low' },
  { key: 'name', label: 'Name A–Z' },
]

export default function Products() {
  const [params, setParams] = useSearchParams()
  const style = params.get('style') ?? ''
  const audience = params.get('audience') ?? ''
  const sort = params.get('sort') ?? 'popular'
  const q = params.get('q') ?? ''
  const inStock = params.get('in_stock') === 'true'
  const page = Number(params.get('page') ?? '1') || 1

  // Filtering and paging run on the preloaded catalogue, so they're instant.
  const catalog = useCatalog()
  const filters = { data: catalog.filters }
  const results = {
    loading: catalog.loading,
    error: catalog.error,
    data: catalog.loading || catalog.error ? null : catalog.query({ style, audience, sort, q, inStock, page }),
  }

  function update(changes: Record<string, string>) {
    const next = new URLSearchParams(params)
    for (const [k, v] of Object.entries(changes)) {
      if (v) next.set(k, v)
      else next.delete(k)
    }
    if (!('page' in changes)) next.delete('page')
    setParams(next)
  }

  function goToPage(p: number) {
    update({ page: p > 1 ? String(p) : '' })
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <section className="section">
      <h1>Products</h1>

      <div className="filters">
        <label>
          Category
          <select value={style} onChange={(e) => update({ style: e.target.value })}>
            <option value="">All styles</option>
            {filters.data?.styles.map((s) => <option key={s.key} value={s.key}>{s.label}</option>)}
          </select>
        </label>
        <label>
          Fit for
          <select value={audience} onChange={(e) => update({ audience: e.target.value })}>
            <option value="">Everyone</option>
            {filters.data?.audiences.map((a) => <option key={a.key} value={a.key}>{a.label}</option>)}
          </select>
        </label>
        <label>
          Sort by
          <select value={sort} onChange={(e) => update({ sort: e.target.value === 'popular' ? '' : e.target.value })}>
            {SORTS.map((s) => <option key={s.key} value={s.key}>{s.label}</option>)}
          </select>
        </label>
        <label className="filters__search">
          Search
          <input
            type="search"
            defaultValue={q}
            placeholder="hockey, Saybrook, gray…"
            onKeyDown={(e) => e.key === 'Enter' && update({ q: e.currentTarget.value.trim() })}
            onBlur={(e) => e.target.value.trim() !== q && update({ q: e.target.value.trim() })}
          />
        </label>
        <label className="filters__check">
          <input type="checkbox" checked={inStock} onChange={(e) => update({ in_stock: e.target.checked ? 'true' : '' })} />
          In stock only
        </label>
      </div>
      {(audience === 'mens' || audience === 'womens') && (
        <p className="hint">Includes unisex styles that fit everyone.</p>
      )}

      {results.loading && <Loading label="Rounding up the merch" />}
      {results.error && <ErrorMessage message={results.error} />}
      {results.data && !results.loading && (
        <>
          <p className="hint">{results.data.total} item{results.data.total === 1 ? '' : 's'}</p>
          {results.data.items.length === 0 ? (
            <p className="empty">No products match those filters. Try widening your search.</p>
          ) : (
            <div className="grid">
              {results.data.items.map((p) => <ProductCard key={p.product_id} product={p} />)}
            </div>
          )}
          {results.data.pages > 1 && (
            <nav className="pager" aria-label="Product pages">
              <button disabled={page <= 1} onClick={() => goToPage(page - 1)}>‹ Prev</button>
              {Array.from({ length: results.data.pages }, (_, i) => i + 1).map((p) => (
                <button key={p} aria-current={p === page ? 'page' : undefined} onClick={() => goToPage(p)}>{p}</button>
              ))}
              <button disabled={page >= results.data.pages} onClick={() => goToPage(page + 1)}>Next ›</button>
            </nav>
          )}
        </>
      )}
    </section>
  )
}
