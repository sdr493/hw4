import { useEffect, useState } from 'react'

interface Props {
  size?: number
  walking?: boolean
  /** Periodically pull out a bone and chew it. */
  chews?: boolean
}

/** Drop a photo of Handsome Dan here (frontend/public) and it replaces the drawn fallback. */
const PHOTO_URL = '/handsome-dan.jpg'
const CHEW_EVERY_MS = 6000
const CHEW_FOR_MS = 3000

let photoAvailable: Promise<boolean> | null = null
function checkPhoto(): Promise<boolean> {
  photoAvailable ??= new Promise((resolve) => {
    const img = new Image()
    img.onload = () => resolve(true)
    img.onerror = () => resolve(false)
    img.src = PHOTO_URL
  })
  return photoAvailable
}

function useChewing(enabled: boolean) {
  const [chewing, setChewing] = useState(false)
  useEffect(() => {
    if (!enabled || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
    let stop: number | undefined
    const cycle = () => {
      setChewing(true)
      stop = window.setTimeout(() => setChewing(false), CHEW_FOR_MS)
    }
    const first = window.setTimeout(cycle, 1500)
    const repeat = window.setInterval(cycle, CHEW_EVERY_MS)
    return () => {
      window.clearTimeout(first)
      window.clearTimeout(stop)
      window.clearInterval(repeat)
    }
  }, [enabled])
  return chewing
}

function Bone() {
  return (
    <svg className="dan__bone" viewBox="0 0 60 20" aria-hidden="true">
      <rect x="9" y="6" width="42" height="8" rx="4" fill="#fffdf6" stroke="#6b5a40" strokeWidth="2" />
      <circle cx="9" cy="6" r="5" fill="#fffdf6" stroke="#6b5a40" strokeWidth="2" />
      <circle cx="9" cy="14" r="5" fill="#fffdf6" stroke="#6b5a40" strokeWidth="2" />
      <circle cx="51" cy="6" r="5" fill="#fffdf6" stroke="#6b5a40" strokeWidth="2" />
      <circle cx="51" cy="14" r="5" fill="#fffdf6" stroke="#6b5a40" strokeWidth="2" />
      <rect x="10" y="7.5" width="40" height="5" fill="#fffdf6" />
    </svg>
  )
}

function Bandana() {
  return (
    <svg className="dan__bandana" viewBox="0 0 100 50" aria-hidden="true">
      <path d="M4 4 Q50 16 96 4 L50 48 Z" fill="#00356b" />
      <path d="M4 4 Q50 16 96 4" stroke="#002147" strokeWidth="5" fill="none" />
      <text x="50" y="32" textAnchor="middle" fontFamily="Georgia, serif" fontWeight="700" fontSize="18" fill="#fff">Y</text>
    </svg>
  )
}

/** Handsome Dan, the Yale bulldog, in a Yale bandana. */
export default function HandsomeDan({ size = 72, walking = false, chews = false }: Props) {
  const chewing = useChewing(chews)
  const [hasPhoto, setHasPhoto] = useState(false)
  useEffect(() => {
    checkPhoto().then(setHasPhoto)
  }, [])

  const classes = ['dan', walking && 'dan--walking', chewing && 'dan--chewing', hasPhoto && 'dan--photo']
    .filter(Boolean)
    .join(' ')

  return (
    <span className={classes} style={{ width: size, height: size }} aria-hidden="true">
      {hasPhoto ? (
        <>
          <span className="dan__frame">
            <img className="dan__photo" src={PHOTO_URL} alt="" draggable={false} />
          </span>
          <Bandana />
        </>
      ) : (
        <DrawnDan />
      )}
      <Bone />
    </span>
  )
}

/** Fallback illustration, used until a photo is added. */
function DrawnDan() {
  return (
    <svg className="dan__drawn" viewBox="0 0 100 100">
      <circle cx="50" cy="50" r="48" fill="#f5f5f7" />
      <path d="M18 34 q-8 -18 12 -18 q6 10 2 22z" fill="#a8916f" />
      <path d="M82 34 q8 -18 -12 -18 q-6 10 -2 22z" fill="#a8916f" />
      <ellipse cx="50" cy="52" rx="34" ry="30" fill="#e9dcc6" />
      <path d="M30 40 q20 -10 40 0" stroke="#c4ad8a" strokeWidth="2.5" fill="none" />
      <circle cx="38" cy="47" r="4.5" fill="#1d1d1f" />
      <circle cx="62" cy="47" r="4.5" fill="#1d1d1f" />
      <circle cx="39.5" cy="45.5" r="1.4" fill="#fff" />
      <circle cx="63.5" cy="45.5" r="1.4" fill="#fff" />
      <ellipse cx="50" cy="64" rx="20" ry="13" fill="#f7f0e4" />
      <ellipse cx="50" cy="58" rx="8" ry="5.5" fill="#2b2b2b" />
      <path className="dan__mouth" d="M36 68 q14 10 28 0" stroke="#7d6648" strokeWidth="2.5" fill="none" strokeLinecap="round" />
      <path d="M22 76 Q50 86 78 76 L50 99 Z" fill="#00356b" />
      <text x="50" y="91" textAnchor="middle" fontFamily="Georgia, serif" fontWeight="700" fontSize="11" fill="#fff">Y</text>
    </svg>
  )
}
