'use client'

import { useState, useEffect, useCallback } from 'react'
import { transactionsApi } from '@/lib/api'
import { Card } from '@/components/ui/Card'
import AddTransactionModal from './AddTransactionModal'

interface TxInfo {
  id: string
  tx_hash: string
  token_symbol: string | null
  chain: string
  tx_type: string
  quantity: number | null
  price_usd: number | null
  timestamp: string | null
}

interface IssueCategory {
  count: number
  transactions: TxInfo[]
}

interface ReconcileData {
  missing_price: IssueCategory
  unknown_token: IssueCategory
  unclassified_type: IssueCategory
  duplicate_hash: IssueCategory
  total_issues: number
}

type IssueKey = 'missing_price' | 'unknown_token' | 'unclassified_type' | 'duplicate_hash'

const ISSUE_LABELS: Record<IssueKey, { label: string; icon: string; color: string }> = {
  missing_price: { label: 'Missing Price Data', icon: '🔴', color: 'text-loss' },
  unknown_token: { label: 'Unknown Token Symbols', icon: '🟡', color: 'text-yellow-400' },
  unclassified_type: { label: 'Unclassified Types', icon: '🟠', color: 'text-orange-400' },
  duplicate_hash: { label: 'Duplicate Tx Hashes', icon: '⚪', color: 'text-muted' },
}

export default function ReconciliationPanel() {
  const [data, setData] = useState<ReconcileData | null>(null)
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState<IssueKey | null>(null)
  const [editTx, setEditTx] = useState<{ id: string; data: any } | null>(null)
  const [modalOpen, setModalOpen] = useState(false)

  const fetchReconcile = useCallback(async () => {
    setLoading(true)
    try {
      const response = await transactionsApi.reconcile()
      setData(response.data)
    } catch {
      // silently fail
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchReconcile()
  }, [fetchReconcile])

  const handleEdit = (tx: TxInfo) => {
    const formData = {
      chain: tx.chain || 'eth',
      tx_type: tx.tx_type || 'trade',
      token_symbol: tx.token_symbol || '',
      token_address: '',
      quantity: tx.quantity?.toString() || '',
      price_usd: tx.price_usd?.toString() || '',
      value_usd: '',
      fee_usd: '',
      timestamp: tx.timestamp ? tx.timestamp.slice(0, 16) : new Date().toISOString().slice(0, 16),
      notes: '',
    }
    setEditTx({ id: tx.id, data: formData })
    setModalOpen(true)
  }

  const handleSaveEdit = async (formData: any) => {
    if (!editTx) return
    const payload: Record<string, any> = {
      chain: formData.chain,
      tx_type: formData.tx_type,
      token_symbol: formData.token_symbol,
      quantity: formData.quantity ? parseFloat(formData.quantity) : 0,
      price_usd: formData.price_usd ? parseFloat(formData.price_usd) : null,
      timestamp: formData.timestamp,
    }
    await transactionsApi.update(editTx.id, payload)
    setModalOpen(false)
    setEditTx(null)
    fetchReconcile()
  }

  if (loading) {
    return (
      <Card className="p-6">
        <h3 className="text-md font-semibold text-main mb-4">Error Reconciliation</h3>
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-400" />
        </div>
      </Card>
    )
  }

  if (!data || data.total_issues === 0) {
    return (
      <Card className="p-6">
        <h3 className="text-md font-semibold text-main mb-4">Error Reconciliation</h3>
        <div className="text-center py-6">
          <svg className="mx-auto h-8 w-8 text-emerald-400 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-sm text-muted">No issues found — all transactions look good!</p>
        </div>
      </Card>
    )
  }

  const issueKeys: IssueKey[] = ['missing_price', 'unknown_token', 'unclassified_type', 'duplicate_hash']
  const hasIssues = (key: IssueKey) => data[key]?.count > 0

  const getChainBadge = (chain: string) => {
    const colors: Record<string, string> = {
      eth: 'text-indigo-400', bnb: 'text-yellow-400', polygon: 'text-purple-400',
      sol: 'text-green-400', arbitrum: 'text-blue-400', optimism: 'text-red-400',
      base: 'text-blue-300', btc: 'text-orange-400',
    }
    return <span className={`font-mono text-xs ${colors[chain] || 'text-muted'}`}>{chain}</span>
  }

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-md font-semibold text-main">Error Reconciliation</h3>
        <button
          onClick={fetchReconcile}
          className="text-xs text-muted hover:text-main transition-colors font-mono"
        >
          ↻ Refresh
        </button>
      </div>

      <p className="text-sm text-muted mb-4">
        {data.total_issues} issue{data.total_issues !== 1 ? 's' : ''} found
      </p>

      <div className="space-y-2">
        {issueKeys.map((key) => {
          if (!hasIssues(key)) return null
          const cat = data[key]
          const meta = ISSUE_LABELS[key]
          const isExpanded = expanded === key

          return (
            <div key={key} className="border border-border-dim rounded-lg overflow-hidden">
              <button
                onClick={() => setExpanded(isExpanded ? null : key)}
                className="w-full flex items-center justify-between px-4 py-3 hover:bg-surface transition-colors text-left"
              >
                <div className="flex items-center gap-2">
                  <span>{meta.icon}</span>
                  <span className={`text-sm font-medium ${meta.color}`}>{meta.label}</span>
                  <span className="text-xs text-faint bg-surface px-2 py-0.5 rounded-full">
                    {cat.count}
                  </span>
                </div>
                <svg
                  className={`w-4 h-4 text-muted transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                  fill="none" viewBox="0 0 24 24" stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {isExpanded && (
                <div className="border-t border-border-dim divide-y divide-border-dim">
                  {cat.transactions.map((tx) => (
                    <div key={tx.id} className="px-4 py-2.5 flex items-center justify-between gap-4">
                      <div className="flex items-center gap-3 text-xs font-mono text-muted flex-1 min-w-0">
                        {getChainBadge(tx.chain)}
                        <span className="text-main truncate">{tx.token_symbol || 'N/A'}</span>
                        <span>{tx.tx_type}</span>
                        {tx.quantity != null && <span>{tx.quantity}</span>}
                        {tx.price_usd != null && <span>${tx.price_usd.toFixed(2)}</span>}
                      </div>
                      <button
                        onClick={() => handleEdit(tx)}
                        className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors whitespace-nowrap font-mono"
                      >
                        Fix
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>

      <AddTransactionModal
        isOpen={modalOpen}
        onClose={() => { setModalOpen(false); setEditTx(null) }}
        onSave={handleSaveEdit}
        initialData={editTx?.data}
        title="Edit Transaction"
      />
    </Card>
  )
}
