import React from 'react';

interface IconProps {
  size?: number;
  color?: string;
  className?: string;
}

// DeviantArt-inspired icon components
export const DashboardIcon: React.FC<IconProps> = ({ size = 20, color = 'currentColor', className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <path d="M3 3h7v7H3V3zM14 3h7v7h-7V3zM3 14h7v7H3v-7zM14 14h7v7h-7v-7z" 
          stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

export const SettingsIcon: React.FC<IconProps> = ({ size = 20, color = 'currentColor', className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <path d="M12 15a3 3 0 100-6 3 3 0 000 6z" stroke={color} strokeWidth="2"/>
    <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z" 
          stroke={color} strokeWidth="2"/>
  </svg>
);

export const DiamondIcon: React.FC<IconProps> = ({ size = 20, color = 'currentColor', className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" 
          stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

export const UsersIcon: React.FC<IconProps> = ({ size = 20, color = 'currentColor', className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" stroke={color} strokeWidth="2"/>
    <circle cx="9" cy="7" r="4" stroke={color} strokeWidth="2"/>
    <path d="M23 21v-2a4 4 0 00-3-3.87" stroke={color} strokeWidth="2"/>
    <path d="M16 3.13a4 4 0 010 7.75" stroke={color} strokeWidth="2"/>
  </svg>
);

export const AnalyticsIcon: React.FC<IconProps> = ({ size = 20, color = 'currentColor', className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <path d="M3 3v18h18" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

export const LogsIcon: React.FC<IconProps> = ({ size = 20, color = 'currentColor', className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" stroke={color} strokeWidth="2"/>
    <path d="M14 2v6h6" stroke={color} strokeWidth="2"/>
    <path d="M16 13H8" stroke={color} strokeWidth="2"/>
    <path d="M16 17H8" stroke={color} strokeWidth="2"/>
    <path d="M10 9H8" stroke={color} strokeWidth="2"/>
  </svg>
);

export const LightningIcon: React.FC<IconProps> = ({ size = 20, color = 'currentColor', className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

export const MessageIcon: React.FC<IconProps> = ({ size = 20, color = 'currentColor', className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" stroke={color} strokeWidth="2"/>
  </svg>
);

export const MoneyIcon: React.FC<IconProps> = ({ size = 20, color = 'currentColor', className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <circle cx="12" cy="12" r="8" stroke={color} strokeWidth="2"/>
    <path d="M12 8v8" stroke={color} strokeWidth="2"/>
    <path d="M8 12h8" stroke={color} strokeWidth="2"/>
  </svg>
);

export const CreditCardIcon: React.FC<IconProps> = ({ size = 20, color = 'currentColor', className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <rect x="1" y="4" width="22" height="16" rx="2" ry="2" stroke={color} strokeWidth="2"/>
    <path d="M1 10h22" stroke={color} strokeWidth="2"/>
  </svg>
);

export const PurchaseIcon: React.FC<IconProps> = ({ size = 20, color = 'currentColor', className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z" stroke={color} strokeWidth="2"/>
    <path d="M3 6h18" stroke={color} strokeWidth="2"/>
    <path d="M16 10a4 4 0 01-8 0" stroke={color} strokeWidth="2"/>
  </svg>
);

export const RegistrationIcon: React.FC<IconProps> = ({ size = 20, color = 'currentColor', className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" stroke={color} strokeWidth="2"/>
    <circle cx="12" cy="7" r="4" stroke={color} strokeWidth="2"/>
  </svg>
);

export const SystemIcon: React.FC<IconProps> = ({ size = 20, color = 'currentColor', className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <rect x="2" y="3" width="20" height="14" rx="2" ry="2" stroke={color} strokeWidth="2"/>
    <path d="M8 21h8" stroke={color} strokeWidth="2"/>
    <path d="M12 17v4" stroke={color} strokeWidth="2"/>
  </svg>
);

export const RefreshIcon: React.FC<IconProps> = ({ size = 20, color = 'currentColor', className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <path d="M23 4v6h-6" stroke={color} strokeWidth="2"/>
    <path d="M1 20v-6h6" stroke={color} strokeWidth="2"/>
    <path d="M20.49 9A9 9 0 005.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 013.51 15" stroke={color} strokeWidth="2"/>
  </svg>
);

export const MenuIcon: React.FC<IconProps> = ({ size = 20, color = 'currentColor', className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <path d="M3 12h18" stroke={color} strokeWidth="2"/>
    <path d="M3 6h18" stroke={color} strokeWidth="2"/>
    <path d="M3 18h18" stroke={color} strokeWidth="2"/>
  </svg>
);

export const PlusIcon: React.FC<IconProps> = ({ size = 20, color = 'currentColor', className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <path d="M12 5v14" stroke={color} strokeWidth="2"/>
    <path d="M5 12h14" stroke={color} strokeWidth="2"/>
  </svg>
);

export const ExportIcon: React.FC<IconProps> = ({ size = 20, color = 'currentColor', className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" stroke={color} strokeWidth="2"/>
    <path d="M7 10l5 5 5-5" stroke={color} strokeWidth="2"/>
    <path d="M12 15V3" stroke={color} strokeWidth="2"/>
  </svg>
);

export const BotIcon: React.FC<IconProps> = ({ size = 20, color = 'currentColor', className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <rect x="3" y="11" width="18" height="10" rx="2" ry="2" stroke={color} strokeWidth="2"/>
    <circle cx="12" cy="16" r="2" stroke={color} strokeWidth="2"/>
    <path d="M8 11V7a4 4 0 018 0v4" stroke={color} strokeWidth="2"/>
    <path d="M7 7h10" stroke={color} strokeWidth="2"/>
  </svg>
);

// Icon mapping for easy replacement
export const iconMap = {
  dashboard: DashboardIcon,
  settings: SettingsIcon,
  diamond: DiamondIcon,
  users: UsersIcon,
  analytics: AnalyticsIcon,
  logs: LogsIcon,
  lightning: LightningIcon,
  message: MessageIcon,
  money: MoneyIcon,
  creditCard: CreditCardIcon,
  purchase: PurchaseIcon,
  registration: RegistrationIcon,
  system: SystemIcon,
  refresh: RefreshIcon,
  menu: MenuIcon,
  plus: PlusIcon,
  export: ExportIcon,
  bot: BotIcon,
};

// Helper component for easy icon usage
export const DeviantIcon: React.FC<IconProps & { name: keyof typeof iconMap }> = ({ 
  name, 
  size = 20, 
  color = 'currentColor', 
  className = '' 
}) => {
  const IconComponent = iconMap[name];
  return IconComponent ? <IconComponent size={size} color={color} className={className} /> : null;
}; 