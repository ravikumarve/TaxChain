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

  // Generate available financial years (current year + 4 previous years)
  const getAvailableYears = () => {
    const currentYear = new Date().getFullYear()
    const years = []
    for (let i = 0; i < 5; i++) {
      const year = currentYear - i
      years.push(`${year}-${String(year + 1).slice(-2)}`)
    }
    return years
  }

  const availableYears = getAvailableYears()

  // Set default to current financial year
  useEffect(() => {
    const currentYear = new Date().getFullYear()
    const currentFY = `${currentYear}-${String(currentYear + 1).slice(-2)}`
    setSelectedYear(currentFY)
  }, [])

  // Fetch tax summary when year changes
  useEffect(() => {
    if (selectedYear) {
      fetchTaxSummary()
    }
  }, [selectedYear])

  const fetchTaxSummary = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await taxApi.summary(selectedYear)
      setTaxSummary(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch tax summary')
      console.error('Error fetching tax summary:', err)
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value)
  }

  const formatNumber = (value: number) => {
    return new Intl.NumberFormat('en-US').format(value)
  }

  const getGainLossColor = (value: number) => {
    return value >= 0 ? 'text-green-600' : 'text-red-600'
  }

  const getGainLossIcon = (value: number) => {
    return value >= 0 ? '↑' : '↓'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Tax Summary</h1>
          <p className="text-gray-600 mt-1">
            View your capital gains and losses by financial year
          </p>
        </div>

        {/* Financial Year Selector */}
        <div className="flex items-center gap-2">
          <label htmlFor="year-select" className="text-sm font-medium text-gray-700">
            Financial Year:
          </label>
          <select
            id="year-select"
            value={selectedYear}
            onChange={(e) => setSelectedYear(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
          >
            {availableYears.map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <Card className="p-6 bg-red-50 border-red-200">
          <p className="text-red-800">{error}</p>
          <Button
            onClick={fetchTaxSummary}
            className="mt-4"
            variant="outline"
          >
            Retry
          </Button>
        </Card>
      )}

      {/* Tax Summary Content */}
      {!loading && !error && taxSummary && (
        <div className="space-y-6">
          {/* Overall Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Total Gain/Loss */}
            <Card className="p-6">
              <h3 className="text-sm font-medium text-gray-600 mb-2">
                Total Gain/Loss
              </h3>
              <div className={`text-3xl font-bold ${getGainLossColor(taxSummary.total_gain_loss_usd)}`}>
                {getGainLossIcon(taxSummary.total_gain_loss_usd)}{' '}
                {formatCurrency(Math.abs(taxSummary.total_gain_loss_usd))}
              </div>
            </Card>

            {/* Short-Term Gain/Loss */}
            <Card className="p-6">
              <h3 className="text-sm font-medium text-gray-600 mb-2">
                Short-Term Gain/Loss
              </h3>
              <div className={`text-2xl font-bold ${getGainLossColor(taxSummary.short_term_gain_loss_usd)}`}>
                {getGainLossIcon(taxSummary.short_term_gain_loss_usd)}{' '}
                {formatCurrency(Math.abs(taxSummary.short_term_gain_loss_usd))}
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Held less than 365 days
              </p>
            </Card>

            {/* Long-Term Gain/Loss */}
            <Card className="p-6">
              <h3 className="text-sm font-medium text-gray-600 mb-2">
                Long-Term Gain/Loss
              </h3>
              <div className={`text-2xl font-bold ${getGainLossColor(taxSummary.long_term_gain_loss_usd)}`}>
                {getGainLossIcon(taxSummary.long_term_gain_loss_usd)}{' '}
                {formatCurrency(Math.abs(taxSummary.long_term_gain_loss_usd))}
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Held 365 days or more
              </p>
            </Card>
          </div>

          {/* Transaction Summary */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Transaction Summary
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Total Transactions</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatNumber(taxSummary.transaction_count)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Tax Events Calculated</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatNumber(taxSummary.tax_event_count)}
                </p>
              </div>
            </div>

            {taxSummary.date_range && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Period:</span>{' '}
                  {new Date(taxSummary.date_range.start_date).toLocaleDateString()} -{' '}
                  {new Date(taxSummary.date_range.end_date).toLocaleDateString()}
                </p>
              </div>
            )}
          </Card>

          {/* Token Breakdown */}
          {taxSummary.token_breakdown && taxSummary.token_breakdown.length > 0 && (
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Token Breakdown
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">
                        Token
                      </th>
                      <th className="text-right py-3 px-4 text-sm font-medium text-gray-600">
                        Total Gain/Loss
                      </th>
                      <th className="text-right py-3 px-4 text-sm font-medium text-gray-600">
                        Short-Term
                      </th>
                      <th className="text-right py-3 px-4 text-sm font-medium text-gray-600">
                        Long-Term
                      </th>
                      <th className="text-right py-3 px-4 text-sm font-medium text-gray-600">
                        Transactions
                      </th>
                      <th className="text-right py-3 px-4 text-sm font-medium text-gray-600">
                        Tax Events
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {taxSummary.token_breakdown.map((token, index) => (
                      <tr
                        key={index}
                        className="border-b border-gray-100 hover:bg-gray-50"
                      >
                        <td className="py-3 px-4">
                          <span className="font-medium text-gray-900">
                            {token.token_symbol}
                          </span>
                        </td>
                        <td className={`py-3 px-4 text-right font-medium ${getGainLossColor(token.total_gain_loss_usd)}`}>
                          {formatCurrency(token.total_gain_loss_usd)}
                        </td>
                        <td className={`py-3 px-4 text-right ${getGainLossColor(token.short_term_gain_loss_usd)}`}>
                          {formatCurrency(token.short_term_gain_loss_usd)}
                        </td>
                        <td className={`py-3 px-4 text-right ${getGainLossColor(token.long_term_gain_loss_usd)}`}>
                          {formatCurrency(token.long_term_gain_loss_usd)}
                        </td>
                        <td className="py-3 px-4 text-right text-gray-600">
                          {formatNumber(token.transaction_count)}
                        </td>
                        <td className="py-3 px-4 text-right text-gray-600">
                          {formatNumber(token.tax_event_count)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          )}

          {/* Empty State */}
          {taxSummary.transaction_count === 0 && (
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
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No transactions found
              </h3>
              <p className="text-gray-600 mb-4">
                There are no transactions for this financial year. Add wallets and sync
                transactions to see your tax summary.
              </p>
              <Button onClick={() => (window.location.href = '/dashboard/wallets')}>
                Add Wallets
              </Button>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}