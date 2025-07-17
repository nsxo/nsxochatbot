import React from 'react'
import { 
  Button, 
  Box, 
  Typography, 
  Chip,
  Stack
} from '@mui/material'
import { motion } from 'framer-motion'
import { 
  ArrowRight,
  Plus,
  Download,
  Share2,
  Heart,
  Star,
  Zap,
  Crown,
  Palette,
  Upload,
  Camera,
  Brush,
  Sparkles,
  Award,
  Users,
  MessageSquare
} from 'lucide-react'
import { deviantArtColors } from '../styles/DeviantArtTheme'

interface ArtisticActionButtonProps {
  title: string
  description: string
  icon?: string
  variant?: 'primary' | 'secondary' | 'artistic' | 'warm' | 'cool' | 'community'
  size?: 'small' | 'medium' | 'large'
  badge?: string
  badgeColor?: 'new' | 'hot' | 'popular' | 'premium'
  showArrow?: boolean
  disabled?: boolean
  loading?: boolean
  onClick?: () => void
  delay?: number
  popularity?: {
    likes?: number
    views?: number
    shares?: number
    trending?: boolean
  }
}

const iconMap = {
  plus: Plus,
  download: Download,
  share: Share2,
  heart: Heart,
  star: Star,
  zap: Zap,
  crown: Crown,
  palette: Palette,
  upload: Upload,
  camera: Camera,
  brush: Brush,
  sparkles: Sparkles,
  award: Award,
  users: Users,
  message: MessageSquare,
  arrow: ArrowRight
}

const gradientMap = {
  primary: deviantArtColors.gradients.creative,
  secondary: deviantArtColors.gradients.artistic,
  artistic: 'linear-gradient(135deg, #8B5FBF 0%, #05CC47 50%, #FF6B35 100%)',
  warm: deviantArtColors.gradients.warm,
  cool: deviantArtColors.gradients.cool,
  community: 'linear-gradient(135deg, #FF7B94 0%, #8B5FBF 50%, #26D0CE 100%)'
}

const badgeColorMap = {
  new: { bg: deviantArtColors.accent.teal, text: '#FFFFFF' },
  hot: { bg: deviantArtColors.accent.orange, text: '#FFFFFF' },
  popular: { bg: deviantArtColors.accent.yellow, text: deviantArtColors.neutral[900] },
  premium: { bg: deviantArtColors.gradients.creative, text: '#FFFFFF' }
}

const glowColors = {
  primary: '5, 204, 71',
  secondary: '139, 95, 191',
  artistic: '255, 107, 53',
  warm: '255, 217, 61',
  cool: '74, 144, 226',
  community: '255, 123, 148'
}

export const ArtisticActionButton: React.FC<ArtisticActionButtonProps> = ({
  title,
  description,
  icon = 'sparkles',
  variant = 'primary',
  size = 'medium',
  badge,
  badgeColor = 'new',
  showArrow = true,
  disabled = false,
  loading = false,
  onClick,
  delay = 0,
  popularity
}) => {
  const IconComponent = iconMap[icon as keyof typeof iconMap] || Sparkles
  
  const buttonVariants = {
    hidden: { 
      opacity: 0, 
      scale: 0.8,
      y: 20
    },
    visible: { 
      opacity: 1, 
      scale: 1,
      y: 0,
      transition: {
        duration: 0.5,
        delay,
        ease: "backOut"
      }
    },
    hover: {
      scale: 1.05,
      y: -4,
      transition: {
        duration: 0.2,
        ease: "easeOut"
      }
    },
    tap: {
      scale: 0.95,
      transition: {
        duration: 0.1
      }
    }
  }

  const iconVariants = {
    hidden: { rotate: -180, scale: 0 },
    visible: { 
      rotate: 0, 
      scale: 1,
      transition: {
        duration: 0.4,
        delay: delay + 0.2,
        ease: "backOut"
      }
    },
    hover: {
      rotate: 10,
      scale: 1.1,
      transition: { duration: 0.2 }
    }
  }

  const arrowVariants = {
    rest: { x: 0 },
    hover: { 
      x: 4,
      transition: { 
        duration: 0.2,
        ease: "easeOut"
      }
    }
  }

  const getButtonHeight = () => {
    switch (size) {
      case 'small': return 80
      case 'large': return 120
      default: return 100
    }
  }

  const getIconSize = () => {
    switch (size) {
      case 'small': return 20
      case 'large': return 28
      default: return 24
    }
  }

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
    return num.toString()
  }

  return (
    <motion.div
      variants={buttonVariants}
      initial="hidden"
      animate="visible"
      whileHover="hover"
      whileTap="tap"
    >
      <Button
        fullWidth
        disabled={disabled || loading}
        onClick={onClick}
        sx={{
          height: getButtonHeight(),
          borderRadius: size === 'large' ? 20 : 16,
          padding: size === 'large' ? 3 : size === 'small' ? 2 : 2.5,
          background: gradientMap[variant],
          border: 'none',
          position: 'relative',
          overflow: 'hidden',
          textTransform: 'none',
          boxShadow: `0 8px 24px rgba(${glowColors[variant]}, 0.25)`,
          '&:hover': {
            background: gradientMap[variant],
            boxShadow: `0 12px 32px rgba(${glowColors[variant]}, 0.35)`,
            filter: 'brightness(1.1)',
            '&::before': {
              opacity: 1
            }
          },
          '&:disabled': {
            background: deviantArtColors.neutral[700],
            color: deviantArtColors.neutral[400],
            boxShadow: 'none'
          },
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'linear-gradient(135deg, rgba(255,255,255,0.2) 0%, transparent 50%, rgba(255,255,255,0.1) 100%)',
            opacity: 0,
            transition: 'opacity 0.3s ease'
          },
          '&::after': disabled ? {} : {
            content: '""',
            position: 'absolute',
            top: -50,
            left: -50,
            width: 20,
            height: 100,
            background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)',
            transform: 'rotate(45deg)',
            animation: loading ? 'none' : 'shine 3s infinite',
            animationDelay: `${delay}s`
          }
        }}
      >
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            width: '100%',
            position: 'relative',
            zIndex: 1
          }}
        >
          {/* Left Section - Icon and Content */}
          <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
            <motion.div
              variants={iconVariants}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: getIconSize() + 16,
                height: getIconSize() + 16,
                borderRadius: '50%',
                background: 'rgba(255, 255, 255, 0.2)',
                backdropFilter: 'blur(8px)',
                marginRight: size === 'small' ? 12 : 16,
                border: '1px solid rgba(255, 255, 255, 0.3)'
              }}
            >
              <IconComponent 
                size={getIconSize()} 
                color="white"
                style={{ filter: 'drop-shadow(0 1px 2px rgba(0,0,0,0.3))' }}
              />
            </motion.div>
            
            <Box sx={{ flex: 1, textAlign: 'left' }}>
              <Typography
                variant={size === 'large' ? 'h6' : size === 'small' ? 'body2' : 'subtitle1'}
                sx={{
                  color: 'white',
                  fontWeight: 700,
                  mb: 0.5,
                  filter: 'drop-shadow(0 1px 2px rgba(0,0,0,0.3))',
                  fontSize: size === 'small' ? '0.875rem' : size === 'large' ? '1.125rem' : '1rem'
                }}
              >
                {title}
              </Typography>
              
              <Typography
                variant="caption"
                sx={{
                  color: 'rgba(255, 255, 255, 0.8)',
                  fontSize: size === 'small' ? '0.7rem' : '0.75rem',
                  fontWeight: 500,
                  filter: 'drop-shadow(0 1px 2px rgba(0,0,0,0.2))',
                  display: '-webkit-box',
                  WebkitLineClamp: size === 'small' ? 1 : 2,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden'
                }}
              >
                {description}
              </Typography>

              {/* Popularity Indicators */}
              {popularity && size !== 'small' && (
                <Stack direction="row" spacing={1} sx={{ mt: 0.5 }}>
                  {popularity.likes && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <Heart size={10} color="rgba(255, 255, 255, 0.7)" />
                      <Typography variant="caption" sx={{ fontSize: '0.65rem', color: 'rgba(255, 255, 255, 0.7)' }}>
                        {formatNumber(popularity.likes)}
                      </Typography>
                    </Box>
                  )}
                  {popularity.views && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <Typography variant="caption" sx={{ fontSize: '0.65rem', color: 'rgba(255, 255, 255, 0.7)' }}>
                        {formatNumber(popularity.views)} views
                      </Typography>
                    </Box>
                  )}
                  {popularity.trending && (
                    <Chip
                      label="Trending"
                      size="small"
                      sx={{
                        height: 16,
                        fontSize: '0.6rem',
                        fontWeight: 600,
                        background: 'rgba(255, 255, 255, 0.2)',
                        color: 'white',
                        '& .MuiChip-label': { px: 1 }
                      }}
                    />
                  )}
                </Stack>
              )}
            </Box>
          </Box>

          {/* Right Section - Badge and Arrow */}
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            flexDirection: 'column',
            gap: 1
          }}>
            {badge && (
              <Chip
                label={badge}
                size="small"
                sx={{
                  background: badgeColorMap[badgeColor].bg,
                  color: badgeColorMap[badgeColor].text,
                  fontWeight: 600,
                  fontSize: '0.7rem',
                  height: size === 'small' ? 20 : 24,
                  '& .MuiChip-label': {
                    px: size === 'small' ? 1 : 1.5
                  },
                  boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
                }}
              />
            )}
            
            {showArrow && !disabled && (
              <motion.div
                variants={arrowVariants}
                initial="rest"
                whileHover="hover"
              >
                <ArrowRight 
                  size={size === 'small' ? 16 : 20} 
                  color="rgba(255, 255, 255, 0.8)"
                  style={{ filter: 'drop-shadow(0 1px 2px rgba(0,0,0,0.3))' }}
                />
              </motion.div>
            )}
          </Box>
        </Box>

        {/* Loading Overlay */}
        {loading && (
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'rgba(0, 0, 0, 0.3)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 2
            }}
          >
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            >
              <Sparkles size={24} color="white" />
            </motion.div>
          </Box>
        )}
      </Button>
      
      <style>{`
        @keyframes shine {
          0% { transform: translateX(-200px) rotate(45deg); }
          50% { transform: translateX(-200px) rotate(45deg); }
          100% { transform: translateX(400px) rotate(45deg); }
        }
      `}</style>
    </motion.div>
  )
}

export default ArtisticActionButton 