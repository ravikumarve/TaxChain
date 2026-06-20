'use client'

import { useState, useEffect, useCallback } from 'react'
import { Card } from '@/components/ui/Card'
import api from '@/lib/api'

interface MethodOption {
  id: string
  label: string
  description: string
}

const METHODS: MethodOption[] = [
  {
    id: 'fifo',
    label: 'FIFO',
    description: 'First In, First Out — Default method. Oldest lots sold first.',
  },
  {
    id: 'lifo',
    label: 'LIFO',
    description: 'Last In, First Out — Newest lots sold first. Higher cost basis → lower gains.',
  },
  {
    id: 'hifo',
    label: 'HIFO',
    description: 'Highest Cost, First Out — Highest-cost lots sold first. Minimizes taxable gains.',
  },
  {
    id: 'avg_cost',
    label: 'Avg Cost',
    description: 'Average Cost Basis — Smooths cost across all lots. Simple but not accepted by all jurisdictions.',
  },
]

export default function SettingsPage() {
  const [currentMethod, setCurrentMethod] = useState<string>('fifo')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null)

  const fetchMethod = useCallback(async () => {
    try {
      setLoading(true)
      const response = await api.get('/settings/cost-basis-method')
      setCurrentMethod(response.data.method)
    } catch (err) {
      console.error('Failed to fetch cost basis method:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchMethod()
  }, [fetchMethod])

  const handleSelect = async (method: string) => {
    if (method === currentMethod) return

    setSaving(true)
    setToast(null)
    try {
      const response = await api.put('/settings/cost-basis-method', { method })
      setCurrentMethod(response.data.method)
      setToast({ type: 'success', message: `Method updated to ${method.toUpperCase()}. ${response.data.events_recalculated} tax events recalculated.` })
    } catch (err: any) {
      setToast({ type: 'error', message: err?.response?.data?.detail || 'Failed to update method' })
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-main">Settings</h1>
        <p className="text-muted text-sm mt-1">Configure your cost basis accounting method</p>
      </div>

      {/* Toast */}
      {toast && (
        <div className={`px-4 py-3 rounded-lg text-sm ${
          toast.type === 'success'
            ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-300'
            : 'bg-red-500/10 border border-red-500/20 text-red-300'
        }`}>
          {toast.message}
        </div>
      )}

      {loading ? (
        <Card className="bg-surface border-border-dim p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-indigo-500/10 rounded w-1/3" />
            <div className="h-12 bg-indigo-500/10 rounded" />
            <div className="h-12 bg-indigo-500/10 rounded" />
            <div className="h-12 bg-indigo-500/10 rounded" />
          </div>
        </Card>
      ) : (
        <Card className="bg-surface border-border-dim p-6">
          <h2 className="text-lg font-semibold text-main mb-1">Cost Basis Method</h2>
          <p className="text-sm text-muted mb-6">
            Select how gains and losses are calculated when you sell or trade crypto assets.
            Changing this method will recalculate all your tax events.
          </p>

          {saving && (
            <div className="mb-4 px-4 py-3 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-sm flex items-center gap-2">
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Recalculating tax events...
            </div>
          )}

          <div className="grid gap-3">
            {METHODS.map((method) => (
              <button
                key={method.id}
                onClick={() => handleSelect(method.id)}
                disabled={saving}
                className={`w-full text-left px-4 py-3 rounded-lg border transition-colors ${
                  currentMethod === method.id
                    ? 'border-indigo-500/50 bg-indigo-500/10'
                    : 'border-border-dim bg-void hover:border-indigo-500/30'
                } ${saving ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <span className="text-sm font-semibold text-main">{method.label}</span>
                    <p className="text-xs text-muted mt-0.5">{method.description}</p>
                  </div>
                  {currentMethod === method.id && (
                    <span className="inline-flex items-center justify-center w-5 h-5 rounded-full bg-indigo-500">
                      <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                      </svg>
                    </span>
                  )}
                </div>
              </button>
            ))}
          </div>

          <div className="mt-6 p-3 rounded-lg bg-void border border-border-dim">
            <p className="text-xs text-faint">
              <span className="font-semibold text-muted">Note:</span> Average Cost is not accepted by all tax jurisdictions.
              Check with your local tax authority before using this method.
            </p>
          </div>
        </Card>
      )}
    </div>
  )
}
