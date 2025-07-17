import axios from 'axios'

// Configure base URL based on environment
const baseURL = process.env.NODE_ENV === 'production' 
  ? `${window.location.origin}/api`  // Railway will serve both frontend and API
  : 'http://localhost:8000/api'      // Local development

export const api = axios.create({
  baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for authentication
api.interceptors.request.use(
  (config) => {
    // Add any auth tokens here if needed
    const token = localStorage.getItem('admin_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('admin_token')
      window.location.href = '/login'
    }
    
    // Return a more user-friendly error message
    const message = error.response?.data?.message || error.message || 'An error occurred'
    return Promise.reject(new Error(message))
  }
)

export default api 