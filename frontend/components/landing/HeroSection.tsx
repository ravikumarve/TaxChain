import Link from 'next/link'
import WalletCard from './WalletCard'
import TaxTerminal from './TaxTerminal'

/**
 * HeroSection — 2-column hero with left text + right dual viewport cards.
 * Left: mono badge, gradient headline, muted subtitle, dual CTAs.
 * Right: WalletCard (-3deg) + TaxTerminal (+2deg) with hover lift.
 */
export default function HeroSection() {
  return (
    <section className="relative z-10 min-h-[85vh] flex items-center pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-6 w-full">
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_1.1fr] gap-12 items-center">
          {/* Left column */}
          <div className="space-y-8">
            {/* Mono badge */}
            <div className="mono-badge text-xs">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald inline-block" />
              MULTI-WALLET, MULTI-CHAIN SAAS
            </div>

            {/* Headline */}
            <h1 className="text-5xl lg:text-[5rem] font-bold leading-[1.05] tracking-tight max-w-[540px]">
              <span className="text-gradient">
                Institutional-grade crypto tax engine.
              </span>
            </h1>

            {/* Subtitle */}
            <p className="text-muted text-lg leading-relaxed max-w-[540px] font-light">
              Connect your wallets. Let TaxChain handle FIFO cost basis,
              multi-currency conversion, and jurisdiction-specific tax format generation.
            </p>

            {/* CTAs */}
            <div className="flex flex-wrap gap-4">
              <Link
                href="/auth/signup"
                className="btn btn-primary"
              >
                Generate Report
              </Link>
              <a
                href="#compliance"
                className="btn btn-outline"
              >
                View Supported Chains
              </a>
            </div>
          </div>

          {/* Right column — dual viewport */}
          <div className="relative flex flex-col items-end gap-6 min-h-[400px] justify-center">
            <div className="self-start ml-8">
              <WalletCard />
            </div>
            <div className="self-end mr-4 -mt-16">
              <TaxTerminal />
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
