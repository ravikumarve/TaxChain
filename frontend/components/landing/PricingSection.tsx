import PricingCard from './PricingCard'

const plans = [
  {
    name: 'Free',
    price: '$0',
    sub: 'Perfect for getting started',
    volume: 'TRIAL ACCESS',
    wallets: '1',
    chains: 'ETH only',
    csv: false,
    pdf: false,
    itr: false,
    irs: false,
    cta: 'Create Account',
  },
  {
    name: 'Starter',
    price: '$9',
    sub: 'For serious crypto investors',
    volume: 'EVM ESSENTIALS',
    wallets: '3',
    chains: 'ETH, BNB, Polygon, Arbitrum',
    csv: true,
    pdf: false,
    itr: false,
    irs: true,
    popular: true,
    cta: 'Select Starter',
  },
  {
    name: 'Pro',
    price: '$19',
    sub: 'Complete institutional solution',
    volume: 'INSTITUTIONAL ACCESS',
    wallets: 'Unlimited',
    chains: 'All 8 chains',
    csv: true,
    pdf: true,
    itr: true,
    irs: true,
    cta: 'Select Pro',
  },
]

/**
 * PricingSection — 4-column pricing matrix with Free / Starter / Pro / Enterprise cards.
 */
export default function PricingSection() {
  return (
    <section id="pricing" className="relative z-10 py-24">
      <div className="max-w-7xl mx-auto px-6">
        {/* Section header */}
        <div className="mb-16 text-center">
          <div className="mono-badge text-xs mb-6 inline-flex">
            SIMPLE PRICING
          </div>
          <h2 className="text-4xl lg:text-5xl font-bold text-main mb-4">
            Transparent pricing.<br />
            <span className="text-gradient">No hidden fees.</span>
          </h2>
          <p className="text-muted text-lg max-w-2xl mx-auto font-light">
            Start free. Upgrade when you need more wallets, chains, or export formats.
          </p>
        </div>

        {/* Pricing cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
          {plans.map((plan) => (
            <PricingCard key={plan.name} {...plan} />
          ))}

          {/* Enterprise card — separate because feature set is different */}
          <div className="price-card flex flex-col">
            <div>
              <h3 className="text-2xl font-bold text-main">Enterprise</h3>
              <div className="mt-4 mb-2">
                <span className="text-4xl font-bold text-main">Custom</span>
              </div>
              <p className="text-muted text-sm font-light">API ACCESS</p>
            </div>

            <div className="mt-2 mb-6">
              <div className="font-mono text-[10px] tracking-widest text-indigo-400 uppercase">
                EMBEDDED LICENSING
              </div>
            </div>

            {/* Feature list */}
            <div className="flex-1 space-y-3 text-sm">
              <EnterpriseFeature label="Unlimited API calls" />
              <EnterpriseFeature label="White-label tax engine" />
              <EnterpriseFeature label="ITR VDA as JSON API" />
              <EnterpriseFeature label="HMAC-signed webhooks" />
              <EnterpriseFeature label="Priority support + SLA" />
              <EnterpriseFeature label="Custom chain integrations" />
            </div>

            <a
              href="mailto:taxchain@example.com"
              className="btn btn-outline mt-8 w-full text-center"
            >
              Contact Us
            </a>
          </div>
        </div>

        {/* Enterprise note */}
        <p className="mt-10 text-center font-mono text-[10px] tracking-wider text-faint max-w-xl mx-auto leading-relaxed">
          Enterprise clients include crypto exchanges, wallets, and fintech platforms needing embedded tax calculation.
        </p>
      </div>
    </section>
  )
}

function EnterpriseFeature({ label }: { label: string }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-muted">{label}</span>
      <span className="text-emerald">✓</span>
    </div>
  )
}
