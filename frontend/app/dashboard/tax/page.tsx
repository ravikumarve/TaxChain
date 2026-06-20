'use client'

import { useState, useEffect } from 'react'
import { useAppStore } from '@/store/useAppStore'
import { taxApi } from '@/lib/api'
import { TaxSummary } from '@/types'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'

export default function TaxPage() {
  const { user } = useAppStore()
  const [taxSummary, setTaxSummary] = useState<TaxSummary | null>(null)
  const [selectedYear, setSelectedYear] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const getAvailableYears = () => {
    const currentYear = new Date().getFullYear()
    return Array.from({ length: 5 }, (_, i) => {
      const year = currentYear - i
      return `${year}-${String(year + 1).slice(-2)}`
    })
  }

  const availableYears = getAvailableYears()

  useEffect(() => {
    const currentYear = new Date().getFullYear()
    setSelectedYear(`${currentYear}-${String(currentYear + 1).slice(-2)}`)
  }, [])

  useEffect(() => { if (selectedYear) fetchTaxSummary() }, [selectedYear])

  const fetchTaxSummary = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await taxApi.summary(selectedYear)
      setTaxSummary(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch tax summary')
    } finally { setLoading(false) }
  }

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 2 }).format(value)

  const formatNumber = (value: number) =>
    new Intl.NumberFormat('en-US').format(value)

  const glColor = (value: number) => value >= 0 ? 'text-emerald' : 'text-loss'
  const glIcon = (value: number) => value >= 0 ? '↑' : '↓'

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-main">Tax Summary</h1>
          <p className="text-muted text-sm mt-1">View your capital gains and losses by financial year</p>
        </div>
        <div className="flex items-center gap-2">
          <label htmlFor="year-select" className="text-sm font-medium text-muted">Financial Year:</label>
          <select
            id="year-select" value={selectedYear}
            onChange={(e) => setSelectedYear(e.target.value)}
            className="px-3 py-2 bg-surface border border-border-dim rounded-lg focus:ring-2 focus:ring-indigo-500/40 focus:border-indigo-500 text-sm text-main"
          >
            {availableYears.map(y => <option key={y} value={y}>{y}</option>)}
          </select>
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-400" />
        </div>
      )}

      {/* Error */}
      {error && !loading && (
        <Card className="p-4 bg-red-500/10 border border-red-500/20">
          <p className="text-red-300 text-sm mb-3">{error}</p>
          <Button onClick={fetchTaxSummary} variant="outline" className="text-xs">Retry</Button>
        </Card>
      )}

      {/* Content */}
      {!loading && !error && taxSummary && (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { label: 'Total Gain/Loss', value: taxSummary.total_gain_loss_usd },
              { label: 'Short-Term Gain/Loss', value: taxSummary.short_term_gain_loss_usd, sub: 'Held less than 365 days' },
              { label: 'Long-Term Gain/Loss', value: taxSummary.long_term_gain_loss_usd, sub: 'Held 365 days or more' },
            ].map(item => (
              <Card key={item.label} className="p-6">
                <h3 className="text-sm font-medium text-muted mb-2">{item.label}</h3>
                <div className={`text-3xl font-bold ${glColor(item.value)}`}>
                  {glIcon(item.value)} {formatCurrency(Math.abs(item.value))}
                </div>
                {item.sub && <p className="text-xs text-faint mt-1">{item.sub}</p>}
              </Card>
            ))}
          </div>

          {/* Transaction Summary */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-main mb-4">Transaction Summary</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted">Total Transactions</p>
                <p className="text-2xl font-bold text-main">{formatNumber(taxSummary.transaction_count)}</p>
              </div>
              <div>
                <p className="text-sm text-muted">Tax Events Calculated</p>
                <p className="text-2xl font-bold text-main">{formatNumber(taxSummary.tax_event_count)}</p>
              </div>
            </div>
            {taxSummary.date_range && (
              <div className="mt-4 pt-4 border-t border-border-dim">
                <p className="text-sm text-muted">
                  <span className="font-medium text-main">Period:</span>{' '}
                  {new Date(taxSummary.date_range.start_date).toLocaleDateString()} —{' '}
                  {new Date(taxSummary.date_range.end_date).toLocaleDateString()}
                </p>
              </div>
            )}
          </Card>

          {/* Token Breakdown */}
          {taxSummary.token_breakdown && taxSummary.token_breakdown.length > 0 && (
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-main mb-4">Token Breakdown</h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border-dim">
                      {['Token', 'Total Gain/Loss', 'Short-Term', 'Long-Term', 'Transactions', 'Tax Events'].map(h => (
                        <th key={h} className="text-left py-3 px-4 text-sm font-medium text-faint font-mono">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {taxSummary.token_breakdown.map((token, i) => (
                      <tr key={i} className="border-b border-border-dim hover:bg-indigo-500/5 transition-colors">
                        <td className="py-3 px-4"><span className="font-medium text-main">{token.token_symbol}</span></td>
                        <td className={`py-3 px-4 text-right font-medium ${glColor(token.total_gain_loss_usd)}`}>{formatCurrency(token.total_gain_loss_usd)}</td>
                        <td className={`py-3 px-4 text-right ${glColor(token.short_term_gain_loss_usd)}`}>{formatCurrency(token.short_term_gain_loss_usd)}</td>
                        <td className={`py-3 px-4 text-right ${glColor(token.long_term_gain_loss_usd)}`}>{formatCurrency(token.long_term_gain_loss_usd)}</td>
                        <td className="py-3 px-4 text-right text-muted">{formatNumber(token.transaction_count)}</td>
                        <td className="py-3 px-4 text-right text-muted">{formatNumber(token.tax_event_count)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          )}

          {/* India Tax Summary */}
          {taxSummary.india_tax && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-main">India Tax Summary (Section 115BBH)</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-surface border border-border-dim rounded-xl p-4">
                  <span className="text-xs text-muted font-mono uppercase tracking-wider">Total Gains</span>
                  <p className="text-lg font-mono text-emerald font-semibold mt-1">
                    {'\u20B9'}{Number(taxSummary.india_tax.total_gains_inr).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </p>
                </div>
                <div className="bg-surface border border-border-dim rounded-xl p-4">
                  <span className="text-xs text-muted font-mono uppercase tracking-wider">Total Losses</span>
                  <p className="text-lg font-mono text-loss font-semibold mt-1">
                    {'\u20B9'}{Number(taxSummary.india_tax.total_losses_inr).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </p>
                  <span className="text-xs text-faint">Non-deductible per Indian tax law</span>
                </div>
                <div className="bg-surface border border-border-dim rounded-xl p-4">
                  <span className="text-xs text-muted font-mono uppercase tracking-wider">Estimated Tax (30%)</span>
                  <p className="text-lg font-mono text-main font-semibold mt-1">
                    {'\u20B9'}{Number(taxSummary.india_tax.estimated_tax_inr).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </p>
                </div>
                <div className="bg-surface border border-border-dim rounded-xl p-4">
                  <span className="text-xs text-muted font-mono uppercase tracking-wider">TDS Deducted</span>
                  <p className="text-lg font-mono text-indigo-400 font-semibold mt-1">
                    {'\u20B9'}{Number(taxSummary.india_tax.total_tds_deducted_inr).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </p>
                  <span className="text-xs text-faint">Credit available in ITR</span>
                </div>
              </div>
              <div className="bg-surface border border-amber-500/20 rounded-xl p-4">
                <div className="flex items-start gap-3">
                  <span className="text-amber-400 text-lg">⚠</span>
                  <div>
                    <p className="text-sm font-semibold text-main">Net Tax Due</p>
                    <p className="text-2xl font-mono text-main font-bold mt-1">
                      {'\u20B9'}{Number(taxSummary.india_tax.net_tax_due_inr).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </p>
                    <p className="text-xs text-faint mt-2">
                      {taxSummary.india_tax.loss_offsetting}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Empty */}
          {taxSummary.transaction_count === 0 && (
            <Card className="p-12 text-center">
              <div className="text-faint mb-4">
                <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-main mb-2">No transactions found</h3>
              <p className="text-muted text-sm mb-4">Add wallets and sync transactions to see your tax summary.</p>
              <Button onClick={() => (window.location.href = '/dashboard/wallets')}>Add Wallets</Button>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}
