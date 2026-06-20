'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { transactionsApi, walletsApi } from '@/lib/api'
import { Transaction } from '@/types'
import { Card } from '@/components/ui/Card'
import { ChainBadge } from '@/components/dashboard/ChainBadge'
import AddTransactionModal from '@/components/ledger/AddTransactionModal'
import CsvImportPanel from '@/components/ledger/CsvImportPanel'
import ReconciliationPanel from '@/components/ledger/ReconciliationPanel'

type Tab = 'ledger' | 'import' | 'reconcile' | 'defi'

const TABS: { key: Tab; label: string }[] = [
  { key: 'ledger', label: 'Transaction Ledger' },
  { key: 'import', label: 'CSV Import' },
  { key: 'reconcile', label: 'Reconciliation' },
  { key: 'defi', label: 'DeFi Transactions' },
]

export default function LedgerPage() {
  const [activeTab, setActiveTab] = useState<Tab>('ledger')
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [modalOpen, setModalOpen] = useState(false)
  const [editTx, setEditTx] = useState<{ id: string; data: any } | null>(null)
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  const fetchTransactions = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await transactionsApi.list({ page, limit: 50 })
      setTransactions(response.data.transactions || [])
      setTotalPages(response.data.pagination?.pages || 1)
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to fetch transactions')
    } finally {
      setLoading(false)
    }
  }, [page])

  useEffect(() => {
    fetchTransactions()
  }, [fetchTransactions, refreshTrigger])

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
      lp_deposit: 'bg-cyan-500/15 text-cyan-300',
      lp_withdraw: 'bg-orange-500/15 text-orange-300',
      borrow: 'bg-rose-500/15 text-rose-300',
      repay: 'bg-teal-500/15 text-teal-300',
      yield_farm: 'bg-violet-500/15 text-violet-300',
      liquidation: 'bg-red-600/15 text-red-400',
    }
    return colors[type] || 'bg-muted/15 text-muted'
  }

  const getTransactionTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      trade: 'Trade', transfer_in: 'Transfer In', transfer_out: 'Transfer Out',
      staking: 'Staking', airdrop: 'Airdrop', nft_sale: 'NFT Sale', fee: 'Fee',
      lp_deposit: 'LP Deposit', lp_withdraw: 'LP Withdraw',
      borrow: 'Borrow', repay: 'Repay',
      yield_farm: 'Yield Farm', liquidation: 'Liquidation',
    }
    return labels[type] || type
  }

  const isManualTx = (tx: Transaction) => tx.tx_hash?.startsWith('manual_')

  const handleAdd = () => {
    setEditTx(null)
    setModalOpen(true)
  }

  const handleEdit = (tx: Transaction) => {
    const formData = {
      chain: tx.chain || 'eth',
      tx_type: tx.tx_type || 'trade',
      token_symbol: tx.token_symbol || '',
      token_address: '',
      quantity: tx.quantity?.toString() || '',
      price_usd: tx.price_usd?.toString() || '',
      value_usd: tx.value_usd?.toString() || '',
      fee_usd: tx.fee_usd?.toString() || '',
      timestamp: tx.timestamp ? tx.timestamp.slice(0, 16) : new Date().toISOString().slice(0, 16),
      notes: '',
    }
    setEditTx({ id: tx.id, data: formData })
    setModalOpen(true)
  }

  const handleSave = async (formData: any) => {
    if (editTx) {
      await transactionsApi.update(editTx.id, {
        chain: formData.chain,
        tx_type: formData.tx_type,
        token_symbol: formData.token_symbol,
        quantity: formData.quantity ? parseFloat(formData.quantity) : 0,
        price_usd: formData.price_usd ? parseFloat(formData.price_usd) : null,
        value_usd: formData.value_usd ? parseFloat(formData.value_usd) : null,
        fee_usd: formData.fee_usd ? parseFloat(formData.fee_usd) : null,
        timestamp: formData.timestamp,
        notes: formData.notes || undefined,
      })
    } else {
      await transactionsApi.createManual({
        chain: formData.chain,
        tx_type: formData.tx_type,
        token_symbol: formData.token_symbol,
        quantity: formData.quantity ? parseFloat(formData.quantity) : 0,
        price_usd: formData.price_usd ? parseFloat(formData.price_usd) : null,
        value_usd: formData.value_usd ? parseFloat(formData.value_usd) : null,
        fee_usd: formData.fee_usd ? parseFloat(formData.fee_usd) : null,
        timestamp: new Date(formData.timestamp).toISOString(),
        notes: formData.notes || undefined,
      })
    }
    setModalOpen(false)
    setEditTx(null)
    setRefreshTrigger((r) => r + 1)
  }

  const handleDelete = async (txId: string) => {
    try {
      await transactionsApi.delete(txId)
      setDeleteConfirm(null)
      setRefreshTrigger((r) => r + 1)
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to delete transaction')
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-main">Ledger</h1>
        <p className="text-muted text-sm mt-1">Manage, import, and reconcile your transactions</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-surface border border-border-dim rounded-lg p-1">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
              activeTab === tab.key
                ? 'bg-indigo-500/15 text-indigo-300'
                : 'text-muted hover:text-main'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab: Ledger */}
      {activeTab === 'ledger' && (
        <>
          <div className="flex justify-end">
            <button onClick={handleAdd} className="btn btn-primary text-sm">
              + Add Transaction
            </button>
          </div>

          {loading && (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-400" />
            </div>
          )}

          {error && !loading && (
            <Card className="p-4 bg-loss/10 border border-loss/20">
              <p className="text-loss text-sm">{error}</p>
            </Card>
          )}

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
                  <p className="text-muted text-sm mb-4">Add wallets to sync transactions or create manual entries.</p>
                  <button onClick={handleAdd} className="btn btn-primary text-sm">
                    Add Your First Transaction
                  </button>
                </Card>
              ) : (
                <Card className="overflow-hidden">
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-surface border-b border-border-dim">
                        <tr>
                          {['Date', 'Type', 'Chain', 'Token', 'Quantity', 'Price', 'Value', 'Fee', 'Source', 'Actions'].map((h) => (
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
                            <td className="px-6 py-4 whitespace-nowrap">
                              {isManualTx(tx) ? (
                                <span className="text-xs text-indigo-400 font-mono">Manual</span>
                              ) : (
                                <span className="text-xs text-muted font-mono">Synced</span>
                              )}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              {isManualTx(tx) ? (
                                <div className="flex gap-2">
                                  <button
                                    onClick={() => handleEdit(tx)}
                                    className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors font-mono"
                                  >
                                    Edit
                                  </button>
                                  <button
                                    onClick={() => setDeleteConfirm(tx.id)}
                                    className="text-xs text-loss hover:text-loss/80 transition-colors font-mono"
                                  >
                                    Delete
                                  </button>
                                </div>
                              ) : (
                                <span className="text-xs text-faint">—</span>
                              )}
                            </td>
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
                        <button
                          onClick={() => setPage(Math.max(1, page - 1))}
                          disabled={page === 1}
                          className="px-3 py-1.5 text-xs font-mono border border-border-dim rounded-lg text-muted hover:text-main hover:border-indigo-500/40 disabled:opacity-50 transition-colors"
                        >
                          Previous
                        </button>
                        <button
                          onClick={() => setPage(Math.min(totalPages, page + 1))}
                          disabled={page === totalPages}
                          className="px-3 py-1.5 text-xs font-mono border border-border-dim rounded-lg text-muted hover:text-main hover:border-indigo-500/40 disabled:opacity-50 transition-colors"
                        >
                          Next
                        </button>
                      </div>
                    </div>
                  )}
                </Card>
              )}
            </>
          )}
        </>
      )}

      {/* Tab: CSV Import */}
      {activeTab === 'import' && <CsvImportPanel />}

      {/* Tab: Reconciliation */}
      {activeTab === 'reconcile' && <ReconciliationPanel />}

      {/* Tab: DeFi Transactions */}
      {activeTab === 'defi' && <DeFiTransactionsTab />}

      {/* Add/Edit Modal */}
      <AddTransactionModal
        isOpen={modalOpen}
        onClose={() => { setModalOpen(false); setEditTx(null) }}
        onSave={handleSave}
        initialData={editTx?.data}
        title={editTx ? 'Edit Transaction' : 'Add Transaction'}
      />

      {/* Delete Confirmation */}
      {deleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
          <div className="bg-surface border border-border-dim rounded-xl p-6 w-full max-w-sm">
            <h3 className="text-lg font-semibold text-main mb-2">Delete Transaction</h3>
            <p className="text-sm text-muted mb-6">
              Are you sure you want to delete this transaction? This action cannot be undone.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setDeleteConfirm(null)}
                className="btn btn-outline text-sm"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDelete(deleteConfirm)}
                className="px-4 py-2 text-sm font-medium rounded-md bg-loss text-white hover:bg-loss/90 transition-colors"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function DeFiTransactionsTab() {
  const [lpPositions, setLpPositions] = useState<any[]>([])
  const [yieldFarms, setYieldFarms] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetch = async () => {
      try {
        setLoading(true)
        const response = await walletsApi.defiPositions()
        setLpPositions(response.data.lp_positions || [])
        setYieldFarms(response.data.yield_farms || [])
      } catch (err: any) {
        setError(err?.response?.data?.detail || 'Failed to fetch DeFi positions')
      } finally {
        setLoading(false)
      }
    }
    fetch()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-400" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4 bg-loss/10 border border-loss/20 rounded-lg">
        <p className="text-loss text-sm">{error}</p>
      </div>
    )
  }

  if (lpPositions.length === 0 && yieldFarms.length === 0) {
    return (
      <div className="p-12 text-center bg-surface border border-border-dim rounded-xl">
        <p className="text-muted text-sm">No DeFi transactions found. Add wallets with DeFi activity to see your positions here.</p>
      </div>
    )
  }

  const protocolLabel = (chain: string, token: string) => {
    const chainProtocols: Record<string, string> = {
      eth: 'Uniswap V3',
      bnb: 'PancakeSwap',
      polygon: 'QuickSwap',
      arbitrum: 'Camelot',
      optimism: 'Velodrome',
      base: 'Aerodrome',
    }
    return chainProtocols[chain] || `${chain.toUpperCase()} DEX`
  }

  return (
    <div className="space-y-4">
      {lpPositions.filter(p => p.is_active).length > 0 && (
        <div className="bg-surface border border-border-dim rounded-xl overflow-hidden">
          <div className="p-4 border-b border-border-dim">
            <h3 className="text-sm font-semibold text-main">Active Liquidity Positions</h3>
          </div>
          <div className="divide-y divide-border-dim">
            {lpPositions.filter(p => p.is_active).map((pos, i) => (
              <div key={i} className="p-4 flex items-center justify-between">
                <div>
                  <p className="text-xs text-muted font-mono">{protocolLabel(pos.chain, pos.token_symbol)}</p>
                  <p className="text-sm font-semibold text-main mt-0.5">{pos.token_symbol} Pool</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-mono text-main">{pos.net_quantity.toFixed(6)}</p>
                  <p className="text-xs text-muted">{pos.deposit_count} deposits / {pos.withdrawal_count} withdrawals</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {yieldFarms.length > 0 && (
        <div className="bg-surface border border-border-dim rounded-xl overflow-hidden">
          <div className="p-4 border-b border-border-dim">
            <h3 className="text-sm font-semibold text-main">Yield Farms</h3>
          </div>
          <div className="divide-y divide-border-dim">
            {yieldFarms.map((farm, i) => (
              <div key={i} className="p-4 flex items-center justify-between">
                <div>
                  <p className="text-xs text-muted font-mono">{protocolLabel(farm.chain, farm.token_symbol)}</p>
                  <p className="text-sm font-semibold text-main mt-0.5">{farm.token_symbol}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-mono text-main">{farm.total_deposited.toFixed(6)}</p>
                  <p className="text-xs text-muted">{farm.deposit_count} deposits</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
