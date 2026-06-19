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
    <div className="p-6">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-text-primary">Dashboard</h1>
            <p className="text-text-secondary">Your crypto portfolio overview</p>
          </div>
          <button
            onClick={() => setIsAddModalOpen(true)}
            className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary/80 transition-colors"
          >
            Add Wallet
          </button>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <PortfolioCard
          title="Portfolio Value"
          value={0}
          subtitle="Total portfolio value"
        />
        
        <PortfolioCard
          title="Total Gain/Loss"
          value={0}
          subtitle="All-time performance"
        />
        
        <PortfolioCard
          title="Connected Wallets"
          value={0}
          valuePrefix=""
          subtitle="Total wallets connected"
        />
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Your Wallets</h2>
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