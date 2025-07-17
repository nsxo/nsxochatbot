import { UserData, StatsData } from '../types/telegram'

// Base API URL - adjust this to match your bot's webhook server
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-domain.com/api'  // Replace with your actual domain
  : 'http://localhost:8000/api'    // Your local webhook server

// API client class
export class BotAPI {
  private static instance: BotAPI
  private baseURL: string

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL
  }

  static getInstance(): BotAPI {
    if (!BotAPI.instance) {
      BotAPI.instance = new BotAPI()
    }
    return BotAPI.instance
  }

  // Validate Telegram WebApp init data
  async validateInitData(initData: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseURL}/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ initData })
      })
      return response.ok
    } catch (error) {
      console.error('Init data validation failed:', error)
      return false
    }
  }

  // Get user data from bot database
  async getUserData(userId: number, initData?: string): Promise<UserData | null> {
    try {
      const response = await fetch(`${this.baseURL}/user/${userId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `tg-init-data ${initData || ''}`
        }
      })

      if (!response.ok) {
        throw new Error('Failed to fetch user data')
      }

      return await response.json()
    } catch (error) {
      console.error('Failed to get user data:', error)
      return null
    }
  }

  // Get user statistics
  async getUserStats(userId: number, initData?: string): Promise<StatsData | null> {
    try {
      const response = await fetch(`${this.baseURL}/user/${userId}/stats`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `tg-init-data ${initData || ''}`
        }
      })

      if (!response.ok) {
        throw new Error('Failed to fetch user stats')
      }

      return await response.json()
    } catch (error) {
      console.error('Failed to get user stats:', error)
      return null
    }
  }

  // Create Stripe payment session
  async createPaymentSession(userId: number, packageId: string, initData?: string): Promise<string | null> {
    try {
      const response = await fetch(`${this.baseURL}/payment/create-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `tg-init-data ${initData || ''}`
        },
        body: JSON.stringify({
          userId,
          packageId,
          platform: 'telegram_mini_app'
        })
      })

      if (!response.ok) {
        throw new Error('Failed to create payment session')
      }

      const data = await response.json()
      return data.checkout_url
    } catch (error) {
      console.error('Failed to create payment session:', error)
      return null
    }
  }

  // Update user settings
  async updateUserSettings(userId: number, settings: Record<string, any>, initData?: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseURL}/user/${userId}/settings`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `tg-init-data ${initData || ''}`
        },
        body: JSON.stringify(settings)
      })

      return response.ok
    } catch (error) {
      console.error('Failed to update user settings:', error)
      return false
    }
  }

  // Get conversation history
  async getConversationHistory(userId: number, limit: number = 50, initData?: string): Promise<any[]> {
    try {
      const response = await fetch(`${this.baseURL}/user/${userId}/conversations?limit=${limit}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `tg-init-data ${initData || ''}`
        }
      })

      if (!response.ok) {
        throw new Error('Failed to fetch conversation history')
      }

      return await response.json()
    } catch (error) {
      console.error('Failed to get conversation history:', error)
      return []
    }
  }

  // Send action to bot (for WebApp data sending)
  async sendAction(action: string, data: Record<string, any> = {}): Promise<boolean> {
    try {
      // This would typically be handled by Telegram's sendData
      // but we can also provide a fallback API endpoint
      const response = await fetch(`${this.baseURL}/action`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action,
          data,
          timestamp: Date.now()
        })
      })

      return response.ok
    } catch (error) {
      console.error('Failed to send action:', error)
      return false
    }
  }
}

// Export singleton instance
export const botAPI = BotAPI.getInstance()

// Utility functions
export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

export const formatDate = (date: string | Date): string => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(date))
}

export const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
} 