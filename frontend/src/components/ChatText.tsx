import type { ReactNode } from 'react'

const OUT_OF_STOCK = /(out of stock|sold out)/gi
const IS_OUT_OF_STOCK = /out of stock|sold out/i

/** Shows "out of stock" / "sold out" in bold red. */
function highlightStock(text: string, keyBase: string): ReactNode[] {
  return text.split(OUT_OF_STOCK).map((part, i) =>
    i % 2 === 1 ? <strong key={`${keyBase}-${i}`} className="oos">{part}</strong> : part,
  )
}

/** Renders an assistant message: **bold** markdown plus bold red out-of-stock labels. No HTML is injected. */
export default function ChatText({ text }: { text: string }) {
  const nodes = text.split(/\*\*(.+?)\*\*/g).flatMap((part, i) => {
    if (i % 2 === 0) return highlightStock(part, String(i))
    return IS_OUT_OF_STOCK.test(part)
      ? [<strong key={i} className="oos">{part}</strong>]
      : [<strong key={i}>{part}</strong>]
  })
  return <>{nodes}</>
}
