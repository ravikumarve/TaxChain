import Link from 'next/link'

/**
 * Footer — 4-column footer with brand, platform, developers, company.
 * Bottom bar with copyright + systems operational indicator.
 */
export default function Footer() {
  return (
    <footer className="relative z-10 bg-surface border-t border-border-dim">
      <div className="max-w-7xl mx-auto px-6 py-16">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-[2fr_1fr_1fr_1fr] gap-12">
          {/* Brand column */}
          <div>
            <Link href="/" className="flex items-center gap-3 text-sm mb-4">
              <span className="inline-flex items-center justify-center w-8 h-8 bg-indigo-500/20 border border-indigo-500/40 rounded text-indigo-300 font-bold text-xs">
                #TC
              </span>
              <span className="font-ui font-semibold tracking-tight text-main">TaxChain</span>
            </Link>
            <p className="text-muted text-sm leading-relaxed max-w-xs">
              Multi-wallet, multi-chain crypto tax calculations and portfolio tracking.
              Built for individuals, trusted by professionals.
            </p>
          </div>

          {/* Platform */}
          <div>
            <h4 className="font-mono text-[10px] tracking-widest text-muted uppercase mb-4">
              Platform
            </h4>
            <ul className="space-y-2 text-sm">
              <li><a href="#compliance" className="text-muted hover:text-main transition-colors">Compliance</a></li>
              <li><a href="#infrastructure" className="text-muted hover:text-main transition-colors">Infrastructure</a></li>
              <li><a href="#pricing" className="text-muted hover:text-main transition-colors">Pricing</a></li>
            </ul>
          </div>

          {/* Developers */}
          <div>
            <h4 className="font-mono text-[10px] tracking-widest text-muted uppercase mb-4">
              Developers
            </h4>
            <ul className="space-y-2 text-sm">
              <li><a href="#api" className="text-muted hover:text-main transition-colors">API Reference</a></li>
              <li><a href="https://github.com/ravikumarve/TaxChain" target="_blank" rel="noopener noreferrer" className="text-muted hover:text-main transition-colors">GitHub Repository</a></li>
              <li><a href="https://github.com/ravikumarve/TaxChain/issues" target="_blank" rel="noopener noreferrer" className="text-muted hover:text-main transition-colors">Issue Tracker</a></li>
              <li><a href="https://github.com/ravikumarve/TaxChain/discussions" target="_blank" rel="noopener noreferrer" className="text-muted hover:text-main transition-colors">Discussions</a></li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h4 className="font-mono text-[10px] tracking-widest text-muted uppercase mb-4">
              Company
            </h4>
            <ul className="space-y-2 text-sm">
              <li><a href="#" className="text-muted hover:text-main transition-colors">About</a></li>
              <li><a href="#" className="text-muted hover:text-main transition-colors">Privacy</a></li>
              <li><a href="#" className="text-muted hover:text-main transition-colors">Terms</a></li>
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-12 pt-6 border-t border-border-dim flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-faint text-xs font-mono">
            &copy; 2026 TAXCHAIN &middot; A <span className="text-indigo-400">0xMATRIX</span> PRODUCT
          </p>
          <div className="flex items-center gap-2 text-xs text-emerald font-mono">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald inline-block animate-pulse" />
            SYSTEMS OPERATIONAL
          </div>
        </div>
      </div>
    </footer>
  )
}
