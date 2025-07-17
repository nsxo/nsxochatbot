import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Container, Box, Typography } from '@mui/material'
import { Zap } from 'lucide-react'
import { TelegramWebApp, UserData, StatsData } from '../types/telegram'
import PremiumStatsCard from '../components/PremiumStatsCard'
import PremiumActionButton from '../components/PremiumActionButton'

interface DashboardProps {
  user: any
  telegramApp: TelegramWebApp | null
  onNavigate: (page: 'dashboard' | 'credits' | 'settings') => void
}

export default function DashboardEnhanced({ user, telegramApp, onNavigate }: DashboardProps) {
  const [userData, setUserData] = useState<UserData | null>(null)
  const [stats, setStats] = useState<StatsData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Fetch user data from your bot API
    fetchUserData()
  }, [user])

  const fetchUserData = async () => {
    try {
      // Mock data for now - replace with actual API calls to your bot
      setTimeout(() => {
        setUserData({
          id: user?.id || 123456789,
          first_name: user?.first_name || 'User',
          last_name: user?.last_name,
          username: user?.username,
          credits: 150,
          tier: 'Premium',
          messages_sent: 342,
          total_spent: 89.50
        })
        
        setStats({
          total_credits: 150,
          messages_sent: 342,
          total_spent: 89.50,
          active_conversations: 5,
          tier: 'Premium',
          weekly_usage: 28,
          success_rate: 96.8
        })
        
        setLoading(false)
      }, 1000)
    } catch (error) {
      console.error('Error fetching user data:', error)
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        minHeight: '50vh',
        flexDirection: 'column'
      }}>
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          style={{ marginBottom: 16 }}
        >
          <Zap size={32} color="#2196F3" />
        </motion.div>
        <Typography variant="h6" color="text.secondary">
          Loading your enhanced dashboard...
        </Typography>
      </Box>
    )
  }

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      {/* Welcome Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <Box sx={{ mb: 4 }}>
          <Typography 
            variant="h4" 
            sx={{ 
              fontWeight: 700,
              background: 'linear-gradient(135deg, #2196F3 0%, #21CBF3 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              mb: 1
            }}
          >
            Welcome back, {userData?.first_name}! 👋
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Here's your enhanced AI chat dashboard with premium components
          </Typography>
        </Box>
      </motion.div>

      {/* Stats Grid - Simple Flexbox Layout */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" sx={{ fontWeight: 600, mb: 3 }}>
          Your Statistics
        </Typography>
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr 1fr' },
          gap: 3 
        }}>
          <PremiumStatsCard
            title="Credits Balance"
            value={userData?.credits || 0}
            subtitle="Available for AI chats"
            icon="zap"
            progress={75}
            trend="up"
            trendValue="+12 this week"
            gradient="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
            delay={0}
          />
          
          <PremiumStatsCard
            title="Messages Sent"
            value={stats?.messages_sent || 0}
            subtitle="Total conversations"
            icon="message"
            progress={85}
            trend="up"
            trendValue="+28 today"
            gradient="linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"
            delay={0.1}
          />
          
          <PremiumStatsCard
            title="Success Rate"
            value={`${stats?.success_rate || 96.8}%`}
            subtitle="AI response quality"
            icon="crown"
            progress={96.8}
            trend="up"
            trendValue="Excellent"
            gradient="linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
            delay={0.2}
          />
          
          <PremiumStatsCard
            title="Total Spent"
            value={`$${stats?.total_spent || 0}`}
            subtitle="Lifetime investment"
            icon="dollar"
            trend="neutral"
            trendValue="This month"
            gradient="linear-gradient(135deg, #fa709a 0%, #fee140 100%)"
            delay={0.3}
          />
        </Box>
      </Box>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
      >
        <Typography variant="h5" sx={{ fontWeight: 600, mb: 3 }}>
          Premium Quick Actions
        </Typography>
        
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr' },
          gap: 2 
        }}>
          <PremiumActionButton
            title="Buy Credits"
            subtitle="Get more AI chat credits"
            icon="cart"
            variant="primary"
            badge="Popular"
            fullWidth
            onClick={() => onNavigate('credits')}
          />
          
          <PremiumActionButton
            title="Chat History"
            subtitle="View past conversations"
            icon="clock"
            variant="secondary"
            fullWidth
            onClick={() => {
              telegramApp?.showAlert('Chat history feature coming soon!')
            }}
          />
          
          <PremiumActionButton
            title="Account Settings"
            subtitle="Manage your preferences"
            icon="settings"
            variant="success"
            fullWidth
            onClick={() => onNavigate('settings')}
          />
          
          <PremiumActionButton
            title="Upgrade to Pro"
            subtitle="Unlock premium features"
            icon="crown"
            variant="warning"
            badge="New"
            fullWidth
            onClick={() => {
              telegramApp?.showAlert('Pro upgrade coming soon!')
            }}
          />
          
          <PremiumActionButton
            title="Invite Friends"
            subtitle="Share and earn rewards"
            icon="star"
            variant="error"
            badge="Earn $5"
            fullWidth
            onClick={() => {
              telegramApp?.showAlert('Referral program coming soon!')
            }}
          />
          
          <PremiumActionButton
            title="Download Report"
            subtitle="Export your data"
            icon="download"
            variant="primary"
            fullWidth
            onClick={() => {
              telegramApp?.showAlert('Report download coming soon!')
            }}
          />
        </Box>
      </motion.div>

      {/* Recent Activity Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.6 }}
        style={{ marginTop: 32 }}
      >
        <Typography variant="h5" sx={{ fontWeight: 600, mb: 3 }}>
          Recent Activity
        </Typography>
        
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: { xs: '1fr', md: '2fr 1fr' },
          gap: 3 
        }}>
          <PremiumStatsCard
            title="Weekly Usage"
            value={`${stats?.weekly_usage || 28} hours`}
            subtitle="Time spent in AI conversations"
            icon="clock"
            progress={70}
            trend="up"
            trendValue="+5 hrs vs last week"
            gradient="linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)"
          />
          
          <PremiumStatsCard
            title="Active Users"
            value="2,847"
            subtitle="Community members"
            icon="users"
            trend="up"
            trendValue="+156 today"
            gradient="linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)"
          />
        </Box>
      </motion.div>

      {/* Features Showcase */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.8 }}
        style={{ marginTop: 32 }}
      >
        <Box sx={{ 
          p: 4, 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderRadius: 4,
          textAlign: 'center'
        }}>
          <Typography variant="h5" sx={{ color: 'white', fontWeight: 600, mb: 2 }}>
            🎉 Premium Components Showcase
          </Typography>
          <Typography variant="body1" sx={{ color: 'white', opacity: 0.9, mb: 3 }}>
            You're now using Material-UI + Lucide React + TelegramUI for the ultimate premium experience!
          </Typography>
          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'center', 
            gap: 2,
            flexWrap: 'wrap'
          }}>
            <Box sx={{ 
              px: 3, py: 1, 
              background: 'rgba(255,255,255,0.2)', 
              borderRadius: 2,
              color: 'white',
              fontSize: '0.875rem',
              fontWeight: 500
            }}>
              ✨ Material-UI Theme
            </Box>
            <Box sx={{ 
              px: 3, py: 1, 
              background: 'rgba(255,255,255,0.2)', 
              borderRadius: 2,
              color: 'white',
              fontSize: '0.875rem',
              fontWeight: 500
            }}>
              🎨 Lucide React Icons
            </Box>
            <Box sx={{ 
              px: 3, py: 1, 
              background: 'rgba(255,255,255,0.2)', 
              borderRadius: 2,
              color: 'white',
              fontSize: '0.875rem',
              fontWeight: 500
            }}>
              📱 Telegram Integration
            </Box>
            <Box sx={{ 
              px: 3, py: 1, 
              background: 'rgba(255,255,255,0.2)', 
              borderRadius: 2,
              color: 'white',
              fontSize: '0.875rem',
              fontWeight: 500
            }}>
              🚀 Framer Motion
            </Box>
          </Box>
        </Box>
      </motion.div>
    </Container>
  )
} 