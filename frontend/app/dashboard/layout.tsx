'use client'

import { useEffect, useState } from 'react'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [userEmail, setUserEmail] = useState<string>('')

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('accessToken')
    if (!token) {
      window.location.href = '/auth/login'
      return
    }

    // Extract email from token (simple decode for display)
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      setUserEmail(payload.sub || '')
    } catch (error) {
      console.error('Error decoding token:', error)
    }
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    window.location.href = '/auth/login'
  }

  return (
    <div className="flex h-screen bg-bg-secondary">
      {/* Sidebar */}
      <div className="w-64 bg-sidebar-bg text-sidebar-text">
        <div className="p-6">
          <h1 className="text-xl font-bold">TaxChain</h1>
          {userEmail && (
            <p className="text-sm text-sidebar-text/60 mt-1">{userEmail}</p>
          )}
        </div>
        
        <nav className="mt-6">
          <ul className="space-y-2">
            <li>
              <a href="/dashboard" className="block px-6 py-2 text-sidebar-text/80 hover:text-sidebar-text hover:bg-sidebar-bg/50">
                Dashboard
              </a>
            </li>
            <li>
              <a href="#" className="block px-6 py-2 text-sidebar-text/80 hover:text-sidebar-text hover:bg-sidebar-bg/50">
                Wallets
              </a>
            </li>
            <li>
              <a href="#" className="block px-6 py-2 text-sidebar-text/80 hover:text-sidebar-text hover:bg-sidebar-bg/50">
                Transactions
              </a>
            </li>
            <li>
              <a href="#" className="block px-6 py-2 text-sidebar-text/80 hover:text-sidebar-text hover:bg-sidebar-bg/50">
                Tax Report
              </a>
            </li>
            <li>
              <a href="#" className="block px-6 py-2 text-sidebar-text/80 hover:text-sidebar-text hover:bg-sidebar-bg/50">
                Export
              </a>
            </li>
          </ul>
        </nav>

        {/* Logout button */}
        <div className="absolute bottom-4 left-4 right-4">
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
    </div>
  )
}