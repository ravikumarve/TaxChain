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
 * PricingSection — 3-column pricing matrix with Free / Starter / Pro cards.
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
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {plans.map((plan) => (
            <PricingCard key={plan.name} {...plan} />
          ))}
        </div>
      </div>
    </section>
  )
}
