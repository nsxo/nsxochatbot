import { motion } from 'framer-motion'
import { Plus, MessageCircle, CreditCard } from 'lucide-react'
import { useState } from 'react'

interface FloatingActionButtonProps {
  onAction: (action: string) => void
}

export default function FloatingActionButton({ onAction }: FloatingActionButtonProps) {
  const [isOpen, setIsOpen] = useState(false)

  const actions = [
    { 
      id: 'new-chat', 
      icon: MessageCircle, 
      label: 'New Chat',
      color: 'from-brand-electric-blue to-brand-blue-gradient'
    },
    { 
      id: 'buy-credits', 
      icon: CreditCard, 
      label: 'Buy Credits',
      color: 'from-brand-red to-brand-red-gradient'
    }
  ]

  const handleAction = (actionId: string) => {
    onAction(actionId)
    setIsOpen(false)
  }

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Action Menu */}
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          className="absolute bottom-16 right-0 space-y-3"
        >
          {actions.map((action, index) => (
            <motion.button
              key={action.id}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              onClick={() => handleAction(action.id)}
              className="flex items-center gap-3 px-4 py-3 glass-card hover:bg-white/15 transition-all duration-300 group whitespace-nowrap"
            >
              <div className={`p-2 rounded-lg bg-gradient-to-r ${action.color}`}>
                <action.icon className="w-4 h-4 text-white" />
              </div>
              <span className="text-white font-medium text-sm">{action.label}</span>
            </motion.button>
          ))}
        </motion.div>
      )}

      {/* Main FAB */}
      <motion.button
        className="fab ripple-effect"
        onClick={() => setIsOpen(!isOpen)}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        animate={{ rotate: isOpen ? 45 : 0 }}
        transition={{ duration: 0.3 }}
      >
        <Plus className="w-6 h-6 text-white" />
      </motion.button>
    </div>
  )
} 