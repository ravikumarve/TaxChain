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
    features: [
      '3 wallets',
      '3 chains (ETH, BNB, Polygon)',
      '3 years history',
      'CSV export',
    ],
  },
  {
    id: 'pro',
    name: 'Pro',
    price: { inr: '₹1,599', usd: '$19' },
    features: [
      'Unlimited wallets',
      'All chains including Solana',
      '10 years history',
      'CSV + PDF + ITR export',
      'Priority support',
    ],
  },
]

export default function UpgradeModal({ isOpen, onClose, currentPlan, onUpgrade }: UpgradeModalProps) {
  const [loading, setLoading] = useState(false)
  const [country, setCountry] = useState('IN') // Default to India

  if (!isOpen) return null

  const handleUpgrade = async (planId: string) => {
    setLoading(true)
    try {
      await onUpgrade(planId)
      onClose()
    } catch (error) {
      console.error('Upgrade failed:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Upgrade Your Plan</h2>
              <p className="text-gray-600 mt-1">
                Current plan: <span className="font-semibold capitalize">{currentPlan}</span>
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {plans.map((plan) => (
              <div
                key={plan.id}
                className="border-2 border-gray-200 rounded-lg p-6 hover:border-primary transition-colors"
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold text-gray-900">{plan.name}</h3>
                  <span className="text-2xl font-bold text-primary">
                    {country === 'IN' ? plan.price.inr : plan.price.usd}
                    <span className="text-sm font-normal text-gray-600">/mo</span>
                  </span>
                </div>

                <ul className="space-y-3 mb-6">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-start">
                      <svg
                        className="h-5 w-5 text-green-500 mt-0.5 mr-3 flex-shrink-0"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M5 13l4 4L19 7"
                        />
                      </svg>
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>

                <button
                  onClick={() => handleUpgrade(plan.id)}
                  disabled={loading}
                  className="w-full py-3 px-4 rounded-lg font-semibold bg-primary text-white hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Processing...' : `Upgrade to ${plan.name}`}
                </button>
              </div>
            ))}
          </div>

          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>Secure payment:</strong> We use Razorpay for Indian users and Lemon Squeezy for international users.
              Your payment information is never stored on our servers.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}