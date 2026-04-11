'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { walletsApi } from '@/lib/api'

interface AddWalletModalProps {
  isOpen: boolean
  onClose: () => void
  onWalletAdded: () => void
}

export default function AddWalletModal({ isOpen, onClose, onWalletAdded }: AddWalletModalProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [formData, setFormData] = useState({
    address: '',
    chain: 'eth',
    label: ''
  })
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      // Basic client-side validation
      if (!formData.address.trim()) {
        setError('Wallet address is required')
        return
      }
      
      if (!formData.chain) {
        setError('Please select a blockchain')
        return
      }
      
      await walletsApi.create(formData.address, formData.chain, formData.label || undefined)
      onWalletAdded()
      handleClose()
    } catch (err: any) {
      const errorDetail = err.response?.data?.detail || 'Failed to add wallet'
      
      // Show specific error messages
      if (errorDetail.includes('Invalid') && errorDetail.includes('address format')) {
        setError(`Invalid ${formData.chain.toUpperCase()} address format. Please check and try again.`)
      } else if (errorDetail.includes('already exists')) {
        setError('This wallet is already connected to your account')
      } else if (errorDetail.includes('Free tier limited')) {
        setError('Free tier limited to 1 wallet. Upgrade to add more wallets.')
      } else if (errorDetail.includes('Invalid chain')) {
        setError('Please select a supported blockchain')
      } else {
        setError(errorDetail)
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    
    // Clear error when user starts typing
    if (name === 'address' && error) {
      setError('')
    }
    
    // Real-time validation for address format
    if (name === 'address' || name === 'chain') {
      const validationError = validateAddressFormat(
        name === 'address' ? value : formData.address,
        name === 'chain' ? value : formData.chain
      )
      
      if (validationError) {
        setError(validationError)
      } else if (error && error.includes('address format')) {
        setError('')
      }
    }
  }
  
  const validateAddressFormat = (address: string, chain: string): string | null => {
    if (!address.trim()) return null
    
    const patterns: { [key: string]: RegExp } = {
      eth: /^0x[a-fA-F0-9]{40}$/,
      bnb: /^0x[a-fA-F0-9]{40}$/,
      polygon: /^0x[a-fA-F0-9]{40}$/,
      sol: /^[1-9A-HJ-NP-Za-km-z]{32,44}$/
    }
    
    const pattern = patterns[chain]
    if (!pattern) return null
    
    if (!pattern.test(address)) {
      return `This doesn't look like a valid ${chain.toUpperCase()} address`
    }
    
    return null
  }

  const handleClose = () => {
    setFormData({ address: '', chain: 'eth', label: '' })
    setError('')
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Add Wallet</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="chain" className="block text-sm font-medium text-gray-700 mb-1">
              Blockchain
            </label>
            <select
              id="chain"
              name="chain"
              value={formData.chain}
              onChange={handleChange}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent ${
                error && error.includes('chain') 
                  ? 'border-red-300' 
                  : 'border-gray-300'
              }`}
              required
            >
              <option value="eth">Ethereum</option>
              <option value="bnb">BNB Chain</option>
              <option value="polygon">Polygon</option>
              <option value="sol">Solana</option>
            </select>
          </div>

          <div>
            <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-1">
              Wallet Address
            </label>
            <input
              id="address"
              name="address"
              type="text"
              required
              value={formData.address}
              onChange={handleChange}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent ${
                error && error.includes('address format') 
                  ? 'border-red-300' 
                  : 'border-gray-300'
              }`}
              placeholder="Enter wallet address"
            />
          </div>

          <div>
            <label htmlFor="label" className="block text-sm font-medium text-gray-700 mb-1">
              Label (Optional)
            </label>
            <input
              id="label"
              name="label"
              type="text"
              value={formData.label}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              placeholder="e.g., My Main Wallet"
            />
          </div>

          {error && (
            <div className="text-red-600 text-sm">{error}</div>
          )}

          <div className="flex space-x-3 pt-4">
            <Button
              type="button"
              variant="secondary"
              onClick={handleClose}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              isLoading={isLoading}
              className="flex-1"
            >
              Add Wallet
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}