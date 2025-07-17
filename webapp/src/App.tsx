import { useState } from 'react'
import Layout from './components/Layout'
import DashboardPage from './components/DashboardPage'
import './styles/deviant-theme.css'

// Settings Page - Focused on core bot configuration
const SettingsPage = () => (
  <div>
    {/* Bot Configuration */}
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
              defaultValue="Welcome to NSXoChat! 🤖 This is a premium AI chat service. Purchase credits to start chatting with our advanced AI."
              rows={4}
            />
            <small className="text-secondary">This message is sent to new users when they first interact with your bot.</small>
          </div>
          
          {/* Bot Information */}
          <div className="form-group">
            <label className="form-label">Bot Information</label>
            <div style={{ display: 'grid', gap: 'var(--spacing-sm)' }}>
              <div>
                <label className="form-label text-small">Bot Name</label>
                <input type="text" className="form-input" defaultValue="NSXoChat Bot" aria-label="Bot name" />
              </div>
              <div>
                <label className="form-label text-small">Bot Description</label>
                <input type="text" className="form-input" defaultValue="Premium AI Chat Service" aria-label="Bot description" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    {/* Pricing Configuration */}
    <div className="card mb-lg">
      <div className="card-header">
        <h3 className="card-title">Message Pricing</h3>
        <div className="flex gap-sm">
          <button className="btn btn-secondary btn-sm">🔄 Reset to Default</button>
          <button className="btn btn-success btn-sm">💾 Save Changes</button>
        </div>
      </div>
      <div className="card-body">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 'var(--spacing-lg)' }}>
          <div className="form-group">
            <label className="form-label">Text Messages</label>
            <div className="flex items-center gap-md">
              <input type="number" className="form-input" defaultValue="1" aria-label="Text message cost" style={{ maxWidth: '100px' }} />
              <span className="text-secondary">credits per message</span>
            </div>
            <small className="text-secondary">Cost for basic text messages</small>
          </div>
          
          <div className="form-group">
            <label className="form-label">Photo Messages</label>
            <div className="flex items-center gap-md">
              <input type="number" className="form-input" defaultValue="3" aria-label="Photo message cost" style={{ maxWidth: '100px' }} />
              <span className="text-secondary">credits per message</span>
            </div>
            <small className="text-secondary">Cost for messages with photos</small>
          </div>
          
          <div className="form-group">
            <label className="form-label">Voice Messages</label>
            <div className="flex items-center gap-md">
              <input type="number" className="form-input" defaultValue="5" aria-label="Voice message cost" style={{ maxWidth: '100px' }} />
              <span className="text-secondary">credits per message</span>
            </div>
            <small className="text-secondary">Cost for voice messages</small>
          </div>
        </div>
      </div>
    </div>

    {/* System Configuration */}
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">System Settings</h3>
        <div className="badge badge-info">Configuration</div>
      </div>
      <div className="card-body">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 'var(--spacing-lg)' }}>
          <div className="flex items-center justify-between p-md bg-tertiary rounded">
            <div>
              <div style={{ fontWeight: 'var(--font-weight-medium)', color: 'var(--text-primary)' }}>Low Credit Alerts</div>
              <div className="text-secondary text-small">Notify users when credits are running low</div>
              <div className="text-secondary text-small">Threshold: 10 credits</div>
            </div>
            <label className="switch">
              <input type="checkbox" defaultChecked aria-label="Enable low credit alerts" />
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
          
          <div className="flex items-center justify-between p-md bg-tertiary rounded">
            <div>
              <div style={{ fontWeight: 'var(--font-weight-medium)', color: 'var(--text-primary)' }}>Welcome Message</div>
              <div className="text-secondary text-small">Send welcome message to new users</div>
              <div className="text-secondary text-small">Automatic greeting</div>
            </div>
            <label className="switch">
              <input type="checkbox" defaultChecked aria-label="Enable welcome messages" />
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

          <div className="flex items-center justify-between p-md bg-tertiary rounded">
            <div>
              <div style={{ fontWeight: 'var(--font-weight-medium)', color: 'var(--text-primary)' }}>Usage Analytics</div>
              <div className="text-secondary text-small">Track user interactions and usage patterns</div>
              <div className="text-secondary text-small">For optimization</div>
            </div>
            <label className="switch">
              <input type="checkbox" defaultChecked aria-label="Enable analytics" />
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

// Products Page - Streamlined credit package management
const ProductsPage = () => (
  <div>
    <div className="flex justify-between items-center mb-lg">
      <div>
        <h2 style={{ color: 'var(--text-primary)' }}>Credit Packages</h2>
        <p className="text-secondary">Manage your bot's credit packages and pricing tiers</p>
      </div>
      <div className="flex gap-sm">
        <button className="btn btn-secondary">📊 View Analytics</button>
        <button className="btn btn-success">➕ Add Package</button>
      </div>
    </div>

    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--spacing-lg)' }}>
      {[
        { name: 'Starter Pack', credits: 50, price: '$5.00', popular: false, sales: 24 },
        { name: 'Power User', credits: 200, price: '$15.00', popular: true, sales: 89 },
        { name: 'Premium Pack', credits: 500, price: '$30.00', popular: false, sales: 45 },
        { name: 'Enterprise', credits: 1000, price: '$50.00', popular: false, sales: 12 },
      ].map((product, index) => (
        <div key={index} className="card" style={{ position: 'relative' }}>
          {product.popular && (
            <div style={{
              position: 'absolute',
              top: '-8px',
              right: '16px',
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
              <div className="text-secondary" style={{ fontSize: '1rem' }}>
                {product.credits} credits
              </div>
              <div className="text-secondary text-small">
                ${(parseFloat(product.price.replace('$', '')) / product.credits).toFixed(3)} per credit
              </div>
            </div>
            
            {/* Package Stats */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)', marginBottom: 'var(--spacing-lg)' }}>
              <div className="flex items-center justify-between">
                <span className="text-secondary text-small">Monthly Sales</span>
                <span style={{ color: 'var(--text-primary)', fontWeight: 'var(--font-weight-medium)' }}>{product.sales}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-secondary text-small">Revenue</span>
                <span style={{ color: 'var(--accent-green)', fontWeight: 'var(--font-weight-medium)' }}>
                  ${(parseFloat(product.price.replace('$', '')) * product.sales).toFixed(0)}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-secondary text-small">Value Rating</span>
                <div className="flex">
                  {Array.from({ length: 5 }, (_, i) => (
                    <span key={i} style={{ color: i < (product.popular ? 5 : 3) ? 'var(--accent-orange)' : 'var(--border-color)' }}>⭐</span>
                  ))}
                </div>
              </div>
            </div>

            {/* Package Features */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)', marginBottom: 'var(--spacing-lg)' }}>
              <div className="flex items-center gap-sm">
                <span style={{ color: 'var(--accent-green)' }}>✓</span>
                <span className="text-small" style={{ color: 'var(--text-primary)' }}>{product.credits} message credits</span>
              </div>
              <div className="flex items-center gap-sm">
                <span style={{ color: 'var(--accent-green)' }}>✓</span>
                <span className="text-small" style={{ color: 'var(--text-primary)' }}>No expiration</span>
              </div>
              <div className="flex items-center gap-sm">
                <span style={{ color: 'var(--accent-green)' }}>✓</span>
                <span className="text-small" style={{ color: 'var(--text-primary)' }}>All message types</span>
              </div>
              {product.popular && (
                <div className="flex items-center gap-sm">
                  <span style={{ color: 'var(--accent-orange)' }}>⭐</span>
                  <span className="text-small" style={{ color: 'var(--accent-orange)' }}>Best value</span>
                </div>
              )}
            </div>
          </div>
          
          <div className="card-footer">
            <button className="btn btn-secondary btn-sm">✏️ Edit Package</button>
            <button className="btn btn-secondary btn-sm">📊 View Stats</button>
          </div>
        </div>
      ))}
    </div>

    {/* Package Analytics Summary */}
    <div className="card" style={{ marginTop: 'var(--spacing-xl)' }}>
      <div className="card-header">
        <h3 className="card-title">Package Performance</h3>
        <div className="flex gap-sm">
          <button className="btn btn-success btn-sm">This Month</button>
          <button className="btn btn-secondary btn-sm">Last 30 Days</button>
          <button className="btn btn-secondary btn-sm">All Time</button>
        </div>
      </div>
      <div className="card-body">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 'var(--spacing-lg)' }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', color: 'var(--accent-green)', marginBottom: 'var(--spacing-sm)' }}>170</div>
            <div style={{ fontWeight: 'var(--font-weight-medium)', color: 'var(--text-primary)' }}>Total Sales</div>
            <div className="text-secondary text-small">This month</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', color: 'var(--accent-blue)', marginBottom: 'var(--spacing-sm)' }}>$2,580</div>
            <div style={{ fontWeight: 'var(--font-weight-medium)', color: 'var(--text-primary)' }}>Revenue</div>
            <div className="text-secondary text-small">Monthly total</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', color: 'var(--accent-orange)', marginBottom: 'var(--spacing-sm)' }}>$15.18</div>
            <div style={{ fontWeight: 'var(--font-weight-medium)', color: 'var(--text-primary)' }}>Avg Order</div>
            <div className="text-secondary text-small">Per transaction</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', color: 'var(--accent-green)', marginBottom: 'var(--spacing-sm)' }}>52%</div>
            <div style={{ fontWeight: 'var(--font-weight-medium)', color: 'var(--text-primary)' }}>Power User</div>
            <div className="text-secondary text-small">Most popular</div>
          </div>
        </div>
      </div>
    </div>
  </div>
);

// Users Page - Enhanced for better management
const UsersPage = () => (
  <div>
    <div className="flex justify-between items-center mb-lg">
      <div>
        <h2 style={{ color: 'var(--text-primary)' }}>User Management</h2>
        <p className="text-secondary">Monitor and manage your bot users</p>
      </div>
      <div className="flex gap-sm">
        <button className="btn btn-secondary">🔍 Search Users</button>
        <button className="btn btn-secondary">📊 Export Data</button>
        <button className="btn btn-secondary">👥 User Analytics</button>
      </div>
    </div>

    {/* User Stats Cards */}
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--spacing-lg)', marginBottom: 'var(--spacing-xl)' }}>
      <div className="stat-card">
        <div className="stat-header">
          <div className="stat-title">Active Users</div>
          <div className="stat-icon">👥</div>
        </div>
        <div className="stat-value">128</div>
        <div className="stat-change positive">
          <span>↗️</span>
          <span>+15%</span>
          <span className="text-secondary">vs last week</span>
        </div>
      </div>
      
      <div className="stat-card">
        <div className="stat-header">
          <div className="stat-title">New Users</div>
          <div className="stat-icon">🆕</div>
        </div>
        <div className="stat-value">23</div>
        <div className="stat-change positive">
          <span>↗️</span>
          <span>+8%</span>
          <span className="text-secondary">this week</span>
        </div>
      </div>
      
      <div className="stat-card">
        <div className="stat-header">
          <div className="stat-title">Total Credits</div>
          <div className="stat-icon">💎</div>
        </div>
        <div className="stat-value">45.2k</div>
        <div className="stat-change negative">
          <span>↘️</span>
          <span>-12%</span>
          <span className="text-secondary">consumed</span>
        </div>
      </div>
    </div>

    {/* Users Table */}
    <div className="table-container">
      <table className="table">
        <thead>
          <tr>
            <th>User</th>
            <th>Credits</th>
            <th>Activity</th>
            <th>Joined</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {[
            { name: 'Admin User', username: '@admin', credits: 1000, activity: 'Very Active', joined: '2024-01-01', status: 'admin' },
            { name: 'Premium User', username: '@premium', credits: 500, activity: 'Active', joined: '2024-01-15', status: 'premium' },
            { name: 'Regular User', username: '@user123', credits: 25, activity: 'Moderate', joined: '2024-02-01', status: 'active' },
            { name: 'New User', username: '@newbie', credits: 10, activity: 'New', joined: '2024-02-10', status: 'new' },
            { name: 'Power User', username: '@poweruser', credits: 750, activity: 'Very Active', joined: '2024-01-20', status: 'premium' },
          ].map((user, index) => (
            <tr key={index}>
              <td>
                <div className="flex items-center gap-sm">
                  <div style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: '50%',
                    background: user.status === 'admin' ? 'linear-gradient(135deg, var(--accent-orange), var(--accent-pink))' :
                               user.status === 'premium' ? 'linear-gradient(135deg, var(--accent-green), var(--accent-blue))' :
                               'linear-gradient(135deg, var(--bg-tertiary), var(--border-color))',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '0.875rem',
                    fontWeight: 'var(--font-weight-bold)',
                    color: 'var(--text-primary)'
                  }}>
                    {user.status === 'admin' ? '👑' : user.status === 'premium' ? '⭐' : user.name.charAt(0)}
                  </div>
                  <div>
                    <div style={{ fontWeight: 'var(--font-weight-medium)', color: 'var(--text-primary)' }}>{user.name}</div>
                    <div className="text-secondary text-small">{user.username}</div>
                  </div>
                </div>
              </td>
              <td>
                <span className="badge badge-info">{user.credits}</span>
              </td>
              <td>
                <span className={`badge ${
                  user.activity === 'Very Active' ? 'badge-success' :
                  user.activity === 'Active' ? 'badge-info' :
                  user.activity === 'Moderate' ? 'badge-warning' : 'badge-info'
                }`}>
                  {user.activity}
                </span>
              </td>
              <td className="text-secondary">{user.joined}</td>
              <td>
                <div className="flex gap-xs">
                  <button className="btn btn-secondary btn-sm">👁️ View</button>
                  <button className="btn btn-secondary btn-sm">✏️ Edit</button>
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