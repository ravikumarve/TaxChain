'use client'

import { useState, useEffect } from 'react'
import { walletsApi } from '@/lib/api'

interface Wallet {
  id: string
  address: string
  chain: string
  label: string | null
  last_synced_at: string | null
  tx_count: number
  created_at: string
}

interface WalletListProps {
  refreshTrigger: number
}

export default function WalletList({ refreshTrigger }: WalletListProps) {
  const [wallets, setWallets] = useState<Wallet[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [syncingWallets, setSyncingWallets] = useState<Set<string>>(new Set())

  useEffect(() => { loadWallets() }, [refreshTrigger])

  const loadWallets = async () => {
    try {
      setLoading(true)
      const response = await walletsApi.list()
      setWallets(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load wallets')
    } finally { setLoading(false) }
  }

  const handleDelete = async (walletId: string) => {
    if (!confirm('Are you sure you want to delete this wallet? This will also remove all associated transactions.')) return
    try {
      await walletsApi.delete(walletId)
      setWallets(wallets.filter(w => w.id !== walletId))
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete wallet')
    }
  }

  const handleSync = async (walletId: string) => {
    try {
      setSyncingWallets(prev => new Set(prev).add(walletId))
      await walletsApi.sync(walletId)
      alert('Wallet sync started. It may take a few minutes to complete.')
      loadWallets()
    } catch (err: any) {
      alert(`Sync failed: ${err.response?.data?.detail || 'Unknown error'}`)
    } finally {
      setSyncingWallets(prev => {
        const newSet = new Set(prev)
        newSet.delete(walletId)
        return newSet
      })
    }
  }

  const getChainName = (chain: string) => {
    const names: Record<string, string> = {
      eth: 'Ethereum', bnb: 'BNB Chain', polygon: 'Polygon', sol: 'Solana',
      arbitrum: 'Arbitrum', optimism: 'Optimism', base: 'Base', btc: 'Bitcoin',
    }
    return names[chain] || chain
  }

  const chainDots: Record<string, string> = {
    eth: '#627EEA', bnb: '#F3BA2F', polygon: '#8247E5', sol: '#9945FF',
    arbitrum: '#28A0F0', optimism: '#FF0420', base: '#0052FF', btc: '#F7931A',
  }

  const getRelativeTime = (dateString: string) => {
    const diffMs = Date.now() - new Date(dateString).getTime()
    const mins = Math.floor(diffMs / 60000)
    const hrs = Math.floor(diffMs / 3600000)
    const days = Math.floor(diffMs / 86400000)
    if (mins < 1) return 'just now'
    if (mins < 60) return `${mins}m ago`
    if (hrs < 24) return `${hrs}h ago`
    if (days < 7) return `${days}d ago`
    return new Date(dateString).toLocaleDateString()
  }

  const formatAddress = (address: string) => `${address.slice(0, 8)}...${address.slice(-6)}`

  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map(i => (
          <div key={i} className="animate-pulse bg-surface rounded-xl p-5 h-20 border border-border-dim" />
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <div className="text-loss text-sm mb-2">{error}</div>
        <button onClick={loadWallets} className="text-indigo-400 hover:text-indigo-300 text-sm">Try Again</button>
      </div>
    )
  }

  if (wallets.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-muted mb-2">No wallets connected yet</div>
        <div className="text-faint text-sm">Add your first wallet to start tracking transactions</div>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {wallets.map(wallet => (
        <div key={wallet.id} className="bg-surface border border-border-dim rounded-xl p-5 hover:border-indigo-500/20 transition-colors">
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-2">
                <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: chainDots[wallet.chain] || '#94a3b8' }} />
                <span className="text-sm font-medium text-main">{getChainName(wallet.chain)}</span>
                {syncingWallets.has(wallet.id) && (
                  <span className="inline-flex items-center gap-1 text-xs text-indigo-400">
                    <svg className="animate-spin h-3 w-3" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Syncing
                  </span>
                )}
                {wallet.label && <span className="text-sm text-muted">({wallet.label})</span>}
              </div>

              <p className="text-sm font-mono text-muted mb-2 truncate" title={wallet.address}>
                {formatAddress(wallet.address)}
              </p>

              <div className="text-xs text-faint space-y-0.5">
                <span>Transactions: {wallet.tx_count}</span>
                {wallet.last_synced_at ? (
                  <span className="ml-3" title={new Date(wallet.last_synced_at).toLocaleString()}>
                    Last sync: {getRelativeTime(wallet.last_synced_at)}
                  </span>
                ) : (
                  <span className="ml-3 text-yellow-500">Never synced</span>
                )}
              </div>
            </div>

            <div className="flex flex-col gap-2 ml-4 shrink-0">
              <button
                onClick={() => handleSync(wallet.id)}
                disabled={syncingWallets.has(wallet.id)}
                className="text-xs bg-indigo-500/20 text-indigo-300 px-3 py-1.5 rounded-lg hover:bg-indigo-500/30 transition-colors disabled:opacity-50 font-mono"
              >
                {syncingWallets.has(wallet.id) ? 'Syncing...' : 'Sync'}
              </button>
              <button
                onClick={() => handleDelete(wallet.id)}
                className="text-xs bg-red-500/15 text-red-300 px-3 py-1.5 rounded-lg hover:bg-red-500/25 transition-colors font-mono"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
