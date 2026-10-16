import HandsomeDan from './HandsomeDan'

/** Loading screen: Handsome Dan walks across while data loads. */
export default function Loading({ label = 'Loading' }: { label?: string }) {
  return (
    <div className="loading" role="status" aria-live="polite">
      <div className="loading__track">
        <div className="loading__walker">
          <HandsomeDan size={96} walking />
        </div>
      </div>
      <p>{label}…</p>
    </div>
  )
}
