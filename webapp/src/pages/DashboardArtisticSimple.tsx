import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Container, 
  Box, 
  Typography, 
  Paper,
  Stack,
  Avatar,
  Chip
} from '@mui/material'
import { 
  Crown, 
  Palette,
  Sparkles,
  Award,
  Heart
} from 'lucide-react'
import { TelegramWebApp, UserData, StatsData } from '../types/telegram'
import ArtisticStatsCard from '../components/ArtisticStatsCard'
import ArtisticActionButton from '../components/ArtisticActionButton'
import { deviantArtColors } from '../styles/DeviantArtTheme'

interface DashboardArtisticProps {
  user: any
  telegramApp: TelegramWebApp | null
  onNavigate: (page: 'dashboard' | 'credits' | 'settings') => void
}

export default function DashboardArtisticSimple({ user, onNavigate }: DashboardArtisticProps) {
  const [userData, setUserData] = useState<UserData | null>(null)
  const [stats, setStats] = useState<StatsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [greeting, setGreeting] = useState('')

  useEffect(() => {
    fetchUserData()
    setDynamicGreeting()
  }, [user])

  const setDynamicGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) setGreeting('Good Morning')
    else if (hour < 17) setGreeting('Good Afternoon')
    else setGreeting('Good Evening')
  }

  const fetchUserData = async () => {
    try {
      setTimeout(() => {
        setUserData({
          id: user?.id || 123456789,
          first_name: user?.first_name || 'Creative',
          last_name: user?.last_name || 'Artist',
          username: user?.username,
          credits: 150,
          tier: 'Premium Creator',
          messages_sent: 342,
          total_spent: 89.50
        })
        
        setStats({
          total_credits: 150,
          messages_sent: 342,
          total_spent: 89.50,
          active_conversations: 5,
          tier: 'Premium Creator',
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
      <Container maxWidth="lg" sx={{ py: 4, minHeight: '100vh' }}>
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          minHeight: '60vh',
          flexDirection: 'column',
          gap: 3
        }}>
          <motion.div
            animate={{ 
              rotate: 360,
              scale: [1, 1.2, 1]
            }}
            transition={{ 
              rotate: { duration: 2, repeat: Infinity, ease: "linear" },
              scale: { duration: 1, repeat: Infinity, ease: "easeInOut" }
            }}
          >
            <Palette size={48} color={deviantArtColors.primary.main} />
          </motion.div>
          <Typography 
            variant="h6" 
            sx={{ 
              color: deviantArtColors.neutral[300],
              background: deviantArtColors.gradients.creative,
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}
          >
            Loading your creative dashboard...
          </Typography>
        </Box>
      </Container>
    )
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4, position: 'relative' }}>
      {/* Background Artistic Elements */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '300px',
          background: `radial-gradient(ellipse at top, ${deviantArtColors.primary.main}15 0%, transparent 60%)`,
          zIndex: -1,
          pointerEvents: 'none'
        }}
      />
      
      {/* Header Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <Paper
          elevation={0}
          sx={{
            background: `linear-gradient(135deg, 
              rgba(42, 51, 42, 0.95) 0%, 
              rgba(78, 98, 82, 0.85) 100%)`,
            backdropFilter: 'blur(20px)',
            border: `1px solid ${deviantArtColors.neutral[700]}`,
            borderRadius: 6,
            p: 4,
            mb: 4,
            position: 'relative',
            overflow: 'hidden'
          }}
        >
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'space-between',
            position: 'relative',
            zIndex: 1
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
              <Avatar
                sx={{
                  width: 72,
                  height: 72,
                  background: deviantArtColors.gradients.creative,
                  fontSize: '1.5rem',
                  fontWeight: 700,
                  boxShadow: '0 8px 24px rgba(5, 204, 71, 0.3)',
                  border: '3px solid rgba(255, 255, 255, 0.2)'
                }}
              >
                {userData?.first_name?.charAt(0) || 'U'}
              </Avatar>
              
              <Box>
                <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 1 }}>
                  <Typography
                    variant="h4"
                    sx={{
                      fontWeight: 800,
                      background: deviantArtColors.gradients.creative,
                      backgroundClip: 'text',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                      filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.3))'
                    }}
                  >
                    {greeting}, {userData?.first_name}! 
                  </Typography>
                  <motion.div
                    animate={{ rotate: [0, 15, -15, 0] }}
                    transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                  >
                    <Sparkles size={32} color={deviantArtColors.accent.yellow} />
                  </motion.div>
                </Stack>
                
                <Typography
                  variant="h6"
                  sx={{ 
                    color: deviantArtColors.neutral[300],
                    mb: 2,
                    fontWeight: 500
                  }}
                >
                  Welcome to your enhanced creative AI dashboard
                </Typography>
                
                <Stack direction="row" spacing={2} alignItems="center">
                  <Chip
                    icon={<Crown size={16} />}
                    label={userData?.tier || 'Free Tier'}
                    sx={{
                      background: deviantArtColors.gradients.artistic,
                      color: 'white',
                      fontWeight: 600,
                      '& .MuiChip-icon': { color: 'white' }
                    }}
                  />
                  <Chip
                    icon={<Award size={16} />}
                    label="Active Creator"
                    variant="outlined"
                    sx={{
                      borderColor: deviantArtColors.accent.teal,
                      color: deviantArtColors.accent.teal,
                      fontWeight: 500,
                      '& .MuiChip-icon': { color: deviantArtColors.accent.teal }
                    }}
                  />
                </Stack>
              </Box>
            </Box>
          </Box>
        </Paper>
      </motion.div>

      {/* Statistics Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <Typography
          variant="h5"
          sx={{
            fontWeight: 700,
            color: deviantArtColors.neutral[200],
            mb: 3,
            background: deviantArtColors.gradients.creative,
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}
        >
          🎨 Your Creative Statistics
        </Typography>
        
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr 1fr' },
          gap: 3,
          mb: 5 
        }}>
          <ArtisticStatsCard
            title="Credits Balance"
            value={stats?.total_credits || 0}
            subtitle="Available for AI chats"
            description="Your current credits for generating creative content and conversations"
            progress={75}
            icon="zap"
            variant="primary"
            showBadge={true}
            badgeText="Active"
            interactions={{ likes: 24, views: 892 }}
            trendValue="+12 this week"
            trend="up"
            delay={0.1}
          />
          
          <ArtisticStatsCard
            title="Messages Sent"
            value={stats?.messages_sent || 0}
            subtitle="Total conversations"
            description="Total number of creative messages and interactions"
            progress={85}
            icon="message"
            variant="secondary"
            showBadge={true}
            badgeText="Popular"
            interactions={{ likes: 156, shares: 23 }}
            trendValue="+28 today"
            trend="up"
            delay={0.2}
          />
          
          <ArtisticStatsCard
            title="Success Rate"
            value={`${stats?.success_rate || 0}%`}
            subtitle="AI response quality"
            description="Quality rating of AI-generated creative content"
            progress={Math.round(stats?.success_rate || 0)}
            icon="award"
            variant="artistic"
            showBadge={true}
            badgeText="Excellent"
            interactions={{ likes: 89, views: 1247 }}
            trendValue="Excellent"
            trend="up"
            delay={0.3}
          />
          
          <ArtisticStatsCard
            title="Total Spent"
            value={`$${stats?.total_spent || 0}`}
            subtitle="Lifetime investment"
            description="Total amount invested in your creative AI journey"
            icon="crown"
            variant="warm"
            showBadge={true}
            badgeText="Premium"
            interactions={{ views: 445 }}
            trendValue="This month"
            delay={0.4}
          />
        </Box>
      </motion.div>

      {/* Quick Actions Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
      >
        <Typography
          variant="h5"
          sx={{
            fontWeight: 700,
            color: deviantArtColors.neutral[200],
            mb: 3,
            background: deviantArtColors.gradients.artistic,
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}
        >
          🚀 Creative Quick Actions
        </Typography>
        
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr' },
          gap: 3,
          mb: 5 
        }}>
          <ArtisticActionButton
            title="Start Creating"
            description="Begin a new AI-powered creative conversation"
            icon="palette"
            variant="primary"
            badge="Popular"
            badgeColor="hot"
            popularity={{ likes: 1247, views: 5623, trending: true }}
            onClick={() => onNavigate('dashboard')}
            delay={0.1}
          />
          
          <ArtisticActionButton
            title="Buy Credits"
            description="Recharge your account with AI chat credits"
            icon="zap"
            variant="warm"
            badge="Best Value"
            badgeColor="popular"
            popularity={{ likes: 892, views: 3456 }}
            onClick={() => onNavigate('credits')}
            delay={0.2}
          />
          
          <ArtisticActionButton
            title="Account Settings"
            description="Manage your preferences and creative profile"
            icon="settings"
            variant="artistic"
            popularity={{ views: 445 }}
            onClick={() => onNavigate('settings')}
            delay={0.3}
          />
        </Box>
      </motion.div>

      {/* Creative Showcase Banner */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.6 }}
        style={{ marginTop: '3rem' }}
      >
        <Paper
          elevation={0}
          sx={{
            background: deviantArtColors.gradients.artistic,
            borderRadius: 6,
            p: 4,
            textAlign: 'center',
            position: 'relative',
            overflow: 'hidden'
          }}
        >
          <Typography
            variant="h4"
            sx={{
              fontWeight: 800,
              color: 'white',
              mb: 2,
              filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.3))'
            }}
          >
            ✨ Your Creative AI Journey Awaits
          </Typography>
          <Typography
            variant="h6"
            sx={{
              color: 'rgba(255, 255, 255, 0.9)',
              mb: 3,
              maxWidth: '600px',
              mx: 'auto'
            }}
          >
            Join thousands of creators using AI to unlock their artistic potential. 
            Create, share, and inspire with the power of artificial intelligence.
          </Typography>
          
          <Stack direction="row" justifyContent="center" spacing={2}>
            <Chip
              icon={<Sparkles size={16} />}
              label="Premium Components"
              sx={{
                background: 'rgba(255, 255, 255, 0.2)',
                color: 'white',
                fontWeight: 600,
                '& .MuiChip-icon': { color: 'white' }
              }}
            />
            <Chip
              icon={<Heart size={16} />}
              label="DeviantArt Inspired"
              sx={{
                background: 'rgba(255, 255, 255, 0.2)',
                color: 'white',
                fontWeight: 600,
                '& .MuiChip-icon': { color: 'white' }
              }}
            />
            <Chip
              icon={<Award size={16} />}
              label="Creative Excellence"
              sx={{
                background: 'rgba(255, 255, 255, 0.2)',
                color: 'white',
                fontWeight: 600,
                '& .MuiChip-icon': { color: 'white' }
              }}
            />
          </Stack>
        </Paper>
      </motion.div>
    </Container>
  )
} 