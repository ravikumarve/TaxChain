'use client'

import { useState } from 'react'
import { useAppStore } from '@/store/useAppStore'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import AddWalletModal from '@/components/wallets/AddWalletModal'
import WalletList from '@/components/wallets/WalletList'

export default function WalletsPage() {
  const { user } = useAppStore()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  const handleWalletAdded = () => {
    setIsModalOpen(false)
    setRefreshTrigger(n => n + 1)
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
      {user?.plan === 'free' && (
        <Card className="p-4 bg-yellow-50 border-yellow-200">
          <p className="text-yellow-800 text-sm">
            Free plan limited to 1 wallet.{' '}
            <a href="/pricing" className="font-medium underline">
              Upgrade to Starter or Pro
            </a>{' '}
            to add more wallets.
          </p>
        </Card>
      )}

      {/* Wallets List */}
      <WalletList refreshTrigger={refreshTrigger} />

      {/* Add Wallet Modal */}
      <AddWalletModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onWalletAdded={handleWalletAdded}
      />
    </div>
  )
}
