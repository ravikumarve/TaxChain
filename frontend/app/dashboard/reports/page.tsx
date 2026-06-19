'use client'

import { useState } from 'react'
import { useAppStore } from '@/store/useAppStore'
import { taxApi } from '@/lib/api'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'

type ExportType = 'csv' | 'pdf' | 'itr'

export default function ReportsPage() {
  const { user } = useAppStore()
  const [selectedYear, setSelectedYear] = useState('')
  const [downloading, setDownloading] = useState<ExportType | null>(null)
  const [error, setError] = useState<string | null>(null)

  const getAvailableYears = () => {
    const currentYear = new Date().getFullYear()
    return Array.from({ length: 5 }, (_, i) => {
      const year = currentYear - i
      return `${year}-${String(year + 1).slice(-2)}`
    })
  }

  const availableYears = getAvailableYears()

  // Set default year
  useState(() => {
    const currentYear = new Date().getFullYear()
    setSelectedYear(`${currentYear}-${String(currentYear + 1).slice(-2)}`)
  })

  const handleDownload = async (type: ExportType) => {
    if (type === 'itr' && user?.plan !== 'pro') {
      setError('ITR Schedule VDA export requires Pro plan. Please upgrade to access this feature.')
      return
    }
    if (type === 'pdf' && user?.plan === 'free') {
      setError('PDF export requires Starter plan or higher. Please upgrade to access this feature.')
      return
    }

    setDownloading(type)
    setError(null)

    try {
      let response
      let filename: string
      let contentType: string

      switch (type) {
        case 'csv':
          response = await taxApi.generateCSV(selectedYear)
          filename = `taxchain_report_${selectedYear}_${Date.now()}.csv`
          contentType = 'text/csv'
          break
        case 'pdf':
          response = await taxApi.generatePDF(selectedYear)
          filename = `taxchain_tax_report_${selectedYear}_${Date.now()}.pdf`
          contentType = 'application/pdf'
          break
        case 'itr':
          response = await taxApi.generateITR(selectedYear)
          filename = `itr_schedule_vda_${selectedYear}_${Date.now()}.csv`
          contentType = 'text/csv'
          break
      }

      const url = window.URL.createObjectURL(new Blob([response.data], { type: contentType }))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', filename!)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (err: any) {
      setError(err.response?.data?.detail || `Failed to generate ${type.toUpperCase()} report`)
    } finally { setDownloading(null) }
  }

  const planHierarchy = ['free', 'starter', 'pro']
  const currentPlan = user?.plan || 'free'
  const canAccess = (requiredPlan: 'free' | 'starter' | 'pro') =>
    planHierarchy.indexOf(currentPlan) >= planHierarchy.indexOf(requiredPlan)

  const PlanBadge = ({ requiredPlan }: { requiredPlan: string }) => {
    const colors: Record<string, string> = {
      free: 'bg-muted/10 text-muted',
      starter: 'bg-indigo-500/15 text-indigo-300',
      pro: 'bg-purple-500/15 text-purple-300',
    }
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[requiredPlan] || colors.free}`}>
        {requiredPlan.charAt(0).toUpperCase() + requiredPlan.slice(1)}
      </span>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-main">Export Reports</h1>
        <p className="text-muted text-sm mt-1">Download comprehensive tax reports in various formats</p>
      </div>

      {/* Year selector */}
      <Card className="p-4">
        <div className="flex items-center gap-4">
          <label htmlFor="year-select" className="text-sm font-medium text-muted">Financial Year:</label>
          <select
            id="year-select" value={selectedYear}
            onChange={(e) => setSelectedYear(e.target.value)}
            className="px-3 py-2 bg-surface border border-border-dim rounded-lg focus:ring-2 focus:ring-indigo-500/40 focus:border-indigo-500 text-sm text-main"
          >
            {availableYears.map(y => <option key={y} value={y}>{y}</option>)}
          </select>
        </div>
      </Card>

      {/* Error */}
      {error && (
        <Card className="p-4 bg-red-500/10 border border-red-500/20">
          <p className="text-red-300 text-sm">{error}</p>
        </Card>
      )}

      {/* Export cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {([
          { type: 'csv' as ExportType, title: 'CSV Report', plan: 'starter' as const, icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z', iconBg: 'bg-emerald-500/15', iconColor: 'text-emerald-400', features: ['Transaction details', 'Tax calculations', 'Gain/loss analysis'] },
          { type: 'pdf' as ExportType, title: 'PDF Report', plan: 'starter' as const, icon: 'M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z', iconBg: 'bg-red-500/15', iconColor: 'text-red-400', features: ['Professional formatting', 'Executive summary', 'Print-ready format'] },
          { type: 'itr' as ExportType, title: 'ITR Schedule VDA', plan: 'pro' as const, icon: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z', iconBg: 'bg-purple-500/15', iconColor: 'text-purple-400', features: ['ITR-compliant format', 'INR conversion', 'Tax-ready data'] },
        ]).map(({ type, title, plan, icon, iconBg, iconColor, features }) => {
          const accessible = canAccess(plan)
          return (
            <Card key={type} className="p-6 flex flex-col">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={`p-3 rounded-lg ${iconBg}`}>
                    <svg className={`w-6 h-6 ${iconColor}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={icon} />
                    </svg>
                  </div>
                  <div>
                    <h3 className="font-semibold text-main">{title}</h3>
                    <PlanBadge requiredPlan={plan} />
                  </div>
                </div>
              </div>

              <p className="text-sm text-muted mb-4 flex-1">
                {type === 'csv' && 'Comprehensive transaction report with tax calculations, gain/loss analysis, and cost basis details.'}
                {type === 'pdf' && 'Professional PDF report with executive summary, detailed breakdown, and methodology explanation.'}
                {type === 'itr' && 'Official Indian tax filing format for Virtual Digital Assets. Ready for ITR submission.'}
              </p>

              <ul className="text-sm text-muted space-y-2 mb-6">
                {features.map(f => (
                  <li key={f} className="flex items-center gap-2">
                    <svg className="w-4 h-4 text-emerald shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    {f}
                  </li>
                ))}
              </ul>

              <Button
                onClick={() => handleDownload(type)}
                disabled={downloading === type || !accessible}
                className="w-full"
                variant={accessible ? 'primary' : 'outline'}
              >
                {downloading === type ? (
                  <span className="flex items-center gap-2">
                    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Generating...
                  </span>
                ) : accessible ? (
                  `Download ${type === 'itr' ? 'ITR VDA' : type.toUpperCase()}`
                ) : (
                  'Upgrade Required'
                )}
              </Button>
            </Card>
          )
        })}
      </div>

      {/* Plan info */}
      <Card className="p-6 bg-gradient-to-r from-indigo-500/10 to-purple-500/10 border border-indigo-500/20">
        <h3 className="font-semibold text-main mb-4">Plan Features</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          {[
            { name: 'Free Plan', items: ['1 wallet', 'ETH chain only', 'Current FY data', 'No exports'], danger: true },
            { name: 'Starter ($9/mo)', items: ['3 wallets', 'ETH, BNB, Polygon', '3 years history', 'CSV + PDF exports'] },
            { name: 'Pro ($19/mo)', items: ['Unlimited wallets', 'All 8 chains', 'Full history', 'All exports + ITR VDA'] },
          ].map(plan => (
            <div key={plan.name}>
              <h4 className="font-medium text-main mb-2">{plan.name}</h4>
              <ul className="text-muted space-y-1">
                {plan.items.map((item, i) => (
                  <li key={i} className={i === plan.items.length - 1 && plan.danger ? 'text-loss' : ''}>
                    • {item}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <div className="mt-4 pt-4 border-t border-indigo-500/20">
          <a href="/pricing" className="btn btn-outline text-xs inline-flex">View Pricing Plans</a>
        </div>
      </Card>
    </div>
  )
}
