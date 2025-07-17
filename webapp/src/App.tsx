import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { ThemeProvider } from '@mui/material/styles'
import { CssBaseline, Box } from '@mui/material'
import TelegramHeader from './components/TelegramHeader'
import TelegramNavigation from './components/TelegramNavigation'
import { useTelegramWebApp } from './hooks/useTelegramWebApp'
import { useDynamicTheme } from './hooks/useDynamicTheme'
import { usePageNavigation } from './hooks/useGestureNavigation'
import { 
  DashboardArtisticSimple, 
  CreditPurchase, 
  Settings,
  initializePerformanceOptimizations
} from './utils/lazyComponents'

type Page = 'dashboard' | 'credits' | 'settings'

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('dashboard')
  
  // Enhanced Telegram WebApp integration
  const {
    isLoaded,
    user,
    hapticFeedback,
    showAlert,
    showConfirm,
    cloudStorage,
    shareContent,
    hasHapticFeedback,
    hasCloudStorage,
    isMobile,
    isDesktop
  } = useTelegramWebApp()

  // Dynamic theme with Telegram sync
  const {
    theme,
    themeMode,
    isTransitioning,
    themeVariables,
    isDarkMode,
    toggleTheme,
    hasTelegramTheme,
    telegramColorScheme
  } = useDynamicTheme({
    enableAutoSync: true,
    preferredMode: 'auto',
    animationDuration: 300
  })

  const navigateToPage = (page: Page) => {
    // Add haptic feedback for navigation
    if (hasHapticFeedback) {
      hapticFeedback.selection()
    }
    setCurrentPage(page)
  }

  // Gesture navigation for mobile users
  const pages = ['dashboard', 'credits', 'settings']
  const {
    isGesturing,
    gestureIndicator,
    canSwipeLeft,
    canSwipeRight,
    isMobileDevice
  } = usePageNavigation(pages, currentPage, (page: string) => navigateToPage(page as Page), {
    threshold: 80,
    velocityThreshold: 0.4,
    preventScroll: true
  })

  useEffect(() => {
    // Initialize performance optimizations
    initializePerformanceOptimizations()
    
    // Log integration status
    console.log('🚀 Enhanced Telegram Mini App loaded:', {
      telegramLoaded: isLoaded,
      hapticFeedback: hasHapticFeedback,
      cloudStorage: hasCloudStorage,
      telegramTheme: hasTelegramTheme,
      deviceType: isMobile ? 'mobile' : isDesktop ? 'desktop' : 'unknown'
    })
  }, [isLoaded, hasHapticFeedback, hasCloudStorage, hasTelegramTheme, isMobile, isDesktop])

  const handleShare = async () => {
    try {
      await shareContent(
        '🎨 Check out this amazing AI-powered creative dashboard!',
        'https://nsxochatbot.surge.sh'
      )
      
      if (hasHapticFeedback) {
        hapticFeedback.notification('success')
      }
    } catch (error) {
      console.error('Share failed:', error)
      showAlert('Sharing is not available on this platform')
    }
  }

  const handleThemeToggle = async () => {
    if (hasHapticFeedback) {
      hapticFeedback.impact('light')
    }
    await toggleTheme()
  }

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <DashboardArtisticSimple />
      case 'credits':
        return <CreditPurchase />
      case 'settings':
        return <Settings />
      default:
        return <DashboardArtisticSimple />
    }
  }

  if (!isLoaded) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box 
          sx={{ 
            ...themeVariables,
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: theme.palette.background.default,
            transition: `background-color ${theme.transitions.duration?.standard}ms ${theme.transitions.easing?.easeInOut}`
          }}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
          >
            {/* Loading will be handled by lazy components */}
          </motion.div>
        </Box>
      </ThemeProvider>
    )
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box 
        sx={{ 
          ...themeVariables,
          minHeight: '100vh',
          backgroundColor: theme.palette.background.default,
          color: theme.palette.text.primary,
          transition: `all ${theme.transitions.duration?.standard}ms ${theme.transitions.easing?.easeInOut}`,
          ...(isTransitioning && {
            pointerEvents: 'none'
          })
        }}
      >
        {/* Enhanced Header */}
        <TelegramHeader 
          user={user}
        />

        {/* Main Content with enhanced transitions */}
        <motion.main
          key={currentPage}
          initial={{ 
            opacity: 0, 
            x: 20,
            filter: 'blur(4px)'
          }}
          animate={{ 
            opacity: 1, 
            x: 0,
            filter: 'blur(0px)'
          }}
          exit={{ 
            opacity: 0, 
            x: -20,
            filter: 'blur(4px)'
          }}
          transition={{
            duration: 0.4,
            ease: [0.4, 0, 0.2, 1]
          }}
          style={{
            paddingBottom: '80px' // Account for navigation
          }}
        >
          {renderCurrentPage()}
        </motion.main>

        {/* Enhanced Navigation */}
        <TelegramNavigation 
          currentPage={currentPage}
          onNavigate={navigateToPage}
        />

        {/* Gesture indicator for mobile users */}
        {isGesturing && gestureIndicator && isMobileDevice && (
          <Box
            sx={{
              position: 'fixed',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              backgroundColor: 'rgba(0,0,0,0.8)',
              color: 'white',
              px: 3,
              py: 2,
              borderRadius: 3,
              zIndex: 9999,
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              backdropFilter: 'blur(10px)',
              border: `2px solid ${gestureIndicator.isValid ? theme.palette.success.main : theme.palette.warning.main}`,
              transition: 'all 0.2s ease'
            }}
          >
            <Box sx={{ fontSize: '1.5rem' }}>
              {gestureIndicator.direction === 'left' && '→'}
              {gestureIndicator.direction === 'right' && '←'}
              {gestureIndicator.direction === 'up' && '↑'}
              {gestureIndicator.direction === 'down' && '↓'}
            </Box>
            <Box sx={{ fontSize: '0.9rem', fontWeight: 600 }}>
              {gestureIndicator.direction === 'left' && canSwipeLeft && 'Next Page'}
              {gestureIndicator.direction === 'right' && canSwipeRight && 'Previous Page'}
              {!((gestureIndicator.direction === 'left' && canSwipeLeft) || (gestureIndicator.direction === 'right' && canSwipeRight)) && 'Swipe'}
            </Box>
          </Box>
        )}

        {/* Development info (remove in production) */}
        {process.env.NODE_ENV === 'development' && (
          <Box
            sx={{
              position: 'fixed',
              top: 10,
              right: 10,
              p: 1,
              backgroundColor: 'rgba(0,0,0,0.7)',
              color: 'white',
              fontSize: '0.7rem',
              borderRadius: 1,
              zIndex: 9999,
              fontFamily: 'monospace'
            }}
          >
            Theme: {themeMode} | TG: {hasTelegramTheme ? 'Yes' : 'No'} | 
            Haptic: {hasHapticFeedback ? 'Yes' : 'No'} | 
            Device: {isMobile ? 'Mobile' : isDesktop ? 'Desktop' : 'Unknown'} |
            Gestures: {isMobileDevice ? 'On' : 'Off'}
          </Box>
        )}
      </Box>
    </ThemeProvider>
  )
}

export default App 