'use client'

interface ChainBadgeProps {
  chain: 'eth' | 'bnb' | 'polygon' | 'sol'
  className?: string
}

const chainConfig = {
  eth: {
    name: 'Ethereum',
    color: 'bg-chains-eth',
    textColor: 'text-white',
  },
  bnb: {
    name: 'BNB Chain',
    color: 'bg-chains-bnb',
    textColor: 'text-gray-900',
  },
  polygon: {
    name: 'Polygon',
    color: 'bg-chains-polygon',
    textColor: 'text-white',
  },
  sol: {
    name: 'Solana',
    color: 'bg-chains-sol',
    textColor: 'text-white',
  },
}

export function ChainBadge({ chain, className = '' }: ChainBadgeProps) {
  const config = chainConfig[chain]

  return (
    <span
      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${config.color} ${config.textColor} ${className}`}
    >
      <div className="w-2 h-2 rounded-full bg-white/30 mr-1" />
      {config.name}
    </span>
  )
}