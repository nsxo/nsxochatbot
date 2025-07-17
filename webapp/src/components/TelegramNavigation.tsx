import React from 'react'
import { motion } from 'framer-motion'
import { BarChart3, CreditCard, Settings } from 'lucide-react'

type Page = 'dashboard' | 'credits' | 'settings'

interface TelegramNavigationProps {
  currentPage: Page
  onNavigate: (page: Page) => void
}

export const TelegramNavigation: React.FC<TelegramNavigationProps> = ({
  currentPage,
  onNavigate
}) => {
  const navItems = [
    {
      id: 'dashboard' as Page,
      label: 'Dashboard',
      icon: BarChart3,
      gradient: 'from-blue-500 to-cyan-500'
    },
    {
      id: 'credits' as Page,
      label: 'Credits',
      icon: CreditCard,
      gradient: 'from-green-500 to-emerald-500'
    },
    {
      id: 'settings' as Page,
      label: 'Settings',
      icon: Settings,
      gradient: 'from-purple-500 to-pink-500'
    }
  ]

  return (
    <motion.div
      initial={{ y: 100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className="fixed bottom-0 left-0 right-0 z-50 bg-black/80 backdrop-blur-lg border-t border-white/10"
    >
      <div className="flex items-center justify-around px-4 py-2 safe-area-pb">
        {navItems.map((item) => {
          const IconComponent = item.icon
          return (
            <motion.button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`
                relative flex flex-col items-center justify-center p-3 rounded-2xl
                transition-all duration-300 min-w-[80px]
                ${currentPage === item.id 
                  ? 'bg-white/20 scale-105' 
                  : 'hover:bg-white/10 active:scale-95'
                }
              `}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {/* Active indicator */}
              {currentPage === item.id && (
                <motion.div
                  layoutId="activeTab"
                  className={`absolute inset-0 rounded-2xl bg-gradient-to-r ${item.gradient} opacity-20`}
                  transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                />
              )}
              
              {/* Icon */}
              <motion.div
                className="mb-1"
                animate={{ scale: currentPage === item.id ? 1.1 : 1 }}
                transition={{ duration: 0.2 }}
              >
                <IconComponent 
                  size={24} 
                  className={`transition-colors duration-200 ${
                    currentPage === item.id ? 'text-white' : 'text-gray-400'
                  }`}
                />
              </motion.div>
              
              {/* Label */}
              <span className={`
                text-xs font-medium transition-colors duration-200
                ${currentPage === item.id ? 'text-white' : 'text-gray-400'}
              `}>
                {item.label}
              </span>
              
              {/* Active dot */}
              {currentPage === item.id && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className={`absolute -top-1 w-2 h-2 rounded-full bg-gradient-to-r ${item.gradient}`}
                />
              )}
            </motion.button>
          )
        })}
      </div>
    </motion.div>
  )
}

export default TelegramNavigation 