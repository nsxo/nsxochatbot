import React from 'react'
import { Button, Box, Typography, Chip } from '@mui/material'
import { motion } from 'framer-motion'
import { 
  ArrowRight, 
  Zap, 
  Crown, 
  Star,
  Plus,
  ShoppingCart,
  Settings,
  Download,
  Upload,
  Play,
  Pause,
  Check
} from 'lucide-react'

interface PremiumActionButtonProps {
  title: string
  subtitle?: string
  icon?: string
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'error'
  size?: 'small' | 'medium' | 'large'
  fullWidth?: boolean
  disabled?: boolean
  loading?: boolean
  badge?: string
  onClick?: () => void
  className?: string
}

const iconMap = {
  arrow: ArrowRight,
  zap: Zap,
  crown: Crown,
  star: Star,
  plus: Plus,
  cart: ShoppingCart,
  settings: Settings,
  download: Download,
  upload: Upload,
  play: Play,
  pause: Pause,
  check: Check,
}

const variantStyles = {
  primary: {
    gradient: 'linear-gradient(135deg, #2196F3 0%, #21CBF3 100%)',
    shadow: 'rgba(33, 150, 243, 0.4)',
  },
  secondary: {
    gradient: 'linear-gradient(135deg, #FF4081 0%, #FF6EC7 100%)',
    shadow: 'rgba(255, 64, 129, 0.4)',
  },
  success: {
    gradient: 'linear-gradient(135deg, #10B981 0%, #34D399 100%)',
    shadow: 'rgba(16, 185, 129, 0.4)',
  },
  warning: {
    gradient: 'linear-gradient(135deg, #F59E0B 0%, #FCD34D 100%)',
    shadow: 'rgba(245, 158, 11, 0.4)',
  },
  error: {
    gradient: 'linear-gradient(135deg, #EF4444 0%, #F87171 100%)',
    shadow: 'rgba(239, 68, 68, 0.4)',
  },
}

export const PremiumActionButton: React.FC<PremiumActionButtonProps> = ({
  title,
  subtitle,
  icon = 'arrow',
  variant = 'primary',
  size = 'medium',
  fullWidth = false,
  disabled = false,
  loading = false,
  badge,
  onClick,
  className
}) => {
  const IconComponent = iconMap[icon as keyof typeof iconMap] || ArrowRight
  const styles = variantStyles[variant]

  const getSize = () => {
    switch (size) {
      case 'small': return { py: 1.5, px: 3, minHeight: 44 }
      case 'large': return { py: 2.5, px: 4, minHeight: 64 }
      default: return { py: 2, px: 3.5, minHeight: 56 }
    }
  }

  const getIconSize = () => {
    switch (size) {
      case 'small': return 18
      case 'large': return 28
      default: return 22
    }
  }

  return (
    <motion.div
      whileHover={{ scale: disabled ? 1 : 1.02 }}
      whileTap={{ scale: disabled ? 1 : 0.98 }}
      transition={{ duration: 0.2 }}
      className={className}
    >
      <Button
        onClick={onClick}
        disabled={disabled || loading}
        fullWidth={fullWidth}
        sx={{
          position: 'relative',
          overflow: 'hidden',
          background: styles.gradient,
          ...getSize(),
          borderRadius: 3,
          textTransform: 'none',
          fontWeight: 600,
          boxShadow: 'none',
          border: 'none',
          color: 'white',
          '&:hover': {
            background: styles.gradient,
            boxShadow: `0 8px 24px ${styles.shadow}`,
            transform: 'translateY(-1px)',
          },
          '&:active': {
            transform: 'translateY(0px)',
          },
          '&:disabled': {
            background: 'rgba(148, 163, 184, 0.3)',
            color: 'rgba(148, 163, 184, 0.7)',
          },
        }}
      >
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          width: '100%',
          position: 'relative',
          zIndex: 1
        }}>
          {/* Left content */}
          <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
            <Box sx={{ mr: subtitle ? 2 : 1.5 }}>
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center',
                justifyContent: 'center',
                width: size === 'large' ? 40 : size === 'small' ? 32 : 36,
                height: size === 'large' ? 40 : size === 'small' ? 32 : 36,
                borderRadius: 2,
                backgroundColor: 'rgba(255, 255, 255, 0.2)',
              }}>
                {loading ? (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  >
                    <Zap size={getIconSize() - 4} />
                  </motion.div>
                ) : (
                  <IconComponent size={getIconSize()} />
                )}
              </Box>
            </Box>
            
            <Box sx={{ textAlign: 'left', flex: 1 }}>
              <Typography 
                variant={size === 'large' ? 'body1' : 'body2'}
                sx={{ 
                  fontWeight: 600,
                  lineHeight: 1.2,
                  color: 'inherit'
                }}
              >
                {title}
              </Typography>
              {subtitle && (
                <Typography 
                  variant="caption"
                  sx={{ 
                    opacity: 0.9,
                    display: 'block',
                    lineHeight: 1.2,
                    mt: 0.25,
                    color: 'inherit'
                  }}
                >
                  {subtitle}
                </Typography>
              )}
            </Box>
          </Box>

          {/* Right content */}
          <Box sx={{ display: 'flex', alignItems: 'center', ml: 1 }}>
            {badge && (
              <Chip
                label={badge}
                size="small"
                sx={{
                  backgroundColor: 'rgba(255, 255, 255, 0.2)',
                  color: 'white',
                  fontWeight: 500,
                  mr: 1,
                  height: 24,
                  fontSize: '0.75rem',
                }}
              />
            )}
            
            <motion.div
              animate={{ x: [0, 4, 0] }}
              transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
            >
              <ArrowRight size={getIconSize() - 2} />
            </motion.div>
          </Box>
        </Box>

        {/* Shimmer effect */}
        {!disabled && !loading && (
          <motion.div
            className="absolute inset-0"
            initial={{ x: '-100%' }}
            animate={{ x: '100%' }}
            transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
            style={{
              background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent)',
              width: '50%',
            }}
          />
        )}

        {/* Ripple effect background */}
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: `radial-gradient(circle at center, rgba(255,255,255,0.1) 0%, transparent 70%)`,
            opacity: 0,
            transition: 'opacity 0.3s ease',
            '.MuiButton-root:hover &': {
              opacity: 1,
            },
          }}
        />
      </Button>
    </motion.div>
  )
}

export default PremiumActionButton 