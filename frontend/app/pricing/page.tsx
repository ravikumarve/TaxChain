'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

const plans = [
  {
    name: 'Free',
    price: { inr: 0, usd: 0 },
    description: 'Perfect for getting started',
    features: [
      '1 wallet',
      'Ethereum only',
      'Current financial year',
      'Basic portfolio tracking',
    ],
    limitations: [
      'No CSV export',
      'No PDF reports',
      'No ITR Schedule VDA',
    ],
    cta: 'Current Plan',
    popular: false,
  },
  {
    name: 'Starter',
    price: { inr: 749, usd: 9 },
    description: 'For serious crypto investors',
    features: [
      '3 wallets',
      'Ethereum, BNB, Polygon',
      '3 years history',
      'CSV export',
      'Basic portfolio tracking',
    ],
    limitations: [
      'No PDF reports',
      'No ITR Schedule VDA',
    ],
    cta: 'Upgrade to Starter',
    popular: true,
  },
  {
    name: 'Pro',
    price: { inr: 1599, usd: 19 },
    description: 'Complete tax solution',
    features: [
      'Unlimited wallets',
      'All chains (ETH, BNB, Polygon, Sol)',
      '10 years history',
      'CSV export',
      'PDF reports',
      'India ITR Schedule VDA',
      'Priority support',
    ],
    limitations: [],
    cta: 'Upgrade to Pro',
    popular: false,
  },
]

export default function PricingPage() {
  const router = useRouter()
  const [currentPlan, setCurrentPlan] = useState('free')
  const [loading, setLoading] = useState(true)
  const [country, setCountry] = useState('IN') // Default to India

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('accessToken')
    if (!token) {
      router.push('/auth/login')
      return
    }

    // Get user's current plan
    const fetchCurrentPlan = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/payments/subscription-status`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        })

        if (response.ok) {
          const data = await response.json()
          setCurrentPlan(data.plan)
        }
      } catch (error) {
        console.error('Failed to fetch current plan:', error)
      } finally {
        setLoading(false)
      }
    }

    // Detect user's country (simplified)
    const detectCountry = () => {
      // In production, use a proper IP geolocation service
      // For now, default to India
      setCountry('IN')
    }

    fetchCurrentPlan()
    detectCountry()
  }, [router])

  const handleUpgrade = async (plan: string) => {
    try {
      const token = localStorage.getItem('accessToken')
      
      // Determine provider based on country
      const provider = country === 'IN' ? 'razorpay' : 'lemonsqueezy'
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/payments/create-order`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          plan,
          provider,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to create payment order')
      }

      const data = await response.json()

      if (provider === 'razorpay') {
        // Initialize Razorpay checkout
        const options = {
          key: data.key_id,
          amount: data.amount,
          currency: data.currency,
          name: 'TaxChain',
          description: `${plan.charAt(0).toUpperCase() + plan.slice(1)} Plan`,
          order_id: data.order_id,
          handler: function (response: any) {
            // Payment successful
            console.log('Payment successful:', response)
            // Refresh page to update plan
            window.location.reload()
          },
          prefill: {
            name: '',
            email: '',
            contact: '',
          },
          theme: {
            color: '#6366F1',
          },
        }

        // @ts-ignore - Razorpay is loaded via script
        const rzp = new Razorpay(options)
        rzp.open()
      } else {
        // Redirect to Lemon Squeezy checkout
        window.location.href = data.checkout_url
      }
    } catch (error) {
      console.error('Upgrade failed:', error)
      alert('Failed to initiate upgrade. Please try again.')
    }
  }

  const formatPrice = (price: { inr: number; usd: number }) => {
    if (country === 'IN') {
      return `₹${price.inr}/mo`
    }
    return `$${price.usd}/mo`
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Pricing</h1>
              <p className="mt-2 text-gray-600">Choose the perfect plan for your crypto tax needs</p>
            </div>
            <button
              onClick={() => router.push('/dashboard')}
              className="text-gray-600 hover:text-gray-900"
            >
              ← Back to Dashboard
            </button>
          </div>
        </div>
      </div>

      {/* Pricing Cards */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map((plan) => {
            const isCurrentPlan = plan.name.toLowerCase() === currentPlan
            const canUpgrade = !isCurrentPlan && currentPlan !== 'pro'

            return (
              <div
                key={plan.name}
                className={`relative bg-white rounded-2xl shadow-sm border-2 ${
                  plan.popular ? 'border-primary ring-2 ring-primary ring-opacity-50' : 'border-gray-200'
                } ${isCurrentPlan ? 'opacity-75' : ''}`}
              >
                {plan.popular && (
                  <div className="absolute top-0 right-0 -mt-3 -mr-3">
                    <span className="bg-primary text-white text-xs font-semibold px-3 py-1 rounded-full">
                      Most Popular
                    </span>
                  </div>
                )}

                <div className="p-8">
                  <h3 className="text-2xl font-bold text-gray-900">{plan.name}</h3>
                  <p className="mt-2 text-gray-600">{plan.description}</p>
                  
                  <div className="mt-6">
                    <span className="text-4xl font-bold text-gray-900">
                      {formatPrice(plan.price)}
                    </span>
                  </div>

                  <ul className="mt-8 space-y-4">
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
                    {plan.limitations.map((limitation) => (
                      <li key={limitation} className="flex items-start">
                        <svg
                          className="h-5 w-5 text-red-400 mt-0.5 mr-3 flex-shrink-0"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M6 18L18 6M6 6l12 12"
                          />
                        </svg>
                        <span className="text-gray-500">{limitation}</span>
                      </li>
                    ))}
                  </ul>

                  <button
                    onClick={() => isCurrentPlan ? null : handleUpgrade(plan.name.toLowerCase())}
                    disabled={!canUpgrade}
                    className={`mt-8 w-full py-3 px-4 rounded-lg font-semibold transition-colors ${
                      isCurrentPlan
                        ? 'bg-gray-100 text-gray-500 cursor-not-allowed'
                        : canUpgrade
                        ? 'bg-primary text-white hover:bg-primary/90'
                        : 'bg-gray-100 text-gray-500 cursor-not-allowed'
                    }`}
                  >
                    {isCurrentPlan ? 'Current Plan' : plan.cta}
                  </button>
                </div>
              </div>
            )
          })}
        </div>

        {/* FAQ Section */}
        <div className="mt-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-8">Frequently Asked Questions</h2>
          
          <div className="space-y-4">
            {[
              {
                question: 'Can I change my plan later?',
                answer: 'Yes! You can upgrade or downgrade your plan at any time. When upgrading, you\'ll be charged the prorated difference. When downgrading, the new rate applies at the next billing cycle.',
              },
              {
                question: 'What payment methods do you accept?',
                answer: 'For Indian users, we accept UPI, cards, net banking, and wallets via Razorpay. For international users, we accept all major credit cards via Lemon Squeezy.',
              },
              {
                question: 'Is my data secure?',
                answer: 'Absolutely! We use bank-level encryption and never store your private keys. Your wallet data is read-only and used solely for tax calculations.',
              },
              {
                question: 'Can I cancel my subscription?',
                answer: 'Yes, you can cancel anytime. Your plan remains active until the end of your current billing period, so you won\'t lose access immediately.',
              },
              {
                question: 'Do you offer refunds?',
                answer: 'We offer a 7-day money-back guarantee. If you\'re not satisfied with TaxChain, contact support within 7 days of purchase for a full refund.',
              },
            ].map((faq, index) => (
              <div key={index} className="bg-white rounded-lg border border-gray-200 p-6">
                <h3 className="font-semibold text-gray-900 mb-2">{faq.question}</h3>
                <p className="text-gray-600">{faq.answer}</p>
              </div>
            ))}
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-16 text-center bg-gradient-to-r from-primary to-purple-600 rounded-2xl p-12">
          <h2 className="text-3xl font-bold text-white mb-4">Ready to simplify your crypto taxes?</h2>
          <p className="text-white/80 mb-8 max-w-2xl mx-auto">
            Join thousands of crypto investors who trust TaxChain for accurate tax calculations and hassle-free reporting.
          </p>
          <button
            onClick={() => router.push('/auth/signup')}
            className="bg-white text-primary font-semibold px-8 py-3 rounded-lg hover:bg-gray-100 transition-colors"
          >
            Get Started Free
          </button>
        </div>
      </div>
    </div>
  )
}