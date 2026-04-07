export default function DashboardPage() {
  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Your crypto portfolio overview</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Portfolio Value</h3>
          <p className="text-3xl font-bold text-gray-900">$0.00</p>
          <p className="text-sm text-gray-600">Total portfolio value</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Total Gain/Loss</h3>
          <p className="text-3xl font-bold text-green-600">$0.00</p>
          <p className="text-sm text-gray-600">All-time performance</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Connected Wallets</h3>
          <p className="text-3xl font-bold text-gray-900">0</p>
          <p className="text-sm text-gray-600">Total wallets connected</p>
        </div>
      </div>
    </div>
  )
}