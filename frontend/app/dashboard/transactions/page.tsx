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
  const [filters, setFilters] = useState({
    chain: '',
    tx_type: '',
  })

  useEffect(() => {
    fetchTransactions()
  }, [page, filters])

  const fetchTransactions = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await transactionsApi.list({
        page,
        limit: 50,
        chain: filters.chain || undefined,
        tx_type: filters.tx_type || undefined,
      })
      setTransactions(response.data.data)
      setTotalPages(response.data.pagination.pages)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch transactions')
      console.error('Error fetching transactions:', err)
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (value?: number) => {
    if (value === undefined || value === null) return 'N/A'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value)
  }

  const formatCrypto = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 8,
    }).format(value)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  const getTransactionTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      trade: 'bg-blue-100 text-blue-800',
      transfer_in: 'bg-green-100 text-green-800',
      transfer_out: 'bg-red-100 text-red-800',
      staking: 'bg-purple-100 text-purple-800',
      airdrop: 'bg-yellow-100 text-yellow-800',
      nft_sale: 'bg-pink-100 text-pink-800',
      fee: 'bg-gray-100 text-gray-800',
    }
    return colors[type] || 'bg-gray-100 text-gray-800'
  }

  const getTransactionTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      trade: 'Trade',
      transfer_in: 'Transfer In',
      transfer_out: 'Transfer Out',
      staking: 'Staking',
      airdrop: 'Airdrop',
      nft_sale: 'NFT Sale',
      fee: 'Fee',
    }
    return labels[type] || type
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Transactions</h1>
        <p className="text-gray-600 mt-1">
          View and filter your transaction history
        </p>
      </div>

      {/* Filters */}
      <Card className="p-4">
        <div className="flex flex-wrap gap-4">
          <div>
            <label htmlFor="chain-filter" className="block text-sm font-medium text-gray-700 mb-1">
              Chain
            </label>
            <select
              id="chain-filter"
              value={filters.chain}
              onChange={(e) => {
                setFilters({ ...filters, chain: e.target.value })
                setPage(1)
              }}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
            >
              <option value="">All Chains</option>
              <option value="eth">Ethereum</option>
              <option value="bnb">BNB Chain</option>
              <option value="polygon">Polygon</option>
              <option value="sol">Solana</option>
            </select>
          </div>

          <div>
            <label htmlFor="type-filter" className="block text-sm font-medium text-gray-700 mb-1">
              Type
            </label>
            <select
              id="type-filter"
              value={filters.tx_type}
              onChange={(e) => {
                setFilters({ ...filters, tx_type: e.target.value })
                setPage(1)
              }}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
            >
              <option value="">All Types</option>
              <option value="trade">Trade</option>
              <option value="transfer_in">Transfer In</option>
              <option value="transfer_out">Transfer Out</option>
              <option value="staking">Staking</option>
              <option value="airdrop">Airdrop</option>
              <option value="nft_sale">NFT Sale</option>
              <option value="fee">Fee</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <Card className="p-6 bg-red-50 border-red-200">
          <p className="text-red-800">{error}</p>
        </Card>
      )}

      {/* Transactions Table */}
      {!loading && !error && (
        <>
          {transactions.length === 0 ? (
            <Card className="p-12 text-center">
              <div className="text-gray-400 mb-4">
                <svg
                  className="mx-auto h-12 w-12"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                  />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No transactions found
              </h3>
              <p className="text-gray-600 mb-4">
                {filters.chain || filters.tx_type
                  ? 'Try adjusting your filters or add more wallets to see transactions.'
                  : 'Add wallets and sync transactions to see your transaction history.'}
              </p>
              {!filters.chain && !filters.tx_type && (
                <button
                  onClick={() => (window.location.href = '/dashboard/wallets')}
                  className="text-indigo-600 hover:text-indigo-800 font-medium"
                >
                  Add Wallets →
                </button>
              )}
            </Card>
          ) : (
            <Card className="overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Date
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Type
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Chain
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Token
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Quantity
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Price
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Value
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Fee
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {transactions.map((tx) => (
                      <tr key={tx.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatDate(tx.timestamp)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getTransactionTypeColor(tx.tx_type)}`}>
                            {getTransactionTypeLabel(tx.tx_type)}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <ChainBadge chain={tx.chain} />
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {tx.token_symbol || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right font-mono">
                          {formatCrypto(tx.quantity)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right font-mono">
                          {formatCurrency(tx.price_usd)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right font-mono">
                          {formatCurrency(tx.value_usd)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right font-mono">
                          {formatCurrency(tx.fee_usd)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="bg-gray-50 px-6 py-3 flex items-center justify-between border-t border-gray-200">
                  <div className="flex-1 flex justify-between sm:hidden">
                    <button
                      onClick={() => setPage(Math.max(1, page - 1))}
                      disabled={page === 1}
                      className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Previous
                    </button>
                    <button
                      onClick={() => setPage(Math.min(totalPages, page + 1))}
                      disabled={page === totalPages}
                      className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Next
                    </button>
                  </div>
                  <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                    <div>
                      <p className="text-sm text-gray-700">
                        Showing page <span className="font-medium">{page}</span> of{' '}
                        <span className="font-medium">{totalPages}</span>
                      </p>
                    </div>
                    <div>
                      <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                        <button
                          onClick={() => setPage(Math.max(1, page - 1))}
                          disabled={page === 1}
                          className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          Previous
                        </button>
                        <button
                          onClick={() => setPage(Math.min(totalPages, page + 1))}
                          disabled={page === totalPages}
                          className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          Next
                        </button>
                      </nav>
                    </div>
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