import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'

const StatCard = ({ title, value, trend, trendValue, icon, color = 'blue' }) => {
  const colorClasses = {
    blue: 'text-blue-600 bg-blue-100',
    green: 'text-green-600 bg-green-100',
    purple: 'text-purple-600 bg-purple-100',
    orange: 'text-orange-600 bg-orange-100',
  }

  return (
    <div className="card p-6 animate-slide-up">
      <div className="flex items-center">
        <div className="flex-shrink-0">
          <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
            <span className="text-2xl">{icon}</span>
          </div>
        </div>
        <div className="ml-5 w-0 flex-1">
          <dl>
            <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
            <dd className="flex items-baseline">
              <div className="text-2xl font-semibold text-gray-900">{value}</div>
              {trend && (
                <div className={`ml-2 flex items-baseline text-sm font-semibold ${
                  trend === 'up' ? 'text-green-600' : 'text-red-600'
                }`}>
                  <span className="text-lg">{trend === 'up' ? '↗️' : '↘️'}</span>
                  <span className="sr-only">{trend === 'up' ? 'Increased' : 'Decreased'} by</span>
                  {trendValue}
                </div>
              )}
            </dd>
          </dl>
        </div>
      </div>
    </div>
  )
}

const QuickAction = ({ title, description, icon, to, color = 'blue' }) => {
  const colorClasses = {
    blue: 'text-blue-600 bg-blue-100 hover:bg-blue-200',
    green: 'text-green-600 bg-green-100 hover:bg-green-200',
    purple: 'text-purple-600 bg-purple-100 hover:bg-purple-200',
    orange: 'text-orange-600 bg-orange-100 hover:bg-orange-200',
  }

  return (
    <Link to={to} className="block">
      <div className="card p-6 hover:shadow-lg transition-all duration-200 hover:scale-105">
        <div className="flex items-center">
          <div className={`p-3 rounded-lg ${colorClasses[color]} transition-colors`}>
            <span className="text-2xl">{icon}</span>
          </div>
          <div className="ml-4">
            <h3 className="text-lg font-medium text-gray-900">{title}</h3>
            <p className="text-sm text-gray-500">{description}</p>
          </div>
        </div>
      </div>
    </Link>
  )
}

export default function Dashboard() {
  const [stats, setStats] = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      const response = await api.get('/admin/dashboard')
      setStats(response.data)
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
      // Set mock data for demo
      setStats({
        total_users: 150,
        active_users: 45,
        total_messages: 1234,
        total_revenue: 2500,
        trends: {
          users: { direction: 'up', value: '12%' },
          messages: { direction: 'up', value: '8%' },
          revenue: { direction: 'up', value: '15%' },
        }
      })
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Welcome to your bot admin dashboard. Monitor performance and manage settings.
        </p>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Users"
          value={stats.total_users?.toLocaleString() || '0'}
          icon="👥"
          trend={stats.trends?.users?.direction}
          trendValue={stats.trends?.users?.value}
          color="blue"
        />
        
        <StatCard
          title="Active Users"
          value={stats.active_users?.toLocaleString() || '0'}
          icon="🟢"
          trend={stats.trends?.active?.direction}
          trendValue={stats.trends?.active?.value}
          color="green"
        />
        
        <StatCard
          title="Total Messages"
          value={stats.total_messages?.toLocaleString() || '0'}
          icon="💬"
          trend={stats.trends?.messages?.direction}
          trendValue={stats.trends?.messages?.value}
          color="purple"
        />
        
        <StatCard
          title="Revenue ($)"
          value={`$${(stats.total_revenue || 0).toLocaleString()}`}
          icon="💰"
          trend={stats.trends?.revenue?.direction}
          trendValue={stats.trends?.revenue?.value}
          color="orange"
        />
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <QuickAction
            title="Bot Settings"
            description="Update welcome messages, pricing, and automated responses"
            icon="⚙️"
            to="/settings"
            color="blue"
          />
          
          <QuickAction
            title="Manage Products"
            description="Create, edit, and manage credit packages and pricing"
            icon="🛒"
            to="/products"
            color="green"
          />
          
          <QuickAction
            title="View Messages"
            description="Monitor conversations and manage automated messages"
            icon="💬"
            to="/messages"
            color="purple"
          />
          
          <QuickAction
            title="User Management"
            description="View user analytics and manage user accounts"
            icon="👥"
            to="/users"
            color="orange"
          />
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-4">
          {stats.recent_activity?.length > 0 ? (
            stats.recent_activity.map((activity, index) => (
              <div key={index} className="flex items-center space-x-4">
                <div className="flex-shrink-0 w-2 h-2 bg-blue-400 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm text-gray-900">{activity.description}</p>
                  <p className="text-xs text-gray-500">{activity.timestamp}</p>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-8">
              <span className="text-6xl mb-4 block">💬</span>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No recent activity</h3>
              <p className="mt-1 text-sm text-gray-500">Activity will appear here as users interact with your bot.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
} 