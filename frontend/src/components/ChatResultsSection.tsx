import { useEffect, useRef } from 'react'
import { useMatch } from 'react-router-dom'
import { useChatResults } from '../chatResults'
import ProductCard from './ProductCard'

/** Renders the chat agent's product matches on the page. Hidden on single item pages. */
export default function ChatResultsSection() {
  const { results, clear } = useChatResults()
  const onItemPage = useMatch('/products/:productId')
  const ref = useRef<HTMLElement>(null)
  // Results restored from an earlier visit don't scroll; new results from the chat do.
  const lastShown = useRef<number | null>(results?.id ?? null)

  useEffect(() => {
    if (results && results.id !== lastShown.current && !onItemPage) {
      ref.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      lastShown.current = results.id
    }
  }, [results, onItemPage])

  if (!results || onItemPage) return null

  return (
    <section className="chat-results" ref={ref} aria-label="Products from your chat" aria-live="polite">
      <div className="chat-results__inner">
        <div className="section__head">
          <div>
            <p className="chat-results__eyebrow">From your chat</p>
            <h2>{results.title}</h2>
          </div>
          <button className="chat-results__clear" onClick={clear}>Clear</button>
        </div>
        <div className="grid">
          {results.products.map((p) => <ProductCard key={p.product_id} product={p} />)}
        </div>
      </div>
    </section>
  )
}
