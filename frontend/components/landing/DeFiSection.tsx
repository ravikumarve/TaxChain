/**
 * DeFiSection — Dedicated DeFi support showcase.
 * Shows 8 DeFi transaction types with correct tax treatment,
 * and a protocol badge row.
 * Inserted between Infrastructure and Pricing sections.
 */
export default function DeFiSection() {
  const leftItems = [
    {
      name: 'LP Deposit',
      protocols: 'Uniswap V2/V3',
      tax: 'Not taxable',
      taxClass: 'text-emerald',
      desc: 'Providing liquidity is not a disposal event. LP tokens represent proportional ownership.',
    },
    {
      name: 'LP Withdraw',
      protocols: 'Uniswap V2/V3',
      tax: 'Taxable',
      taxClass: 'text-amber-400',
      desc: 'Returning LP tokens for underlying assets triggers a realized gain/loss.',
    },
    {
      name: 'Yield Farm',
      protocols: 'Curve · Convex',
      tax: 'Not taxable',
      taxClass: 'text-emerald',
      desc: 'Staking LP tokens in a farm is not taxable on deposit. Rewards are taxable when claimed.',
    },
    {
      name: 'Staking Rewards',
      protocols: 'Lido · Rocket Pool',
      tax: 'Taxable as income',
      taxClass: 'text-amber-400',
      desc: 'Staking rewards are taxable as income at fair market value on receipt.',
    },
  ]

  const rightItems = [
    {
      name: 'Borrow',
      protocols: 'AAVE · Compound',
      tax: 'Not taxable',
      taxClass: 'text-emerald',
      desc: 'Taking out a collateralized loan is not a taxable event. Repaying principal has no tax impact.',
    },
    {
      name: 'Liquidation',
      protocols: 'AAVE · Compound',
      tax: 'Taxable event',
      taxClass: 'text-rose-400',
      desc: 'Liquidation is treated as a forced disposal. Gains/losses are realized immediately.',
    },
    {
      name: 'Airdrop',
      protocols: 'Arbitrum · Optimism',
      tax: 'Taxable as income',
      taxClass: 'text-amber-400',
      desc: 'Airdropped tokens are taxable as income at FMV on receipt. Subsequent sale is a separate disposal.',
    },
    {
      name: 'DEX Trade',
      protocols: 'PancakeSwap · Camelot',
      tax: 'Taxable gain/loss',
      taxClass: 'text-rose-400',
      desc: 'Swapping one token for another is a disposal event. Gain/loss = FMV of received − cost basis of sent.',
    },
  ]

  const protocols = [
    'Uniswap V2',
    'Uniswap V3',
    'AAVE V2',
    'AAVE V3',
    'Compound',
    'Curve',
    'Lido',
    'PancakeSwap',
    'Camelot',
    'Velodrome',
  ]

  return (
    <section id="defi" className="relative z-10 py-24">
      <div className="max-w-7xl mx-auto px-6">
        {/* Section header */}
        <div className="mb-16 text-center">
          <div className="mono-badge text-xs mb-6 inline-flex">
            DEFI-NATIVE TAX ENGINE
          </div>
          <h2 className="text-4xl lg:text-5xl font-bold text-main mb-4">
            DeFi-native. Not an <br />
            <span className="text-gradient">afterthought.</span>
          </h2>
          <p className="text-muted text-lg max-w-2xl mx-auto font-light">
            Most tax tools treat DeFi as &quot;other&quot;. TaxChain understands LP
            deposits, yield farms, liquidations, and staking rewards — with
            correct tax treatment for each.
          </p>
        </div>

        {/* 2-column grid of DeFi actions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left column */}
          <div className="space-y-5">
            {leftItems.map((item, i) => (
              <DeFiActionCard key={i} {...item} />
            ))}
          </div>

          {/* Right column */}
          <div className="space-y-5">
            {rightItems.map((item, i) => (
              <DeFiActionCard key={i} {...item} />
            ))}
          </div>
        </div>

        {/* Protocol badges row */}
        <div className="mt-16 text-center">
          <p className="font-mono text-[10px] tracking-widest text-faint uppercase mb-5">
            Supported Protocols
          </p>
          <div className="flex flex-wrap justify-center gap-2.5">
            {protocols.map((p) => (
              <span key={p} className="chain-badge text-xs">
                {p}
              </span>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}

/* ── Single DeFi action card ──────────────────────────────────── */

interface DeFiActionCardProps {
  name: string
  protocols: string
  tax: string
  taxClass: string
  desc: string
}

function DeFiActionCard({ name, protocols, tax, taxClass, desc }: DeFiActionCardProps) {
  return (
    <div className="glass-pane !transform-none p-5 border border-border-dim hover:!border-indigo-500/30 transition-colors">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="flex items-center gap-3 mb-1">
            <h3 className="text-sm font-semibold text-main">{name}</h3>
            <span className="text-[10px] font-mono text-faint tracking-wider uppercase shrink-0">
              {protocols}
            </span>
          </div>
          <p className="text-xs text-muted leading-relaxed">{desc}</p>
        </div>
        <span
          className={`shrink-0 font-mono text-[10px] tracking-wider uppercase px-2.5 py-1 rounded-full border ${taxClass} border-current/20 bg-current/5`}
        >
          {tax}
        </span>
      </div>
    </div>
  )
}
