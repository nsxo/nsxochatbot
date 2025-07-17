import { useState, useEffect, useMemo } from 'react'
import { createTheme, Theme } from '@mui/material/styles'
import { createDeviantArtTheme, deviantArtColors } from '../styles/DeviantArtTheme'
import { useTelegramWebApp } from './useTelegramWebApp'

interface DynamicThemeConfig {
  enableAutoSync: boolean
  preferredMode: 'auto' | 'light' | 'dark'
  customColors?: {
    primary?: string
    secondary?: string
    accent?: string
  }
  animationDuration: number
}

const defaultConfig: DynamicThemeConfig = {
  enableAutoSync: true,
  preferredMode: 'auto',
  animationDuration: 300
}

export const useDynamicTheme = (config: Partial<DynamicThemeConfig> = {}) => {
  const mergedConfig = { ...defaultConfig, ...config }
  const { colorScheme, themeParams, isDark, isLight, cloudStorage } = useTelegramWebApp()
  
  const [themeMode, setThemeMode] = useState<'light' | 'dark'>('dark')
  const [isTransitioning, setIsTransitioning] = useState(false)
  const [customThemeParams, setCustomThemeParams] = useState(themeParams)

  // Determine the effective theme mode
  const effectiveMode = useMemo(() => {
    switch (mergedConfig.preferredMode) {
      case 'light':
        return 'light'
      case 'dark':
        return 'dark'
      case 'auto':
      default:
        if (mergedConfig.enableAutoSync) {
          return colorScheme
        }
        return themeMode
    }
  }, [mergedConfig.preferredMode, mergedConfig.enableAutoSync, colorScheme, themeMode])

  // Update theme when Telegram theme changes
  useEffect(() => {
    if (mergedConfig.enableAutoSync && effectiveMode !== themeMode) {
      setIsTransitioning(true)
      
      const transitionTimer = setTimeout(() => {
        setThemeMode(effectiveMode)
        setCustomThemeParams(themeParams)
        setIsTransitioning(false)
      }, mergedConfig.animationDuration / 2)

      return () => clearTimeout(transitionTimer)
    }
  }, [effectiveMode, themeMode, themeParams, mergedConfig.enableAutoSync, mergedConfig.animationDuration])

  // Create enhanced theme with Telegram parameters
  const theme = useMemo(() => {
    const baseTheme = createDeviantArtTheme(effectiveMode)
    
    // Extract Telegram theme colors if available
    const telegramColors = {
      background: customThemeParams.bg_color,
      text: customThemeParams.text_color,
      hint: customThemeParams.hint_color,
      link: customThemeParams.link_color,
      button: customThemeParams.button_color,
      buttonText: customThemeParams.button_text_color,
      secondaryBg: customThemeParams.secondary_bg_color,
      headerBg: customThemeParams.header_bg_color,
      accentText: customThemeParams.accent_text_color,
      sectionBg: customThemeParams.section_bg_color,
      sectionHeaderText: customThemeParams.section_header_text_color,
      subtitleText: customThemeParams.subtitle_text_color,
      destructiveText: customThemeParams.destructive_text_color
    }

    // Create enhanced theme with Telegram integration
    const enhancedTheme = createTheme({
      ...baseTheme,
      palette: {
        ...baseTheme.palette,
        mode: effectiveMode,
        
        // Override with Telegram colors if available
        ...(telegramColors.background && {
          background: {
            ...baseTheme.palette?.background,
            default: telegramColors.background,
            paper: telegramColors.secondaryBg || telegramColors.background
          }
        }),
        
        ...(telegramColors.text && {
          text: {
            ...baseTheme.palette?.text,
            primary: telegramColors.text,
            secondary: telegramColors.hint || telegramColors.text
          }
        }),
        
        // Custom color overrides
        ...(mergedConfig.customColors && {
          primary: {
            ...baseTheme.palette?.primary,
            main: mergedConfig.customColors.primary || baseTheme.palette?.primary?.main || deviantArtColors.primary.main
          },
          secondary: {
            ...baseTheme.palette?.secondary,
            main: mergedConfig.customColors.secondary || baseTheme.palette?.secondary?.main || deviantArtColors.secondary.main
          }
        })
      },
      
      // Add theme transition properties
      transitions: {
        ...baseTheme.transitions,
        create: (props, options) => {
          const defaultOptions = {
            duration: mergedConfig.animationDuration,
            easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
          }
          return baseTheme.transitions?.create(props, { ...defaultOptions, ...options }) || ''
        }
      },

      // Enhanced component overrides for theme transitions
      components: {
        ...baseTheme.components,
        MuiCssBaseline: {
          styleOverrides: {
            body: {
              transition: `background-color ${mergedConfig.animationDuration}ms cubic-bezier(0.4, 0, 0.2, 1), color ${mergedConfig.animationDuration}ms cubic-bezier(0.4, 0, 0.2, 1)`,
              ...(isTransitioning && {
                pointerEvents: 'none'
              })
            }
          }
        },
        MuiCard: {
          styleOverrides: {
            root: {
              ...baseTheme.components?.MuiCard?.styleOverrides?.root,
              transition: `all ${mergedConfig.animationDuration}ms cubic-bezier(0.4, 0, 0.2, 1)`,
              
              // Add special Telegram-aware styling
              ...(telegramColors.sectionBg && {
                backgroundColor: `${telegramColors.sectionBg}dd`,
                backdropFilter: 'blur(20px)'
              })
            }
          }
        },
        MuiButton: {
          styleOverrides: {
            root: {
              ...baseTheme.components?.MuiButton?.styleOverrides?.root,
              transition: `all ${mergedConfig.animationDuration}ms cubic-bezier(0.4, 0, 0.2, 1)`,
              
              // Use Telegram button colors if available
              ...(telegramColors.button && {
                '&.MuiButton-contained': {
                  backgroundColor: telegramColors.button,
                  color: telegramColors.buttonText || '#FFFFFF',
                  '&:hover': {
                    backgroundColor: telegramColors.button,
                    filter: 'brightness(1.1)'
                  }
                }
              })
            }
          }
        },
        MuiTypography: {
          styleOverrides: {
            root: {
              transition: `color ${mergedConfig.animationDuration}ms cubic-bezier(0.4, 0, 0.2, 1)`
            }
          }
        }
      }
    })

    return enhancedTheme
  }, [effectiveMode, customThemeParams, mergedConfig, isTransitioning])

  // Theme control functions
  const setLightMode = async () => {
    setThemeMode('light')
    await cloudStorage.setItem('preferredTheme', 'light')
  }

  const setDarkMode = async () => {
    setThemeMode('dark')
    await cloudStorage.setItem('preferredTheme', 'dark')
  }

  const toggleTheme = async () => {
    const newMode = themeMode === 'light' ? 'dark' : 'light'
    setThemeMode(newMode)
    await cloudStorage.setItem('preferredTheme', newMode)
  }

  const enableAutoSync = async () => {
    await cloudStorage.setItem('autoSyncTheme', 'true')
  }

  const disableAutoSync = async () => {
    await cloudStorage.setItem('autoSyncTheme', 'false')
  }

  // Load saved preferences
  useEffect(() => {
    const loadPreferences = async () => {
      try {
        const savedTheme = await cloudStorage.getItem('preferredTheme')
        const savedAutoSync = await cloudStorage.getItem('autoSyncTheme')
        
        if (savedTheme && (savedTheme === 'light' || savedTheme === 'dark')) {
          setThemeMode(savedTheme)
        }
        
        // Auto-sync is enabled by default
        if (savedAutoSync === 'false') {
          mergedConfig.enableAutoSync = false
        }
      } catch (error) {
        console.log('Failed to load theme preferences:', error)
      }
    }

    loadPreferences()
  }, [cloudStorage])

  // Generate CSS variables for smooth transitions
  const themeVariables = useMemo(() => {
    return {
      '--theme-primary': theme.palette.primary.main,
      '--theme-secondary': theme.palette.secondary.main,
      '--theme-background': theme.palette.background.default,
      '--theme-paper': theme.palette.background.paper,
      '--theme-text-primary': theme.palette.text.primary,
      '--theme-text-secondary': theme.palette.text.secondary,
      '--theme-transition-duration': `${mergedConfig.animationDuration}ms`,
      '--telegram-bg': customThemeParams.bg_color || 'transparent',
      '--telegram-text': customThemeParams.text_color || theme.palette.text.primary,
      '--telegram-button': customThemeParams.button_color || theme.palette.primary.main,
      '--telegram-accent': customThemeParams.accent_text_color || theme.palette.secondary.main
    } as React.CSSProperties
  }, [theme, mergedConfig.animationDuration, customThemeParams])

  return {
    theme,
    themeMode: effectiveMode,
    isTransitioning,
    themeVariables,
    
    // Theme information
    isDarkMode: effectiveMode === 'dark',
    isLightMode: effectiveMode === 'light',
    isAutoSyncEnabled: mergedConfig.enableAutoSync,
    telegramThemeParams: customThemeParams,
    
    // Theme controls
    setLightMode,
    setDarkMode,
    toggleTheme,
    enableAutoSync,
    disableAutoSync,
    
    // Telegram integration status
    hasTelegramTheme: Object.keys(customThemeParams).length > 0,
    telegramColorScheme: colorScheme
  }
}

export default useDynamicTheme 