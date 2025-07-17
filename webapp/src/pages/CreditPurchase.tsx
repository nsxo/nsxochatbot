import { useState } from 'react'
import { motion } from 'framer-motion'
import { CreditCard, Star, Zap, Crown, Check } from 'lucide-react'
import { TelegramWebApp } from '../types/telegram'

interface CreditPurchaseProps {
  user: any
  telegramApp: TelegramWebApp | null
  onNavigate: (page: 'dashboard' | 'credits' | 'settings') => void
}

interface CreditPackage {
  id: string
  credits: number
  price: number
  originalPrice?: number
  popular?: boolean
  tier: 'basic' | 'premium' | 'ultimate'
  features: string[]
}

export default function CreditPurchase({ user, telegramApp }: CreditPurchaseProps) {
  const [selectedPackage, setSelectedPackage] = useState<string>('')
  const [loading, setLoading] = useState(false)

  const packages: CreditPackage[] = [
    {
      id: 'basic',
      credits: 50,
      price: 9.99,
      tier: 'basic',
      features: ['50 AI Messages', 'Basic Support', '7 Days Valid']
    },
    {
      id: 'premium',
      credits: 150,
      price: 24.99,
      originalPrice: 29.99,
      popular: true,
      tier: 'premium',
      features: ['150 AI Messages', 'Priority Support', '30 Days Valid', 'Advanced Features']
    },
    {
      id: 'ultimate',
      credits: 300,
      price: 44.99,
      originalPrice: 59.99,
      tier: 'ultimate',
      features: ['300 AI Messages', 'VIP Support', '60 Days Valid', 'All Features', 'Exclusive Access']
    }
  ]

  const handlePurchase = async (packageId: string) => {
    setLoading(true)
    
    // Haptic feedback
    if (telegramApp?.HapticFeedback) {
      telegramApp.HapticFeedback.impactOccurred('heavy')
    }

    try {
      // Send purchase request to bot
      if (telegramApp) {
        telegramApp.sendData(JSON.stringify({
          action: 'purchase_credits',
          package_id: packageId,
          user_id: user?.id
        }))
      }
    } catch (error) {
      console.error('Purchase failed:', error)
      if (telegramApp?.HapticFeedback) {
        telegramApp.HapticFeedback.notificationOccurred('error')
      }
    } finally {
      setLoading(false)
    }
  }

  const getTierIcon = (tier: string) => {
    switch (tier) {
      case 'basic': return <CreditCard className="w-6 h-6" />
      case 'premium': return <Star className="w-6 h-6" />
      case 'ultimate': return <Crown className="w-6 h-6" />
      default: return <Zap className="w-6 h-6" />
    }
  }

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'basic': return 'text-blue-400'
      case 'premium': return 'text-yellow-400'
      case 'ultimate': return 'text-purple-400'
      default: return 'text-telegram-blue'
    }
  }

  return (
    <motion.div
      className="min-h-screen bg-telegram-bg p-4 pb-8"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-2">Buy Credits</h1>
        <p className="text-telegram-light">Choose a package that fits your needs</p>
      </div>

      {/* Packages */}
      <div className="space-y-4 mb-8">
        {packages.map((pkg, index) => (
          <motion.div
            key={pkg.id}
            className={`glass-card p-6 cursor-pointer border-2 transition-all duration-200 ${
              selectedPackage === pkg.id 
                ? 'border-telegram-blue bg-telegram-blue/10' 
                : 'border-white/20 hover:border-white/40'
            } ${pkg.popular ? 'relative' : ''}`}
            onClick={() => setSelectedPackage(pkg.id)}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {pkg.popular && (
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                <div className="bg-gradient-to-r from-yellow-400 to-orange-500 text-black px-4 py-1 rounded-full text-sm font-bold">
                  Most Popular
                </div>
              </div>
            )}

            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className={`p-2 bg-white/10 rounded-lg ${getTierColor(pkg.tier)}`}>
                  {getTierIcon(pkg.tier)}
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white capitalize">{pkg.tier}</h3>
                  <p className="text-telegram-light">{pkg.credits} Credits</p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-white">${pkg.price}</div>
                {pkg.originalPrice && (
                  <div className="text-sm text-telegram-light line-through">
                    ${pkg.originalPrice}
                  </div>
                )}
              </div>
            </div>

            <div className="space-y-2">
              {pkg.features.map((feature, i) => (
                <div key={i} className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-green-400" />
                  <span className="text-sm text-telegram-light">{feature}</span>
                </div>
              ))}
            </div>

            {pkg.originalPrice && (
              <div className="mt-4 p-3 bg-green-500/10 rounded-lg border border-green-500/20">
                <div className="text-green-400 text-sm font-medium">
                  Save ${(pkg.originalPrice - pkg.price).toFixed(2)} 
                  ({Math.round(((pkg.originalPrice - pkg.price) / pkg.originalPrice) * 100)}% off)
                </div>
              </div>
            )}
          </motion.div>
        ))}
      </div>

      {/* Purchase Button */}
      {selectedPackage && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="fixed bottom-4 left-4 right-4"
        >
          <button
            onClick={() => handlePurchase(selectedPackage)}
            disabled={loading}
            className="w-full button-primary flex items-center justify-center gap-2"
          >
            {loading ? (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            ) : (
              <>
                <CreditCard className="w-5 h-5" />
                Purchase {packages.find(p => p.id === selectedPackage)?.credits} Credits
              </>
            )}
          </button>
        </motion.div>
      )}
    </motion.div>
  )
} 