'use client'

import { useState, useEffect } from 'react'
import { useAppStore } from '@/store/useAppStore'
import { transactionsApi } from '@/lib/api'
import { Transaction } from '@/types'
import { Card } from '@/components/ui/Card'
import { ChainBadge } from '@/components/dashboard/ChainBadge'

export default function TransactionsPage() {
  const { user } = useAppStore()
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [filters, setFilters] = useState({ chain: '', tx_type: '' })

  useEffect(() => { fetchTransactions() }, [page, filters])

  const fetchTransactions = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await transactionsApi.list({
        page, limit: 50,
        chain: filters.chain || undefined,
        tx_type: filters.tx_type || undefined,
      })
      setTransactions(response.data.transactions || [])
      setTotalPages(response.data.pagination?.pages || 1)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch transactions')
    } finally { setLoading(false) }
  }

  const formatCurrency = (value?: number) => {
    if (value === undefined || value === null) return 'N/A'
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(value)
  }

  const formatCrypto = (value: number) =>
    new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 8 }).format(value)

  const formatDate = (dateString: string) => new Date(dateString).toLocaleString()

  const getTransactionTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      trade: 'bg-indigo-500/15 text-indigo-300',
      transfer_in: 'bg-emerald-500/15 text-emerald-300',
      transfer_out: 'bg-red-500/15 text-red-300',
      staking: 'bg-purple-500/15 text-purple-300',
      airdrop: 'bg-yellow-500/15 text-yellow-300',
      nft_sale: 'bg-pink-500/15 text-pink-300',
      fee: 'bg-muted/15 text-muted',
    }
    return colors[type] || 'bg-muted/15 text-muted'
  }

  const getTransactionTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      trade: 'Trade', transfer_in: 'Transfer In', transfer_out: 'Transfer Out',
      staking: 'Staking', airdrop: 'Airdrop', nft_sale: 'NFT Sale', fee: 'Fee',
    }
    return labels[type] || type
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-main">Transactions</h1>
        <p className="text-muted text-sm mt-1">View and filter your transaction history</p>
      </div>

      {/* Filters */}
      <Card className="p-4">
        <div className="flex flex-wrap gap-4">
          <div>
            <label htmlFor="chain-filter" className="block text-sm font-medium text-muted mb-1">
              Chain
            </label>
            <select
              id="chain-filter"
              value={filters.chain}
              onChange={(e) => { setFilters({ ...filters, chain: e.target.value }); setPage(1) }}
              className="px-3 py-2 bg-surface border border-border-dim rounded-lg focus:ring-2 focus:ring-indigo-500/40 focus:border-indigo-500 text-sm text-main"
            >
              <option value="">All Chains</option>
              {['eth', 'bnb', 'polygon', 'sol', 'arbitrum', 'optimism', 'base', 'btc'].map(c => (
                <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="type-filter" className="block text-sm font-medium text-muted mb-1">
              Type
            </label>
            <select
              id="type-filter"
              value={filters.tx_type}
              onChange={(e) => { setFilters({ ...filters, tx_type: e.target.value }); setPage(1) }}
              className="px-3 py-2 bg-surface border border-border-dim rounded-lg focus:ring-2 focus:ring-indigo-500/40 focus:border-indigo-500 text-sm text-main"
            >
              <option value="">All Types</option>
              {['trade', 'transfer_in', 'transfer_out', 'staking', 'airdrop', 'nft_sale', 'fee'].map(t => (
                <option key={t} value={t}>{getTransactionTypeLabel(t)}</option>
              ))}
            </select>
          </div>
        </div>
      </Card>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-400" />
        </div>
      )}

      {/* Error */}
      {error && !loading && (
        <Card className="p-4 bg-red-500/10 border border-red-500/20">
          <p className="text-red-300 text-sm">{error}</p>
        </Card>
      )}

      {/* Table */}
      {!loading && !error && (
        <>
          {transactions.length === 0 ? (
            <Card className="p-12 text-center">
              <div className="text-faint mb-4">
                <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-main mb-2">No transactions found</h3>
              <p className="text-muted text-sm mb-4">
                {filters.chain || filters.tx_type
                  ? 'Try adjusting your filters or add more wallets.'
                  : 'Add wallets and sync transactions to see your history.'}
              </p>
              {!filters.chain && !filters.tx_type && (
                <a href="/dashboard/wallets" className="text-indigo-400 hover:text-indigo-300 font-medium text-sm">
                  Add Wallets →
                </a>
              )}
            </Card>
          ) : (
            <Card className="overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-surface border-b border-border-dim">
                    <tr>
                      {['Date', 'Type', 'Chain', 'Token', 'Quantity', 'Price', 'Value', 'Fee'].map(h => (
                        <th key={h} className="px-6 py-3 text-left text-xs font-medium text-faint uppercase tracking-wider font-mono">
                          {h}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border-dim">
                    {transactions.map((tx) => (
                      <tr key={tx.id} className="hover:bg-indigo-500/5 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-muted">{formatDate(tx.timestamp)}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getTransactionTypeColor(tx.tx_type)}`}>
                            {getTransactionTypeLabel(tx.tx_type)}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap"><ChainBadge chain={tx.chain} /></td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-main font-mono">{tx.token_symbol || 'N/A'}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-main text-right font-mono">{formatCrypto(tx.quantity)}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-main text-right font-mono">{formatCurrency(tx.price_usd)}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-main text-right font-mono">{formatCurrency(tx.value_usd)}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-faint text-right font-mono">{formatCurrency(tx.fee_usd)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="bg-surface border-t border-border-dim px-6 py-3 flex items-center justify-between">
                  <p className="text-sm text-muted">
                    Page <span className="font-medium text-main">{page}</span> of{' '}
                    <span className="font-medium text-main">{totalPages}</span>
                  </p>
                  <div className="flex gap-2">
                    <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1}
                      className="px-3 py-1.5 text-xs font-mono border border-border-dim rounded-lg text-muted hover:text-main hover:border-indigo-500/40 disabled:opacity-50 transition-colors">
                      Previous
                    </button>
                    <button onClick={() => setPage(Math.min(totalPages, page + 1))} disabled={page === totalPages}
                      className="px-3 py-1.5 text-xs font-mono border border-border-dim rounded-lg text-muted hover:text-main hover:border-indigo-500/40 disabled:opacity-50 transition-colors">
                      Next
                    </button>
                  </div>
                </div>
              )}
            </Card>
          )}
        </>
      )}
    </div>
  )
}
