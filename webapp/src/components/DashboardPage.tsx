import React, { useState, useEffect } from 'react';
import StatCard from './StatCard';
import { DeviantIcon } from './DeviantIcons';

interface DashboardStats {
  totalUsers: number;
  activeUsers: number;
  messagesToday: number;
  totalCredits: number;
  monthlyPayments: number;
  estimatedRevenue: number;
  lastUpdated: string;
}

interface RecentActivity {
  id: string;
  type: 'purchase' | 'message' | 'registration' | 'system';
  user: string;
  description: string;
  amount?: string;
  timestamp: string;
  status: 'completed' | 'pending' | 'failed';
}

const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  useEffect(() => {
    const loadStats = async () => {
      try {
        const response = await fetch('/api/dashboard/stats');
        if (!response.ok) throw new Error('Failed to fetch stats');
        const data = await response.json();
        setStats(data);
        setLastRefresh(new Date());
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load stats');
      } finally {
        setLoading(false);
      }
    };

    loadStats();
    const interval = setInterval(loadStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const refreshData = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/dashboard/stats');
      if (!response.ok) throw new Error('Failed to fetch stats');
      const data = await response.json();
      setStats(data);
      setLastRefresh(new Date());
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load stats');
    } finally {
      setLoading(false);
    }
  };

  // Mock recent activities for better UX demonstration
  const recentActivities: RecentActivity[] = [
    {
      id: '1',
      type: 'purchase',
      user: 'user123',
      description: 'Purchased Power User package',
      amount: '$15.00',
      timestamp: '2 minutes ago',
      status: 'completed'
    },
    {
      id: '2',
      type: 'message',
      user: 'user456',
      description: 'Sent 5 messages',
      amount: '5 credits',
      timestamp: '8 minutes ago',
      status: 'completed'
    },
    {
      id: '3',
      type: 'registration',
      user: 'user789',
      description: 'New user registered',
      amount: '10 credits',
      timestamp: '15 minutes ago',
      status: 'completed'
    },
    {
      id: '4',
      type: 'purchase',
      user: 'user101',
      description: 'Purchased Enterprise package',
      amount: '$50.00',
      timestamp: '23 minutes ago',
      status: 'completed'
    }
  ];

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'purchase': return <DeviantIcon name="purchase" size={12} />;
      case 'message': return <DeviantIcon name="message" size={12} />;
      case 'registration': return <DeviantIcon name="registration" size={12} />;
      case 'system': return <DeviantIcon name="system" size={12} />;
      default: return <DeviantIcon name="system" size={12} />;
    }
  };

  const getActivityColor = (type: string) => {
    switch (type) {
      case 'purchase': return 'var(--accent-green)';
      case 'message': return 'var(--accent-blue)';
      case 'registration': return 'var(--accent-orange)';
      case 'system': return 'var(--text-secondary)';
      default: return 'var(--text-secondary)';
    }
  };

  if (error) {
    return (
      <div className="flex items-center justify-center" style={{ minHeight: '400px' }}>
        <div className="card" style={{ textAlign: 'center', maxWidth: '500px' }}>
          <div style={{ fontSize: '3rem', marginBottom: 'var(--spacing-md)' }}>
            <DeviantIcon name="system" size={48} color="var(--accent-red)" />
          </div>
          <h2>Dashboard Error</h2>
          <p className="text-secondary">{error}</p>
          <div className="flex gap-md justify-center" style={{ marginTop: 'var(--spacing-lg)' }}>
            <button 
              className="btn btn-primary"
              onClick={refreshData}
            >
              <DeviantIcon name="refresh" size={16} /> Try Again
            </button>
            <button 
              className="btn btn-secondary"
              onClick={() => window.location.reload()}
            >
              <DeviantIcon name="refresh" size={16} /> Reload Page
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Compact Dashboard Header */}
      <div className="flex justify-between items-center mb-md">
        <div>
          <div className="flex items-center gap-md mb-xs">
            <h2 style={{ margin: 0, color: 'var(--text-primary)', fontSize: '1.5rem' }}>Overview</h2>
            <button 
              className="btn btn-secondary btn-sm"
              onClick={refreshData}
              disabled={loading}
              title="Refresh dashboard data"
            >
              <DeviantIcon name="refresh" size={16} />
            </button>
          </div>
          <p className="text-muted" style={{ fontSize: '0.75rem', margin: 0 }}>
            Updated {lastRefresh.toLocaleTimeString()} • Auto-refresh 30s
          </p>
        </div>
      </div>

      {/* Compact Metrics Grid */}
      <div className="stats-grid">
        <StatCard
          title="Total Users"
          value={stats?.totalUsers || 0}
          icon="users"
          change={{
            value: '+12%',
            type: 'positive'
          }}
          loading={loading}
        />
        <StatCard
          title="Active Today"
          value={stats?.activeUsers || 0}
          icon="lightning"
          change={{
            value: '+8%',
            type: 'positive'
          }}
          loading={loading}
        />
        <StatCard
          title="Messages"
          value={stats?.messagesToday || 0}
          icon="message"
          change={{
            value: '+25%',
            type: 'positive'
          }}
          loading={loading}
        />
        <StatCard
          title="Credits"
          value={stats?.totalCredits?.toLocaleString() || 0}
          icon="diamond"
          change={{
            value: '-3%',
            type: 'negative'
          }}
          loading={loading}
        />
        <StatCard
          title="Revenue"
          value={`$${stats?.estimatedRevenue || 0}`}
          icon="money"
          change={{
            value: '+18%',
            type: 'positive'
          }}
          loading={loading}
        />
        <StatCard
          title="Transactions"
          value={stats?.monthlyPayments || 0}
          icon="creditCard"
          change={{
            value: '+6%',
            type: 'positive'
          }}
          loading={loading}
        />
      </div>

      {/* Main Content Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 'var(--spacing-md)', marginBottom: 'var(--spacing-lg)' }}>
        
        {/* Railway-style Activity Feed */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Recent Activity</h3>
            <div className="flex gap-xs">
              <span className="badge badge-info text-small">{recentActivities.length}</span>
              <button className="btn btn-secondary btn-sm">View All</button>
            </div>
          </div>
          <div className="card-body">
            <div style={{ 
              backgroundColor: 'var(--bg-tertiary)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-sm)',
              overflow: 'hidden'
            }}>
              {recentActivities.map((activity, index) => (
                <div key={activity.id} style={{
                  display: 'flex',
                  alignItems: 'center',
                  padding: 'var(--spacing-md)',
                  borderBottom: index < recentActivities.length - 1 ? '1px solid var(--border-color)' : 'none',
                  backgroundColor: 'var(--bg-secondary)',
                  transition: 'var(--transition-fast)'
                }}>
                  <div style={{
                    backgroundColor: activity.status === 'completed' ? 'var(--accent-green)' :
                                   activity.status === 'pending' ? 'var(--accent-orange)' : 'var(--accent-red)',
                    color: 'var(--text-primary)',
                    padding: '4px 8px',
                    borderRadius: 'var(--radius-xs)',
                    fontSize: '0.75rem',
                    fontWeight: 'var(--font-weight-bold)',
                    marginRight: 'var(--spacing-md)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                    minWidth: '80px',
                    textAlign: 'center'
                  }}>
                    {activity.status}
                  </div>
                  <div className="flex items-center gap-sm" style={{ flex: 1 }}>
                    <div style={{
                      width: '20px',
                      height: '20px',
                      backgroundColor: 'var(--bg-tertiary)',
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '0.75rem',
                      border: '1px solid var(--border-color)'
                    }}>
                      {getActivityIcon(activity.type)}
                    </div>
                    <span style={{ fontWeight: 'var(--font-weight-medium)', color: 'var(--text-primary)' }}>
                      {activity.description}
                    </span>
                  </div>
                  <div className="flex items-center gap-sm">
                    {activity.amount && (
                      <span style={{ 
                        fontSize: '0.875rem',
                        fontWeight: 'var(--font-weight-bold)',
                        color: activity.type === 'purchase' ? 'var(--accent-green)' : 'var(--text-primary)'
                      }}>
                        {activity.amount}
                      </span>
                    )}
                    <div className="text-secondary" style={{ fontSize: '0.875rem' }}>
                      {activity.timestamp} via Telegram
                    </div>
                  </div>
                  <button style={{
                    backgroundColor: 'transparent',
                    border: 'none',
                    color: 'var(--text-secondary)',
                    padding: 'var(--spacing-xs)',
                    marginLeft: 'var(--spacing-sm)',
                    cursor: 'pointer'
                  }}>
                    ⋯
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Compact System Health & Actions */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
          
          {/* System Health */}
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">System</h3>
              <div className="badge badge-success">Healthy</div>
            </div>
            <div className="card-body">
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-xs">
                    <div style={{ width: '8px', height: '8px', backgroundColor: 'var(--accent-green)', borderRadius: '50%' }}></div>
                    <span style={{ fontSize: '0.875rem', color: 'var(--text-primary)' }}>Database</span>
                  </div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Connected</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-xs">
                    <div style={{ width: '8px', height: '8px', backgroundColor: 'var(--accent-green)', borderRadius: '50%' }}></div>
                    <span style={{ fontSize: '0.875rem', color: 'var(--text-primary)' }}>Bot API</span>
                  </div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Online</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-xs">
                    <div style={{ width: '8px', height: '8px', backgroundColor: 'var(--accent-blue)', borderRadius: '50%' }}></div>
                    <span style={{ fontSize: '0.875rem', color: 'var(--text-primary)' }}>Payments</span>
                  </div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Processing</span>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Actions</h3>
            </div>
            <div className="card-body">
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
                <button className="btn btn-secondary w-full btn-sm">
                  📊 Export Data
                </button>
                <button className="btn btn-secondary w-full btn-sm">
                  👥 Users
                </button>
                <button className="btn btn-secondary w-full btn-sm">
                  ⚙️ Settings
                </button>
                <button className="btn btn-success w-full btn-sm">
                  💎 Packages
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Compact Performance Metrics */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Performance</h3>
          <div className="flex gap-xs">
            <button className="btn btn-success btn-sm">Today</button>
            <button className="btn btn-secondary btn-sm">7D</button>
            <button className="btn btn-secondary btn-sm">30D</button>
          </div>
        </div>
        <div className="card-body">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 'var(--spacing-md)' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', color: 'var(--accent-green)', marginBottom: 'var(--spacing-xs)' }}>
                98.5%
              </div>
              <div style={{ fontSize: '0.875rem', fontWeight: 'var(--font-weight-medium)', color: 'var(--text-primary)' }}>Uptime</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Last 30 days</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', color: 'var(--accent-blue)', marginBottom: 'var(--spacing-xs)' }}>
                1.2s
              </div>
              <div style={{ fontSize: '0.875rem', fontWeight: 'var(--font-weight-medium)', color: 'var(--text-primary)' }}>Response</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Avg processing</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', color: 'var(--accent-orange)', marginBottom: 'var(--spacing-xs)' }}>
                {((stats?.totalCredits || 0) / 100).toFixed(1)}k
              </div>
              <div style={{ fontSize: '0.875rem', fontWeight: 'var(--font-weight-medium)', color: 'var(--text-primary)' }}>Credits Used</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>This month</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', color: 'var(--accent-green)', marginBottom: 'var(--spacing-xs)' }}>
                ${((stats?.estimatedRevenue || 0) * 12).toFixed(0)}
              </div>
              <div style={{ fontSize: '0.875rem', fontWeight: 'var(--font-weight-medium)', color: 'var(--text-primary)' }}>Projected</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Annual revenue</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage; 