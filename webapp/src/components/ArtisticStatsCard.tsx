import React from 'react'
import { 
  Card, 
  CardContent, 
  Typography, 
  Box, 
  Chip,
  Avatar,
  Stack,
  Divider
} from '@mui/material'
import { motion, useAnimation } from 'framer-motion'
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
  Sparkles,
  Heart,
  Eye,
  Share2,
  Award
} from 'lucide-react'
import { deviantArtColors } from '../styles/DeviantArtTheme'

interface ArtisticStatsCardProps {
  title: string
  value: string | number
  subtitle?: string
  description?: string
  trend?: 'up' | 'down' | 'neutral'
  trendValue?: string
  progress?: number
  icon?: string
  variant?: 'primary' | 'secondary' | 'artistic' | 'warm' | 'cool' | 'community'
  size?: 'compact' | 'default' | 'large'
  showBadge?: boolean
  badgeText?: string
  interactions?: {
    likes?: number
    views?: number
    shares?: number
  }
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
  heart: Heart,
  eye: Eye,
  share: Share2,
  award: Award,
}

const gradientMap = {
  primary: deviantArtColors.gradients.creative,
  secondary: deviantArtColors.gradients.artistic,
  artistic: 'linear-gradient(135deg, #8B5FBF 0%, #05CC47 50%, #FF6B35 100%)',
  warm: deviantArtColors.gradients.warm,
  cool: deviantArtColors.gradients.cool,
  community: 'linear-gradient(135deg, #FF7B94 0%, #8B5FBF 50%, #26D0CE 100%)'
}

const glowColors = {
  primary: '5, 204, 71',
  secondary: '139, 95, 191',
  artistic: '255, 107, 53',
  warm: '255, 217, 61',
  cool: '74, 144, 226',
  community: '255, 123, 148'
}

export const ArtisticStatsCard: React.FC<ArtisticStatsCardProps> = ({
  title,
  value,
  subtitle,
  description,
  trend = 'neutral',
  trendValue,
  progress,
  icon = 'sparkles',
  variant = 'primary',
  size = 'default',
  showBadge = false,
  badgeText,
  interactions,
  delay = 0
}) => {
  const IconComponent = iconMap[icon as keyof typeof iconMap] || Sparkles
  const controls = useAnimation()
  
  const cardVariants = {
    hidden: { 
      opacity: 0, 
      y: 30,
      scale: 0.95
    },
    visible: { 
      opacity: 1, 
      y: 0,
      scale: 1,
      transition: {
        duration: 0.6,
        delay,
        ease: "easeOut"
      }
    },
    hover: {
      y: -8,
      scale: 1.02,
      transition: {
        duration: 0.3,
        ease: "easeOut"
      }
    }
  }

  const iconVariants = {
    hidden: { scale: 0, rotate: -180 },
    visible: { 
      scale: 1, 
      rotate: 0,
      transition: {
        duration: 0.5,
        delay: delay + 0.2,
        ease: "backOut"
      }
    },
    hover: {
      scale: 1.1,
      rotate: 5,
      transition: { duration: 0.2 }
    }
  }

  const progressVariants = {
    hidden: { width: 0 },
    visible: { 
      width: `${progress}%`,
      transition: {
        duration: 1.2,
        delay: delay + 0.4,
        ease: "easeOut"
      }
    }
  }

  const getCardHeight = () => {
    switch (size) {
      case 'compact': return 140
      case 'large': return 280
      default: return 200
    }
  }

  const getIconSize = () => {
    switch (size) {
      case 'compact': return 20
      case 'large': return 32
      default: return 24
    }
  }

  const getTrendIcon = () => {
    switch (trend) {
      case 'up': return <TrendingUp size={16} />
      case 'down': return <TrendingDown size={16} />
      default: return null
    }
  }

  const getTrendColor = () => {
    switch (trend) {
      case 'up': return deviantArtColors.accent.teal
      case 'down': return deviantArtColors.accent.red
      default: return deviantArtColors.neutral[400]
    }
  }

  return (
    <motion.div
      variants={cardVariants}
      initial="hidden"
      animate="visible"
      whileHover="hover"
      onHoverStart={() => controls.start("hover")}
      onHoverEnd={() => controls.start("visible")}
    >
      <Card
        sx={{
          height: getCardHeight(),
          position: 'relative',
          overflow: 'hidden',
          background: `linear-gradient(135deg, 
            rgba(42, 51, 42, 0.95) 0%, 
            rgba(78, 98, 82, 0.85) 100%)`,
          backdropFilter: 'blur(20px)',
          border: `1px solid rgba(${glowColors[variant]}, 0.2)`,
          borderRadius: size === 'large' ? 32 : 24,
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: '4px',
            background: gradientMap[variant],
            zIndex: 1
          },
          '&:hover': {
            boxShadow: `0 20px 40px rgba(${glowColors[variant]}, 0.15)`,
            '&::before': {
              height: '6px',
            }
          },
          transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)'
        }}
      >
        <CardContent sx={{ 
          p: size === 'large' ? 4 : size === 'compact' ? 2 : 3,
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          position: 'relative'
        }}>
          {/* Background Artistic Element */}
          <Box
            sx={{
              position: 'absolute',
              top: -20,
              right: -20,
              width: 80,
              height: 80,
              borderRadius: '50%',
              background: `radial-gradient(circle, rgba(${glowColors[variant]}, 0.1) 0%, transparent 70%)`,
              zIndex: 0
            }}
          />
          
          {/* Header Section */}
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'flex-start', 
            justifyContent: 'space-between',
            mb: size === 'compact' ? 1 : 2,
            position: 'relative',
            zIndex: 1
          }}>
            <motion.div
              variants={iconVariants}
              animate={controls}
            >
              <Avatar
                sx={{
                  width: getIconSize() + 16,
                  height: getIconSize() + 16,
                  background: gradientMap[variant],
                  boxShadow: `0 8px 16px rgba(${glowColors[variant]}, 0.3)`,
                  '& svg': {
                    filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.2))'
                  }
                }}
              >
                <IconComponent size={getIconSize()} color="white" />
              </Avatar>
            </motion.div>
            
            {showBadge && badgeText && (
              <Chip
                label={badgeText}
                size="small"
                sx={{
                  background: `rgba(${glowColors[variant]}, 0.2)`,
                  color: deviantArtColors.neutral[50],
                  fontWeight: 600,
                  fontSize: '0.7rem',
                  '& .MuiChip-label': {
                    px: 1.5
                  }
                }}
              />
            )}
          </Box>

          {/* Main Content */}
          <Box sx={{ flex: 1, position: 'relative', zIndex: 1 }}>
            <Typography
              variant="caption"
              sx={{
                color: deviantArtColors.neutral[300],
                fontWeight: 500,
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                fontSize: size === 'compact' ? '0.65rem' : '0.75rem'
              }}
            >
              {title}
            </Typography>
            
            <Typography
              variant={size === 'large' ? 'h3' : size === 'compact' ? 'h6' : 'h5'}
              sx={{
                fontWeight: 800,
                color: deviantArtColors.neutral[50],
                mt: 0.5,
                mb: size === 'compact' ? 0.5 : 1,
                background: gradientMap[variant],
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                filter: 'drop-shadow(0 1px 2px rgba(0,0,0,0.3))'
              }}
            >
              {value}
            </Typography>

            {subtitle && (
              <Typography
                variant="body2"
                sx={{
                  color: deviantArtColors.neutral[400],
                  fontSize: size === 'compact' ? '0.75rem' : '0.875rem',
                  mb: 1
                }}
              >
                {subtitle}
              </Typography>
            )}

            {description && size !== 'compact' && (
              <Typography
                variant="caption"
                sx={{
                  color: deviantArtColors.neutral[500],
                  fontSize: '0.7rem',
                  lineHeight: 1.3,
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden'
                }}
              >
                {description}
              </Typography>
            )}
          </Box>

          {/* Progress Bar */}
          {progress !== undefined && (
            <Box sx={{ mt: 'auto', position: 'relative', zIndex: 1 }}>
              <Box sx={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                mb: 1
              }}>
                <Typography
                  variant="caption"
                  sx={{ 
                    color: deviantArtColors.neutral[400],
                    fontSize: '0.7rem'
                  }}
                >
                  Progress
                </Typography>
                <Typography
                  variant="caption"
                  sx={{ 
                    color: deviantArtColors.neutral[300],
                    fontWeight: 600,
                    fontSize: '0.7rem'
                  }}
                >
                  {progress}%
                </Typography>
              </Box>
              <Box
                sx={{
                  width: '100%',
                  height: 6,
                  backgroundColor: deviantArtColors.neutral[700],
                  borderRadius: 3,
                  overflow: 'hidden',
                  position: 'relative'
                }}
              >
                <motion.div
                  variants={progressVariants}
                  style={{
                    height: '100%',
                    background: gradientMap[variant],
                    borderRadius: 3,
                    position: 'relative'
                  }}
                >
                  <Box
                    sx={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      bottom: 0,
                      background: 'linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.3) 50%, transparent 100%)',
                      animation: 'shimmer 2s infinite linear'
                    }}
                  />
                </motion.div>
              </Box>
            </Box>
          )}

          {/* Trend and Interactions */}
          {(trendValue || interactions) && size !== 'compact' && (
            <>
              <Divider sx={{ 
                my: 2, 
                borderColor: deviantArtColors.neutral[700],
                opacity: 0.5
              }} />
              <Box sx={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center'
              }}>
                {/* Trend */}
                {trendValue && (
                  <Stack direction="row" alignItems="center" spacing={0.5}>
                    <Box sx={{ color: getTrendColor() }}>
                      {getTrendIcon()}
                    </Box>
                    <Typography
                      variant="caption"
                      sx={{
                        color: getTrendColor(),
                        fontWeight: 600,
                        fontSize: '0.75rem'
                      }}
                    >
                      {trendValue}
                    </Typography>
                  </Stack>
                )}

                {/* Interactions */}
                {interactions && (
                  <Stack direction="row" spacing={2}>
                    {interactions.likes && (
                      <Stack direction="row" alignItems="center" spacing={0.5}>
                        <Heart size={12} color={deviantArtColors.accent.pink} />
                        <Typography variant="caption" sx={{ fontSize: '0.65rem', color: deviantArtColors.neutral[400] }}>
                          {interactions.likes}
                        </Typography>
                      </Stack>
                    )}
                    {interactions.views && (
                      <Stack direction="row" alignItems="center" spacing={0.5}>
                        <Eye size={12} color={deviantArtColors.accent.blue} />
                        <Typography variant="caption" sx={{ fontSize: '0.65rem', color: deviantArtColors.neutral[400] }}>
                          {interactions.views}
                        </Typography>
                      </Stack>
                    )}
                    {interactions.shares && (
                      <Stack direction="row" alignItems="center" spacing={0.5}>
                        <Share2 size={12} color={deviantArtColors.accent.teal} />
                        <Typography variant="caption" sx={{ fontSize: '0.65rem', color: deviantArtColors.neutral[400] }}>
                          {interactions.shares}
                        </Typography>
                      </Stack>
                    )}
                  </Stack>
                )}
              </Box>
            </>
          )}
        </CardContent>
      </Card>
      
      <style>{`
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(200%); }
        }
      `}</style>
    </motion.div>
  )
}

export default ArtisticStatsCard 