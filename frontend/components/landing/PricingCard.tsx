interface PricingCardProps {
  name: string
  price: string
  sub: string
  volume: string
  wallets: string
  chains: string
  csv: boolean
  pdf: boolean
  itr: boolean
  irs: boolean
  popular?: boolean
  cta: string
}

/**
 * PricingCard — Individual pricing plan card.
 * Has hover lift + glow. Popular variant has "MOST POPULAR" banner + gradient bg.
 */
export default function PricingCard({
  name, price, sub, volume, wallets, chains, csv, pdf, itr, irs, popular, cta,
}: PricingCardProps) {
  return (
    <div className={`price-card flex flex-col ${popular ? 'popular' : ''}`}>
      {popular && (
        <div className="absolute top-0 left-0 right-0 bg-indigo-600/90 text-white text-[10px] font-mono tracking-widest text-center py-2 uppercase">
          Most Popular
        </div>
      )}

      <div className={`${popular ? 'mt-6' : ''}`}>
        <h3 className="text-2xl font-bold text-main">{name}</h3>
        <div className="mt-4 mb-2">
          <span className="text-4xl font-bold text-main">{price}</span>
          {price !== '$0' && <span className="text-muted text-sm ml-1">/mo</span>}
        </div>
        <p className="text-muted text-sm font-light">{sub}</p>
      </div>

      <div className="mt-2 mb-6">
        <div className="font-mono text-[10px] tracking-widest text-indigo-400 uppercase">
          {volume}
        </div>
      </div>

      {/* Feature list */}
      <div className="flex-1 space-y-3 text-sm">
        <div className="flex items-center justify-between">
          <span className="text-muted">Wallets</span>
          <span className="text-main font-mono">{wallets}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-muted">Chains</span>
          <span className="text-main font-mono">{chains}</span>
        </div>
        <hr className="border-border-dim" />
        <FeatureRow label="CSV Export" enabled={csv} />
        <FeatureRow label="PDF Summary" enabled={pdf} />
        <FeatureRow label="ITR VDA (India)" enabled={itr} />
        <FeatureRow label="IRS / HMRC / ATO" enabled={irs} />
      </div>

      <a
        href="/auth/signup"
        className={`btn mt-8 w-full text-center ${popular ? 'btn-primary' : 'btn-outline'}`}
      >
        {cta}
      </a>
    </div>
  )
}

function FeatureRow({ label, enabled }: { label: string; enabled: boolean }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-muted">{label}</span>
      <span className={enabled ? 'text-emerald' : 'text-faint'}>
        {enabled ? '✓' : '—'}
      </span>
    </div>
  )
}
