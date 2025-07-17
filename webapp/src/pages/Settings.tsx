import { useState } from 'react'
import { motion } from 'framer-motion'
import { User, Bell, Shield, CreditCard, HelpCircle, LogOut } from 'lucide-react'
import { TelegramWebApp } from '../types/telegram'

interface SettingsProps {
  user: any
  telegramApp: TelegramWebApp | null
  onNavigate: (page: 'dashboard' | 'credits' | 'settings') => void
}

export default function Settings({ user, telegramApp, onNavigate }: SettingsProps) {
  const [notifications, setNotifications] = useState(true)
  const [privacy, setPrivacy] = useState(true)

  const handleSettingChange = (setting: string, value: boolean) => {
    // Haptic feedback
    if (telegramApp?.HapticFeedback) {
      telegramApp.HapticFeedback.selectionChanged()
    }

    switch (setting) {
      case 'notifications':
        setNotifications(value)
        break
      case 'privacy':
        setPrivacy(value)
        break
    }

    // Send settings update to bot
    if (telegramApp) {
      telegramApp.sendData(JSON.stringify({
        action: 'update_settings',
        setting,
        value,
        user_id: user?.id
      }))
    }
  }

  const handleAction = (action: string) => {
    if (telegramApp?.HapticFeedback) {
      telegramApp.HapticFeedback.impactOccurred('medium')
    }

    if (telegramApp) {
      telegramApp.sendData(JSON.stringify({
        action,
        user_id: user?.id
      }))
    }
  }

  const settingsItems = [
    {
      title: 'Profile',
      icon: <User className="w-5 h-5" />,
      action: () => handleAction('view_profile'),
      type: 'action'
    },
    {
      title: 'Notifications',
      icon: <Bell className="w-5 h-5" />,
      action: () => handleSettingChange('notifications', !notifications),
      type: 'toggle',
      value: notifications
    },
    {
      title: 'Privacy Settings',
      icon: <Shield className="w-5 h-5" />,
      action: () => handleSettingChange('privacy', !privacy),
      type: 'toggle',
      value: privacy
    },
    {
      title: 'Payment Methods',
      icon: <CreditCard className="w-5 h-5" />,
      action: () => handleAction('manage_payments'),
      type: 'action'
    },
    {
      title: 'Help & Support',
      icon: <HelpCircle className="w-5 h-5" />,
      action: () => handleAction('get_support'),
      type: 'action'
    }
  ]

  return (
    <motion.div
      className="min-h-screen bg-telegram-bg p-4 pb-8"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-2">Settings</h1>
        <p className="text-telegram-light">Manage your account and preferences</p>
      </div>

      {/* User Info */}
      <motion.div
        className="glass-card p-6 mb-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-telegram-blue/20 rounded-full flex items-center justify-center">
            <User className="w-8 h-8 text-telegram-blue" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-white">
              {user?.first_name} {user?.last_name || ''}
            </h3>
            <p className="text-telegram-light">@{user?.username || 'username'}</p>
            <p className="text-sm text-telegram-light">Premium Member</p>
          </div>
        </div>
      </motion.div>

      {/* Settings List */}
      <div className="space-y-4">
        {settingsItems.map((item, index) => (
          <motion.div
            key={item.title}
            className="glass-card p-4 cursor-pointer hover:bg-white/15 transition-all duration-200"
            onClick={item.action}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 + index * 0.05 }}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="text-telegram-blue">
                  {item.icon}
                </div>
                <span className="text-white font-medium">{item.title}</span>
              </div>
              
              {item.type === 'toggle' ? (
                <div className={`w-12 h-6 rounded-full transition-all duration-200 ${
                  item.value ? 'bg-telegram-blue' : 'bg-gray-600'
                }`}>
                  <div className={`w-6 h-6 bg-white rounded-full transition-all duration-200 transform ${
                    item.value ? 'translate-x-6' : 'translate-x-0'
                  }`} />
                </div>
              ) : (
                <div className="text-telegram-light">
                  →
                </div>
              )}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Footer Actions */}
      <motion.div
        className="mt-8 space-y-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <button
          onClick={() => onNavigate('dashboard')}
          className="w-full button-secondary"
        >
          Back to Dashboard
        </button>
        
        <button
          onClick={() => handleAction('logout')}
          className="w-full bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/20 font-medium py-3 px-6 rounded-lg transition-all duration-200 flex items-center justify-center gap-2"
        >
          <LogOut className="w-5 h-5" />
          Sign Out
        </button>
      </motion.div>
    </motion.div>
  )
} 