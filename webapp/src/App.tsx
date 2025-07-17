import { useState } from 'react'
import './styles/index.css'

// Simple pages
const Dashboard = () => (
  <div className="min-h-screen bg-gray-50 p-4">
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Admin Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Users</p>
              <p className="text-3xl font-bold text-gray-900">1,234</p>
            </div>
            <div className="text-2xl">👥</div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Messages Today</p>
              <p className="text-3xl font-bold text-gray-900">567</p>
            </div>
            <div className="text-2xl">💬</div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Revenue</p>
              <p className="text-3xl font-bold text-gray-900">$890</p>
            </div>
            <div className="text-2xl">💰</div>
          </div>
        </div>
      </div>
      
      <div className="bg-white rounded-lg shadow">
        <div className="p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-left">
              <div className="text-lg mb-2">⚙️</div>
              <div className="font-medium">Settings</div>
              <div className="text-sm text-gray-600">Configure bot settings</div>
            </button>
            <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-left">
              <div className="text-lg mb-2">🛒</div>
              <div className="font-medium">Products</div>
              <div className="text-sm text-gray-600">Manage credit packages</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
)

const Settings = () => (
  <div className="min-h-screen bg-gray-50 p-4">
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Settings</h1>
      
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Welcome Message</h2>
          <textarea 
            className="w-full p-3 border border-gray-300 rounded-lg"
            rows={4}
            placeholder="Enter welcome message..."
          />
          <button className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
            Save Changes
          </button>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Pricing Configuration</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Credits per Dollar
              </label>
              <input 
                type="number" 
                className="w-full p-3 border border-gray-300 rounded-lg"
                placeholder="100"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Minimum Purchase
              </label>
              <input 
                type="number" 
                className="w-full p-3 border border-gray-300 rounded-lg"
                placeholder="1"
              />
            </div>
          </div>
          <button className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
            Save Changes
          </button>
        </div>
      </div>
    </div>
  </div>
)

const Products = () => (
  <div className="min-h-screen bg-gray-50 p-4">
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Credit Packages</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-2">Starter</h3>
          <p className="text-3xl font-bold text-blue-600 mb-4">$5</p>
          <p className="text-gray-600 mb-4">500 Credits</p>
          <button className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">
            Edit Package
          </button>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-2">Pro</h3>
          <p className="text-3xl font-bold text-blue-600 mb-4">$10</p>
          <p className="text-gray-600 mb-4">1,200 Credits</p>
          <button className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">
            Edit Package
          </button>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-2">Premium</h3>
          <p className="text-3xl font-bold text-blue-600 mb-4">$20</p>
          <p className="text-gray-600 mb-4">2,500 Credits</p>
          <button className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">
            Edit Package
          </button>
        </div>
      </div>
      
      <div className="mt-8">
        <button className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700">
          + Add New Package
        </button>
      </div>
    </div>
  </div>
)

const Navigation = ({ currentPage, onNavigate }: { currentPage: string, onNavigate: (page: string) => void }) => (
  <div className="bg-white shadow">
    <div className="max-w-4xl mx-auto px-4">
      <div className="flex space-x-8">
        <button 
          onClick={() => onNavigate('dashboard')}
          className={`py-4 px-2 border-b-2 ${currentPage === 'dashboard' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
        >
          🏠 Dashboard
        </button>
        <button 
          onClick={() => onNavigate('settings')}
          className={`py-4 px-2 border-b-2 ${currentPage === 'settings' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
        >
          ⚙️ Settings
        </button>
        <button 
          onClick={() => onNavigate('products')}
          className={`py-4 px-2 border-b-2 ${currentPage === 'products' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
                >
          🛒 Products
        </button>
      </div>
    </div>
  </div>
)

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard')

  const renderPage = () => {
    switch (currentPage) {
      case 'settings':
        return <Settings />
      case 'products':
        return <Products />
      default:
        return <Dashboard />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation currentPage={currentPage} onNavigate={setCurrentPage} />
      {renderPage()}
    </div>
  )
}

export default App 