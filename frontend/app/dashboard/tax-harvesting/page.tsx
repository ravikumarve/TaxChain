'use client'

import { useState, useEffect, useCallback } from 'react'
import api from '@/lib/api'
import { Card } from '@/components/ui/Card'

interface LossItem {
  token_symbol: string
  quantity: number
  loss_amount_usd: number
  proceeds_usd: number
  cost_basis_usd: number
  disposed_at: string
  is_short_term: boolean
  tax_event_id: string
}

interface WashSale {
  token_symbol: string
  sale_date: string
  loss_amount_usd: number
  buy_date: string
  buy_quantity: number
  days_apart: number
  is_wash: boolean
  loss_disallowed: boolean
}

interface Recommendation {
  type: string
  token_symbol: string
  loss_amount_usd: number
  action: string
  priority: string
}

interface ExpiringLoss {
  token_symbol: string
  loss_amount_usd: number
  acquired_at: string
  disposed_at: string
  holding_period_days: number
  days_until_long_term: number
  action: string
}

interface HarvestingReport {
  summary: {
    total_realized_gains: number
    total_realized_losses: number
    net_gain_loss: number
    harvesting_potential: number
  }
  realized_losses: LossItem[]
  wash_sales: WashSale[]
  recommendations: Recommendation[]
  expiring_losses: ExpiringLoss[]
}

const EMPTY_REPORT: HarvestingReport = {
  summary: { total_realized_gains: 0, total_realized_losses: 0, net_gain_loss: 0, harvesting_potential: 0 },
  realized_losses: [],
  wash_sales: [],
  recommendations: [],
  expiring_losses: [],
}

export default function TaxHarvestingPage() {
  const [report, setReport] = useState<HarvestingReport>(EMPTY_REPORT)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchReport = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.get('/reports/tax-loss-harvesting')
      setReport(response.data)
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to fetch tax-loss harvesting report')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchReport()
  }, [fetchReport])

  const formatUSD = (v: number) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 2 }).format(v)

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-main">Tax-Loss Harvesting</h1>
        <p className="text-muted text-sm mt-1">Identify opportunities to offset gains and minimize your tax liability</p>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-400" />
        </div>
      )}

      {error && (
        <Card className="p-4 bg-loss/10 border border-loss/20">
          <p className="text-loss text-sm">{error}</p>
          <button onClick={fetchReport} className="mt-2 text-xs text-indigo-400 hover:text-indigo-300">Retry</button>
        </Card>
      )}

      {!loading && !error && (
        <>
          {/* Summary Banner */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <Card className="bg-surface border-border-dim p-4">
              <p className="text-xs text-muted font-mono uppercase tracking-wider">Realized Gains</p>
              <p className="text-xl font-semibold font-mono text-gain mt-1">{formatUSD(report.summary.total_realized_gains)}</p>
            </Card>
            <Card className="bg-surface border-border-dim p-4">
              <p className="text-xs text-muted font-mono uppercase tracking-wider">Realized Losses</p>
              <p className="text-xl font-semibold font-mono text-loss mt-1">{formatUSD(report.summary.total_realized_losses)}</p>
            </Card>
            <Card className="bg-surface border-border-dim p-4">
              <p className="text-xs text-muted font-mono uppercase tracking-wider">Net Gain/Loss</p>
              <p className={`text-xl font-semibold font-mono mt-1 ${report.summary.net_gain_loss >= 0 ? 'text-main' : 'text-loss'}`}>
                {formatUSD(report.summary.net_gain_loss)}
              </p>
            </Card>
            <Card className="bg-surface border-border-dim p-4">
              <p className="text-xs text-muted font-mono uppercase tracking-wider">Harvesting Potential</p>
              <p className="text-xl font-semibold font-mono text-indigo-300 mt-1">{formatUSD(report.summary.harvesting_potential)}</p>
            </Card>
          </div>

          {/* Realized Losses Table */}
          {report.realized_losses.length > 0 && (
            <Card className="bg-surface border-border-dim overflow-hidden">
              <div className="p-4 border-b border-border-dim">
                <h2 className="text-sm font-semibold text-main">Realized Losses</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-void">
                    <tr>
                      {['Token', 'Loss Amount', 'Proceeds', 'Cost Basis', 'Date', 'Term'].map((h) => (
                        <th key={h} className="px-4 py-2 text-left text-xs font-medium text-faint uppercase tracking-wider font-mono">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border-dim">
                    {report.realized_losses.map((loss, i) => (
                      <tr key={i} className="hover:bg-indigo-500/5">
                        <td className="px-4 py-3 text-sm font-mono text-main">{loss.token_symbol}</td>
                        <td className="px-4 py-3 text-sm font-mono text-loss">{formatUSD(loss.loss_amount_usd)}</td>
                        <td className="px-4 py-3 text-sm font-mono text-main">{formatUSD(loss.proceeds_usd)}</td>
                        <td className="px-4 py-3 text-sm font-mono text-main">{formatUSD(loss.cost_basis_usd)}</td>
                        <td className="px-4 py-3 text-sm text-muted">{new Date(loss.disposed_at).toLocaleDateString()}</td>
                        <td className="px-4 py-3">
                          <span className={`text-xs px-2 py-0.5 rounded-full ${loss.is_short_term ? 'bg-red-500/15 text-red-300' : 'bg-yellow-500/15 text-yellow-300'}`}>
                            {loss.is_short_term ? 'Short' : 'Long'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          )}

          {/* Wash Sales */}
          {report.wash_sales.length > 0 && (
            <Card className="bg-surface border border-loss/30 overflow-hidden">
              <div className="p-4 border-b border-loss/20">
                <h2 className="text-sm font-semibold text-loss flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.068 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                  Wash Sales Detected
                </h2>
              </div>
              <div className="divide-y divide-loss/10">
                {report.wash_sales.map((ws, i) => (
                  <div key={i} className="p-4 grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <p className="text-xs text-muted font-mono">Token</p>
                      <p className="text-sm font-mono text-main">{ws.token_symbol}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted font-mono">Disallowed Loss</p>
                      <p className="text-sm font-mono text-loss">{formatUSD(ws.loss_amount_usd)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted font-mono">Sale → Buy</p>
                      <p className="text-sm text-muted">{new Date(ws.sale_date).toLocaleDateString()} → {new Date(ws.buy_date).toLocaleDateString()}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted font-mono">Days Apart</p>
                      <p className="text-sm font-mono text-main">{ws.days_apart}d</p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Recommendations */}
          {report.recommendations.length > 0 && (
            <Card className="bg-surface border-border-dim">
              <div className="p-4 border-b border-border-dim">
                <h2 className="text-sm font-semibold text-main">Recommendations</h2>
              </div>
              <div className="divide-y divide-border-dim">
                {report.recommendations.map((rec, i) => (
                  <div key={i} className="p-4 flex items-start gap-3">
                    <span className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold flex-shrink-0 ${
                      rec.priority === 'high' ? 'bg-loss/15 text-loss' : 'bg-yellow-500/15 text-yellow-300'
                    }`}>
                      {rec.priority === 'high' ? '!' : 'i'}
                    </span>
                    <div>
                      <p className="text-sm text-main"><span className="font-semibold font-mono">{rec.token_symbol}</span> — {formatUSD(rec.loss_amount_usd)} loss</p>
                      <p className="text-xs text-muted mt-0.5">{rec.action}</p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Expiring Losses */}
          {report.expiring_losses.length > 0 && (
            <Card className="bg-surface border border-yellow-500/20">
              <div className="p-4 border-b border-yellow-500/10">
                <h2 className="text-sm font-semibold text-yellow-300 flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Expiring Losses — {report.expiring_losses.length} within 90 days of long-term
                </h2>
              </div>
              <div className="divide-y divide-yellow-500/10">
                {report.expiring_losses.map((el, i) => (
                  <div key={i} className="p-4 grid grid-cols-2 md:grid-cols-5 gap-4">
                    <div>
                      <p className="text-xs text-muted font-mono">Token</p>
                      <p className="text-sm font-mono text-main">{el.token_symbol}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted font-mono">Loss</p>
                      <p className="text-sm font-mono text-loss">{formatUSD(el.loss_amount_usd)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted font-mono">Held</p>
                      <p className="text-sm font-mono text-main">{el.holding_period_days}d</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted font-mono">Expires In</p>
                      <p className="text-sm font-mono text-yellow-300">{el.days_until_long_term}d</p>
                    </div>
                    <div className="md:col-span-1">
                      <p className="text-xs text-muted">{el.action}</p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {report.realized_losses.length === 0 && report.wash_sales.length === 0 && (
            <Card className="p-12 text-center bg-surface border-border-dim">
              <p className="text-muted text-sm">No tax-loss harvesting opportunities found for the current period.</p>
            </Card>
          )}
        </>
      )}
    </div>
  )
}
