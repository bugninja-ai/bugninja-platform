import './App.css'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-400 via-pink-500 to-red-500">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto text-center">
          {/* Header */}
          <div className="mb-8">
            <div className="w-20 h-20 mx-auto mb-6 bg-white rounded-2xl flex items-center justify-center shadow-lg">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-600 to-blue-600 rounded-xl flex items-center justify-center">
                <div className="w-3 h-3 bg-white rounded-full mr-1"></div>
                <div className="w-3 h-3 bg-white rounded-full"></div>
              </div>
            </div>
            <h1 className="text-5xl font-bold text-white mb-4">
              Bugninja Platform
            </h1>
            <p className="text-xl text-white/90 max-w-2xl mx-auto">
              Fully automated AI-based testing that never sleeps. 
              Find bugs before they cost you money.
            </p>
          </div>

          {/* Status Cards */}
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <div className="w-12 h-12 bg-green-500 rounded-lg mx-auto mb-4 flex items-center justify-center">
                <div className="w-3 h-3 bg-white rounded-full"></div>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Frontend</h3>
              <p className="text-green-200">✅ Running</p>
            </div>

            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <div className="w-12 h-12 bg-red-500 rounded-lg mx-auto mb-4 flex items-center justify-center">
                <div className="w-6 h-1 bg-white rounded"></div>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Redis</h3>
              <p className="text-yellow-200">⏳ Starting...</p>
            </div>

            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <div className="w-12 h-12 bg-blue-500 rounded-lg mx-auto mb-4 flex items-center justify-center">
                <div className="w-6 h-6 border-2 border-white rounded"></div>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Supabase</h3>
              <p className="text-yellow-200">⏳ Starting...</p>
            </div>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-white text-purple-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
              Get Started
            </button>
            <button className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white/10 transition-colors">
              View Documentation
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App 