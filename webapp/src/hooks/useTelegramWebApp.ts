import { useState, useEffect, useCallback } from 'react'
import { TelegramWebApp } from '../types/telegram'

export interface TelegramUser {
  id: number
  first_name: string
  last_name?: string
  username?: string
  language_code?: string
  is_premium?: boolean
  allows_write_to_pm?: boolean
  photo_url?: string
}

export interface TelegramState {
  isLoaded: boolean
  user: TelegramUser | null
  colorScheme: 'light' | 'dark'
  themeParams: Record<string, string>
  isExpanded: boolean
  viewportHeight: number
  platform: string
  version: string
}

export const useTelegramWebApp = () => {
  const [state, setState] = useState<TelegramState>({
    isLoaded: false,
    user: null,
    colorScheme: 'dark',
    themeParams: {},
    isExpanded: false,
    viewportHeight: 0,
    platform: 'unknown',
    version: '6.0'
  })

  const webApp = window.Telegram?.WebApp

  // Initialize Telegram WebApp
  useEffect(() => {
    if (webApp) {
      // Configure the WebApp
      webApp.ready()
      webApp.expand()
      
      // Set initial state
      setState(prev => ({
        ...prev,
        isLoaded: true,
        user: webApp.initDataUnsafe?.user || null,
        colorScheme: (webApp as any).colorScheme || 'dark',
        themeParams: (webApp as any).themeParams || {},
        isExpanded: (webApp as any).isExpanded || false,
        viewportHeight: (webApp as any).viewportHeight || 0,
        platform: (webApp as any).platform || 'unknown',
        version: (webApp as any).version || '6.0'
      }))

      // Listen for theme changes
      const handleThemeChanged = () => {
        setState(prev => ({
          ...prev,
          colorScheme: (webApp as any).colorScheme || prev.colorScheme,
          themeParams: (webApp as any).themeParams || prev.themeParams
        }))
      }

      // Listen for viewport changes
      const handleViewportChanged = () => {
        setState(prev => ({
          ...prev,
          isExpanded: (webApp as any).isExpanded || prev.isExpanded,
          viewportHeight: (webApp as any).viewportHeight || prev.viewportHeight
        }))
      }

      // Add event listeners if available
      if ((webApp as any).onEvent) {
        (webApp as any).onEvent('themeChanged', handleThemeChanged)
        ;(webApp as any).onEvent('viewportChanged', handleViewportChanged)
      }

      return () => {
        if ((webApp as any).offEvent) {
          (webApp as any).offEvent('themeChanged', handleThemeChanged)
          ;(webApp as any).offEvent('viewportChanged', handleViewportChanged)
        }
      }
    }
  }, [webApp])

  // Haptic feedback functions
  const hapticFeedback = {
    impact: useCallback((style: 'light' | 'medium' | 'heavy' = 'medium') => {
      try {
        (webApp as any)?.HapticFeedback?.impactOccurred(style)
      } catch (error) {
        console.log('Haptic feedback not available:', error)
      }
    }, [webApp]),

    notification: useCallback((type: 'error' | 'success' | 'warning') => {
      try {
        (webApp as any)?.HapticFeedback?.notificationOccurred(type)
      } catch (error) {
        console.log('Haptic feedback not available:', error)
      }
    }, [webApp]),

    selection: useCallback(() => {
      try {
        (webApp as any)?.HapticFeedback?.selectionChanged()
      } catch (error) {
        console.log('Haptic feedback not available:', error)
      }
    }, [webApp])
  }

  // Enhanced alert functions with haptic feedback
  const showAlert = useCallback((message: string, callback?: () => void) => {
    hapticFeedback.notification('warning')
    if ((webApp as any)?.showAlert) {
      (webApp as any).showAlert(message, callback)
    } else {
      alert(message)
      callback?.()
    }
  }, [webApp, hapticFeedback])

  const showConfirm = useCallback((message: string, callback?: (confirmed: boolean) => void) => {
    hapticFeedback.impact('light')
    if ((webApp as any)?.showConfirm) {
      (webApp as any).showConfirm(message, (confirmed: boolean) => {
        hapticFeedback.notification(confirmed ? 'success' : 'error')
        callback?.(confirmed)
      })
    } else {
      const confirmed = confirm(message)
      hapticFeedback.notification(confirmed ? 'success' : 'error')
      callback?.(confirmed)
    }
  }, [webApp, hapticFeedback])

  // Cloud storage functions
  const cloudStorage = {
    setItem: useCallback(async (key: string, value: string): Promise<boolean> => {
      try {
        if ((webApp as any)?.CloudStorage?.setItem) {
          return new Promise((resolve) => {
            (webApp as any).CloudStorage.setItem(key, value, (error: string | null, stored: boolean) => {
              if (error) {
                hapticFeedback.notification('error')
                console.error('CloudStorage setItem error:', error)
                resolve(false)
              } else {
                hapticFeedback.notification('success')
                resolve(stored)
              }
            })
          })
        } else {
          // Fallback to localStorage
          localStorage.setItem(`tg_${key}`, value)
          return true
        }
      } catch (error) {
        console.error('Storage error:', error)
        return false
      }
    }, [webApp, hapticFeedback]),

    getItem: useCallback(async (key: string): Promise<string | null> => {
      try {
        if ((webApp as any)?.CloudStorage?.getItem) {
          return new Promise((resolve) => {
            (webApp as any).CloudStorage.getItem(key, (error: string | null, value: string | null) => {
              if (error) {
                console.error('CloudStorage getItem error:', error)
                resolve(null)
              } else {
                resolve(value)
              }
            })
          })
        } else {
          // Fallback to localStorage
          return localStorage.getItem(`tg_${key}`)
        }
      } catch (error) {
        console.error('Storage error:', error)
        return null
      }
    }, [webApp]),

    removeItem: useCallback(async (key: string): Promise<boolean> => {
      try {
        if ((webApp as any)?.CloudStorage?.removeItem) {
          return new Promise((resolve) => {
            (webApp as any).CloudStorage.removeItem(key, (error: string | null, removed: boolean) => {
              if (error) {
                hapticFeedback.notification('error')
                console.error('CloudStorage removeItem error:', error)
                resolve(false)
              } else {
                resolve(removed)
              }
            })
          })
        } else {
          // Fallback to localStorage
          localStorage.removeItem(`tg_${key}`)
          return true
        }
      } catch (error) {
        console.error('Storage error:', error)
        return false
      }
    }, [webApp, hapticFeedback])
  }

  // Utility functions
  const openLink = useCallback((url: string, tryInstantView = true) => {
    hapticFeedback.impact('light')
    if ((webApp as any)?.openLink) {
      (webApp as any).openLink(url, { try_instant_view: tryInstantView })
    } else {
      window.open(url, '_blank')
    }
  }, [webApp, hapticFeedback])

  const openTelegramLink = useCallback((url: string) => {
    hapticFeedback.impact('light')
    if ((webApp as any)?.openTelegramLink) {
      (webApp as any).openTelegramLink(url)
    } else {
      window.open(url, '_blank')
    }
  }, [webApp, hapticFeedback])

  const sendData = useCallback((data: object) => {
    hapticFeedback.impact('medium')
    if ((webApp as any)?.sendData) {
      (webApp as any).sendData(JSON.stringify(data))
    } else {
      console.log('SendData:', data)
    }
  }, [webApp, hapticFeedback])

  const close = useCallback(() => {
    hapticFeedback.impact('heavy')
    if ((webApp as any)?.close) {
      (webApp as any).close()
    } else {
      window.close()
    }
  }, [webApp, hapticFeedback])

  // Share function for content
  const shareContent = useCallback((text: string, url?: string) => {
    const shareData = url ? `${text}\n${url}` : text
    
    // Try native Web Share API first
    if (navigator.share) {
      navigator.share({
        text: shareData,
        url: url
      }).catch(() => {
        // Fallback to Telegram sendData
        sendData({ action: 'share', content: shareData })
      })
    } else {
      // Fallback to Telegram sendData
      sendData({ action: 'share', content: shareData })
    }
  }, [sendData])

  return {
    // State
    ...state,
    webApp,
    
    // Enhanced functions
    hapticFeedback,
    showAlert,
    showConfirm,
    cloudStorage,
    
    // Utility functions
    openLink,
    openTelegramLink,
    sendData,
    close,
    shareContent,
    
    // Theme helpers
    isDark: state.colorScheme === 'dark',
    isLight: state.colorScheme === 'light',
    
    // Device helpers
    isMobile: state.platform === 'android' || state.platform === 'ios',
    isDesktop: state.platform === 'web' || state.platform === 'desktop',
    
    // Feature availability
    hasHapticFeedback: !!(webApp as any)?.HapticFeedback,
    hasCloudStorage: !!(webApp as any)?.CloudStorage,
    hasWebShare: !!navigator.share
  }
}

export default useTelegramWebApp 