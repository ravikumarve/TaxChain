'use client'

import { useState } from 'react'

const logLines = [
  { time: '00:00:04.829', level: 'SYNC', msg: 'Fetching tx for 0x1a2b...3c4d' },
  { time: '00:00:07.112', level: 'ENGINE', msg: 'FIFO lot match: BUY 0.5 ETH @ $3,420.10' },
  { time: '00:00:09.443', level: 'MATCH', msg: 'SELL 0.3 ETH → matched with lot #8721' },
  { time: '00:00:11.087', level: 'PRICING', msg: 'Oracle: EUR/USD 1.0823, GBP/USD 1.2650' },
  { time: '00:00:14.201', level: 'SUCCESS', msg: 'Schedule VDA generated for FY 2025-26' },
]

const levelColors: Record<string, string> = {
  SUCCESS: 'text-emerald',
  SYNC: 'text-indigo-400',
  ENGINE: 'text-indigo-300',
  MATCH: 'text-blue-400',
  PRICING: 'text-muted',
}

/**
 * TaxTerminal — Glass card with FIFO engine terminal log.
 * Fixed width on desktop (460px), full-width on mobile with no rotation.
 */
export default function TaxTerminal() {
  const [hovered, setHovered] = useState(false)

  return (
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      className={`glass-pane p-5 cursor-default transition-all duration-[600ms] ease-[cubic-bezier(0.16,1,0.3,1)] ${
        hovered ? 'border-border-glow' : ''
      }`}
      style={{
        width: 'clamp(280px, 90vw, 460px)',
        transform: hovered
          ? 'rotate(0deg) translateY(-10px)'
          : 'rotate(0deg) translateY(0px)',
      }}
    >
      <div className="flex items-center gap-3 mb-5">
        <div className="flex gap-1.5 shrink-0">
          <span className="w-2.5 h-2.5 rounded-full bg-loss" />
          <span className="w-2.5 h-2.5 rounded-full bg-yellow-500" />
          <span className="w-2.5 h-2.5 rounded-full bg-emerald" />
        </div>
        <span className="font-mono text-[10px] tracking-widest text-muted uppercase">
          Tax Engine — FIFO v2.1.4
        </span>
      </div>
      <div className="font-mono space-y-2">
        {logLines.map((line, i) => (
          <div key={i} className="flex items-start gap-1.5 sm:gap-2 text-[10px] sm:text-[11px] leading-5">
            <span className="text-faint shrink-0 w-14 hidden sm:inline">{line.time}</span>
            <span className={`tracking-wider uppercase whitespace-nowrap shrink-0 ${levelColors[line.level] || 'text-muted'}`}>
              [{line.level}]
            </span>
            <span className="text-main/80 break-words min-w-0 leading-snug">{line.msg}</span>
          </div>
        ))}
        <div className="flex items-center gap-2 text-[11px] text-emerald mt-3 pt-3 border-t border-border-dim">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald animate-pulse shrink-0" />
          ENGINE RUNNING — 6 WATCHERS
        </div>
      </div>
    </div>
  )
}
