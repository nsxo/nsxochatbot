import { ThemeOptions } from '@mui/material/styles'

// DeviantArt-Inspired Design System
// Based on research of DeviantArt's design patterns and community-focused aesthetic

export const deviantArtColors = {
  // Primary DeviantArt Green Palette
  primary: {
    main: '#05CC47',        // DeviantArt signature green
    light: '#4FFFA6',       // Lighter green for highlights
    dark: '#00A012',        // Darker green for depth
    50: '#E8F8F0',
    100: '#C6EFD8',
    200: '#A0E5BE',
    300: '#7ADBA4',
    400: '#5FD490',
    500: '#05CC47',
    600: '#04B83F',
    700: '#03A236',
    800: '#028B2E',
    900: '#016B1F'
  },

  // Artistic Secondary Palette (Purple/Violet)
  secondary: {
    main: '#8B5FBF',        // Creative purple
    light: '#B794E6',       // Light lavender
    dark: '#5D3E7F',        // Deep purple
    50: '#F3EEFA',
    100: '#E0D4F2',
    200: '#CBB7E8',
    300: '#B69ADE',
    400: '#A682D6',
    500: '#8B5FBF',
    600: '#7D55AB',
    700: '#6C4893',
    800: '#5C3C7B',
    900: '#4A2C5A'
  },

  // DeviantArt Inspired Neutral Palette
  neutral: {
    50: '#FAFBFA',          // Pure white with slight green tint
    100: '#F4F6F4',         // Light gray-green
    200: '#E8ECE8',         // Soft gray
    300: '#D1D9D1',         // Medium light gray
    400: '#A8B3A8',         // Medium gray
    500: '#7F8C7F',         // Base gray
    600: '#5C6B5C',         // Dark gray
    700: '#4E5A4E',         // Darker gray
    800: '#3A443A',         // Very dark gray
    900: '#2A332A'          // Almost black with green tint
  },

  // Creative Accent Colors
  accent: {
    orange: '#FF6B35',      // DeviantArt orange accent
    blue: '#4A90E2',        // Trust blue
    yellow: '#FFD93D',      // Highlight yellow
    red: '#E74C3C',         // Alert red
    teal: '#26D0CE',        // Creative teal
    pink: '#FF7B94'         // Community pink
  },

  // Art-focused gradients
  gradients: {
    creative: 'linear-gradient(135deg, #05CC47 0%, #8B5FBF 100%)',
    warm: 'linear-gradient(135deg, #FF6B35 0%, #FFD93D 100%)',
    cool: 'linear-gradient(135deg, #4A90E2 0%, #26D0CE 100%)',
    artistic: 'linear-gradient(135deg, #8B5FBF 0%, #FF7B94 100%)',
    glass: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)'
  }
}

// Typography system inspired by DeviantArt's clean, readable design
export const deviantArtTypography = {
  fontFamily: {
    primary: '"Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    secondary: '"Poppins", "SF Pro Text", system-ui, sans-serif',
    monospace: '"SF Mono", "Monaco", "Inconsolata", "Roboto Mono", monospace'
  },
  
  // DeviantArt-inspired text styles
  variants: {
    hero: {
      fontSize: '3.5rem',
      fontWeight: 800,
      lineHeight: 1.1,
      letterSpacing: '-0.02em'
    },
    title: {
      fontSize: '2.25rem',
      fontWeight: 700,
      lineHeight: 1.2,
      letterSpacing: '-0.01em'
    },
    subtitle: {
      fontSize: '1.5rem',
      fontWeight: 600,
      lineHeight: 1.3,
      letterSpacing: '0em'
    },
    body: {
      fontSize: '1rem',
      fontWeight: 400,
      lineHeight: 1.6,
      letterSpacing: '0.01em'
    },
    caption: {
      fontSize: '0.875rem',
      fontWeight: 500,
      lineHeight: 1.4,
      letterSpacing: '0.02em'
    },
    micro: {
      fontSize: '0.75rem',
      fontWeight: 500,
      lineHeight: 1.3,
      letterSpacing: '0.03em'
    }
  }
}

// DeviantArt-inspired spacing and layout system
export const deviantArtSpacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  '2xl': 48,
  '3xl': 64,
  '4xl': 96
}

// Glass morphism and artistic effects
export const deviantArtEffects = {
  glassMorphism: {
    background: 'rgba(255, 255, 255, 0.08)',
    backdropFilter: 'blur(16px)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)'
  },
  
  creativeShadow: {
    light: '0 2px 8px rgba(5, 204, 71, 0.15)',
    medium: '0 4px 16px rgba(5, 204, 71, 0.2)',
    heavy: '0 8px 32px rgba(5, 204, 71, 0.25)'
  },
  
  artisticBlur: {
    subtle: 'blur(4px)',
    medium: 'blur(8px)',
    heavy: 'blur(16px)'
  }
}

// Create DeviantArt-inspired Material-UI theme
export const createDeviantArtTheme = (mode: 'light' | 'dark' = 'dark'): ThemeOptions => ({
  palette: {
    mode,
    primary: {
      main: deviantArtColors.primary.main,
      light: deviantArtColors.primary.light,
      dark: deviantArtColors.primary.dark,
      contrastText: '#FFFFFF'
    },
    secondary: {
      main: deviantArtColors.secondary.main,
      light: deviantArtColors.secondary.light,
      dark: deviantArtColors.secondary.dark,
      contrastText: '#FFFFFF'
    },
    background: {
      default: mode === 'dark' ? deviantArtColors.neutral[900] : deviantArtColors.neutral[50],
      paper: mode === 'dark' ? deviantArtColors.neutral[800] : deviantArtColors.neutral[100]
    },
    text: {
      primary: mode === 'dark' ? deviantArtColors.neutral[50] : deviantArtColors.neutral[900],
      secondary: mode === 'dark' ? deviantArtColors.neutral[300] : deviantArtColors.neutral[600]
    },
    divider: mode === 'dark' ? deviantArtColors.neutral[700] : deviantArtColors.neutral[200]
  },
  
  typography: {
    fontFamily: deviantArtTypography.fontFamily.primary,
    h1: {
      ...deviantArtTypography.variants.hero,
      background: deviantArtColors.gradients.creative,
      backgroundClip: 'text',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent'
    },
    h2: deviantArtTypography.variants.title,
    h3: deviantArtTypography.variants.subtitle,
    body1: deviantArtTypography.variants.body,
    caption: deviantArtTypography.variants.caption
  },
  
  spacing: 8,
  
  shape: {
    borderRadius: 16
  },
  
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          background: mode === 'dark' 
            ? 'rgba(42, 51, 42, 0.9)' 
            : 'rgba(250, 251, 250, 0.9)',
          backdropFilter: 'blur(20px)',
          border: `1px solid ${mode === 'dark' 
            ? 'rgba(255, 255, 255, 0.08)' 
            : 'rgba(0, 0, 0, 0.04)'}`,
          boxShadow: mode === 'dark'
            ? '0 8px 32px rgba(0, 0, 0, 0.3)'
            : '0 8px 32px rgba(0, 0, 0, 0.1)',
          borderRadius: 24,
          overflow: 'hidden',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: mode === 'dark'
              ? '0 12px 40px rgba(0, 0, 0, 0.4)'
              : '0 12px 40px rgba(0, 0, 0, 0.15)'
          }
        }
      }
    },
    
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          textTransform: 'none',
          fontWeight: 600,
          padding: '12px 24px',
          fontSize: '0.95rem',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: deviantArtEffects.creativeShadow.medium
          }
        },
        contained: {
          background: deviantArtColors.gradients.creative,
          color: '#FFFFFF',
          '&:hover': {
            background: deviantArtColors.gradients.creative,
            filter: 'brightness(1.1)'
          }
        }
      }
    },
    
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          fontWeight: 500,
          border: 'none',
          background: deviantArtColors.gradients.glass,
          backdropFilter: 'blur(8px)',
          '&.MuiChip-colorPrimary': {
            background: deviantArtColors.gradients.creative,
            color: '#FFFFFF'
          }
        }
      }
    },
    
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          height: 8,
          backgroundColor: mode === 'dark' 
            ? deviantArtColors.neutral[700] 
            : deviantArtColors.neutral[200]
        },
        bar: {
          borderRadius: 8,
          background: deviantArtColors.gradients.creative
        }
      }
    }
  }
})

// DeviantArt Design Principles
export const deviantArtDesignPrinciples = {
  // 1. Creative Expression - UI should inspire and showcase creativity
  creativeExpression: {
    description: 'Every element should feel artistic and inspire creativity',
    implementation: [
      'Use artistic gradients and color combinations',
      'Incorporate subtle animations and hover effects',
      'Create visual hierarchy that draws attention like artwork'
    ]
  },
  
  // 2. Community Focus - Design for sharing and interaction
  communityFocus: {
    description: 'Design elements that promote sharing and community interaction',
    implementation: [
      'Prominent sharing and action buttons',
      'Clear social indicators (likes, comments, views)',
      'Easy navigation between different content types'
    ]
  },
  
  // 3. Content First - Let the content be the hero
  contentFirst: {
    description: 'UI should enhance, not overshadow the main content',
    implementation: [
      'Subtle backgrounds that don\'t compete with content',
      'Generous white space around important elements',
      'Clean, minimal interface with artistic touches'
    ]
  },
  
  // 4. Artistic Polish - Every detail should feel crafted
  artisticPolish: {
    description: 'High attention to detail in every visual element',
    implementation: [
      'Custom icons and illustrations',
      'Smooth, meaningful animations',
      'Consistent visual language throughout'
    ]
  }
}

export default createDeviantArtTheme 