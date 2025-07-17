import React from 'react';
import { DeviantIcon } from './DeviantIcons';

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
    <div className="stat-card-compact">
      <div className="stat-card-content">
        <div className="stat-header-compact">
          <div className="stat-icon-compact">
            <DeviantIcon name={icon as keyof typeof import('./DeviantIcons').iconMap} size={20} />
          </div>
          <div className="stat-title-compact">{title}</div>
        </div>
        
        <div className="stat-value-compact">
          {loading ? (
            <div className="loading-spinner" style={{ margin: '0.5rem 0' }}></div>
          ) : (
            <span>{value}</span>
          )}
        </div>
        
        {change && !loading && (
          <div className={`stat-change-compact ${change.type}`}>
            <span className="stat-change-icon">
              {change.type === 'positive' ? '↗' : '↘'}
            </span>
            <span className="stat-change-value">{change.value}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default StatCard; 