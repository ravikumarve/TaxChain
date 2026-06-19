'use client'

const chainConfig: Record<string, { name: string; dot: string }> = {
  eth: { name: 'Ethereum', dot: '#627EEA' },
  bnb: { name: 'BNB Chain', dot: '#F3BA2F' },
  polygon: { name: 'Polygon', dot: '#8247E5' },
  sol: { name: 'Solana', dot: '#9945FF' },
  arbitrum: { name: 'Arbitrum', dot: '#28A0F0' },
  optimism: { name: 'Optimism', dot: '#FF0420' },
  base: { name: 'Base', dot: '#0052FF' },
  btc: { name: 'Bitcoin', dot: '#F7931A' },
}

interface ChainBadgeProps {
  chain: string
  className?: string
}

export function ChainBadge({ chain, className = '' }: ChainBadgeProps) {
  const config = chainConfig[chain] || { name: chain, dot: '#94a3b8' }

  return (
    <span className={`inline-flex items-center gap-1.5 text-xs font-mono ${className}`}>
      <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: config.dot }} />
      {config.name}
    </span>
  )
}
