'use client'

import { useState } from 'react'

const codeBlock = `POST /api/reports/tax-summary
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "wallet": "0x4A9...b2E",
  "chain": "ethereum",
  "method": "HIFO",
  "currency": "INR",
  "tax_year": "2024-25",
  "format": "itr_vda"
}

→ 200 OK
{
  "total_gains": 284500.00,
  "total_losses": 42300.00,
  "net_taxable": 242200.00,
  "currency": "INR",
  "itr_vda_ready": true,
  "lots_processed": 1402,
  "method_used": "HIFO"
}`

/**
 * ApiSection — Developer-focused API showcase.
 * Left: 3 feature pills. Right: JSON request/response code block.
 * Inserted between Compliance and Infrastructure sections.
 */
export default function ApiSection() {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(codeBlock)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <section id="api" className="relative z-10 py-24">
      <div className="max-w-7xl mx-auto px-6">
        {/* Section header */}
        <div className="mb-16 text-center">
          <div className="mono-badge text-xs mb-6 inline-flex">
            DEVELOPER API
          </div>
          <h2 className="text-4xl lg:text-5xl font-bold text-main mb-4">
            Tax calculation.<br />
            <span className="text-gradient">As an API.</span>
          </h2>
          <p className="text-muted text-lg max-w-2xl mx-auto font-light">
            Integrate TaxChain&apos;s engine into your wallet, exchange, or fintech product.
          </p>
        </div>

        {/* 2-column grid */}
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_1.3fr] gap-12 lg:gap-16 items-start">
          {/* Left side — 3 feature pills */}
          <div className="space-y-6">
            <div className="flex items-start gap-4 bg-surface/50 border border-border-dim rounded-xl p-5 hover:border-indigo-500/30 transition-colors">
              <span className="inline-flex items-center justify-center w-10 h-10 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 font-mono text-sm shrink-0">
                01
              </span>
              <div>
                <h3 className="text-sm font-semibold text-main font-ui">REST API</h3>
                <p className="text-xs text-muted mt-1 leading-relaxed">
                  FastAPI-powered endpoints with JSON responses, auto-generated OpenAPI docs at <code className="text-indigo-400 text-[11px]">/docs</code>, and bearer token auth.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4 bg-surface/50 border border-border-dim rounded-xl p-5 hover:border-indigo-500/30 transition-colors">
              <span className="inline-flex items-center justify-center w-10 h-10 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 font-mono text-sm shrink-0">
                02
              </span>
              <div>
                <h3 className="text-sm font-semibold text-main font-ui">ITR VDA Endpoint</h3>
                <p className="text-xs text-muted mt-1 leading-relaxed">
                  India&apos;s Schedule VDA as structured JSON — ready for direct ITR e-filing integration. No CSV parsing needed.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4 bg-surface/50 border border-border-dim rounded-xl p-5 hover:border-indigo-500/30 transition-colors">
              <span className="inline-flex items-center justify-center w-10 h-10 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 font-mono text-sm shrink-0">
                03
              </span>
              <div>
                <h3 className="text-sm font-semibold text-main font-ui">FIFO / HIFO / LIFO</h3>
                <p className="text-xs text-muted mt-1 leading-relaxed">
                  Method selectable per request. Switch between all four cost basis calculators with a single query parameter.
                </p>
              </div>
            </div>
          </div>

          {/* Right side — Code block */}
          <div className="relative">
            <div
              className="glass-pane p-5 font-mono text-[11px] leading-6 overflow-x-auto"
              style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}
            >
              {/* Terminal header */}
              <div className="flex items-center gap-3 mb-4 pb-4 border-b border-border-dim">
                <div className="flex gap-1.5 shrink-0">
                  <span className="w-2.5 h-2.5 rounded-full bg-loss" />
                  <span className="w-2.5 h-2.5 rounded-full bg-yellow-500" />
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald" />
                </div>
                <span className="font-mono text-[10px] tracking-widest text-faint uppercase flex-1">
                  API Playground — cURL
                </span>
                <button
                  onClick={handleCopy}
                  className="text-[10px] tracking-wider text-muted hover:text-main transition-colors uppercase font-mono"
                >
                  {copied ? 'Copied!' : 'Copy'}
                </button>
              </div>

              {/* Code lines with syntax highlighting */}
              <div className="space-y-0">
                <span className="text-emerald">POST</span>
                <span className="text-main/80"> /api/reports/tax-summary{'\n'}</span>
                <span className="text-faint">Authorization: Bearer </span>
                <span className="text-yellow-400/80">{'{api_key}'}</span>
                <span className="text-main/80">{'\n'}</span>
                <span className="text-faint">Content-Type: application/json</span>
                <span className="text-main/80">{'\n\n'}</span>
                <span className="text-faint">{'{'}{'\n'}</span>
                <span className="text-indigo-400/80">  "wallet"</span>
                <span className="text-main/80">: </span>
                <span className="text-emerald/80">"0x4A9...b2E"</span>
                <span className="text-main/80">,{'\n'}</span>
                <span className="text-indigo-400/80">  "chain"</span>
                <span className="text-main/80">: </span>
                <span className="text-emerald/80">"ethereum"</span>
                <span className="text-main/80">,{'\n'}</span>
                <span className="text-indigo-400/80">  "method"</span>
                <span className="text-main/80">: </span>
                <span className="text-emerald/80">"HIFO"</span>
                <span className="text-main/80">,{'\n'}</span>
                <span className="text-indigo-400/80">  "currency"</span>
                <span className="text-main/80">: </span>
                <span className="text-emerald/80">"INR"</span>
                <span className="text-main/80">,{'\n'}</span>
                <span className="text-indigo-400/80">  "tax_year"</span>
                <span className="text-main/80">: </span>
                <span className="text-emerald/80">"2024-25"</span>
                <span className="text-main/80">,{'\n'}</span>
                <span className="text-indigo-400/80">  "format"</span>
                <span className="text-main/80">: </span>
                <span className="text-emerald/80">"itr_vda"</span>
                <span className="text-main/80">{'\n'}{'}'}</span>
                <span className="text-main/80">{'\n\n'}</span>
                <span className="text-faint">→ 200 OK{'\n'}</span>
                <span className="text-faint">{'{'}{'\n'}</span>
                <span className="text-gain">  "total_gains"</span>
                <span className="text-main/80">: </span>
                <span className="text-yellow-400/80">284500.00</span>
                <span className="text-main/80">,{'\n'}</span>
                <span className="text-loss">  "total_losses"</span>
                <span className="text-main/80">: </span>
                <span className="text-yellow-400/80">42300.00</span>
                <span className="text-main/80">,{'\n'}</span>
                <span className="text-cyan-400/80">  "net_taxable"</span>
                <span className="text-main/80">: </span>
                <span className="text-yellow-400/80">242200.00</span>
                <span className="text-main/80">,{'\n'}</span>
                <span className="text-indigo-400/80">  "currency"</span>
                <span className="text-main/80">: </span>
                <span className="text-emerald/80">"INR"</span>
                <span className="text-main/80">,{'\n'}</span>
                <span className="text-indigo-400/80">  "itr_vda_ready"</span>
                <span className="text-main/80">: </span>
                <span className="text-amber-400/80">true</span>
                <span className="text-main/80">,{'\n'}</span>
                <span className="text-indigo-400/80">  "lots_processed"</span>
                <span className="text-main/80">: </span>
                <span className="text-yellow-400/80">1402</span>
                <span className="text-main/80">,{'\n'}</span>
                <span className="text-indigo-400/80">  "method_used"</span>
                <span className="text-main/80">: </span>
                <span className="text-emerald/80">"HIFO"</span>
                <span className="text-main/80">{'\n'}{'}'}</span>
              </div>
            </div>

            {/* Bottom note */}
            <p className="mt-4 text-center font-mono text-[10px] tracking-wider text-faint uppercase">
              Available on Pro plan · Rate limited at 1000 req/day · HMAC-signed webhooks
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
