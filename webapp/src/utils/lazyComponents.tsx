import { lazy, Suspense, ComponentType } from 'react'
import { Box, CircularProgress, Typography, Paper } from '@mui/material'
import { motion } from 'framer-motion'
import { Palette, AlertCircle } from 'lucide-react'
import { deviantArtColors } from '../styles/DeviantArtTheme'

// Enhanced loading component with artistic styling
const ArtisticLoadingComponent = ({ componentName }: { componentName?: string }) => (
  <Box
    sx={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '60vh',
      gap: 3,
      p: 4
    }}
  >
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
    
    <Box sx={{ textAlign: 'center' }}>
      <Typography
        variant="h6"
        sx={{
          background: deviantArtColors.gradients.creative,
          backgroundClip: 'text',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          mb: 1,
          fontWeight: 600
        }}
      >
        Loading {componentName || 'Component'}...
      </Typography>
      <Typography
        variant="body2"
        sx={{
          color: deviantArtColors.neutral[400],
          fontSize: '0.875rem'
        }}
      >
        Preparing your creative experience
      </Typography>
    </Box>
    
    <CircularProgress
      size={24}
      sx={{
        color: deviantArtColors.primary.main,
        '& .MuiCircularProgress-circle': {
          strokeLinecap: 'round'
        }
      }}
    />
  </Box>
)

// Error boundary fallback component
const ErrorFallback = ({ componentName, error }: { componentName?: string, error?: Error }) => (
  <Paper
    elevation={0}
    sx={{
      p: 4,
      m: 2,
      textAlign: 'center',
      background: `linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%)`,
      border: `1px solid ${deviantArtColors.accent.red}20`,
      borderRadius: 3
    }}
  >
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
      <AlertCircle size={48} color={deviantArtColors.accent.red} />
      <Typography variant="h6" sx={{ color: deviantArtColors.accent.red, fontWeight: 600 }}>
        Failed to load {componentName || 'component'}
      </Typography>
      <Typography variant="body2" sx={{ color: deviantArtColors.neutral[400], maxWidth: 400 }}>
        Something went wrong while loading this component. Please try refreshing the page.
      </Typography>
      {error && (
        <Typography variant="caption" sx={{ color: deviantArtColors.neutral[500], mt: 1 }}>
          Error: {error.message}
        </Typography>
      )}
    </Box>
  </Paper>
)

// Higher-order component for lazy loading with enhanced loading states
export const withLazyLoading = <P extends object>(
  importFunc: () => Promise<{ default: ComponentType<P> }>,
  componentName: string,
  preloadCondition?: () => boolean
) => {
  const LazyComponent = lazy(importFunc)
  
  // Preload component if condition is met
  if (preloadCondition?.()) {
    importFunc().catch(() => {
      // Silently fail preloading
    })
  }

  const WrappedComponent = (props: P) => (
    <Suspense fallback={<ArtisticLoadingComponent componentName={componentName} />}>
      <LazyComponent {...props} />
    </Suspense>
  )

  WrappedComponent.displayName = `LazyLoaded(${componentName})`
  WrappedComponent.preload = importFunc

  return WrappedComponent
}

// Lazy-loaded page components
export const DashboardArtisticSimple = withLazyLoading(
  () => import('../pages/DashboardArtisticSimple'),
  'Dashboard',
  () => true // Always preload dashboard
)

export const CreditPurchase = withLazyLoading(
  () => import('../pages/CreditPurchase'),
  'Credit Purchase'
)

export const Settings = withLazyLoading(
  () => import('../pages/Settings'),
  'Settings'
)

// Lazy-loaded component collections
export const ArtisticStatsCard = withLazyLoading(
  () => import('../components/ArtisticStatsCard'),
  'Stats Card'
)

export const ArtisticActionButton = withLazyLoading(
  () => import('../components/ArtisticActionButton'),
  'Action Button'
)

// Preloading utilities
export const preloadComponents = {
  // Preload critical components
  dashboard: () => DashboardArtisticSimple.preload(),
  statsCard: () => ArtisticStatsCard.preload(),
  actionButton: () => ArtisticActionButton.preload(),
  
  // Preload secondary components
  credits: () => CreditPurchase.preload(),
  settings: () => Settings.preload(),
  
  // Preload all components
  all: async () => {
    const preloadPromises = [
      DashboardArtisticSimple.preload(),
      ArtisticStatsCard.preload(),
      ArtisticActionButton.preload(),
      CreditPurchase.preload(),
      Settings.preload()
    ]
    
    try {
      await Promise.allSettled(preloadPromises)
      console.log('All components preloaded successfully')
    } catch (error) {
      console.log('Some components failed to preload:', error)
    }
  }
}

// Progressive loading strategy
export const useProgressiveLoading = () => {
  const preloadOnIdle = (callback: () => void) => {
    if ('requestIdleCallback' in window) {
      requestIdleCallback(callback, { timeout: 2000 })
    } else {
      // Fallback for browsers without requestIdleCallback
      setTimeout(callback, 1)
    }
  }

  const preloadOnHover = (element: HTMLElement, preloadFunc: () => Promise<any>) => {
    let preloaded = false
    
    const handleMouseEnter = () => {
      if (!preloaded) {
        preloaded = true
        preloadFunc().catch(() => {
          preloaded = false // Allow retry on next hover
        })
      }
    }

    element.addEventListener('mouseenter', handleMouseEnter, { once: true })
    
    return () => {
      element.removeEventListener('mouseenter', handleMouseEnter)
    }
  }

  const preloadOnIntersection = (
    element: HTMLElement, 
    preloadFunc: () => Promise<any>,
    options?: IntersectionObserverInit
  ) => {
    let preloaded = false
    
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !preloaded) {
            preloaded = true
            preloadFunc().catch(() => {
              preloaded = false
            })
            observer.unobserve(element)
          }
        })
      },
      { threshold: 0.1, ...options }
    )

    observer.observe(element)
    
    return () => {
      observer.disconnect()
    }
  }

  return {
    preloadOnIdle,
    preloadOnHover,
    preloadOnIntersection
  }
}

// Resource hints for better loading performance
export const addResourceHints = () => {
  // Preconnect to external domains
  const preconnectDomains = [
    'https://fonts.googleapis.com',
    'https://fonts.gstatic.com'
  ]

  preconnectDomains.forEach(domain => {
    const link = document.createElement('link')
    link.rel = 'preconnect'
    link.href = domain
    link.crossOrigin = 'anonymous'
    document.head.appendChild(link)
  })

  // DNS prefetch for potential future connections
  const dnsPrefetchDomains = [
    'https://api.telegram.org',
    'https://core.telegram.org'
  ]

  dnsPrefetchDomains.forEach(domain => {
    const link = document.createElement('link')
    link.rel = 'dns-prefetch'
    link.href = domain
    document.head.appendChild(link)
  })
}

// Initialize performance optimizations
export const initializePerformanceOptimizations = () => {
  // Add resource hints
  addResourceHints()
  
  // Preload critical components on idle
  if ('requestIdleCallback' in window) {
    requestIdleCallback(() => {
      preloadComponents.dashboard()
      preloadComponents.statsCard()
      preloadComponents.actionButton()
    }, { timeout: 2000 })
  }
  
  // Preload non-critical components with delay
  setTimeout(() => {
    preloadComponents.credits()
    preloadComponents.settings()
  }, 3000)
}

export default {
  withLazyLoading,
  preloadComponents,
  useProgressiveLoading,
  initializePerformanceOptimizations,
  ArtisticLoadingComponent,
  ErrorFallback
} 