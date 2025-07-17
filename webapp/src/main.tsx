import React from 'react'
import ReactDOM from 'react-dom/client'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import { CssBaseline } from '@mui/material'
import { AppRoot } from '@telegram-apps/telegram-ui'
import App from './App'
import './styles/index.css'
import { createDeviantArtTheme } from './styles/DeviantArtTheme'

// Create DeviantArt-inspired theme
const telegramTheme = createTheme(createDeviantArtTheme('dark'))

// Initialize Telegram Web App
if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
  window.Telegram.WebApp.ready()
  window.Telegram.WebApp.expand()
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider theme={telegramTheme}>
      <CssBaseline />
      <AppRoot>
        <App />
      </AppRoot>
    </ThemeProvider>
  </React.StrictMode>,
) 