import React from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: string;
  change?: {
    value: string;
    type: 'positive' | 'negative';
  };
  loading?: boolean;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, change, loading = false }) => {
  return (
    <div className="stat-card">
      <div className="stat-header">
        <div className="stat-title">{title}</div>
        <div className="stat-icon">{icon}</div>
      </div>
      
      <div className="stat-value">
        {loading ? (
          <div className="loading-spinner" style={{ margin: '1rem 0' }}></div>
        ) : (
          value
        )}
      </div>
      
      {change && !loading && (
        <div className={`stat-change ${change.type}`}>
          <span>{change.type === 'positive' ? '↗️' : '↘️'}</span>
          <span>{change.value}</span>
          <span className="text-secondary">vs last month</span>
        </div>
      )}
    </div>
  );
};

export default StatCard; 