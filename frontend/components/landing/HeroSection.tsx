import Link from 'next/link'
import WalletCard from './WalletCard'
import TaxTerminal from './TaxTerminal'

/**
 * HeroSection — 2-column hero with left text + right dual cards.
 * Single column on mobile (<1024px). Cards stack vertically.
 */
export default function HeroSection() {
  return (
    <section className="relative z-10 min-h-[70vh] lg:min-h-[85vh] flex items-center pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-6 w-full">
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_1.1fr] gap-8 lg:gap-12 items-center">
          {/* Left column */}
          <div className="space-y-6 lg:space-y-8">
            <div className="mono-badge text-xs">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald inline-block" />
              CRYPTO TAX ENGINE · REST API · INDIA ITR VDA
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-[5rem] font-bold leading-[1.1] tracking-tight max-w-[540px]">
              <span className="text-gradient">
                India's crypto tax engine. For builders.
              </span>
            </h1>

            <p className="text-muted text-base sm:text-lg leading-relaxed max-w-[540px] font-light">
              A production-hardened FIFO/LIFO/HIFO calculation engine with REST API, 8-chain support, and India's only ITR Schedule VDA export. Built for developers, DeFi users, and high-net-worth portfolios.
            </p>

            <div className="flex flex-wrap gap-4">
              <Link href="/auth/signup" className="btn btn-primary">
                Generate Report
              </Link>
              <a href="#compliance" className="btn btn-outline">
                View Supported Chains
              </a>
            </div>
          </div>

          {/* Right column — stacked vertically on mobile */}
          <div className="flex flex-col items-center lg:items-end gap-6">
            <div className="w-full lg:w-auto flex justify-center lg:justify-end">
              <WalletCard />
            </div>
            <div className="w-full lg:w-auto flex justify-center lg:justify-end">
              <TaxTerminal />
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
