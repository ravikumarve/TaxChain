import Link from 'next/link'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            TaxChain
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Automated Crypto Tax Calculations • Multi-Chain Support • Professional Tax Reports
          </p>
          <div className="space-x-4 mb-16">
            <Link href="/auth/login" className="bg-indigo-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-colors">
              Get Started
            </Link>
            <Link href="/dashboard" className="border border-gray-300 text-gray-700 px-8 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors">
              View Demo
            </Link>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="bg-white rounded-lg p-6 shadow-md">
              <div className="text-indigo-600 text-2xl mb-4">💰</div>
              <h3 className="font-semibold text-lg mb-2">Multi-Chain Portfolio</h3>
              <p className="text-gray-600">Track ETH, BNB, Polygon, Solana all in one dashboard</p>
            </div>
            
            <div className="bg-white rounded-lg p-6 shadow-md">
              <div className="text-indigo-600 text-2xl mb-4">📊</div>
              <h3 className="font-semibold text-lg mb-2">Automated Tax Calculations</h3>
              <p className="text-gray-600">FIFO cost basis methodology with proper lot tracking</p>
            </div>
            
            <div className="bg-white rounded-lg p-6 shadow-md">
              <div className="text-indigo-600 text-2xl mb-4">📄</div>
              <h3 className="font-semibold text-lg mb-2">Professional Reports</h3>
              <p className="text-gray-600">CSV, PDF, and India ITR Schedule VDA export formats</p>
            </div>
          </div>

          {/* Trust Indicators */}
          <div className="mt-16">
            <p className="text-gray-500 text-sm mb-4">TRUSTED BY CRYPTO INVESTORS WORLDWIDE</p>
            <div className="flex justify-center items-center space-x-8 text-gray-400">
              <span>🔒 Read-Only Security</span>
              <span>⚡ Real-Time Sync</span>
              <span>💯 Decimal Precision</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}