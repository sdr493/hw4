/**
 * A simplified shield in the style of the Yale coat of arms (open book with Hebrew lettering
 * on a blue field). Replace with the official artwork if you have permission to use it.
 */
export default function CoatOfArms({ size = 140 }: { size?: number }) {
  return (
    <svg width={size} height={size * 1.15} viewBox="0 0 100 115" role="img" aria-label="Yale coat of arms">
      <path d="M8 6 H92 V58 C92 86 70 102 50 110 C30 102 8 86 8 58 Z" fill="#00356b" stroke="#fff" strokeWidth="4" />
      <path d="M22 40 Q36 32 50 40 Q64 32 78 40 V74 Q64 66 50 74 Q36 66 22 74 Z" fill="#fff" />
      <path d="M50 40 V74" stroke="#00356b" strokeWidth="1.5" />
      <text x="36" y="52" textAnchor="middle" fontSize="7" fill="#00356b" fontFamily="serif">אורים</text>
      <text x="64" y="52" textAnchor="middle" fontSize="7" fill="#00356b" fontFamily="serif">ותמים</text>
      <path d="M28 60 H44 M28 65 H44 M56 60 H72 M56 65 H72" stroke="#7a9cc6" strokeWidth="1.2" />
      <text x="50" y="26" textAnchor="middle" fontSize="7.5" fontWeight="700" fill="#fff" fontFamily="Georgia, serif">LUX ET VERITAS</text>
    </svg>
  )
}
