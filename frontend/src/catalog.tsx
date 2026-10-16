import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import type { Filters, Product, ProductDetail, ProductPage, ProductQuery } from './api'

const PAGE_SIZE = 20

interface Bootstrap {
  products: ProductDetail[]
  filters: Filters
  popular_ids: string[]
}

interface CatalogState {
  loading: boolean
  error: string | null
  filters: Filters | null
  popular: Product[]
  getProduct: (id: string) => ProductDetail | undefined
  query: (q: ProductQuery) => ProductPage
}

const CatalogContext = createContext<CatalogState | null>(null)

/** Loads the whole store once (GET /api/bootstrap) so every page after that renders instantly. */
export function CatalogProvider({ children }: { children: ReactNode }) {
  const [data, setData] = useState<Bootstrap | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch('/api/bootstrap')
      .then((r) => {
        if (!r.ok) throw new Error(`Request failed (${r.status})`)
        return r.json() as Promise<Bootstrap>
      })
      .then(setData)
      .catch((e: Error) => setError(e.message))
  }, [])

  const value = useMemo<CatalogState>(() => {
    const products = data?.products ?? []
    const byId = new Map(products.map((p) => [p.product_id, p]))
    return {
      loading: !data && !error,
      error,
      filters: data?.filters ?? null,
      popular: (data?.popular_ids ?? []).map((id) => byId.get(id)).filter((p): p is ProductDetail => !!p),
      getProduct: (id) => byId.get(id),
      query: (q) => queryProducts(products, q),
    }
  }, [data, error])

  return <CatalogContext.Provider value={value}>{children}</CatalogContext.Provider>
}

export function useCatalog(): CatalogState {
  const ctx = useContext(CatalogContext)
  if (!ctx) throw new Error('useCatalog must be used inside CatalogProvider')
  return ctx
}

/** Same filtering, sorting and paging rules as GET /api/products, done in the browser. */
function queryProducts(all: Product[], q: ProductQuery): ProductPage {
  let items = all
  if (q.style) items = items.filter((p) => p.style === q.style)
  if (q.audience === 'mens' || q.audience === 'womens') {
    items = items.filter((p) => p.audience === q.audience || p.audience === 'unisex')
  } else if (q.audience === 'unisex') {
    items = items.filter((p) => p.audience === 'unisex')
  }
  if (q.inStock) items = items.filter((p) => p.total_stock > 0)
  if (q.q) {
    const needle = q.q.toLowerCase()
    items = items.filter((p) =>
      [p.name, p.description, ...p.colors, ...p.search_tags].join(' ').toLowerCase().includes(needle))
  }

  const byName = (a: Product, b: Product) => a.name.localeCompare(b.name)
  const sorted = [...items]
  if (q.sort === 'price_asc') sorted.sort((a, b) => a.price - b.price || byName(a, b))
  else if (q.sort === 'price_desc') sorted.sort((a, b) => b.price - a.price || byName(a, b))
  else if (q.sort === 'name') sorted.sort(byName)
  else sorted.sort((a, b) => b.popularity - a.popularity || byName(a, b))

  const pages = Math.max(1, Math.ceil(sorted.length / PAGE_SIZE))
  const page = Math.min(Math.max(1, q.page ?? 1), pages)
  return { items: sorted.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE), total: sorted.length, page, pages }
}
