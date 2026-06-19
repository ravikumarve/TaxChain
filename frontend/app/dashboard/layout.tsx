'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import PlanBadge from '@/components/payments/PlanBadge'
import UpgradeModal from '@/components/payments/UpgradeModal'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [userEmail, setUserEmail] = useState<string>('')
  const [currentPlan, setCurrentPlan] = useState<string>('free')
  const [isUpgradeModalOpen, setIsUpgradeModalOpen] = useState(false)
  const router = useRouter()

  useEffect(() => {
    const token = localStorage.getItem('accessToken')
    if (!token) {
      router.push('/auth/login')
      return
    }

    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      setUserEmail(payload.sub || '')
    } catch (error) {
      console.error('Error decoding token:', error)
    }

    const fetchPlan = async () => {
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
        console.error('Failed to fetch plan:', error)
      }
    }

    fetchPlan()
  }, [router])

  const handleLogout = () => {
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    router.push('/auth/login')
  }

  const handleUpgrade = async (plan: string) => {
    try {
      const token = localStorage.getItem('accessToken')
      const provider = 'razorpay'

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/payments/create-order`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ plan, provider }),
      })

      if (!response.ok) {
        throw new Error('Failed to create payment order')
      }

      const data = await response.json()

      if (provider === 'razorpay') {
        const options = {
          key: data.key_id,
          amount: data.amount,
          currency: data.currency,
          name: 'TaxChain',
          description: `${plan.charAt(0).toUpperCase() + plan.slice(1)} Plan`,
          order_id: data.order_id,
          handler: function (response: any) {
            window.location.reload()
          },
          prefill: { name: '', email: userEmail, contact: '' },
          theme: { color: '#6366F1' },
        }

        // @ts-ignore - Razorpay is loaded via script
        const rzp = new Razorpay(options)
        rzp.open()
      }
    } catch (error) {
      console.error('Upgrade failed:', error)
      alert('Failed to initiate upgrade. Please try again.')
    }
  }

  return (
    <div className="flex h-screen bg-void">
      {/* Sidebar */}
      <div className="w-64 bg-panel border-r border-border-dim text-sidebar-text flex flex-col">
        <div className="p-6">
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center justify-center w-7 h-7 bg-indigo-500/20 border border-indigo-500/40 rounded text-indigo-300 font-bold text-xs">
              #TC
            </span>
            <h1 className="text-lg font-semibold text-main">TaxChain</h1>
          </div>
          {userEmail && (
            <p className="text-xs text-muted mt-2 font-mono">{userEmail}</p>
          )}
          <div className="mt-4">
            <PlanBadge
              currentPlan={currentPlan}
              showUpgradeButton={currentPlan !== 'pro'}
              onUpgradeClick={() => setIsUpgradeModalOpen(true)}
            />
          </div>
        </div>

        <nav className="mt-2 flex-1 px-3">
          <ul className="space-y-1">
            {[
              { href: '/dashboard', label: 'Dashboard' },
              { href: '/dashboard/wallets', label: 'Wallets' },
              { href: '/dashboard/transactions', label: 'Transactions' },
              { href: '/dashboard/tax', label: 'Tax Report' },
              { href: '/dashboard/reports', label: 'Export' },
            ].map((item) => (
              <li key={item.href}>
                <a
                  href={item.href}
                  className="block px-3 py-2 rounded-lg text-sm text-muted hover:text-main hover:bg-indigo-500/10 transition-colors font-mono tracking-wide"
                >
                  {item.label}
                </a>
              </li>
            ))}
          </ul>
        </nav>

        <div className="p-4 border-t border-border-dim">
          <button
            onClick={handleLogout}
            className="w-full px-3 py-2 text-sm text-muted hover:text-main hover:bg-indigo-500/10 rounded-lg transition-colors text-left font-mono tracking-wide"
          >
            Sign Out
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 overflow-auto bg-void">
        {children}
      </div>

      <UpgradeModal
        isOpen={isUpgradeModalOpen}
        onClose={() => setIsUpgradeModalOpen(false)}
        currentPlan={currentPlan}
        onUpgrade={handleUpgrade}
      />
    </div>
  )
}
