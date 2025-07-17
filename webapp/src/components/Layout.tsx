import React, { useState } from 'react';
import '../styles/deviant-theme.css';

interface LayoutProps {
  currentPage: string;
  onNavigate: (page: string) => void;
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ currentPage, onNavigate, children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navigationItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊', description: 'Analytics & Overview' },
    { id: 'settings', label: 'Settings', icon: '⚙️', description: 'Bot Configuration' },
    { id: 'products', label: 'Products', icon: '🛒', description: 'Credit Packages' },
    { id: 'users', label: 'Users', icon: '👥', description: 'User Management' },
  ];

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        {/* Brand */}
        <div className="nav-brand">
          <div className="nav-brand-icon">
            🚀
          </div>
          <div>
            <div className="nav-brand-text">NSXoChat</div>
            <small className="text-secondary">Admin Dashboard</small>
          </div>
        </div>

        {/* Navigation */}
        <nav>
          <ul className="nav-menu">
            {navigationItems.map((item) => (
              <li key={item.id} className="nav-item">
                <a
                  href="#"
                  className={`nav-link ${currentPage === item.id ? 'active' : ''}`}
                  onClick={(e) => {
                    e.preventDefault();
                    onNavigate(item.id);
                    setSidebarOpen(false);
                  }}
                >
                  <span className="nav-icon">{item.icon}</span>
                  <div>
                    <div>{item.label}</div>
                    <small className="text-secondary">{item.description}</small>
                  </div>
                </a>
              </li>
            ))}
          </ul>
        </nav>

        {/* Sidebar Footer */}
        <div style={{ marginTop: 'auto', paddingTop: 'var(--spacing-xl)' }}>
          <div className="card">
            <div style={{ textAlign: 'center' }}>
              <div className="nav-icon" style={{ fontSize: '2rem', marginBottom: 'var(--spacing-sm)' }}>⚡</div>
              <h3 style={{ marginBottom: 'var(--spacing-sm)' }}>Pro Features</h3>
              <p className="text-secondary" style={{ fontSize: '0.875rem', marginBottom: 'var(--spacing-md)' }}>
                Unlock advanced analytics and automation tools
              </p>
              <button className="btn btn-primary btn-sm w-full">
                Upgrade Now
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {/* Header */}
        <header className="header">
          <div className="flex items-center gap-md">
            <button
              className="btn btn-secondary btn-sm"
              onClick={toggleSidebar}
              style={{ display: 'none' }}
              id="mobile-menu-btn"
            >
              ☰
            </button>
            <div>
              <h1 style={{ margin: 0, fontSize: '1.5rem' }}>
                {navigationItems.find(item => item.id === currentPage)?.label || 'Dashboard'}
              </h1>
              <p className="text-secondary" style={{ margin: 0, fontSize: '0.875rem' }}>
                {navigationItems.find(item => item.id === currentPage)?.description || 'Welcome to your admin dashboard'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-md">
            {/* Status Indicator */}
            <div className="flex items-center gap-sm">
              <div 
                style={{
                  width: '8px',
                  height: '8px',
                  backgroundColor: 'var(--accent-green)',
                  borderRadius: '50%',
                  animation: 'pulse 2s infinite'
                }}
              ></div>
              <span className="text-secondary text-small">System Online</span>
            </div>

            {/* Admin Profile */}
            <div className="flex items-center gap-sm">
              <div 
                style={{
                  width: '32px',
                  height: '32px',
                  backgroundColor: 'var(--accent-green)',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 'var(--font-weight-bold)',
                  fontSize: '0.875rem'
                }}
              >
                AD
              </div>
              <div>
                <div style={{ fontSize: '0.875rem', fontWeight: 'var(--font-weight-medium)' }}>Admin</div>
                <div className="text-secondary" style={{ fontSize: '0.75rem' }}>Super User</div>
              </div>
            </div>
          </div>
        </header>

        {/* Content Area */}
        <div className="content-area fade-in">
          {children}
        </div>
      </main>

      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={() => setSidebarOpen(false)}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            zIndex: 40,
            display: window.innerWidth <= 768 ? 'block' : 'none'
          }}
        />
      )}

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }

        @media (max-width: 768px) {
          #mobile-menu-btn {
            display: block !important;
          }
        }
      `}</style>
    </div>
  );
};

export default Layout; 