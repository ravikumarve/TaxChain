'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { walletsApi } from '@/lib/api'

interface AddWalletModalProps {
  isOpen: boolean
  onClose: () => void
  onWalletAdded: () => void
}

const chains = [
  { value: 'eth', label: 'Ethereum' },
  { value: 'bnb', label: 'BNB Chain' },
  { value: 'polygon', label: 'Polygon' },
  { value: 'sol', label: 'Solana' },
  { value: 'arbitrum', label: 'Arbitrum' },
  { value: 'optimism', label: 'Optimism' },
  { value: 'base', label: 'Base' },
  { value: 'btc', label: 'Bitcoin' },
]

export default function AddWalletModal({ isOpen, onClose, onWalletAdded }: AddWalletModalProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [formData, setFormData] = useState({ address: '', chain: 'eth', label: '' })
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      if (!formData.address.trim()) { setError('Wallet address is required'); return }
      if (!formData.chain) { setError('Please select a blockchain'); return }

      await walletsApi.create(formData.address, formData.chain, formData.label || undefined)
      onWalletAdded()
      handleClose()
    } catch (err: any) {
      const detail = err.response?.data?.detail || 'Failed to add wallet'
      if (detail.includes('Invalid') && detail.includes('address format')) setError(`Invalid ${formData.chain.toUpperCase()} address format.`)
      else if (detail.includes('already exists')) setError('This wallet is already connected.')
      else if (detail.includes('Free tier limited')) setError('Free tier limited to 1 wallet. Upgrade to add more.')
      else setError(detail)
    } finally { setIsLoading(false) }
  }

  const validateAddressFormat = (address: string, chain: string): string | null => {
    if (!address.trim()) return null
    const patterns: Record<string, RegExp> = {
      eth: /^0x[a-fA-F0-9]{40}$/,
      bnb: /^0x[a-fA-F0-9]{40}$/,
      polygon: /^0x[a-fA-F0-9]{40}$/,
      sol: /^[1-9A-HJ-NP-Za-km-z]{32,44}$/,
      btc: /^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$/,
    }
    const pattern = patterns[chain]
    if (!pattern) return null
    if (!pattern.test(address)) return `Invalid ${chain.toUpperCase()} address format`
    return null
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    if (name === 'address' && error && !error.includes('address')) setError('')
    if (name === 'address' || name === 'chain') {
      const validationError = validateAddressFormat(
        name === 'address' ? value : formData.address,
        name === 'chain' ? value : formData.chain
      )
      if (validationError) setError(validationError)
      else if (error && error.includes('address format')) setError('')
    }
  }

  const handleClose = () => {
    setFormData({ address: '', chain: 'eth', label: '' })
    setError('')
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 backdrop-blur-sm">
      <div className="bg-panel border border-border-dim rounded-xl p-6 w-full max-w-md shadow-2xl">
        <h2 className="text-xl font-bold text-main mb-4">Add Wallet</h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="chain" className="block text-sm font-medium text-muted mb-1">
              Blockchain
            </label>
            <select
              id="chain" name="chain" value={formData.chain} onChange={handleChange}
              className={`w-full px-3 py-2.5 bg-surface border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/40 focus:border-indigo-500 text-sm text-main ${
                error && error.includes('chain') ? 'border-red-500/50' : 'border-border-dim'
              }`}
              required
            >
              {chains.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
            </select>
          </div>

          <div>
            <label htmlFor="address" className="block text-sm font-medium text-muted mb-1">
              Wallet Address
            </label>
            <input
              id="address" name="address" type="text" required
              value={formData.address} onChange={handleChange}
              className={`w-full px-3 py-2.5 bg-surface border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/40 focus:border-indigo-500 text-sm text-main placeholder:text-faint font-mono ${
                error && error.includes('address') ? 'border-red-500/50' : 'border-border-dim'
              }`}
              placeholder="0x..."
            />
          </div>

          <div>
            <label htmlFor="label" className="block text-sm font-medium text-muted mb-1">
              Label <span className="text-faint">(Optional)</span>
            </label>
            <input
              id="label" name="label" type="text"
              value={formData.label} onChange={handleChange}
              className="w-full px-3 py-2.5 bg-surface border border-border-dim rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/40 focus:border-indigo-500 text-sm text-main placeholder:text-faint"
              placeholder="e.g., My Main Wallet"
            />
          </div>

          {error && <div className="text-red-400 text-sm">{error}</div>}

          <div className="flex gap-3 pt-4">
            <Button type="button" variant="secondary" onClick={handleClose} className="flex-1">Cancel</Button>
            <Button type="submit" isLoading={isLoading} className="flex-1">Add Wallet</Button>
          </div>
        </form>
      </div>
    </div>
  )
}
