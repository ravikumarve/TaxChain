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
    // Check if user is authenticated
    const token = localStorage.getItem('accessToken')
    if (!token) {
      router.push('/auth/login')
      return
    }

    // Extract email from token (simple decode for display)
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      setUserEmail(payload.sub || '')
    } catch (error) {
      console.error('Error decoding token:', error)
    }

    // Fetch current plan
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
      
      // Determine provider based on user location (simplified)
      const provider = 'razorpay' // Default to Razorpay for India
      
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
            email: userEmail,
            contact: '',
          },
          theme: {
            color: '#6366F1',
          },
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
    <div className="flex h-screen bg-bg-secondary">
      {/* Sidebar */}
      <div className="w-64 bg-sidebar-bg text-sidebar-text flex flex-col">
        <div className="p-6">
          <h1 className="text-xl font-bold">TaxChain</h1>
          {userEmail && (
            <p className="text-sm text-sidebar-text/60 mt-1">{userEmail}</p>
          )}
          <div className="mt-4">
            <PlanBadge
              currentPlan={currentPlan}
              showUpgradeButton={currentPlan !== 'pro'}
              onUpgradeClick={() => setIsUpgradeModalOpen(true)}
            />
          </div>
        </div>
        
        <nav className="mt-6 flex-1">
          <ul className="space-y-2">
            <li>
              <a href="/dashboard" className="block px-6 py-2 text-sidebar-text/80 hover:text-sidebar-text hover:bg-sidebar-bg/50">
                Dashboard
              </a>
            </li>
            <li>
              <a href="/dashboard/wallets" className="block px-6 py-2 text-sidebar-text/80 hover:text-sidebar-text hover:bg-sidebar-bg/50">
                Wallets
              </a>
            </li>
            <li>
              <a href="/dashboard/transactions" className="block px-6 py-2 text-sidebar-text/80 hover:text-sidebar-text hover:bg-sidebar-bg/50">
                Transactions
              </a>
            </li>
            <li>
              <a href="/dashboard/tax" className="block px-6 py-2 text-sidebar-text/80 hover:text-sidebar-text hover:bg-sidebar-bg/50">
                Tax Report
              </a>
            </li>
            <li>
              <a href="/dashboard/reports" className="block px-6 py-2 text-sidebar-text/80 hover:text-sidebar-text hover:bg-sidebar-bg/50">
                Export
              </a>
            </li>
          </ul>
        </nav>

        {/* Logout button */}
        <div className="p-4">
          <button
            onClick={handleLogout}
            className="w-full px-6 py-2 text-sidebar-text/80 hover:text-sidebar-text hover:bg-sidebar-bg/50 text-left"
          >
            Sign Out
          </button>
        </div>
      </div>
      
      {/* Main content */}
      <div className="flex-1 overflow-auto bg-bg-primary">
        {children}
      </div>

      {/* Upgrade Modal */}
      <UpgradeModal
        isOpen={isUpgradeModalOpen}
        onClose={() => setIsUpgradeModalOpen(false)}
        currentPlan={currentPlan}
        onUpgrade={handleUpgrade}
      />
    </div>
  )
}