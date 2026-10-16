/**
 * Bottom banner on every page: an original silhouette of Yale's main campus skyline in New Haven,
 * inspired by Harkness Tower, Sterling Memorial Library, the Woolsey Hall rotunda, Battell Chapel,
 * Phelps Gate and the Old Campus buildings. Stylized, not an exact drawing.
 */
export default function Skyline() {
  return (
    <section className="skyline" aria-label="Yale campus skyline">
      <svg className="skyline__art" viewBox="0 0 1440 260" preserveAspectRatio="xMidYMax slice" aria-hidden="true">
        <defs>
          <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#dce8f6" />
            <stop offset="1" stopColor="#9fbadb" />
          </linearGradient>
        </defs>
        <rect width="1440" height="260" fill="url(#sky)" />
        <circle cx="1180" cy="70" r="26" fill="#fff" opacity=".7" />

        {/* Far layer: rooftops in a lighter blue */}
        <path
          fill="#6f93c0"
          d="M0 200 V170 h60 v-20 h40 v30 h50 v-40 l20 -18 20 18 v40 h60 v-25 h70 v25 h40 v-50 h30 v50 h80 v-30 h60 v30
             h70 v-45 l25 -20 25 20 v45 h90 v-28 h50 v28 h60 v-38 h40 v38 h80 v-22 h60 v22 h70 v-48 l18 -16 18 16 v48
             h70 v-30 h60 v30 h90 v-24 h80 V260 H0 Z"
        />

        {/* Near layer: campus landmarks in Yale navy */}
        <g fill="#00356b">
          {/* Old Campus buildings with chimneys */}
          <path d="M0 260 V214 h40 v-12 h8 v12 h70 l20 -16 20 16 h60 v46 Z" />

          {/* Phelps Gate: tower with an arched passage */}
          <path d="M210 260 V170 l6 -10 v-8 h8 v8 l12 -14 12 14 v-8 h8 v8 l6 10 V260 h-22 v-34 a10 10 0 0 0 -20 0 v34 Z" />

          {/* Battell Chapel: steep roof and square tower */}
          <path d="M276 260 V206 l40 -30 40 30 V260 Z" />
          <path d="M356 260 V150 h6 v-10 h6 v10 h8 v-10 h6 v10 h6 V260 Z" />

          {/* Woolsey Hall rotunda dome */}
          <path d="M400 260 V200 h40 v-14 a42 42 0 0 1 84 0 v14 h40 V260 Z" />
          <rect x="478" y="132" width="8" height="14" />

          {/* Harkness Tower: tiered gothic tower with pinnacles */}
          <path
            d="M600 260 V150 h10 v-8 h6 v8 h12 v-8 h6 v8 h10 V112 h6 v-8 h4 v8 h10 v-8 h4 v8 h6 V150 h10 v-8 h6 v8 h12
               v-8 h6 v8 h10 V260 Z"
          />
          <path d="M638 112 V70 h6 v-8 h4 v8 h12 v-8 h4 v8 h6 V112 Z" />
          <path d="M646 70 V40 l7 -24 7 24 V70 Z" />
          <path d="M638 70 l-4 -14 4 0 Z M670 70 l4 -14 -4 0 Z" />

          {/* Branford & Saybrook courtyards */}
          <path d="M720 260 V196 h20 l10 -12 10 12 h50 l10 -12 10 12 h40 V260 Z" />

          {/* Sterling Memorial Library: long nave with central tower */}
          <path d="M880 260 V190 l30 -22 30 22 h120 l30 -22 30 22 V260 Z" />
          <path d="M970 190 V120 h6 v-10 h6 v10 h8 v-10 h6 v10 h8 v-10 h6 v10 h6 V190 Z" />
          <path d="M984 110 l11 -30 11 30 Z" />

          {/* Science Hill and residential colleges */}
          <path d="M1120 260 V204 h30 v-14 h10 v14 h60 l16 -14 16 14 h50 v-22 h12 v22 h40 v-18 h30 V260 Z" />
          <path d="M1300 260 V180 l8 -10 v-12 h10 v12 l8 10 V260 Z" />
          <path d="M1384 260 V210 h56 V260 Z" />
        </g>

        {/* Lit windows */}
        <g fill="#ffd36b" opacity=".85">
          <rect x="636" y="170" width="6" height="12" rx="3" />
          <rect x="652" y="170" width="6" height="12" rx="3" />
          <rect x="668" y="170" width="6" height="12" rx="3" />
          <rect x="652" y="86" width="6" height="12" rx="3" />
          <rect x="990" y="140" width="5" height="10" rx="2.5" />
          <rect x="1000" y="140" width="5" height="10" rx="2.5" />
          <rect x="910" y="210" width="5" height="9" rx="2" />
          <rect x="1050" y="210" width="5" height="9" rx="2" />
          <rect x="470" y="214" width="6" height="12" rx="3" />
          <rect x="488" y="214" width="6" height="12" rx="3" />
          <rect x="314" y="220" width="5" height="10" rx="2.5" />
        </g>
      </svg>
      <div className="skyline__caption">
        <strong>Campus Customs</strong>
        <span>Bulldog pride from New Haven, Connecticut</span>
      </div>
    </section>
  )
}
