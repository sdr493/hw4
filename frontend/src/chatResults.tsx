import { createContext, useContext, useState, type ReactNode } from 'react'
import type { ProductCardData } from './api'

/** Product matches from the latest chat reply, shown as cards on the page. */
export interface ChatResults {
  id: number
  title: string
  products: ProductCardData[]
}

interface ChatResultsState {
  results: ChatResults | null
  show: (title: string | null, products: ProductCardData[]) => void
  clear: () => void
}

const STORAGE_KEY = 'cc-chat-results'
const ChatResultsContext = createContext<ChatResultsState | null>(null)

// Kept for this browser tab only, so a reload or a trip to an item page keeps the results.
function load(): ChatResults | null {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as ChatResults) : null
  } catch {
    return null
  }
}

function save(results: ChatResults | null) {
  try {
    if (results) sessionStorage.setItem(STORAGE_KEY, JSON.stringify(results))
    else sessionStorage.removeItem(STORAGE_KEY)
  } catch {
    // Storage unavailable: results just won't survive a reload.
  }
}

export function ChatResultsProvider({ children }: { children: ReactNode }) {
  const [results, setResults] = useState<ChatResults | null>(load)

  const update = (next: ChatResults | null) => {
    setResults(next)
    save(next)
  }

  const value: ChatResultsState = {
    results,
    show: (title, products) => update({ id: Date.now(), title: title || 'Matches from chat', products }),
    clear: () => update(null),
  }
  return <ChatResultsContext.Provider value={value}>{children}</ChatResultsContext.Provider>
}

export function useChatResults(): ChatResultsState {
  const ctx = useContext(ChatResultsContext)
  if (!ctx) throw new Error('useChatResults must be used inside ChatResultsProvider')
  return ctx
}
