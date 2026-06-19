'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'

/**
 * Navbar — Scroll-aware glassmorphism navigation.
 * Transparent at top → bg-void/80 + backdrop-blur when scrolled.
 * Mono uppercase links, mobile hamburger menu.
 */
export default function Navbar() {
  const [scrolled, setScrolled] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 40)
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
        scrolled
          ? 'bg-void/80 backdrop-blur-2xl border-b border-border-dim'
          : 'bg-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-3 text-sm">
          <span className="inline-flex items-center justify-center w-8 h-8 bg-indigo-500/20 border border-indigo-500/40 rounded text-indigo-300 font-bold text-xs">
            #TC
          </span>
          <span className="font-ui font-semibold tracking-tight text-main">TaxChain</span>
        </Link>

        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-8">
          <a
            href="#compliance"
            className="font-mono text-xs tracking-widest text-muted hover:text-main transition-colors uppercase"
          >
            Compliance
          </a>
          <a
            href="#infrastructure"
            className="font-mono text-xs tracking-widest text-muted hover:text-main transition-colors uppercase"
          >
            Infrastructure
          </a>
          <a
            href="#pricing"
            className="font-mono text-xs tracking-widest text-muted hover:text-main transition-colors uppercase"
          >
            Pricing
          </a>
        </nav>

        {/* Desktop Actions */}
        <div className="hidden md:flex items-center gap-4">
          <a
            href="https://github.com/ravikumarve/TaxChain"
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-outline text-xs py-2 px-4"
          >
            GitHub
          </a>
          <Link
            href="/auth/login"
            className="btn btn-primary text-xs py-2 px-4"
          >
            Connect Wallet
          </Link>
        </div>

        {/* Mobile hamburger */}
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="md:hidden flex flex-col gap-1.5 p-2"
          aria-label="Toggle menu"
        >
          <span className={`block w-5 h-px bg-muted transition-all ${mobileOpen ? 'rotate-45 translate-y-[3px]' : ''}`} />
          <span className={`block w-5 h-px bg-muted transition-all ${mobileOpen ? 'opacity-0' : ''}`} />
          <span className={`block w-5 h-px bg-muted transition-all ${mobileOpen ? '-rotate-45 -translate-y-[3px]' : ''}`} />
        </button>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden bg-panel border-t border-border-dim px-6 py-6 space-y-4">
          <a href="#compliance" onClick={() => setMobileOpen(false)} className="block font-mono text-xs tracking-widest text-muted hover:text-main uppercase">Compliance</a>
          <a href="#infrastructure" onClick={() => setMobileOpen(false)} className="block font-mono text-xs tracking-widest text-muted hover:text-main uppercase">Infrastructure</a>
          <a href="#pricing" onClick={() => setMobileOpen(false)} className="block font-mono text-xs tracking-widest text-muted hover:text-main uppercase">Pricing</a>
          <hr className="border-border-dim" />
          <Link href="/auth/login" onClick={() => setMobileOpen(false)} className="block btn btn-primary text-xs text-center">Connect Wallet</Link>
        </div>
      )}
    </header>
  )
}
