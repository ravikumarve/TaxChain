'use client'

import { Card, CardContent } from '@/components/ui/Card'

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)
}

function formatCompact(value: number): string {
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(2)}M`
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`
  return value.toLocaleString('en-US')
}

interface StatCardProps {
  label: string
  value: string
  subtitle?: string
  trend?: { value: number; isPositive: boolean }
  isLoading?: boolean
}

function StatCard({ label, value, subtitle, trend, isLoading }: StatCardProps) {
  if (isLoading) {
    return (
      <Card className="bg-panel border-border-dim">
        <CardContent className="p-4">
          <div className="h-3 w-20 bg-surface rounded animate-pulse mb-3" />
          <div className="h-7 w-28 bg-surface rounded animate-pulse mb-2" />
          <div className="h-3 w-16 bg-surface rounded animate-pulse" />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="bg-panel border-border-dim">
      <CardContent className="p-4">
        <p className="text-xs font-medium text-muted uppercase tracking-wider">
          {label}
        </p>
        <p className="text-xl font-bold text-main mt-1 font-mono">
          {value}
        </p>
        {subtitle && (
          <p className="text-xs text-faint mt-1">{subtitle}</p>
        )}
        {trend && (
          <p
            className={`text-xs font-medium mt-1 ${
              trend.isPositive ? 'text-gain' : 'text-loss'
            }`}
          >
            {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value).toFixed(2)}%
          </p>
        )}
      </CardContent>
    </Card>
  )
}

interface PortfolioSummaryProps {
  total_value_usd: number
  unrealized_pnl_usd: number
  unrealized_pnl_percent: number
  wallet_count: number
  transaction_count: number
  source: string
  isLoading?: boolean
}

export function PortfolioSummary({
  total_value_usd,
  unrealized_pnl_usd,
  unrealized_pnl_percent,
  wallet_count,
  transaction_count,
  source,
  isLoading = false,
}: PortfolioSummaryProps) {
  const pnlIsPositive = unrealized_pnl_usd >= 0

  return (
    <div className="space-y-3">
      {/* Simulated data badge */}
      {source === 'simulated' && (
        <div className="flex items-center gap-2 text-xs text-muted">
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-surface border border-border-dim">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
            Simulated data — sync wallets to see live
          </span>
        </div>
      )}

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Total Value"
          value={formatCurrency(total_value_usd)}
          subtitle="USD portfolio value"
          isLoading={isLoading}
        />
        <StatCard
          label="Unrealized P&L"
          value={`${pnlIsPositive ? '+' : ''}${formatCurrency(unrealized_pnl_usd)}`}
          trend={{ value: unrealized_pnl_percent, isPositive: pnlIsPositive }}
          subtitle="Unrealized gain/loss"
          isLoading={isLoading}
        />
        <StatCard
          label="Wallets"
          value={formatCompact(wallet_count)}
          subtitle="Connected wallets"
          isLoading={isLoading}
        />
        <StatCard
          label="Transactions"
          value={formatCompact(transaction_count)}
          subtitle="Total transactions"
          isLoading={isLoading}
        />
      </div>
    </div>
  )
}
