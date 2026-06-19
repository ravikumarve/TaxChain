'use client'

import { useState } from 'react'

interface UpgradeModalProps {
  isOpen: boolean
  onClose: () => void
  currentPlan: string
  onUpgrade: (plan: string) => void
}

const plans = [
  {
    id: 'starter',
    name: 'Starter',
    price: { inr: '₹749', usd: '$9' },
    features: ['3 wallets', '3 chains (ETH, BNB, Polygon)', '3 years history', 'CSV export', 'IRS / HMRC / ATO formats'],
  },
  {
    id: 'pro',
    name: 'Pro',
    price: { inr: '₹1,599', usd: '$19' },
    popular: true,
    features: ['Unlimited wallets', 'All 8 chains', '10 years history', 'CSV + PDF + ITR export', 'IRS / HMRC / ATO formats', 'Priority support'],
  },
]

export default function UpgradeModal({ isOpen, onClose, currentPlan, onUpgrade }: UpgradeModalProps) {
  const [loading, setLoading] = useState(false)
  const [country, setCountry] = useState('IN')

  if (!isOpen) return null

  const handleUpgrade = async (planId: string) => {
    setLoading(true)
    try {
      await onUpgrade(planId)
      onClose()
    } catch (error) {
      console.error('Upgrade failed:', error)
    } finally { setLoading(false) }
  }

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 backdrop-blur-sm">
      <div className="bg-panel border border-border-dim rounded-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto shadow-2xl">
        <div className="p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-main">Upgrade Your Plan</h2>
              <p className="text-muted mt-1">
                Current plan: <span className="font-semibold capitalize text-main">{currentPlan}</span>
              </p>
            </div>
            <button onClick={onClose} className="text-faint hover:text-muted transition-colors">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Currency toggle */}
          <div className="flex gap-2 mb-6">
            <button
              onClick={() => setCountry('IN')}
              className={`px-3 py-1.5 text-xs font-mono rounded-lg border transition-colors ${
                country === 'IN' ? 'bg-indigo-500/20 border-indigo-500/40 text-indigo-300' : 'border-border-dim text-muted hover:text-main'
              }`}
            >
              ₹ INR
            </button>
            <button
              onClick={() => setCountry('US')}
              className={`px-3 py-1.5 text-xs font-mono rounded-lg border transition-colors ${
                country === 'US' ? 'bg-indigo-500/20 border-indigo-500/40 text-indigo-300' : 'border-border-dim text-muted hover:text-main'
              }`}
            >
              $ USD
            </button>
          </div>

          {/* Plan cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {plans.map((plan) => (
              <div
                key={plan.id}
                className={`rounded-xl p-6 border transition-all duration-300 hover:border-indigo-500/40 ${
                  plan.popular ? 'border-indigo-500/30 bg-gradient-to-b from-indigo-500/5 to-transparent' : 'border-border-dim bg-surface'
                }`}
              >
                {plan.popular && (
                  <div className="text-[10px] font-mono tracking-widest text-indigo-400 uppercase mb-2">
                    Most Popular
                  </div>
                )}
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold text-main">{plan.name}</h3>
                  <span className="text-2xl font-bold text-indigo-400">
                    {country === 'IN' ? plan.price.inr : plan.price.usd}
                    <span className="text-sm font-normal text-muted">/mo</span>
                  </span>
                </div>

                <ul className="space-y-3 mb-6">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-3">
                      <svg className="h-5 w-5 text-emerald mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-sm text-muted">{feature}</span>
                    </li>
                  ))}
                </ul>

                <button
                  onClick={() => handleUpgrade(plan.id)}
                  disabled={loading}
                  className={`w-full py-3 px-4 rounded-lg font-semibold text-sm transition-all ${
                    plan.popular
                      ? 'bg-indigo-500 text-white hover:bg-indigo-600'
                      : 'bg-surface border border-border-dim text-muted hover:text-main hover:border-indigo-500/40'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  {loading ? 'Processing...' : `Upgrade to ${plan.name}`}
                </button>
              </div>
            ))}
          </div>

          {/* Secure payment notice */}
          <div className="mt-6 p-4 bg-indigo-500/10 border border-indigo-500/20 rounded-xl">
            <p className="text-sm text-indigo-300">
              <strong>Secure payment:</strong> We use Razorpay for Indian users and Lemon Squeezy for international users.
              Your payment information is never stored on our servers.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
