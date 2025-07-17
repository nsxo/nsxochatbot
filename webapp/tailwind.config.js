/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Enhanced Brand Colors - Updated Design Sheet
        brand: {
          black: '#000000',
          'dark-gray': '#121212', // Optimized dark mode background
          red: '#FF0000',
          'red-light': '#FF4D4D',
          'red-gradient': '#FF6B6B',
          'electric-blue': '#3A3AFF',
          'blue-gradient': '#4DABF7',
          purple: '#8000FF',
          'purple-gradient': '#9775FA',
          gray: '#333333',
          'gray-light': '#666666',
          'gray-dark': '#1E1E1E', // Enhanced card background
          'off-white': '#E0E0E0', // Softer text contrast
          'glass-white': 'rgba(255, 255, 255, 0.1)', // Glassmorphism
          'glass-border': 'rgba(255, 255, 255, 0.3)'
        },
        telegram: {
          blue: '#0088cc',
          light: '#64b5f6',
          dark: '#0066aa',
          bg: '#000000',
          surface: '#333333',
          text: '#ffffff'
        },
        neon: {
          blue: '#3A3AFF',
          purple: '#8000FF',
          pink: '#ec4899',
          green: '#10b981',
          orange: '#f97316'
        },
        dark: {
          900: '#000000',
          800: '#222222',
          700: '#333333',
          600: '#666666'
        }
      },
      animation: {
        'slide-in': 'slideIn 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
        'pulse-slow': 'pulse 3s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'float': 'float 3s ease-in-out infinite',
        'neon-pulse': 'neonPulse 1.5s ease-in-out infinite',
        'glitch': 'glitch 1s ease-in-out infinite',
        'premium-glow': 'premiumGlow 2s ease-in-out infinite alternate',
        'ripple': 'ripple 0.6s linear',
        'slide-up': 'slideUp 0.4s ease-out',
        'text-reveal': 'textReveal 0.8s ease-out',
        'particle-float': 'particleFloat 4s ease-in-out infinite',
      },
      keyframes: {
        slideIn: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        glow: {
          '0%': { boxShadow: '0 0 20px rgba(0, 212, 255, 0.3)' },
          '100%': { boxShadow: '0 0 30px rgba(0, 212, 255, 0.6)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        neonPulse: {
          '0%, 100%': { 
            textShadow: '0 0 5px currentColor, 0 0 10px currentColor, 0 0 15px currentColor',
            opacity: '1'
          },
          '50%': { 
            textShadow: '0 0 2px currentColor, 0 0 5px currentColor, 0 0 8px currentColor',
            opacity: '0.8'
          },
        },
        glitch: {
          '0%': { 
            textShadow: '0.05em 0 0 #FF0000, -0.03em -0.04em 0 #3A3AFF, 0.025em 0.04em 0 #8000FF',
            transform: 'translate(0)'
          },
          '15%': { 
            textShadow: '0.05em 0 0 #FF0000, -0.03em -0.04em 0 #3A3AFF, 0.025em 0.04em 0 #8000FF',
            transform: 'translate(-0.04em, -0.03em)'
          },
          '16%': { 
            textShadow: '-0.05em -0.025em 0 #FF0000, 0.025em 0.035em 0 #3A3AFF, -0.05em -0.05em 0 #8000FF'
          },
          '49%': { 
            textShadow: '-0.05em -0.025em 0 #FF0000, 0.025em 0.035em 0 #3A3AFF, -0.05em -0.05em 0 #8000FF'
          },
          '50%': { 
            textShadow: '0.05em 0.035em 0 #FF0000, 0.03em 0 0 #3A3AFF, 0 -0.04em 0 #8000FF'
          },
          '99%': { 
            textShadow: '0.05em 0.035em 0 #FF0000, 0.03em 0 0 #3A3AFF, 0 -0.04em 0 #8000FF'
          },
          '100%': { 
            textShadow: '0.05em 0 0 #FF0000, -0.03em -0.04em 0 #3A3AFF, 0.025em 0.04em 0 #8000FF',
            transform: 'translate(0)'
          }
        },
        premiumGlow: {
          '0%': { 
            boxShadow: '0 0 10px #3A3AFF, 0 0 20px #8000FF, 0 0 30px #FF0000'
          },
          '100%': { 
            boxShadow: '0 0 20px #3A3AFF, 0 0 30px #8000FF, 0 0 40px #FF0000'
          }
        },
        ripple: {
          '0%': { 
            transform: 'scale(0)',
            opacity: '1'
          },
          '100%': { 
            transform: 'scale(4)',
            opacity: '0'
          }
        },
        slideUp: {
          '0%': { 
            transform: 'translateY(30px)',
            opacity: '0'
          },
          '100%': { 
            transform: 'translateY(0)',
            opacity: '1'
          }
        },
        textReveal: {
          '0%': { 
            transform: 'translateY(100%)',
            opacity: '0'
          },
          '100%': { 
            transform: 'translateY(0)',
            opacity: '1'
          }
        },
        particleFloat: {
          '0%, 100%': { 
            transform: 'translateY(0px) rotate(0deg)',
            opacity: '0.7'
          },
          '50%': { 
            transform: 'translateY(-20px) rotate(180deg)',
            opacity: '1'
          }
        }
      }
    },
  },
  plugins: [],
} 