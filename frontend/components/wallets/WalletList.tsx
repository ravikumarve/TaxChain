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

  useEffect(() => {
    loadWallets()
  }, [refreshTrigger])

  const loadWallets = async () => {
    try {
      setLoading(true)
      const response = await walletsApi.list()
      setWallets(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load wallets')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (walletId: string) => {
    if (!confirm('Are you sure you want to delete this wallet? This will also remove all associated transactions.')) {
      return
    }

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
      
      // Show success notification
      alert('Wallet sync started. It may take a few minutes to complete.')
      
      // Reload wallets to show updated sync status
      loadWallets()
    } catch (err: any) {
      // Show specific error messages
      const errorMessage = err.response?.data?.detail || 'Failed to sync wallet'
      alert(`Sync failed: ${errorMessage}`)
    } finally {
      setSyncingWallets(prev => {
        const newSet = new Set(prev)
        newSet.delete(walletId)
        return newSet
      })
    }
  }

  const getChainName = (chain: string) => {
    const chainNames: { [key: string]: string } = {
      eth: 'Ethereum',
      bnb: 'BNB Chain',
      polygon: 'Polygon',
      sol: 'Solana'
    }
    return chainNames[chain] || chain
  }

  const getChainColor = (chain: string) => {
    const chainColors: { [key: string]: string } = {
      eth: 'bg-blue-500',
      bnb: 'bg-yellow-500',
      polygon: 'bg-purple-500',
      sol: 'bg-violet-500'
    }
    return chainColors[chain] || 'bg-gray-500'
  }

  const getRelativeTime = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / (1000 * 60))
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

    if (diffMins < 1) return 'just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  const formatAddress = (address: string) => {
    return `${address.slice(0, 8)}...${address.slice(-6)}`
  }

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map(i => (
          <div key={i} className="animate-pulse bg-gray-200 rounded-lg p-4 h-20"></div>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <div className="text-red-600 mb-2">{error}</div>
        <button 
          onClick={loadWallets}
          className="text-primary hover:text-primary/80"
        >
          Try Again
        </button>
      </div>
    )
  }

  if (wallets.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-500 mb-4">No wallets connected yet</div>
        <div className="text-sm text-gray-400">Add your first wallet to start tracking transactions</div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {wallets.map(wallet => (
        <div key={wallet.id} className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
               <div className="flex items-center space-x-2 mb-2">
                 <span className={`inline-block w-3 h-3 rounded-full ${getChainColor(wallet.chain)}`}></span>
                 <span className="text-sm font-medium text-gray-900">
                   {getChainName(wallet.chain)}
                 </span>
                 {syncingWallets.has(wallet.id) && (
                   <span className="inline-flex items-center text-xs text-blue-600">
                     <svg className="animate-spin h-3 w-3 mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                       <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                       <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                     </svg>
                     Syncing
                   </span>
                 )}
                 {wallet.label && (
                   <span className="text-sm text-gray-600">({wallet.label})</span>
                 )}
               </div>
              
              <div className="text-sm font-mono text-gray-600 mb-2" title={wallet.address}>
                {formatAddress(wallet.address)}
              </div>

              <div className="text-xs text-gray-500 space-y-1">
                <div>Transactions: {wallet.tx_count}</div>
                {wallet.last_synced_at ? (
                  <div title={new Date(wallet.last_synced_at).toLocaleString()}>
                    Last sync: {getRelativeTime(wallet.last_synced_at)}
                  </div>
                ) : (
                  <div className="text-orange-600">Never synced</div>
                )}
              </div>
            </div>

            <div className="flex flex-col space-y-2">
              <button
                onClick={() => handleSync(wallet.id)}
                disabled={syncingWallets.has(wallet.id)}
                className="text-xs bg-primary text-white px-3 py-1 rounded hover:bg-primary/80 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {syncingWallets.has(wallet.id) ? (
                  <span className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-1 h-3 w-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Syncing...
                  </span>
                ) : (
                  'Sync'
                )}
              </button>
              <button
                onClick={() => handleDelete(wallet.id)}
                className="text-xs bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700 transition-colors"
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