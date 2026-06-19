'use client'

import { useState } from 'react'
import { PortfolioCard } from '@/components/dashboard/PortfolioCard'
import WalletList from '@/components/wallets/WalletList'
import AddWalletModal from '@/components/wallets/AddWalletModal'

export default function DashboardPage() {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  const handleWalletAdded = () => {
    setRefreshTrigger(prev => prev + 1)
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-main">Dashboard</h1>
          <p className="text-muted text-sm mt-1">Your crypto portfolio overview</p>
        </div>
        <button
          onClick={() => setIsAddModalOpen(true)}
          className="btn btn-primary text-xs py-2 px-4"
        >
          + Add Wallet
        </button>
      </div>

      {/* Portfolio Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <PortfolioCard title="Portfolio Value" value={0} subtitle="Total portfolio value" />
        <PortfolioCard title="Total Gain/Loss" value={0} subtitle="All-time performance" />
        <PortfolioCard title="Connected Wallets" value={0} valuePrefix="" subtitle="Total wallets connected" />
      </div>

      {/* Wallet List */}
      <div className="bg-surface border border-border-dim rounded-xl p-6">
        <h2 className="text-lg font-semibold text-main mb-4">Your Wallets</h2>
        <WalletList refreshTrigger={refreshTrigger} />
      </div>

      <AddWalletModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onWalletAdded={handleWalletAdded}
      />
    </div>
  )
}
