import React, { useState, useEffect } from 'react';
import StatCard from './StatCard';

interface DashboardStats {
  totalUsers: number;
  activeUsers: number;
  messagesToday: number;
  totalCredits: number;
  monthlyPayments: number;
  estimatedRevenue: number;
  lastUpdated: string;
}

const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadStats = async () => {
      try {
        const response = await fetch('/api/dashboard/stats');
        if (!response.ok) throw new Error('Failed to fetch stats');
        const data = await response.json();
        setStats(data);
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

  if (error) {
    return (
      <div className="flex items-center justify-center" style={{ minHeight: '400px' }}>
        <div className="card" style={{ textAlign: 'center', maxWidth: '500px' }}>
          <div style={{ fontSize: '3rem', marginBottom: 'var(--spacing-md)' }}>⚠️</div>
          <h2>Error Loading Dashboard</h2>
          <p className="text-secondary">{error}</p>
          <button 
            className="btn btn-primary"
            onClick={() => window.location.reload()}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Quick Actions Bar */}
      <div className="card mb-lg">
        <div className="card-header">
          <h3 className="card-title">Quick Actions</h3>
          <button className="btn btn-secondary btn-sm">
            🔄 Refresh Data
          </button>
        </div>
        <div className="flex gap-md">
          <button className="btn btn-success">
            📊 Export Analytics
          </button>
          <button className="btn btn-secondary">
            ⚙️ Configure Settings
          </button>
          <button className="btn btn-secondary">
            👥 Manage Users
          </button>
          <button className="btn btn-primary">
            🚀 Upgrade Plan
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        <StatCard
          title="Total Users"
          value={stats?.totalUsers || 0}
          icon="👥"
          change={{
            value: '+12%',
            type: 'positive'
          }}
          loading={loading}
        />
        <StatCard
          title="Active Users"
          value={stats?.activeUsers || 0}
          icon="⚡"
          change={{
            value: '+8%',
            type: 'positive'
          }}
          loading={loading}
        />
        <StatCard
          title="Messages Today"
          value={stats?.messagesToday || 0}
          icon="💬"
          change={{
            value: '+25%',
            type: 'positive'
          }}
          loading={loading}
        />
        <StatCard
          title="Total Credits"
          value={stats?.totalCredits?.toLocaleString() || 0}
          icon="💎"
          change={{
            value: '-3%',
            type: 'negative'
          }}
          loading={loading}
        />
        <StatCard
          title="Monthly Revenue"
          value={`$${stats?.estimatedRevenue || 0}`}
          icon="💰"
          change={{
            value: '+18%',
            type: 'positive'
          }}
          loading={loading}
        />
        <StatCard
          title="Payments"
          value={stats?.monthlyPayments || 0}
          icon="💳"
          change={{
            value: '+6%',
            type: 'positive'
          }}
          loading={loading}
        />
      </div>

      {/* Charts & Analytics Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 'var(--spacing-lg)', marginBottom: 'var(--spacing-lg)' }}>
        {/* Activity Chart */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">User Activity</h3>
            <div className="flex gap-sm">
              <button className="btn btn-secondary btn-sm">7D</button>
              <button className="btn btn-success btn-sm">30D</button>
              <button className="btn btn-secondary btn-sm">90D</button>
            </div>
          </div>
          <div className="card-body">
            {/* Placeholder for chart */}
            <div 
              style={{
                height: '300px',
                background: 'linear-gradient(135deg, rgba(0, 229, 155, 0.1), rgba(0, 168, 229, 0.1))',
                borderRadius: 'var(--radius-md)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                border: '2px dashed var(--border-color)'
              }}
            >
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '2rem', marginBottom: 'var(--spacing-sm)' }}>📈</div>
                <p className="text-secondary">Activity Chart</p>
                <p className="text-secondary text-small">Chart component integration</p>
              </div>
            </div>
          </div>
        </div>

        {/* Top Users */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Top Users</h3>
            <button className="btn btn-secondary btn-sm">View All</button>
          </div>
          <div className="card-body">
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
              {[
                { name: 'Admin User', credits: 1000, avatar: '👑' },
                { name: 'Premium User', credits: 500, avatar: '⭐' },
                { name: 'Active User', credits: 250, avatar: '🔥' },
                { name: 'New User', credits: 100, avatar: '🆕' },
              ].map((user, index) => (
                <div key={index} className="flex items-center justify-between p-sm rounded bg-tertiary">
                  <div className="flex items-center gap-sm">
                    <div 
                      style={{
                        width: '32px',
                        height: '32px',
                        borderRadius: '50%',
                        background: 'linear-gradient(135deg, var(--accent-green), var(--accent-blue))',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '1rem'
                      }}
                    >
                      {user.avatar}
                    </div>
                    <div>
                      <div style={{ fontWeight: 'var(--font-weight-medium)', fontSize: '0.875rem', color: 'var(--text-primary)' }}>
                        {user.name}
                      </div>
                      <div className="text-secondary text-small">
                        {user.credits} credits
                      </div>
                    </div>
                  </div>
                  <div className="badge badge-success">
                    Active
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Recent Activity</h3>
          <div className="flex gap-sm">
            <button className="btn btn-secondary btn-sm">Filter</button>
            <button className="btn btn-secondary btn-sm">Export</button>
          </div>
        </div>
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Event</th>
                <th>User</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              {[
                { event: 'Credit Purchase', user: 'user123', amount: '$15.00', status: 'completed', time: '2 min ago' },
                { event: 'Message Sent', user: 'user456', amount: '3 credits', status: 'processed', time: '5 min ago' },
                { event: 'User Registration', user: 'user789', amount: '10 credits', status: 'completed', time: '12 min ago' },
                { event: 'Settings Updated', user: 'admin', amount: '-', status: 'completed', time: '1 hour ago' },
              ].map((activity, index) => (
                <tr key={index}>
                  <td>
                    <div className="flex items-center gap-sm">
                      <span>{activity.event === 'Credit Purchase' ? '💳' : 
                             activity.event === 'Message Sent' ? '💬' :
                             activity.event === 'User Registration' ? '👤' : '⚙️'}</span>
                      <span>{activity.event}</span>
                    </div>
                  </td>
                  <td className="text-accent">{activity.user}</td>
                  <td>{activity.amount}</td>
                  <td>
                    <span className={`badge ${
                      activity.status === 'completed' ? 'badge-success' :
                      activity.status === 'processed' ? 'badge-info' : 'badge-warning'
                    }`}>
                      {activity.status}
                    </span>
                  </td>
                  <td className="text-secondary">{activity.time}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Last Updated */}
      {stats?.lastUpdated && (
        <div style={{ textAlign: 'center', marginTop: 'var(--spacing-lg)' }}>
          <p className="text-secondary text-small">
            Last updated: {new Date(stats.lastUpdated).toLocaleString()}
          </p>
        </div>
      )}
    </div>
  );
};

export default DashboardPage; 