'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'

interface MoverItem {
  token_symbol: string
  pnl_usd: number
  pnl_percent: number
  chain: string
}

interface TopMoversProps {
  movers: MoverItem[]
}

const CHAIN_DOT_COLORS: Record<string, string> = {
  eth: '#627EEA',
  bnb: '#F3BA2F',
  polygon: '#8247E5',
  sol: '#9945FF',
  arbitrum: '#28A0F0',
  optimism: '#FF0420',
  base: '#0052FF',
  btc: '#F7931A',
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)
}

function MoverRow({ item }: { item: MoverItem }) {
  const isGainer = item.pnl_usd >= 0
  const dotColor = CHAIN_DOT_COLORS[item.chain] || '#94a3b8'

  return (
    <div className="flex items-center justify-between py-2.5 border-b border-border-dim last:border-0">
      <div className="flex items-center gap-2.5">
        <span
          className="w-2 h-2 rounded-full flex-shrink-0"
          style={{ backgroundColor: dotColor }}
        />
        <div>
          <p className="text-sm font-medium text-main">{item.token_symbol}</p>
          <p className="text-xs text-faint uppercase" style={{ color: dotColor }}>
            {item.chain}
          </p>
        </div>
      </div>
      <div className={`text-right ${isGainer ? 'text-gain' : 'text-loss'}`}>
        <p className="text-sm font-mono font-medium">
          {isGainer ? '+' : ''}{formatCurrency(item.pnl_usd)}
        </p>
        <p className="text-xs">
          {isGainer ? '+' : ''}{item.pnl_percent.toFixed(1)}%
        </p>
      </div>
    </div>
  )
}

export function TopMovers({ movers }: TopMoversProps) {
  const gainers = movers.filter((m) => m.pnl_usd >= 0).sort((a, b) => b.pnl_usd - a.pnl_usd)
  const losers = movers.filter((m) => m.pnl_usd < 0).sort((a, b) => a.pnl_usd - b.pnl_usd)

  if (!movers.length) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card className="bg-panel border-border-dim">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gain">
              Top Gainers
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-faint text-center py-4">No data yet</p>
          </CardContent>
        </Card>
        <Card className="bg-panel border-border-dim">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-loss">
              Top Losers
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-faint text-center py-4">No data yet</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      {/* Gainers */}
      <Card className="bg-panel border-border-dim">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-gain">
            Top Gainers
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          {gainers.length === 0 ? (
            <p className="text-xs text-faint text-center py-4">No gainers</p>
          ) : (
            gainers.slice(0, 4).map((item, i) => (
              <MoverRow key={`gainer-${i}`} item={item} />
            ))
          )}
        </CardContent>
      </Card>

      {/* Losers */}
      <Card className="bg-panel border-border-dim">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-loss">
            Top Losers
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          {losers.length === 0 ? (
            <p className="text-xs text-faint text-center py-4">No losers</p>
          ) : (
            losers.slice(0, 4).map((item, i) => (
              <MoverRow key={`loser-${i}`} item={item} />
            ))
          )}
        </CardContent>
      </Card>
    </div>
  )
}
