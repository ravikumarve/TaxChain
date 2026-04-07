export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-gray-900 text-white">
        <div className="p-6">
          <h1 className="text-xl font-bold">TaxChain</h1>
        </div>
        
        <nav className="mt-6">
          <ul className="space-y-2">
            <li>
              <a href="/dashboard" className="block px-6 py-2 text-gray-300 hover:text-white hover:bg-gray-800">
                Dashboard
              </a>
            </li>
            <li>
              <a href="/dashboard/wallets" className="block px-6 py-2 text-gray-300 hover:text-white hover:bg-gray-800">
                Wallets
              </a>
            </li>
            <li>
              <a href="/dashboard/transactions" className="block px-6 py-2 text-gray-300 hover:text-white hover:bg-gray-800">
                Transactions
              </a>
            </li>
            <li>
              <a href="/dashboard/tax" className="block px-6 py-2 text-gray-300 hover:text-white hover:bg-gray-800">
                Tax Report
              </a>
            </li>
            <li>
              <a href="/dashboard/reports" className="block px-6 py-2 text-gray-300 hover:text-white hover:bg-gray-800">
                Export
              </a>
            </li>
          </ul>
        </nav>
      </div>
      
      {/* Main content */}
      <div className="flex-1 overflow-auto">
        {children}
      </div>
    </div>
  )
}