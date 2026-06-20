'use client'

import { useState, useEffect, useCallback } from 'react'
import { walletsApi } from '@/lib/api'
import { PortfolioSummary } from '@/components/dashboard/PortfolioSummary'
import { AllocationChart } from '@/components/dashboard/AllocationChart'
import { PnlTimelineChart } from '@/components/dashboard/PnlTimelineChart'
import { TopMovers } from '@/components/dashboard/TopMovers'
import WalletList from '@/components/wallets/WalletList'
import AddWalletModal from '@/components/wallets/AddWalletModal'
import { Card } from '@/components/ui/Card'

interface ChainBreakdownItem {
  chain: string
  value_usd: number
  percentage: number
}

interface TokenBreakdownItem {
  token_symbol: string
  value_usd: number
  percentage: number
  quantity: number
}

interface TimelinePoint {
  date: string
  value_usd: number
}

interface MoverItem {
  token_symbol: string
  pnl_usd: number
  pnl_percent: number
  chain: string
}

interface PortfolioData {
  total_value_usd: number
  total_cost_basis_usd: number
  unrealized_pnl_usd: number
  unrealized_pnl_percent: number
  wallet_count: number
  transaction_count: number
  chain_breakdown: ChainBreakdownItem[]
  token_breakdown: TokenBreakdownItem[]
  pnl_timeline: TimelinePoint[]
  top_movers: MoverItem[]
  source: string
}

const EMPTY_PORTFOLIO: PortfolioData = {
  total_value_usd: 0,
  total_cost_basis_usd: 0,
  unrealized_pnl_usd: 0,
  unrealized_pnl_percent: 0,
  wallet_count: 0,
  transaction_count: 0,
  chain_breakdown: [],
  token_breakdown: [],
  pnl_timeline: [],
  top_movers: [],
  source: 'simulated',
}

export default function DashboardPage() {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  const [refreshTrigger, setRefreshTrigger] = useState(0)
  const [portfolio, setPortfolio] = useState<PortfolioData>(EMPTY_PORTFOLIO)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchPortfolio = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await walletsApi.portfolio()
      setPortfolio(response.data)
    } catch (err: any) {
      console.error('Failed to fetch portfolio:', err)
      setError(err?.response?.data?.detail || err?.message || 'Failed to load portfolio')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchPortfolio()
  }, [fetchPortfolio])

  const handleWalletAdded = () => {
    setRefreshTrigger((prev) => prev + 1)
    fetchPortfolio()
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

      {/* Error state */}
      {error && (
        <Card className="bg-panel border-border-dim p-6">
          <div className="text-center">
            <p className="text-loss text-sm mb-3">{error}</p>
            <button
              onClick={fetchPortfolio}
              className="btn btn-outline text-xs py-2 px-4"
            >
              Retry
            </button>
          </div>
        </Card>
      )}

      {/* Loading state */}
      {loading && !error && (
        <PortfolioSummary
          total_value_usd={0}
          unrealized_pnl_usd={0}
          unrealized_pnl_percent={0}
          wallet_count={0}
          transaction_count={0}
          source="simulated"
          isLoading={true}
        />
      )}

      {/* Portfolio data */}
      {!loading && !error && (
        <>
          <PortfolioSummary
            total_value_usd={portfolio.total_value_usd}
            unrealized_pnl_usd={portfolio.unrealized_pnl_usd}
            unrealized_pnl_percent={portfolio.unrealized_pnl_percent}
            wallet_count={portfolio.wallet_count}
            transaction_count={portfolio.transaction_count}
            source={portfolio.source}
          />

          <AllocationChart
            chainBreakdown={portfolio.chain_breakdown}
            tokenBreakdown={portfolio.token_breakdown}
          />

          <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
            <div className="lg:col-span-3">
              <PnlTimelineChart data={portfolio.pnl_timeline} />
            </div>
            <div className="lg:col-span-2">
              <TopMovers movers={portfolio.top_movers} />
            </div>
          </div>

          {/* Wallet List */}
          <Card className="bg-panel border-border-dim">
            <div className="p-6">
              <h2 className="text-lg font-semibold text-main mb-4">Your Wallets</h2>
              <WalletList refreshTrigger={refreshTrigger} />
            </div>
          </Card>
        </>
      )}

      <AddWalletModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onWalletAdded={handleWalletAdded}
      />
    </div>
  )
}
