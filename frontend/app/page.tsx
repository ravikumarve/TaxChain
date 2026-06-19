'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function LandingPage() {
  const router = useRouter()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const handleGetStarted = () => {
    router.push('/auth/signup')
  }

  const handleViewPricing = () => {
    router.push('/pricing')
  }

  if (!mounted) {
    return null
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-primary">TaxChain</h1>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-600 hover:text-gray-900">
                Features
              </a>
              <a href="#pricing" className="text-gray-600 hover:text-gray-900">
                Pricing
              </a>
              <a href="#faq" className="text-gray-600 hover:text-gray-900">
                FAQ
              </a>
              <button
                onClick={() => router.push('/auth/login')}
                className="text-gray-600 hover:text-gray-900"
              >
                Sign In
              </button>
              <button
                onClick={handleGetStarted}
                className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary/90 transition-colors"
              >
                Get Started
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
              Simplify Your Crypto Taxes
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Track your portfolio across multiple wallets and chains. Calculate accurate capital gains using FIFO.
              Generate tax reports in minutes, not hours.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={handleGetStarted}
                className="bg-primary text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-primary/90 transition-colors"
              >
                Start Free Trial
              </button>
              <button
                onClick={handleViewPricing}
                className="bg-white text-primary border-2 border-primary px-8 py-4 rounded-lg text-lg font-semibold hover:bg-gray-50 transition-colors"
              >
                View Pricing
              </button>
            </div>
            <p className="mt-4 text-gray-500">No credit card required • Free forever for basic use</p>
          </div>

          {/* Hero Image/Graphic */}
          <div className="mt-16 relative">
            <div className="bg-gradient-to-br from-primary/10 to-purple-600/10 rounded-2xl p-8 border border-gray-200">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white rounded-lg p-6 shadow-sm">
                  <div className="text-3xl font-bold text-gray-900 mb-2">$0.00</div>
                  <div className="text-gray-600">Starting Price</div>
                </div>
                <div className="bg-white rounded-lg p-6 shadow-sm">
                  <div className="text-3xl font-bold text-gray-900 mb-2">10+</div>
                  <div className="text-gray-600">Blockchains Supported</div>
                </div>
                <div className="bg-white rounded-lg p-6 shadow-sm">
                  <div className="text-3xl font-bold text-gray-900 mb-2">100%</div>
                  <div className="text-gray-600">Tax Compliant</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Everything You Need</h2>
            <p className="text-xl text-gray-600">
              Powerful features to make crypto tax reporting effortless
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: '🔗',
                title: 'Multi-Wallet Support',
                description: 'Connect unlimited wallets across Ethereum, BNB Chain, Polygon, and Solana.',
              },
              {
                icon: '📊',
                title: 'Real-Time Portfolio Tracking',
                description: 'See your complete portfolio value and P&L in one dashboard.',
              },
              {
                icon: '🧮',
                title: 'FIFO Cost Basis',
                description: 'Accurate capital gains calculation using First-In-First-Out method.',
              },
              {
                icon: '📈',
                title: 'Tax Reports',
                description: 'Generate comprehensive tax reports with transaction-level details.',
              },
              {
                icon: '🇮🇳',
                title: 'India ITR Ready',
                description: 'Export in Schedule VDA format for seamless Indian tax filing.',
              },
              {
                icon: '🔒',
                title: 'Bank-Level Security',
                description: 'Your data is encrypted and secure. We never store private keys.',
              },
            ].map((feature, index) => (
              <div key={index} className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">How It Works</h2>
            <p className="text-xl text-gray-600">
              Get your tax reports in three simple steps
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                step: '1',
                title: 'Connect Your Wallets',
                description: 'Add your wallet addresses. We\'ll fetch your transaction history automatically.',
              },
              {
                step: '2',
                title: 'Review & Categorize',
                description: 'Review your transactions. Our AI categorizes trades, transfers, and more.',
              },
              {
                step: '3',
                title: 'Export Reports',
                description: 'Download your tax reports in CSV, PDF, or ITR format. File your taxes with confidence.',
              },
            ].map((item, index) => (
              <div key={index} className="text-center">
                <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl font-bold text-white">{item.step}</span>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{item.title}</h3>
                <p className="text-gray-600">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Preview */}
      <section id="pricing" className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Simple, Transparent Pricing</h2>
            <p className="text-xl text-gray-600">
              Choose the plan that fits your needs
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {[
              {
                name: 'Free',
                price: '$0',
                description: 'Perfect for getting started',
                features: ['1 wallet', 'Ethereum only', 'Current year'],
              },
              {
                name: 'Starter',
                price: '$9/mo',
                description: 'For serious investors',
                features: ['3 wallets', '3 chains', '3 years history', 'CSV export'],
                popular: true,
              },
              {
                name: 'Pro',
                price: '$19/mo',
                description: 'Complete solution',
                features: ['Unlimited wallets', 'All chains', '10 years history', 'PDF + ITR export'],
              },
            ].map((plan, index) => (
              <div
                key={index}
                className={`bg-white rounded-lg p-8 shadow-sm border-2 ${
                  plan.popular ? 'border-primary' : 'border-gray-200'
                }`}
              >
                {plan.popular && (
                  <div className="text-center mb-4">
                    <span className="bg-primary text-white text-sm font-semibold px-3 py-1 rounded-full">
                      Most Popular
                    </span>
                  </div>
                )}
                <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                <p className="text-gray-600 mb-4">{plan.description}</p>
                <div className="text-4xl font-bold text-gray-900 mb-6">{plan.price}</div>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-center text-gray-700">
                      <svg
                        className="h-5 w-5 text-green-500 mr-3"
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
                      {feature}
                    </li>
                  ))}
                </ul>
                <button
                  onClick={handleViewPricing}
                  className="w-full py-3 px-4 rounded-lg font-semibold bg-primary text-white hover:bg-primary/90 transition-colors"
                >
                  Get Started
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Frequently Asked Questions</h2>
          </div>

          <div className="space-y-6">
            {[
              {
                question: 'Is TaxChain secure?',
                answer: 'Yes! We use bank-level encryption and never store your private keys. Your wallet data is read-only and used solely for tax calculations.',
              },
              {
                question: 'Which blockchains do you support?',
                answer: 'We support Ethereum, BNB Chain, Polygon, and Solana. More chains are coming soon.',
              },
              {
                question: 'How accurate are the tax calculations?',
                answer: 'Our FIFO cost basis calculator is rigorously tested and follows standard tax accounting practices. However, we recommend consulting a tax professional for specific advice.',
              },
              {
                question: 'Can I export my data?',
                answer: 'Yes! Starter and Pro plans can export data in CSV format. Pro users also get PDF reports and India ITR Schedule VDA format.',
              },
              {
                question: 'Do you offer refunds?',
                answer: 'We offer a 7-day money-back guarantee. If you\'re not satisfied, contact support within 7 days for a full refund.',
              },
            ].map((faq, index) => (
              <div key={index} className="bg-gray-50 rounded-lg p-6">
                <h3 className="font-semibold text-gray-900 mb-2">{faq.question}</h3>
                <p className="text-gray-600">{faq.answer}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-primary to-purple-600">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-white mb-4">
            Ready to Simplify Your Crypto Taxes?
          </h2>
          <p className="text-xl text-white/80 mb-8">
            Join thousands of crypto investors who trust TaxChain for accurate tax calculations.
          </p>
          <button
            onClick={handleGetStarted}
            className="bg-white text-primary px-8 py-4 rounded-lg text-lg font-semibold hover:bg-gray-100 transition-colors"
          >
            Get Started Free
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-2xl font-bold mb-4">TaxChain</h3>
              <p className="text-gray-400">
                Simplifying crypto taxes for everyone.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#features" className="hover:text-white">Features</a></li>
                <li><a href="#pricing" className="hover:text-white">Pricing</a></li>
                <li><a href="#faq" className="hover:text-white">FAQ</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">About</a></li>
                <li><a href="#" className="hover:text-white">Blog</a></li>
                <li><a href="#" className="hover:text-white">Contact</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-white">Terms of Service</a></li>
              </ul>
            </div>
          </div>
          <div className="mt-12 pt-8 border-t border-gray-800 text-center text-gray-400">
            <p>&copy; 2024 TaxChain. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}