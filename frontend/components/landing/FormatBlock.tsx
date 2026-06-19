const exportEngines = [
  { name: 'CSV Master', tier: 'Starter+', desc: 'Raw transaction-level data with all fields' },
  { name: 'PDF Summary', tier: 'Pro', desc: 'Professional report with methodology appendix' },
]

const jurisdictional = [
  { name: 'India ITR', code: 'VDA', tier: 'Pro', desc: 'Schedule VDA for direct ITR e-filing' },
  { name: 'US IRS 8949', code: '8949', tier: 'Starter+', desc: 'Short/long-term capital gains' },
  { name: 'UK HMRC', code: 'CGT', tier: 'Starter+', desc: 'Capital Gains Tax in GBP' },
  { name: 'Australia ATO', code: 'CGT', tier: 'Starter+', desc: 'Crypto with CGT discount' },
]

const hardening = [
  'HMAC-SHA256 webhook verification',
  'Rate limiting: 5 req/min on auth, 200ms on external APIs',
  'SQLAlchemy parameterized queries (SQLi immune)',
  'JWT access + refresh token rotation',
  'BCrypt password hashing (12 rounds)',
  'CORS whitelist restricted to production domain',
]

/**
 * FormatBlock — Right column of the Architecture section.
 * Shows export engines, jurisdictional formats, and system hardening.
 */
export default function FormatBlock() {
  return (
    <div className="space-y-8">
      {/* Export Engines */}
      <div>
        <div className="font-mono text-xs tracking-widest text-indigo-400 uppercase mb-4">
          Export Engines
        </div>
        <div className="space-y-3">
          {exportEngines.map((e) => (
            <div key={e.name} className="bg-void/40 rounded-lg p-4 border border-border-dim">
              <div className="flex items-center gap-2 mb-1">
                <span className="font-mono text-emerald text-sm">{e.name}</span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded border border-border-dim text-faint">
                  {e.tier}
                </span>
              </div>
              <p className="text-faint text-xs">{e.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Jurisdictional Formats */}
      <div>
        <div className="font-mono text-xs tracking-widest text-indigo-400 uppercase mb-4">
          Jurisdictional Formats
        </div>
        <div className="space-y-3">
          {jurisdictional.map((j) => (
            <div key={j.name} className="flex items-center justify-between bg-void/40 rounded-lg p-4 border border-border-dim">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-emerald text-xs">{j.code}</span>
                  <span className="text-sm text-main">{j.name}</span>
                </div>
                <p className="text-faint text-xs mt-0.5">{j.desc}</p>
              </div>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded border border-border-dim text-faint shrink-0">
                {j.tier}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* System Hardening */}
      <div>
        <div className="font-mono text-xs tracking-widest text-emerald uppercase mb-4">
          ✓ System Hardening
        </div>
        <div className="space-y-2">
          {hardening.map((h) => (
            <div key={h} className="flex items-center gap-2 text-xs text-muted">
              <span className="text-emerald shrink-0">✓</span>
              {h}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
