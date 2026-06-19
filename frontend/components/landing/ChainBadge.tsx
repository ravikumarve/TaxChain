interface ChainBadgeProps {
  name: string
}

const chainData: Record<string, { symbol: string; color: string }> = {
  Ethereum: { symbol: 'ETH', color: 'text-[#627EEA]' },
  'BNB Chain': { symbol: 'BNB', color: 'text-[#F3BA2F]' },
  Polygon: { symbol: 'POL', color: 'text-[#8247E5]' },
  Arbitrum: { symbol: 'ARB', color: 'text-[#28A0F0]' },
  Optimism: { symbol: 'OP', color: 'text-[#FF0420]' },
  Base: { symbol: 'BASE', color: 'text-[#0052FF]' },
  Solana: { symbol: 'SOL', color: 'text-[#9945FF]' },
  Bitcoin: { symbol: 'BTC', color: 'text-[#F7931A]' },
}

/**
 * ChainBadge — Single chain badge with colored symbol and name.
 * Used in the ArchitectureSection chain grid.
 */
export default function ChainBadge({ name }: ChainBadgeProps) {
  const data = chainData[name] || { symbol: '?', color: 'text-muted' }

  return (
    <div className="flex items-center gap-3 chain-badge">
      <span className={`font-mono text-sm font-bold ${data.color}`}>{data.symbol}</span>
      <span className="text-xs text-muted">{name}</span>
    </div>
  )
}
