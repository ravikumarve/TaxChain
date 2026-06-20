'use client'

import { useState, useEffect, useCallback } from 'react'
import { walletsApi } from '@/lib/api'
import { PortfolioSummary } from '@/components/dashboard/PortfolioSummary'
import { AllocationChart } from '@/components/dashboard/AllocationChart'
import { PnlTimelineChart } from '@/components/dashboard/PnlTimelineChart'
import { TopMovers } from '@/components/dashboard/TopMovers'
import WalletList from '@/components/wallets/WalletList'
import AddWalletModal from '@/components/wallets/AddWalletModal'
import { ChainBadge } from '@/components/dashboard/ChainBadge'
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

interface LpPosition {
  chain: string
  token_symbol: string
  total_deposited: number
  total_withdrawn: number
  net_quantity: number
  deposit_count: number
  withdrawal_count: number
  is_active: boolean
  last_activity: string
}

interface BorrowedPosition {
  chain: string
  token_symbol: string
  net_borrowed: number
  is_active: boolean
}

interface YieldFarmPosition {
  chain: string
  token_symbol: string
  total_deposited: number
  deposit_count: number
  last_deposit: string
}

interface LendingData {
  borrowed_positions: BorrowedPosition[]
  total_active_borrows: number
}

interface DefiPositions {
  lp_positions: LpPosition[]
  lending: LendingData
  yield_farms: YieldFarmPosition[]
  total_positions: number
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
  const [defiPositions, setDefiPositions] = useState<DefiPositions | null>(null)

  const fetchPortfolio = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await walletsApi.portfolio()
      setPortfolio(response.data)

      const defiResp = await walletsApi.defiPositions()
      setDefiPositions(defiResp.data)
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

          {/* DeFi Positions */}
          {defiPositions && defiPositions.total_positions > 0 && (
            <Card className="bg-surface border-border-dim">
              <div className="p-6">
                <h2 className="text-lg font-semibold text-main mb-4">DeFi Positions ({defiPositions.total_positions})</h2>

                {/* LP Positions */}
                {defiPositions.lp_positions.length > 0 && (
                  <div className="mb-4">
                    <p className="text-xs text-muted font-mono uppercase tracking-wider mb-2">Liquidity Pools</p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {defiPositions.lp_positions.filter(p => p.is_active).map((pos, i) => (
                        <div key={i} className="bg-void border border-border-dim rounded-lg p-3">
                          <div className="flex items-start justify-between">
                            <div>
                              <ChainBadge chain={pos.chain} />
                              <p className="text-sm font-semibold text-main mt-1">{pos.token_symbol}</p>
                            </div>
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-emerald-500/15 text-emerald-300">Active</span>
                          </div>
                          <div className="mt-2 grid grid-cols-2 gap-2">
                            <div>
                              <p className="text-xs text-muted">Net Liquidity</p>
                              <p className="text-sm font-mono text-main">{pos.net_quantity.toFixed(6)}</p>
                            </div>
                            <div>
                              <p className="text-xs text-muted">Deposits / Withdrawals</p>
                              <p className="text-sm font-mono text-main">{pos.deposit_count} / {pos.withdrawal_count}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Lending Positions */}
                {defiPositions.lending.borrowed_positions.filter(p => p.is_active).length > 0 && (
                  <div className="mb-4">
                    <p className="text-xs text-muted font-mono uppercase tracking-wider mb-2">Borrowed Assets</p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {defiPositions.lending.borrowed_positions.filter(p => p.is_active).map((pos, i) => (
                        <div key={i} className="bg-void border border-border-dim rounded-lg p-3">
                          <div className="flex items-start justify-between">
                            <div>
                              <ChainBadge chain={pos.chain} />
                              <p className="text-sm font-semibold text-main mt-1">{pos.token_symbol}</p>
                            </div>
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-red-500/15 text-red-300">Borrowed</span>
                          </div>
                          <p className="text-xs text-muted mt-2">Net Borrowed</p>
                          <p className="text-sm font-mono text-loss">{pos.net_borrowed.toFixed(6)}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Yield Farms */}
                {defiPositions.yield_farms.length > 0 && (
                  <div>
                    <p className="text-xs text-muted font-mono uppercase tracking-wider mb-2">Yield Farms</p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {defiPositions.yield_farms.map((pos, i) => (
                        <div key={i} className="bg-void border border-border-dim rounded-lg p-3">
                          <div className="flex items-start justify-between">
                            <div>
                              <ChainBadge chain={pos.chain} />
                              <p className="text-sm font-semibold text-main mt-1">{pos.token_symbol}</p>
                            </div>
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-purple-500/15 text-purple-300">Farming</span>
                          </div>
                          <p className="text-xs text-muted mt-2">Total Deposited</p>
                          <p className="text-sm font-mono text-main">{pos.total_deposited.toFixed(6)}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </Card>
          )}

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
