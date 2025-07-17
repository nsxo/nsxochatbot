import React, { useState } from 'react';
import '../styles/deviant-theme.css';

interface LayoutProps {
  currentPage: string;
  onNavigate: (page: string) => void;
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ currentPage, onNavigate, children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navigationSections = [
    {
      title: "",
      items: [
        { id: 'dashboard', label: 'Dashboard', icon: '🏠', description: 'Analytics & Overview' },
      ]
    },
    {
      title: "Administration",
      items: [
        { id: 'settings', label: 'Bot Settings', icon: '⚙️', description: 'Configuration & Pricing' },
        { id: 'products', label: 'Credit Packages', icon: '💎', description: 'Manage Pricing Plans' },
        { id: 'users', label: 'User Management', icon: '👥', description: 'View User Activity' },
      ]
    },
    {
      title: "Tools",
      items: [
        { id: 'analytics', label: 'Analytics', icon: '📊', description: 'Detailed Reports' },
        { id: 'logs', label: 'System Logs', icon: '📋', description: 'View System Activity' },
      ]
    }
  ];

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);

  return (
    <div className="app-container">
      {/* DeviantArt-Style Sidebar */}
      <aside className={`sidebar-deviant ${sidebarOpen ? 'open' : ''}`}>
        {/* Brand Header */}
        <div className="nav-brand-deviant">
          <div className="nav-brand-logo">
            <span className="brand-icon">🤖</span>
            <span className="brand-text">
              <span className="brand-name">NSXO</span>
              <span className="brand-suffix">CHAT</span>
            </span>
          </div>
          <div className="brand-subtitle">Admin Dashboard</div>
        </div>

        {/* Navigation Sections */}
        <nav className="nav-sections">
          {navigationSections.map((section, sectionIndex) => (
            <div key={sectionIndex} className="nav-section">
              {section.title && (
                <div className="nav-section-header">
                  {section.title}
                </div>
              )}
              
              <ul className="nav-section-items">
                {section.items.map((item) => (
                  <li key={item.id} className="nav-item-deviant">
                    <a
                      href="#"
                      className={`nav-link-deviant ${currentPage === item.id ? 'active' : ''}`}
                      onClick={(e) => {
                        e.preventDefault();
                        onNavigate(item.id);
                        setSidebarOpen(false);
                      }}
                    >
                      <span className="nav-icon-deviant">{item.icon}</span>
                      <span className="nav-text-deviant">{item.label}</span>
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </nav>

        {/* Action Section */}
        <div className="nav-actions">
          <div className="nav-section-header">Quick Actions</div>
          
          <button className="action-button-primary">
            <span className="action-icon">➕</span>
            <span className="action-text">Create Report</span>
          </button>
          
          <div className="action-description">
            Generate detailed analytics and export data for your bot's performance.
          </div>
        </div>

        {/* System Status Footer */}
        <div className="sidebar-footer">
          <div className="system-status">
            <div className="status-item">
              <span className="status-dot online"></span>
              <span className="status-text">System Online</span>
            </div>
            <div className="status-item">
              <span className="status-dot connected"></span>
              <span className="status-text">Database Connected</span>
            </div>
            <div className="version-info">v2.1.0</div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {/* Header */}
        <header className="header">
          <div className="flex items-center gap-md">
            <button
              className="btn btn-secondary btn-sm sidebar-toggle"
              onClick={toggleSidebar}
            >
              ☰
            </button>
            <div>
              <h1 style={{ margin: 0, fontSize: '1.5rem' }}>
                {navigationSections.flatMap(s => s.items).find(item => item.id === currentPage)?.label || 'Dashboard'}
              </h1>
              <p className="text-secondary" style={{ margin: 0, fontSize: '0.875rem' }}>
                {navigationSections.flatMap(s => s.items).find(item => item.id === currentPage)?.description || 'Welcome to your admin dashboard'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-md">
            {/* System Status Indicator */}
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
              <span className="text-secondary text-small">All Systems Operational</span>
            </div>

            {/* Quick Actions */}
            <div className="flex items-center gap-sm">
              <button 
                className="btn btn-secondary btn-sm"
                title="Refresh data"
                onClick={() => window.location.reload()}
              >
                🔄
              </button>
              <button 
                className="btn btn-secondary btn-sm"
                title="View logs"
              >
                📋
              </button>
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
                  fontSize: '0.875rem',
                  color: 'var(--bg-primary)'
                }}
              >
                👤
              </div>
              <div>
                <div style={{ fontSize: '0.875rem', fontWeight: 'var(--font-weight-medium)', color: 'var(--text-primary)' }}>Administrator</div>
                <div className="text-secondary" style={{ fontSize: '0.75rem' }}>Full Access</div>
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
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }

        @media (max-width: 768px) {
          .sidebar-toggle {
            display: block !important;
          }
        }

        @media (min-width: 769px) {
          .sidebar-toggle {
            display: none !important;
          }
        }
      `}</style>
    </div>
  );
};

export default Layout; 