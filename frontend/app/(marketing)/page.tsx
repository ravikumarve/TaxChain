export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            TaxChain
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Multi-wallet, multi-chain crypto tax calculations and portfolio tracking
          </p>
          <div className="space-x-4">
            <button className="bg-indigo-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-colors">
              Get Started
            </button>
            <button className="border border-gray-300 text-gray-700 px-8 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors">
              View Demo
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}