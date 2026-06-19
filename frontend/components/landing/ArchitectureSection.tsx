import ChainBadge from './ChainBadge'
import TechStackCard from './TechStackCard'
import FormatBlock from './FormatBlock'

const chains = ['Ethereum', 'BNB Chain', 'Polygon', 'Arbitrum', 'Optimism', 'Base', 'Solana', 'Bitcoin']

/**
 * ArchitectureSection — Production-ready infrastructure section.
 * Left: headline + chain badges grid + tech stack card.
 * Right: FormatBlock (export engines + hardening).
 */
export default function ArchitectureSection() {
  return (
    <section id="infrastructure" className="relative z-10 py-24">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_1.2fr] gap-16">
          {/* Left column */}
          <div className="space-y-8">
            <div className="mono-badge text-xs inline-flex">
              PRODUCTION ARCHITECTURE
            </div>

            <h2 className="text-4xl lg:text-5xl font-bold text-main leading-tight">
              Production-ready<br />
              <span className="text-gradient">infrastructure.</span>
            </h2>

            <p className="text-muted text-lg leading-relaxed font-light">
              Sync across multiple block explorers, background scheduler for wallet 
              refreshes, non-blocking price oracle calls. Built for scale from day one.
            </p>

            {/* Chain badges — 2 rows of 4 */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {chains.map((chain) => (
                <ChainBadge key={chain} name={chain} />
              ))}
            </div>

            {/* Tech stack card */}
            <TechStackCard />
          </div>

          {/* Right column */}
          <div>
            <FormatBlock />
          </div>
        </div>
      </div>
    </section>
  )
}
