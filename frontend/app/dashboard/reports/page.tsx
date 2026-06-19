'use client'

import { useState } from 'react'
import { useAppStore } from '@/store/useAppStore'
import { taxApi } from '@/lib/api'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'

export default function ReportsPage() {
  const { user } = useAppStore()
  const [selectedYear, setSelectedYear] = useState<string>('')
  const [downloading, setDownloading] = useState<string | null>(null)
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
  useState(() => {
    const currentYear = new Date().getFullYear()
    const currentFY = `${currentYear}-${String(currentYear + 1).slice(-2)}`
    setSelectedYear(currentFY)
  })

  const handleDownload = async (type: 'csv' | 'pdf' | 'itr') => {
    // Check plan permissions
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
      let filename
      let contentType

      switch (type) {
        case 'csv':
          response = await taxApi.generateCSV(selectedYear)
          filename = `taxchain_report_${selectedYear}_${new Date().getTime()}.csv`
          contentType = 'text/csv'
          break
        case 'pdf':
          response = await taxApi.generatePDF(selectedYear)
          filename = `taxchain_tax_report_${selectedYear}_${new Date().getTime()}.pdf`
          contentType = 'application/pdf'
          break
        case 'itr':
          response = await taxApi.generateITR(selectedYear)
          filename = `itr_schedule_vda_${selectedYear}_${new Date().getTime()}.csv`
          contentType = 'text/csv'
          break
      }

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data], { type: contentType }))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (err: any) {
      setError(err.response?.data?.detail || `Failed to generate ${type.toUpperCase()} report`)
      console.error(`Error generating ${type} report:`, err)
    } finally {
      setDownloading(null)
    }
  }

  const getPlanBadge = (requiredPlan: 'free' | 'starter' | 'pro') => {
    const planColors = {
      free: 'bg-gray-100 text-gray-800',
      starter: 'bg-blue-100 text-blue-800',
      pro: 'bg-purple-100 text-purple-800',
    }

    const currentPlan = user?.plan || 'free'
    const isAccessible = ['free', 'starter', 'pro'].indexOf(currentPlan) >= ['free', 'starter', 'pro'].indexOf(requiredPlan)

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${planColors[requiredPlan]}`}>
        {requiredPlan.charAt(0).toUpperCase() + requiredPlan.slice(1)} {isAccessible ? '' : '+'}
      </span>
    )
  }

  const isFeatureAccessible = (requiredPlan: 'free' | 'starter' | 'pro') => {
    const currentPlan = user?.plan || 'free'
    const planHierarchy = ['free', 'starter', 'pro']
    return planHierarchy.indexOf(currentPlan) >= planHierarchy.indexOf(requiredPlan)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Export Reports</h1>
        <p className="text-gray-600 mt-1">
          Download comprehensive tax reports in various formats
        </p>
      </div>

      {/* Financial Year Selector */}
      <Card className="p-6">
        <div className="flex items-center gap-4">
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
      </Card>

      {/* Error Message */}
      {error && (
        <Card className="p-4 bg-red-50 border-red-200">
          <p className="text-red-800 text-sm">{error}</p>
        </Card>
      )}

      {/* Export Options */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* CSV Export */}
        <Card className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-green-100 rounded-lg">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">CSV Report</h3>
                {getPlanBadge('starter')}
              </div>
            </div>
          </div>

          <p className="text-sm text-gray-600 mb-4">
            Comprehensive transaction report with tax calculations, gain/loss analysis, and cost basis details.
          </p>

          <ul className="text-sm text-gray-600 space-y-2 mb-4">
            <li className="flex items-center gap-2">
              <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Transaction details
            </li>
            <li className="flex items-center gap-2">
              <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Tax calculations
            </li>
            <li className="flex items-center gap-2">
              <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Gain/loss analysis
            </li>
          </ul>

          <Button
            onClick={() => handleDownload('csv')}
            disabled={downloading === 'csv' || !isFeatureAccessible('starter')}
            className="w-full"
            variant={isFeatureAccessible('starter') ? 'primary' : 'outline'}
          >
            {downloading === 'csv' ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Generating...
              </>
            ) : isFeatureAccessible('starter') ? (
              'Download CSV'
            ) : (
              'Upgrade Required'
            )}
          </Button>
        </Card>

        {/* PDF Export */}
        <Card className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-red-100 rounded-lg">
                <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">PDF Report</h3>
                {getPlanBadge('starter')}
              </div>
            </div>
          </div>

          <p className="text-sm text-gray-600 mb-4">
            Professional PDF report with executive summary, detailed breakdown, and methodology explanation.
          </p>

          <ul className="text-sm text-gray-600 space-y-2 mb-4">
            <li className="flex items-center gap-2">
              <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Professional formatting
            </li>
            <li className="flex items-center gap-2">
              <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Executive summary
            </li>
            <li className="flex items-center gap-2">
              <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Print-ready format
            </li>
          </ul>

          <Button
            onClick={() => handleDownload('pdf')}
            disabled={downloading === 'pdf' || !isFeatureAccessible('starter')}
            className="w-full"
            variant={isFeatureAccessible('starter') ? 'primary' : 'outline'}
          >
            {downloading === 'pdf' ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Generating...
              </>
            ) : isFeatureAccessible('starter') ? (
              'Download PDF'
            ) : (
              'Upgrade Required'
            )}
          </Button>
        </Card>

        {/* ITR Export */}
        <Card className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-purple-100 rounded-lg">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">ITR Schedule VDA</h3>
                {getPlanBadge('pro')}
              </div>
            </div>
          </div>

          <p className="text-sm text-gray-600 mb-4">
            Official Indian tax filing format for Virtual Digital Assets. Ready for ITR submission.
          </p>

          <ul className="text-sm text-gray-600 space-y-2 mb-4">
            <li className="flex items-center gap-2">
              <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              ITR-compliant format
            </li>
            <li className="flex items-center gap-2">
              <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              INR conversion
            </li>
            <li className="flex items-center gap-2">
              <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Tax-ready data
            </li>
          </ul>

          <Button
            onClick={() => handleDownload('itr')}
            disabled={downloading === 'itr' || !isFeatureAccessible('pro')}
            className="w-full"
            variant={isFeatureAccessible('pro') ? 'primary' : 'outline'}
          >
            {downloading === 'itr' ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Generating...
              </>
            ) : isFeatureAccessible('pro') ? (
              'Download ITR VDA'
            ) : (
              'Pro Required'
            )}
          </Button>
        </Card>
      </div>

      {/* Plan Information */}
      <Card className="p-6 bg-gradient-to-r from-indigo-50 to-purple-50 border-indigo-200">
        <h3 className="font-semibold text-gray-900 mb-3">Plan Features</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <h4 className="font-medium text-gray-700 mb-2">Free Plan</h4>
            <ul className="text-gray-600 space-y-1">
              <li>• 1 wallet</li>
              <li>• ETH chain only</li>
              <li>• Current FY data</li>
              <li className="text-red-600">• No exports</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-gray-700 mb-2">Starter Plan ($9/mo)</h4>
            <ul className="text-gray-600 space-y-1">
              <li>• 3 wallets</li>
              <li>• ETH, BNB, Polygon</li>
              <li>• 3 years history</li>
              <li className="text-green-600">• CSV + PDF exports</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-gray-700 mb-2">Pro Plan ($19/mo)</h4>
            <ul className="text-gray-600 space-y-1">
              <li>• Unlimited wallets</li>
              <li>• All chains</li>
              <li>• Full history</li>
              <li className="text-green-600">• All exports + ITR VDA</li>
            </ul>
          </div>
        </div>
        <div className="mt-4 pt-4 border-t border-indigo-200">
          <Button
            onClick={() => (window.location.href = '/pricing')}
            variant="outline"
            className="text-sm"
          >
            View Pricing Plans
          </Button>
        </div>
      </Card>
    </div>
  )
}