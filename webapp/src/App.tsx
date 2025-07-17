import { useState, useEffect } from 'react'
import './styles/index.css'

// API configuration
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '/api' 
  : 'http://localhost:8000/api'

// Types
interface DashboardStats {
  totalUsers: number
  activeUsers: number
  messagesToday: number
  totalCredits: number
  monthlyPayments: number
  estimatedRevenue: number
  lastUpdated: string
}

interface BotSettings {
  welcomeMessage: string
  costTextMessage: number
  costPhotoMessage: number
  costVoiceMessage: number
  minContentPrice: number
  maxContentPrice: number
  lowCreditThreshold: number
  autoRechargeEnabled: boolean
}

interface Product {
  id: number
  name: string
  credits: number
  description: string
  price: string
  isActive: boolean
  stripeProductId: string
  stripePriceId: string
}

// API functions
const api = {
  async fetchStats(): Promise<DashboardStats> {
    const response = await fetch(`${API_BASE_URL}/dashboard/stats`)
    if (!response.ok) throw new Error('Failed to fetch stats')
    return response.json()
  },

  async fetchSettings(): Promise<BotSettings> {
    const response = await fetch(`${API_BASE_URL}/settings`)
    if (!response.ok) throw new Error('Failed to fetch settings')
    return response.json()
  },

  async updateSettings(settings: Partial<BotSettings>): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/settings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings)
    })
    if (!response.ok) throw new Error('Failed to update settings')
  },

  async fetchProducts(): Promise<Product[]> {
    const response = await fetch(`${API_BASE_URL}/products`)
    if (!response.ok) throw new Error('Failed to fetch products')
    return response.json()
  },

  async createProduct(product: Omit<Product, 'id' | 'price' | 'stripeProductId' | 'stripePriceId'>): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/products`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(product)
    })
    if (!response.ok) throw new Error('Failed to create product')
  },

  async updateProduct(id: number, product: Partial<Product>): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/products/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(product)
    })
    if (!response.ok) throw new Error('Failed to update product')
  },

  async deleteProduct(id: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/products/${id}`, {
      method: 'DELETE'
    })
    if (!response.ok) throw new Error('Failed to delete product')
  }
}

// Dashboard component with real data
const Dashboard = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadStats = async () => {
      try {
        const data = await api.fetchStats()
        setStats(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load stats')
      } finally {
        setLoading(false)
      }
    }

    loadStats()
    // Refresh every 30 seconds
    const interval = setInterval(loadStats, 30000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-4 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-4 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <p className="text-red-600 font-medium">Error: {error}</p>
          <p className="text-gray-600 mt-2">Please check your API connection</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
          <div className="text-sm text-gray-500">
            Last updated: {new Date(stats!.lastUpdated).toLocaleTimeString()}
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Users</p>
                <p className="text-3xl font-bold text-gray-900">{stats!.totalUsers}</p>
                <p className="text-xs text-gray-500">{stats!.activeUsers} active today</p>
              </div>
              <div className="text-2xl">👥</div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Credits in System</p>
                <p className="text-3xl font-bold text-gray-900">{stats!.totalCredits}</p>
                <p className="text-xs text-gray-500">{stats!.messagesToday} messages today</p>
              </div>
              <div className="text-2xl">💬</div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Monthly Revenue</p>
                <p className="text-3xl font-bold text-gray-900">${stats!.estimatedRevenue}</p>
                <p className="text-xs text-gray-500">{stats!.monthlyPayments} payments</p>
              </div>
              <div className="text-2xl">💰</div>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow">
          <div className="p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">System Status</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center mb-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                  <div className="font-medium">Database</div>
                </div>
                <div className="text-sm text-gray-600">Connected and operational</div>
              </div>
              <div className="p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center mb-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                  <div className="font-medium">Bot Service</div>
                </div>
                <div className="text-sm text-gray-600">Running and responsive</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Settings component with real API integration
const Settings = () => {
  const [settings, setSettings] = useState<BotSettings | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<string | null>(null)

  useEffect(() => {
    const loadSettings = async () => {
      try {
        const data = await api.fetchSettings()
        setSettings(data)
      } catch (err) {
        setMessage('Failed to load settings')
      } finally {
        setLoading(false)
      }
    }

    loadSettings()
  }, [])

  const handleSave = async () => {
    if (!settings) return
    
    setSaving(true)
    try {
      await api.updateSettings(settings)
      setMessage('Settings saved successfully!')
      setTimeout(() => setMessage(null), 3000)
    } catch (err) {
      setMessage('Failed to save settings')
    } finally {
      setSaving(false)
    }
  }

  const updateSetting = (key: keyof BotSettings, value: any) => {
    if (!settings) return
    setSettings({ ...settings, [key]: value })
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-4 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Settings</h1>
        
        {message && (
          <div className={`mb-6 p-4 rounded-lg ${
            message.includes('success') ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
          }`}>
            {message}
          </div>
        )}
        
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Welcome Message</h2>
            <textarea 
              className="w-full p-3 border border-gray-300 rounded-lg"
              rows={4}
              value={settings?.welcomeMessage || ''}
              onChange={(e) => updateSetting('welcomeMessage', e.target.value)}
              placeholder="Enter welcome message..."
            />
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Message Pricing</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Text Message Cost
                </label>
                <input 
                  type="number" 
                  className="w-full p-3 border border-gray-300 rounded-lg"
                  value={settings?.costTextMessage || 0}
                  onChange={(e) => updateSetting('costTextMessage', parseInt(e.target.value))}
                  aria-label="Text message cost"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Photo Message Cost
                </label>
                                 <input 
                   type="number" 
                   className="w-full p-3 border border-gray-300 rounded-lg"
                   value={settings?.costPhotoMessage || 0}
                   onChange={(e) => updateSetting('costPhotoMessage', parseInt(e.target.value))}
                   aria-label="Photo message cost"
                 />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Voice Message Cost
                </label>
                <input 
                  type="number" 
                  className="w-full p-3 border border-gray-300 rounded-lg"
                  value={settings?.costVoiceMessage || 0}
                  onChange={(e) => updateSetting('costVoiceMessage', parseInt(e.target.value))}
                />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">System Configuration</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Low Credit Threshold
                </label>
                <input 
                  type="number" 
                  className="w-full p-3 border border-gray-300 rounded-lg"
                  value={settings?.lowCreditThreshold || 0}
                  onChange={(e) => updateSetting('lowCreditThreshold', parseInt(e.target.value))}
                />
              </div>
              <div>
                <label className="flex items-center space-x-2">
                  <input 
                    type="checkbox" 
                    className="rounded"
                    checked={settings?.autoRechargeEnabled || false}
                    onChange={(e) => updateSetting('autoRechargeEnabled', e.target.checked)}
                  />
                  <span className="text-sm font-medium text-gray-700">
                    Enable Auto Recharge
                  </span>
                </label>
              </div>
            </div>
          </div>

          <div className="flex justify-end">
            <button 
              onClick={handleSave}
              disabled={saving}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

// Products component with real CRUD operations
const Products = () => {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [editingProduct, setEditingProduct] = useState<Product | null>(null)
  const [isCreating, setIsCreating] = useState(false)

  useEffect(() => {
    loadProducts()
  }, [])

  const loadProducts = async () => {
    try {
      const data = await api.fetchProducts()
      setProducts(data)
    } catch (err) {
      console.error('Failed to load products:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSaveProduct = async (product: Product | Omit<Product, 'id' | 'price' | 'stripeProductId' | 'stripePriceId'>) => {
    try {
      if ('id' in product) {
        await api.updateProduct(product.id, product)
      } else {
        await api.createProduct(product)
      }
      await loadProducts()
      setEditingProduct(null)
      setIsCreating(false)
    } catch (err) {
      console.error('Failed to save product:', err)
    }
  }

  const handleDeleteProduct = async (id: number) => {
    if (!confirm('Are you sure you want to delete this product?')) return
    
    try {
      await api.deleteProduct(id)
      await loadProducts()
    } catch (err) {
      console.error('Failed to delete product:', err)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-4 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Credit Packages</h1>
          <button 
            onClick={() => setIsCreating(true)}
            className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700"
          >
            + Add New Package
          </button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {products.map((product) => (
            <div key={product.id} className="bg-white rounded-lg shadow p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-2">{product.name}</h3>
              <p className="text-3xl font-bold text-blue-600 mb-2">{product.credits} Credits</p>
              <p className="text-gray-600 mb-4">{product.description}</p>
              <p className="text-sm text-gray-500 mb-4">Price: {product.price}</p>
              <div className="flex space-x-2">
                <button 
                  onClick={() => setEditingProduct(product)}
                  className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700"
                >
                  Edit
                </button>
                <button 
                  onClick={() => handleDeleteProduct(product.id)}
                  className="flex-1 bg-red-600 text-white py-2 rounded-lg hover:bg-red-700"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Product Edit Modal */}
        {(editingProduct || isCreating) && (
          <ProductModal
            product={editingProduct}
            onSave={handleSaveProduct}
            onCancel={() => { setEditingProduct(null); setIsCreating(false) }}
          />
        )}
      </div>
    </div>
  )
}

// Product modal component
const ProductModal = ({ 
  product, 
  onSave, 
  onCancel 
}: { 
  product: Product | null
  onSave: (product: any) => void
  onCancel: () => void 
}) => {
  const [formData, setFormData] = useState({
    name: product?.name || '',
    credits: product?.credits || 0,
    description: product?.description || '',
    isActive: product?.isActive ?? true
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (product) {
      onSave({ ...product, ...formData })
    } else {
      onSave(formData)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">
          {product ? 'Edit Product' : 'Create Product'}
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Package Name
            </label>
            <input 
              type="text"
              className="w-full p-3 border border-gray-300 rounded-lg"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Credits
            </label>
            <input 
              type="number"
              className="w-full p-3 border border-gray-300 rounded-lg"
              value={formData.credits}
              onChange={(e) => setFormData({ ...formData, credits: parseInt(e.target.value) })}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea 
              className="w-full p-3 border border-gray-300 rounded-lg"
              rows={3}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            />
          </div>
          <div>
            <label className="flex items-center space-x-2">
              <input 
                type="checkbox"
                checked={formData.isActive}
                onChange={(e) => setFormData({ ...formData, isActive: e.target.checked })}
              />
              <span className="text-sm font-medium text-gray-700">Active</span>
            </label>
          </div>
          <div className="flex space-x-4">
            <button 
              type="submit"
              className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700"
            >
              Save
            </button>
            <button 
              type="button"
              onClick={onCancel}
              className="flex-1 bg-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-400"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

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