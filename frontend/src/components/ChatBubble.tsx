import { useEffect, useRef, useState, type FormEvent } from 'react'
import { Link, useLocation, useMatch, useNavigate } from 'react-router-dom'
import { fetchChatHistory, sendChat, type ChatHistoryMessage, type ProductCardData } from '../api'
import { useAuth } from '../auth'
import { useChatResults } from '../chatResults'
import ChatText from './ChatText'
import HandsomeDan from './HandsomeDan'
import Price from './Price'

const MAX_MESSAGE_CHARS = 1000
const HISTORY_TO_SEND = 10
const CARDS_IN_CHAT = 3
const GREETING: ChatHistoryMessage = {
  role: 'assistant',
  content: "Hi! I'm the Campus Customs assistant. Ask me about any Yale gear, prices or sizes.",
  products: [],
}

function MiniCard({ product }: { product: ProductCardData }) {
  return (
    <Link to={`/products/${product.product_id}`} className="chat__card">
      <img src={product.image_url} alt="" />
      <span>
        <strong>{product.name}</strong>
        <small><Price amount={product.price} /> · {product.in_stock ? 'In stock' : <strong className="oos">Out of stock</strong>}</small>
      </span>
    </Link>
  )
}

/** Floating chat panel, connected to the shopping agent at /api/chat. */
export default function ChatBubble() {
  const { user } = useAuth()
  const chatResults = useChatResults()
  const onItemPage = useMatch('/products/:productId')
  const navigate = useNavigate()
  const location = useLocation()
  const [open, setOpen] = useState(false)
  const [draft, setDraft] = useState('')
  const [messages, setMessages] = useState<ChatHistoryMessage[]>([GREETING])
  const [sending, setSending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const logRef = useRef<HTMLOListElement>(null)

  // Logged-in shoppers pick up where they left off; guests start fresh.
  useEffect(() => {
    setMessages([GREETING])
    if (!user) return
    fetchChatHistory()
      .then((history) => history.length && setMessages([GREETING, ...history]))
      .catch(() => undefined)
  }, [user])

  useEffect(() => {
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, sending, open])

  // Item pages hide chat matches, so go back to the product list to show them.
  function showOnPage(products: ProductCardData[]) {
    chatResults.show(null, products)
    if (onItemPage) navigate('/products')
  }

  async function send(e: FormEvent) {
    e.preventDefault()
    const text = draft.trim()
    if (!text || sending) return
    // Logged-in history is loaded on the server; guests send this visit's messages (never saved).
    const history = user ? [] : messages.slice(1).slice(-HISTORY_TO_SEND).map(({ role, content }) => ({ role, content }))
    const page = { path: location.pathname, product_id: onItemPage?.params.productId ?? null }
    setMessages((m) => [...m, { role: 'user', content: text, products: [] }])
    setDraft('')
    setError(null)
    setSending(true)
    try {
      const reply = await sendChat(text, history, page)
      setMessages((m) => [...m, { role: 'assistant', content: reply.reply, products: reply.products, manager: reply.manager }])
      // API contract: structured matches in the reply are rendered as cards on the page.
      if (reply.products.length) chatResults.show(reply.results_title, reply.products)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="chat">
      {open && (
        <section className="chat__panel" aria-label="Chat with Campus Customs">
          <header className="chat__head">
            <HandsomeDan size={40} />
            <strong>Ask Campus Customs</strong>
            <button className="chat__close" onClick={() => setOpen(false)} aria-label="Close chat">×</button>
          </header>
          <ol className="chat__log" ref={logRef} aria-live="polite">
            {messages.map((m, i) => (
              <li key={i} className={`chat__item chat__item--${m.role}`}>
                {m.manager && <span className="chat__manager">The manager stepped in</span>}
                <div className={`chat__msg chat__msg--${m.role}`}>
                  {m.role === 'assistant' ? <ChatText text={m.content} /> : m.content}
                </div>
                {m.products.length > 0 && (
                  <div className="chat__cards">
                    {m.products.slice(0, CARDS_IN_CHAT).map((p) => <MiniCard key={p.product_id} product={p} />)}
                    {(m.products.length > CARDS_IN_CHAT || onItemPage) && (
                      <button className="chat__more" onClick={() => showOnPage(m.products)}>
                        See {m.products.length > 1 ? `all ${m.products.length}` : 'it'} on the page
                      </button>
                    )}
                  </div>
                )}
              </li>
            ))}
            {sending && (
              <li className="chat__item chat__item--assistant">
                <div className="chat__msg chat__msg--assistant chat__typing" aria-label="Assistant is typing">
                  <span /><span /><span />
                </div>
              </li>
            )}
          </ol>
          {error && <p className="chat__error" role="alert">{error}. Please try again.</p>}
          <form className="chat__form" onSubmit={send}>
            <label htmlFor="chat-input" className="sr-only">Message</label>
            <input
              id="chat-input"
              value={draft}
              maxLength={MAX_MESSAGE_CHARS}
              onChange={(e) => setDraft(e.target.value)}
              placeholder="Ask about merch…"
              disabled={sending}
            />
            <button type="submit" disabled={sending || !draft.trim()}>Send</button>
          </form>
        </section>
      )}
      <button className="chat__bubble" onClick={() => setOpen((o) => !o)} aria-expanded={open} aria-label={open ? 'Close chat' : 'Open chat'}>
        <svg viewBox="0 0 24 24" width="26" height="26" aria-hidden="true">
          <path d="M4 4h16v11H8l-4 4z" fill="currentColor" />
        </svg>
      </button>
    </div>
  )
}
