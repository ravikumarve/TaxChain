'use client'

import { useEffect, useState } from 'react'
import { useAppStore } from '@/store/useAppStore'
import { walletsApi } from '@/lib/api'
import { Wallet } from '@/types'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { ChainBadge } from '@/components/dashboard/ChainBadge'
import { AddWalletModal } from '@/components/wallets/AddWalletModal'
import { WalletList } from '@/components/wallets/WalletList'

export default function WalletsPage() {
  const { user, wallets, setWallets, addWallet, removeWallet, setLoading, setError } = useAppStore()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [syncingWallets, setSyncingWallets] = useState<Set<string>>(new Set())

  useEffect(() => {
    fetchWallets()
  }, [])

  const fetchWallets = async () => {
    setLoading(true)
    try {
      const response = await walletsApi.list()
      setWallets(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch wallets')
      console.error('Error fetching wallets:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleAddWallet = async (address: string, chain: string, label?: string) => {
    try {
      const response = await walletsApi.create(address, chain, label)
      addWallet(response.data)
      setIsModalOpen(false)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add wallet')
      console.error('Error adding wallet:', err)
    }
  }

  const handleDeleteWallet = async (id: string) => {
    if (!confirm('Are you sure you want to delete this wallet? This action cannot be undone.')) {
      return
    }

    try {
      await walletsApi.delete(id)
      removeWallet(id)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete wallet')
      console.error('Error deleting wallet:', err)
    }
  }

  const handleSyncWallet = async (id: string) => {
    setSyncingWallets(prev => new Set(prev).add(id))
    try {
      await walletsApi.sync(id)
      // Refresh wallets after sync
      await fetchWallets()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to sync wallet')
      console.error('Error syncing wallet:', err)
    } finally {
      setSyncingWallets(prev => {
        const newSet = new Set(prev)
        newSet.delete(id)
        return newSet
      })
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Wallets</h1>
          <p className="text-gray-600 mt-1">
            Manage your crypto wallets and sync transactions
          </p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          Add Wallet
        </Button>
      </div>

      {/* Plan Limit Warning */}
      {user?.plan === 'free' && wallets.length >= 1 && (
        <Card className="p-4 bg-yellow-50 border-yellow-200">
          <p className="text-yellow-800 text-sm">
            You've reached the free plan limit of 1 wallet.{' '}
            <a href="/pricing" className="font-medium underline">
              Upgrade to Starter or Pro
            </a>{' '}
            to add more wallets.
          </p>
        </Card>
      )}

      {/* Wallets List */}
      {wallets.length === 0 ? (
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
                d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
              />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No wallets added yet
          </h3>
          <p className="text-gray-600 mb-4">
            Add your first wallet to start tracking your crypto transactions and tax calculations.
          </p>
          <Button onClick={() => setIsModalOpen(true)}>
            Add Your First Wallet
          </Button>
        </Card>
      ) : (
        <WalletList
          wallets={wallets}
          onDelete={handleDeleteWallet}
          onSync={handleSyncWallet}
          syncingWallets={syncingWallets}
        />
      )}

      {/* Add Wallet Modal */}
      <AddWalletModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onAdd={handleAddWallet}
        currentPlan={user?.plan || 'free'}
        currentWalletCount={wallets.length}
      />
    </div>
  )
}