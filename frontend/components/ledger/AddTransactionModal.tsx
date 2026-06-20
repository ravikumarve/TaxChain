'use client'

import { useState, useEffect } from 'react'

interface TransactionFormData {
  chain: string
  tx_type: string
  token_symbol: string
  token_address: string
  quantity: string
  price_usd: string
  value_usd: string
  fee_usd: string
  timestamp: string
  notes: string
}

interface Props {
  isOpen: boolean
  onClose: () => void
  onSave: (data: TransactionFormData) => Promise<void>
  initialData?: TransactionFormData | null
  title?: string
}

const CHAINS = ['eth', 'bnb', 'polygon', 'sol', 'arbitrum', 'optimism', 'base', 'btc']
const TX_TYPES = ['trade', 'transfer_in', 'transfer_out', 'staking', 'airdrop', 'nft_sale', 'fee']

const defaultForm: TransactionFormData = {
  chain: 'eth',
  tx_type: 'trade',
  token_symbol: '',
  token_address: '',
  quantity: '',
  price_usd: '',
  value_usd: '',
  fee_usd: '',
  timestamp: new Date().toISOString().slice(0, 16),
  notes: '',
}

export default function AddTransactionModal({ isOpen, onClose, onSave, initialData, title }: Props) {
  const [form, setForm] = useState<TransactionFormData>(defaultForm)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (initialData) {
      setForm(initialData)
    } else {
      setForm(defaultForm)
    }
    setError(null)
  }, [initialData, isOpen])

  if (!isOpen) return null

  const handleChange = (field: keyof TransactionFormData, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError(null)
    try {
      await onSave(form)
      onClose()
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to save transaction')
    } finally {
      setSaving(false)
    }
  }

  const inputClass =
    'px-3 py-2 bg-surface border border-border-dim rounded-lg focus:ring-2 focus:ring-indigo-500/40 focus:border-indigo-500 text-sm text-main w-full'

  const labelClass = 'block text-sm font-medium text-muted mb-1'

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60" onClick={onClose}>
      <div
        className="bg-surface border border-border-dim rounded-xl p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-main">{title || 'Add Transaction'}</h2>
          <button onClick={onClose} className="text-muted hover:text-main transition-colors">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-loss/10 border border-loss/20 rounded-lg text-loss text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={labelClass}>Chain</label>
              <select
                value={form.chain}
                onChange={(e) => handleChange('chain', e.target.value)}
                className={inputClass}
              >
                {CHAINS.map((c) => (
                  <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>
                ))}
              </select>
            </div>
            <div>
              <label className={labelClass}>Type</label>
              <select
                value={form.tx_type}
                onChange={(e) => handleChange('tx_type', e.target.value)}
                className={inputClass}
              >
                {TX_TYPES.map((t) => (
                  <option key={t} value={t}>{t.replace('_', ' ').replace(/\b\w/g, (c) => c.toUpperCase())}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className={labelClass}>Token Symbol</label>
            <input
              type="text"
              value={form.token_symbol}
              onChange={(e) => handleChange('token_symbol', e.target.value)}
              className={inputClass}
              placeholder="e.g. ETH"
              required
            />
          </div>

          <div>
            <label className={labelClass}>Token Address (optional)</label>
            <input
              type="text"
              value={form.token_address}
              onChange={(e) => handleChange('token_address', e.target.value)}
              className={inputClass}
              placeholder="0x..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={labelClass}>Quantity</label>
              <input
                type="number"
                step="any"
                value={form.quantity}
                onChange={(e) => handleChange('quantity', e.target.value)}
                className={inputClass}
                placeholder="0.00"
                required
              />
            </div>
            <div>
              <label className={labelClass}>Price USD (optional)</label>
              <input
                type="number"
                step="any"
                value={form.price_usd}
                onChange={(e) => handleChange('price_usd', e.target.value)}
                className={inputClass}
                placeholder="0.00"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={labelClass}>Value USD (optional)</label>
              <input
                type="number"
                step="any"
                value={form.value_usd}
                onChange={(e) => handleChange('value_usd', e.target.value)}
                className={inputClass}
                placeholder="0.00"
              />
            </div>
            <div>
              <label className={labelClass}>Fee USD (optional)</label>
              <input
                type="number"
                step="any"
                value={form.fee_usd}
                onChange={(e) => handleChange('fee_usd', e.target.value)}
                className={inputClass}
                placeholder="0.00"
              />
            </div>
          </div>

          <div>
            <label className={labelClass}>Date & Time</label>
            <input
              type="datetime-local"
              value={form.timestamp}
              onChange={(e) => handleChange('timestamp', e.target.value)}
              className={inputClass}
              required
            />
          </div>

          <div>
            <label className={labelClass}>Notes (optional)</label>
            <textarea
              value={form.notes}
              onChange={(e) => handleChange('notes', e.target.value)}
              className={`${inputClass} h-20 resize-none`}
              placeholder="Any additional notes..."
            />
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="btn btn-outline text-sm"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="btn btn-primary text-sm"
            >
              {saving ? 'Saving...' : 'Save Transaction'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
