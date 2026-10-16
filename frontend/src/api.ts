export interface Product {
  product_id: string
  name: string
  garment_type: string
  style: string
  audience: 'mens' | 'womens' | 'unisex'
  description: string
  colors: string[]
  search_tags: string[]
  image_url: string
  price: number
  total_stock: number
  popularity: number
}

export interface SizeStock {
  size: string
  quantity: number
}

export interface ProductDetail extends Product {
  inventory: SizeStock[]
}

export interface ProductPage {
  items: Product[]
  total: number
  page: number
  pages: number
}

export interface FilterOption {
  key: string
  label: string
}

export interface Filters {
  styles: FilterOption[]
  audiences: FilterOption[]
}

export interface ProductQuery {
  style?: string
  audience?: string
  q?: string
  sort?: string
  inStock?: boolean
  page?: number
}

async function getJson<T>(url: string): Promise<T> {
  const res = await fetch(url)
  if (res.status === 404) throw new Error('not-found')
  if (!res.ok) throw new Error(`Request failed (${res.status})`)
  return res.json() as Promise<T>
}

export const fetchPopular = () => getJson<Product[]>('/api/products/popular?limit=5')

export const fetchFilters = () => getJson<Filters>('/api/filters')

export const fetchProduct = (id: string) =>
  getJson<ProductDetail>(`/api/products/${encodeURIComponent(id)}`)

export function fetchProducts(query: ProductQuery) {
  const params = new URLSearchParams()
  if (query.style) params.set('style', query.style)
  if (query.audience) params.set('audience', query.audience)
  if (query.q) params.set('q', query.q)
  if (query.sort) params.set('sort', query.sort)
  if (query.inStock) params.set('in_stock', 'true')
  params.set('page', String(query.page ?? 1))
  return getJson<ProductPage>(`/api/products?${params}`)
}

export const formatPrice = (price: number) =>
  price.toLocaleString('en-US', { style: 'currency', currency: 'USD' })

export interface ProductCardData {
  product_id: string
  name: string
  price: number
  image_url: string
  description: string
  in_stock: boolean
}

export interface ChatTurn {
  role: 'user' | 'assistant'
  content: string
}

export interface ChatReply {
  reply: string
  products: ProductCardData[]
  results_title: string | null
  stopped: boolean
  manager: boolean
}

export interface ChatHistoryMessage extends ChatTurn {
  products: ProductCardData[]
  manager?: boolean
}

/** Where the shopper is, so the agent knows which product "this" means. */
export interface PageContext {
  path: string
  product_id: string | null
}

export const fetchChatHistory = () => getJson<ChatHistoryMessage[]>('/api/chat/history')

export async function sendChat(message: string, history: ChatTurn[], page: PageContext): Promise<ChatReply> {
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'same-origin',
    body: JSON.stringify({ message, history, page }),
  })
  if (!res.ok) {
    const data = await res.json().catch(() => null)
    throw new Error(typeof data?.detail === 'string' ? data.detail : `Chat failed (${res.status})`)
  }
  return res.json()
}
