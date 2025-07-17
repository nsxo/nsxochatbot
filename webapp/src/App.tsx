import { useState } from 'react'
import Layout from './components/Layout'
import DashboardPage from './components/DashboardPage'
import './styles/deviant-theme.css'

// Import existing components (will be enhanced)
const SettingsPage = () => (
  <div>
    <div className="card mb-lg">
      <div className="card-header">
        <h3 className="card-title">Bot Configuration</h3>
        <div className="badge badge-success">Active</div>
      </div>
      <div className="card-body">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 'var(--spacing-lg)' }}>
          {/* Welcome Message */}
          <div className="form-group">
            <label className="form-label">Welcome Message</label>
            <textarea 
              className="form-textarea"
              placeholder="Enter your bot's welcome message..."
              defaultValue="Welcome to NSXoChat! 🚀 This is a premium AI chat service. Purchase credits to start chatting with our advanced AI."
            />
          </div>
          
          {/* Pricing Configuration */}
          <div className="form-group">
            <label className="form-label">Message Pricing</label>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 'var(--spacing-sm)' }}>
              <div>
                <label className="form-label text-small">Text Message</label>
                <input type="number" className="form-input" defaultValue="1" />
              </div>
              <div>
                <label className="form-label text-small">Photo Message</label>
                <input type="number" className="form-input" defaultValue="3" />
              </div>
              <div>
                <label className="form-label text-small">Voice Message</label>
                <input type="number" className="form-input" defaultValue="5" />
              </div>
            </div>
          </div>
        </div>
        
        <div className="flex gap-md" style={{ marginTop: 'var(--spacing-lg)' }}>
          <button className="btn btn-success">💾 Save Changes</button>
          <button className="btn btn-secondary">🔄 Reset to Default</button>
          <button className="btn btn-secondary">📋 Export Config</button>
        </div>
      </div>
    </div>

    {/* Advanced Settings */}
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Advanced Settings</h3>
        <button className="btn btn-secondary btn-sm">🔧 Configure</button>
      </div>
      <div className="card-body">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 'var(--spacing-lg)' }}>
          <div className="flex items-center justify-between p-md bg-tertiary rounded">
            <div>
              <div className="font-weight-medium">Auto-Recharge</div>
              <div className="text-secondary text-small">Automatically recharge user credits</div>
            </div>
            <label className="switch">
              <input type="checkbox" />
              <span style={{
                position: 'relative',
                width: '44px',
                height: '24px',
                backgroundColor: 'var(--bg-primary)',
                borderRadius: '12px',
                transition: 'var(--transition-fast)',
                cursor: 'pointer'
              }}></span>
            </label>
          </div>
          
          <div className="flex items-center justify-between p-md bg-tertiary rounded">
            <div>
              <div className="font-weight-medium">Low Credit Alerts</div>
              <div className="text-secondary text-small">Notify users when credits are low</div>
            </div>
            <label className="switch">
              <input type="checkbox" defaultChecked />
              <span style={{
                position: 'relative',
                width: '44px',
                height: '24px',
                backgroundColor: 'var(--accent-green)',
                borderRadius: '12px',
                transition: 'var(--transition-fast)',
                cursor: 'pointer'
              }}></span>
            </label>
          </div>
        </div>
      </div>
    </div>
  </div>
);

const ProductsPage = () => (
  <div>
    <div className="flex justify-between items-center mb-lg">
      <div>
        <h2>Credit Packages</h2>
        <p className="text-secondary">Manage your bot's credit packages and pricing</p>
      </div>
      <button className="btn btn-primary">
        ➕ Add Package
      </button>
    </div>

    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 'var(--spacing-lg)' }}>
      {[
        { name: 'Starter Pack', credits: 50, price: '$5.00', popular: false },
        { name: 'Power User', credits: 200, price: '$15.00', popular: true },
        { name: 'Premium Pack', credits: 500, price: '$30.00', popular: false },
        { name: 'Enterprise', credits: 1000, price: '$50.00', popular: false },
      ].map((product, index) => (
        <div key={index} className="card" style={{ position: 'relative' }}>
          {product.popular && (
            <div style={{
              position: 'absolute',
              top: '-10px',
              right: '20px',
              background: 'linear-gradient(to right, var(--accent-orange), var(--accent-pink))',
              color: 'var(--text-primary)',
              padding: '0.25rem 0.75rem',
              borderRadius: 'var(--radius-full)',
              fontSize: '0.75rem',
              fontWeight: 'var(--font-weight-bold)',
              textTransform: 'uppercase'
            }}>
              Most Popular
            </div>
          )}
          
          <div className="card-header">
            <h3 className="card-title">{product.name}</h3>
            <div className="badge badge-success">Active</div>
          </div>
          
          <div className="card-body">
            <div style={{ textAlign: 'center', marginBottom: 'var(--spacing-lg)' }}>
              <div style={{ 
                fontSize: '2.5rem', 
                fontWeight: 'var(--font-weight-bold)', 
                color: 'var(--accent-green)',
                marginBottom: 'var(--spacing-xs)'
              }}>
                {product.price}
              </div>
              <div className="text-secondary">
                {product.credits} credits
              </div>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)', marginBottom: 'var(--spacing-lg)' }}>
              <div className="flex items-center gap-sm">
                <span style={{ color: 'var(--accent-green)' }}>✓</span>
                <span className="text-small">{product.credits} message credits</span>
              </div>
              <div className="flex items-center gap-sm">
                <span style={{ color: 'var(--accent-green)' }}>✓</span>
                <span className="text-small">Priority support</span>
              </div>
              <div className="flex items-center gap-sm">
                <span style={{ color: 'var(--accent-green)' }}>✓</span>
                <span className="text-small">Advanced features</span>
              </div>
            </div>
          </div>
          
          <div className="card-footer">
            <button className="btn btn-secondary btn-sm">✏️ Edit</button>
            <button className="btn btn-danger btn-sm">🗑️ Delete</button>
          </div>
        </div>
      ))}
    </div>
  </div>
);

const UsersPage = () => (
  <div>
    <div className="flex justify-between items-center mb-lg">
      <div>
        <h2>User Management</h2>
        <p className="text-secondary">View and manage your bot users</p>
      </div>
      <div className="flex gap-sm">
        <button className="btn btn-secondary">🔍 Search</button>
        <button className="btn btn-secondary">📊 Export</button>
      </div>
    </div>

    <div className="table-container">
      <table className="table">
        <thead>
          <tr>
            <th>User</th>
            <th>Credits</th>
            <th>Status</th>
            <th>Joined</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {[
            { name: 'Admin User', username: '@admin', credits: 1000, status: 'active', joined: '2024-01-01' },
            { name: 'Premium User', username: '@premium', credits: 500, status: 'active', joined: '2024-01-15' },
            { name: 'Regular User', username: '@user123', credits: 25, status: 'active', joined: '2024-02-01' },
            { name: 'New User', username: '@newbie', credits: 10, status: 'pending', joined: '2024-02-10' },
          ].map((user, index) => (
            <tr key={index}>
              <td>
                <div className="flex items-center gap-sm">
                  <div style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: '50%',
                    background: 'linear-gradient(135deg, var(--accent-green), var(--accent-blue))',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '0.875rem',
                    fontWeight: 'var(--font-weight-bold)'
                  }}>
                    {user.name.charAt(0)}
                  </div>
                  <div>
                    <div className="font-weight-medium">{user.name}</div>
                    <div className="text-secondary text-small">{user.username}</div>
                  </div>
                </div>
              </td>
              <td>
                <span className="badge badge-info">{user.credits}</span>
              </td>
              <td>
                <span className={`badge ${user.status === 'active' ? 'badge-success' : 'badge-warning'}`}>
                  {user.status}
                </span>
              </td>
              <td className="text-secondary">{user.joined}</td>
              <td>
                <div className="flex gap-xs">
                  <button className="btn btn-secondary btn-sm">View</button>
                  <button className="btn btn-secondary btn-sm">Edit</button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard')

  const renderPage = () => {
    switch (currentPage) {
      case 'settings':
        return <SettingsPage />
      case 'products':
        return <ProductsPage />
      case 'users':
        return <UsersPage />
      default:
        return <DashboardPage />
    }
  }

  return (
    <Layout currentPage={currentPage} onNavigate={setCurrentPage}>
      {renderPage()}
    </Layout>
  )
}

export default App 