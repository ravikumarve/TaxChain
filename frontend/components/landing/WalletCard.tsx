'use client'

import { useState } from 'react'

const wallets = [
  { chain: 'E', color: 'text-[#627EEA]', label: 'Ethereum', address: '0x1a2b...3c4d', synced: true },
  { chain: 'B', color: 'text-[#F3BA2F]', label: 'BNB Chain', address: '0x5e6f...7g8h', synced: true },
  { chain: 'P', color: 'text-[#8247E5]', label: 'Polygon', address: '0x9i0j...1k2l', synced: false },
]

/**
 * WalletCard — Left glass card in hero dual viewport.
 * Shows 3 wallet previews with chain-colored badges and sync status.
 * Transforms -3deg at rest → 0deg + lift on hover.
 */
export default function WalletCard() {
  const [hovered, setHovered] = useState(false)

  return (
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      className={`glass-pane p-5 cursor-default transition-all duration-[600ms] ease-[cubic-bezier(0.16,1,0.3,1)] ${
        hovered ? 'border-border-glow' : ''
      }`}
      style={{
        width: 280,
        transform: hovered
          ? 'rotate(0deg) translateY(-10px)'
          : 'rotate(-3deg) translateY(0px)',
      }}
    >
      <div className="font-mono text-[10px] tracking-widest text-muted uppercase mb-4">
        Connected Wallets
      </div>
      <div className="space-y-3">
        {wallets.map((w) => (
          <div key={w.chain} className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className={`font-mono text-sm font-bold ${w.color}`}>{w.chain}</span>
              <div>
                <div className="text-xs text-main font-medium">{w.label}</div>
                <div className="font-mono text-[10px] text-faint">{w.address}</div>
              </div>
            </div>
            <span
              className={`text-[10px] font-mono ${
                w.synced ? 'text-emerald' : 'text-faint'
              }`}
            >
              ● {w.synced ? 'Synced' : 'Pending'}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
