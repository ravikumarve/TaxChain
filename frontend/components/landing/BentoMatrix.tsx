import BentoNode from './BentoNode'

const formats = [
  { name: 'IRS 8949', tier: 'Starter+', desc: 'US IRS Form 8949 with short/long-term classification' },
  { name: 'HMRC', tier: 'Starter+', desc: 'UK HMRC Capital Gains in GBP' },
  { name: 'ATO', tier: 'Starter+', desc: 'Australian ATO Crypto with CGT discount' },
  { name: 'ITR VDA', tier: 'Pro', desc: 'India Schedule VDA for direct ITR filing' },
]

/**
 * BentoMatrix — 12-column bento grid for the Compliance section.
 * 4 nodes spanning different column widths for a dynamic layout.
 */
export default function BentoMatrix() {
  return (
    <section id="compliance" className="relative z-10 py-24">
      <div className="max-w-7xl mx-auto px-6">
        {/* Section header */}
        <div className="mb-16 text-center">
          <div className="mono-badge text-xs mb-6 inline-flex">
            TAX-GRADE COMPLIANCE
          </div>
          <h2 className="text-4xl lg:text-5xl font-bold text-main mb-4">
            Enterprise compliance,<br />
            <span className="text-gradient">developer velocity.</span>
          </h2>
          <p className="text-muted text-lg max-w-2xl mx-auto font-light">
            From multi-method cost basis to jurisdiction-specific tax exports — TaxChain 
            handles the complexity so you don&apos;t have to.
          </p>
        </div>

        {/* Bento grid */}
        <div className="grid grid-cols-12 gap-5">
          {/* 01 — Global Jurisdictions (span-8) */}
          <BentoNode span={8} index="01" label="GLOBAL JURISDICTIONS" title="Official Tax Formats">
            <p>Generate ready-to-file tax reports in 4 jurisdiction-specific formats:</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-4">
              {formats.map((f) => (
                <div key={f.name} className="flex items-start gap-3 bg-void/40 rounded-lg p-3 border border-border-dim">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-emerald text-xs">{f.name}</span>
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded border border-border-dim text-faint">
                        {f.tier}
                      </span>
                    </div>
                    <div className="text-faint text-xs mt-1">{f.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </BentoNode>

          {/* 02 — Methodology (span-4) */}
          <BentoNode span={4} index="02" label="METHODOLOGY" title="4 Accounting Methods">
            <p>Switch between FIFO, LIFO, HIFO, and Average Cost at any time. All 6 export formats recalculate instantly. HIFO minimizes your taxable gains — unique to TaxChain.</p>
            <div className="flex flex-wrap gap-2 mt-4">
              <span className="chain-badge text-xs text-indigo-300 border-indigo-500/30">FIFO</span>
              <span className="chain-badge text-xs text-indigo-300 border-indigo-500/30">LIFO</span>
              <span className="chain-badge text-xs text-gain border-emerald/30">HIFO</span>
              <span className="chain-badge text-xs text-indigo-300 border-indigo-500/30">AVG COST</span>
            </div>
          </BentoNode>

          {/* 03 — Pricing Oracle (span-6) */}
          <BentoNode span={6} index="03" label="PRICING ORACLE" title="Multi-Currency Resolution">
            <p>Historical price data with automatic fallback, supporting 8 fiat currencies:</p>
            <div className="flex flex-wrap gap-2 mt-4">
              {['USD', 'INR', 'EUR', 'GBP', 'AUD', 'SGD', 'CAD', 'JPY'].map((c) => (
                <span key={c} className="chain-badge text-xs">{c}</span>
              ))}
            </div>
            <p className="text-faint text-xs mt-3">
              CoinGecko primary + open.er-api fallback. 10,000-entry LRU cache.
            </p>
          </BentoNode>

          {/* 04 — Zero Compromise (span-6) */}
          <BentoNode span={6} index="04" label="ZERO COMPROMISE" title="Read-Only Security">
            <p>We never store private keys. Wallet data is read-only, encrypted at rest and in transit.</p>
            <div className="grid grid-cols-2 gap-2 mt-4 text-xs">
              {[
                'HMAC-SHA256 webhooks',
                '5/min auth rate limit',
                'SQLAlchemy SQLi defense',
                'JWT with 60min expiry',
                'BCrypt password hashing',
                'CORS restricted to domain',
              ].map((item) => (
                <div key={item} className="flex items-center gap-2 text-muted">
                  <span className="text-emerald text-sm">✓</span>
                  {item}
                </div>
              ))}
            </div>
          </BentoNode>
        </div>
      </div>
    </section>
  )
}
