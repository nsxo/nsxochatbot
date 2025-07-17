import React from 'react'
import { 
  Card, 
  CardContent, 
  Typography, 
  Box, 
  Chip,
  LinearProgress,
  useTheme
} from '@mui/material'
import { motion } from 'framer-motion'
import { 
  TrendingUp, 
  TrendingDown, 
  Zap, 
  Clock, 
  DollarSign,
  Users,
  MessageSquare,
  Settings,
  Crown,
  Sparkles
} from 'lucide-react'

interface StatsCardProps {
  title: string
  value: string | number
  subtitle?: string
  trend?: 'up' | 'down' | 'neutral'
  trendValue?: string
  progress?: number
  icon?: string
  gradient?: string
  delay?: number
}

const iconMap = {
  zap: Zap,
  clock: Clock,
  dollar: DollarSign,
  users: Users,
  message: MessageSquare,
  settings: Settings,
  crown: Crown,
  sparkles: Sparkles,
}

export const PremiumStatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  subtitle,
  trend = 'neutral',
  trendValue,
  progress,
  icon = 'zap',
  gradient = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  delay = 0
}) => {
  const theme = useTheme()
  const IconComponent = iconMap[icon as keyof typeof iconMap] || Zap

  const getTrendColor = () => {
    switch (trend) {
      case 'up': return theme.palette.success.main
      case 'down': return theme.palette.error.main
      default: return theme.palette.text.secondary
    }
  }

  const getTrendIcon = () => {
    switch (trend) {
      case 'up': return <TrendingUp size={16} />
      case 'down': return <TrendingDown size={16} />
      default: return null
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ 
        duration: 0.4, 
        delay,
        type: "spring",
        stiffness: 100,
        damping: 15
      }}
      whileHover={{ 
        scale: 1.02,
        transition: { duration: 0.2 }
      }}
      whileTap={{ scale: 0.98 }}
    >
      <Card 
        sx={{
          position: 'relative',
          overflow: 'hidden',
          height: '100%',
          minHeight: 140,
          cursor: 'pointer',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 12px 24px rgba(0, 0, 0, 0.15)',
          },
        }}
      >
        {/* Background gradient */}
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: '4px',
            background: gradient,
          }}
        />
        
        {/* Floating icon background */}
        <Box
          sx={{
            position: 'absolute',
            top: -10,
            right: -10,
            width: 80,
            height: 80,
            borderRadius: '50%',
            background: `${gradient}, rgba(255, 255, 255, 0.1)`,
            opacity: 0.1,
          }}
        />

        <CardContent sx={{ p: 3, position: 'relative', height: '100%' }}>
          <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ flex: 1 }}>
              <Typography 
                variant="body2" 
                color="text.secondary"
                sx={{ 
                  fontWeight: 500,
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                  fontSize: '0.75rem'
                }}
              >
                {title}
              </Typography>
              
              <Typography 
                variant="h4" 
                sx={{ 
                  fontWeight: 700,
                  mt: 0.5,
                  background: gradient,
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                {value}
              </Typography>
              
              {subtitle && (
                <Typography 
                  variant="body2" 
                  color="text.secondary"
                  sx={{ mt: 0.5, fontSize: '0.875rem' }}
                >
                  {subtitle}
                </Typography>
              )}
            </Box>
            
            {/* Icon */}
            <Box
              sx={{
                width: 48,
                height: 48,
                borderRadius: 2,
                background: `${gradient}, rgba(255, 255, 255, 0.1)`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                flexShrink: 0,
              }}
            >
              <IconComponent size={24} />
            </Box>
          </Box>

          {/* Progress bar */}
          {progress !== undefined && (
            <Box sx={{ mt: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Progress
                </Typography>
                <Typography variant="body2" fontWeight={500}>
                  {progress}%
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={progress}
                sx={{
                  height: 6,
                  borderRadius: 3,
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  '& .MuiLinearProgress-bar': {
                    background: gradient,
                    borderRadius: 3,
                  },
                }}
              />
            </Box>
          )}

          {/* Trend indicator */}
          {trendValue && (
            <Box sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
              <Chip
                icon={getTrendIcon() || undefined}
                label={trendValue}
                size="small"
                sx={{
                  backgroundColor: `${getTrendColor()}15`,
                  color: getTrendColor(),
                  border: `1px solid ${getTrendColor()}30`,
                  fontWeight: 500,
                  '& .MuiChip-icon': {
                    color: getTrendColor(),
                  },
                }}
              />
            </Box>
          )}
        </CardContent>

        {/* Shimmer effect */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full"
          animate={{ x: ['0%', '200%'] }}
          transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
          style={{
            background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent)',
          }}
        />
      </Card>
    </motion.div>
  )
}

export default PremiumStatsCard 