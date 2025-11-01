import axios from 'axios'

// Get base URL from environment variables with fallback
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

// Ensure URL ends with /
const baseURL = API_BASE_URL.endsWith('/') ? API_BASE_URL : `${API_BASE_URL}/`

const api = axios.create({
  baseURL,
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT) || 30000, // Default 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  
  // Handle FormData properly - don't override Content-Type
  if (config.data instanceof FormData) {
    // Don't set Content-Type for FormData - let browser handle it
    delete config.headers['Content-Type']
  }
  
  // Log request for debugging
  console.log('🔄 API Request:', {
    method: config.method?.toUpperCase(),
    url: config.url,
    baseURL: config.baseURL,
    headers: config.headers,
    data: config.data instanceof FormData ? 'FormData object' : config.data
  })
  
  return config
}, error => {
  console.error('❌ Request interceptor error:', error)
  return Promise.reject(error)
})

api.interceptors.response.use(
  response => {
    // Log successful responses for debugging
    console.log('✅ API Response:', {
      method: response.config.method?.toUpperCase(),
      url: response.config.url,
      status: response.status,
      data: response.data
    })
    
    // Windows Electron Fix: Re-enable inputs after successful API calls
    if (window.electronAPI) {
      // We're in Electron, apply Windows input fix
      setTimeout(() => {
        const inputs = document.querySelectorAll('input, textarea, select')
        inputs.forEach(input => {
          input.removeAttribute('disabled')
          input.style.pointerEvents = 'auto'
          input.style.userSelect = 'text'
          input.style.webkitUserSelect = 'text'
          input.tabIndex = input.tabIndex || 0
        })
        console.log('🔓 Auto-enabled inputs after API response (Windows Electron fix)')
      }, 50)
    }
    
    return response
  },
  async error => {
    const originalRequest = error.config
    
    // Enhanced error logging
    console.error('❌ API Error:', {
      method: originalRequest?.method?.toUpperCase(),
      url: originalRequest?.url,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      message: error.message
    })

    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) {
        console.warn('❌ Refresh token not found - redirecting to login')
        // Clear invalid tokens
        localStorage.removeItem('token')
        localStorage.removeItem('refresh_token')
        // Redirect to login if needed
        window.location.href = '/login'
        return Promise.reject(error)
      }

      try {
        console.log('🔄 Attempting token refresh...')
        const response = await axios.post(
        `${baseURL}token/refresh/`,
        {refresh: refreshToken}
        )

        const newAccessToken = response.data.access
        localStorage.setItem('token', newAccessToken)
        console.log('✅ Token refreshed successfully')

        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
        
        // Apply Windows Electron input fix after token refresh
        if (window.electronAPI) {
          setTimeout(() => {
            const inputs = document.querySelectorAll('input, textarea, select')
            inputs.forEach(input => {
              input.removeAttribute('disabled')
              input.style.pointerEvents = 'auto'
              input.style.userSelect = 'text'
              input.style.webkitUserSelect = 'text'
              input.tabIndex = input.tabIndex || 0
            })
            console.log('🔓 Re-enabled inputs after token refresh (Windows Electron fix)')
          }, 100)
        }
        
        return api(originalRequest)
      } catch (refreshError) {
        console.error('❌ Token refresh failed:', refreshError)
        // Clear invalid tokens
        localStorage.removeItem('token')
        localStorage.removeItem('refresh_token')
        // Redirect to login if needed
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// Export both the configured axios instance and the base URL
export default api
export { baseURL, API_BASE_URL }


