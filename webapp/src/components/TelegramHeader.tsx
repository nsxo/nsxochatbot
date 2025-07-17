import React from 'react'
import { motion } from 'framer-motion'

interface TelegramHeaderProps {
  user?: {
    first_name?: string
    last_name?: string
    username?: string
    photo_url?: string
  } | null
  title: string
  subtitle?: string
}

export const TelegramHeader: React.FC<TelegramHeaderProps> = ({
  user,
  title,
  subtitle
}) => {
  const getInitials = () => {
    if (!user) return '🤖'
    const firstName = user.first_name?.[0] || ''
    const lastName = user.last_name?.[0] || ''
    return firstName + lastName || user.username?.[0]?.toUpperCase() || '👤'
  }

  const getUserName = () => {
    if (!user) return 'Guest'
    return user.first_name || user.username || 'User'
  }

  return (
    <motion.div
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className="relative bg-gradient-to-r from-blue-600 via-blue-700 to-blue-800 text-white"
    >
      {/* Background pattern */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_50%,white_1px,transparent_1px)] bg-[length:40px_40px]" />
      </div>
      
      <div className="relative px-6 py-4 safe-area-pt">
        <div className="flex items-center space-x-4">
          {/* User Avatar */}
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="relative"
          >
            {user?.photo_url ? (
              <img
                src={user.photo_url}
                alt={getUserName()}
                className="w-12 h-12 rounded-full border-2 border-white/30 shadow-lg"
              />
            ) : (
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white font-semibold text-lg border-2 border-white/30 shadow-lg">
                {getInitials()}
              </div>
            )}
            
            {/* Online status indicator */}
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2 }}
              className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white shadow-sm"
            />
          </motion.div>
          
          {/* User Info */}
          <div className="flex-1 min-w-0">
            <motion.h1
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.1 }}
              className="text-xl font-bold text-white truncate"
            >
              {title}
            </motion.h1>
            
            <motion.div
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.15 }}
              className="flex items-center space-x-2 text-blue-100"
            >
              <span className="text-sm">
                Hey, {getUserName()}! 👋
              </span>
              {subtitle && (
                <>
                  <span className="text-blue-300">•</span>
                  <span className="text-sm">{subtitle}</span>
                </>
              )}
            </motion.div>
          </div>
          
          {/* Notification Badge */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="relative p-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors"
          >
            <span className="text-xl">🔔</span>
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.3 }}
              className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full border border-white"
            />
          </motion.button>
        </div>
        
        {/* Telegram-style shine effect */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent"
          initial={{ x: '-100%' }}
          animate={{ x: '100%' }}
          transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
        />
      </div>
    </motion.div>
  )
}

export default TelegramHeader 