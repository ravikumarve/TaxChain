/**
 * TrustStrip — Legal disclaimer + trust signals strip.
 * Full-width bar just above the footer.
 * Left: security badges. Right: disclaimer.
 */
export default function TrustStrip() {
  return (
    <div className="relative z-10 bg-surface/80 border-t border-border-dim">
      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="flex flex-col lg:flex-row items-center justify-between gap-4 lg:gap-8">
          {/* Left — Trust badges */}
          <div className="flex flex-wrap items-center justify-center lg:justify-start gap-5 text-xs">
            <span className="flex items-center gap-1.5 text-muted font-mono tracking-wide">
              <span className="text-indigo-400 text-sm">&#x1f512;</span>
              Read-only &mdash; keys never stored
            </span>
            <span className="flex items-center gap-1.5 text-muted font-mono tracking-wide">
              <span className="text-indigo-400 text-sm">&#x26a1;</span>
              Decimal precision throughout
            </span>
            <span className="flex items-center gap-1.5 text-muted font-mono tracking-wide">
              <span className="text-indigo-400 text-sm">&#x1f6e1;&#xfe0f;</span>
              HMAC-SHA256 signed webhooks
            </span>
          </div>

          {/* Right — Disclaimer */}
          <p className="text-faint text-[11px] leading-relaxed italic text-center lg:text-right max-w-lg">
            TaxChain provides tax calculation tools for informational purposes only.
            This is not financial or legal advice. Consult a qualified CA or tax
            professional before filing.
          </p>
        </div>
      </div>
    </div>
  )
}
