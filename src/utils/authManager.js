/**
 * Enhanced Authentication Manager for Windows Electron
 * Prevents auth-related DOM manipulation from disabling inputs
 */

import { jwtDecode } from 'jwt-decode'

class AuthManager {
  constructor() {
    this.isWindowsElectron = window.electronAPI && navigator.platform.includes('Win')
    this.tokenCheckInterval = null
    this.lastTokenStatus = null
    
    console.log('🔐 AuthManager initialized:', {
      isWindowsElectron: this.isWindowsElectron
    })
    
    if (this.isWindowsElectron) {
      this.initTokenMonitoring()
    }
  }

  /**
   * Safe token validation that doesn't affect DOM
   */
  isValidToken(token = null) {
    try {
      const authToken = token || localStorage.getItem('token')
      if (!authToken) return false
      
      const decoded = jwtDecode(authToken)
      const now = Date.now() / 1000
      
      return decoded.exp > now
    } catch (error) {
      console.warn('🔐 Invalid token:', error.message)
      return false
    }
  }

  /**
   * Safe authentication check without DOM manipulation
   */
  checkAuth() {
    const token = localStorage.getItem('token')
    const isValid = this.isValidToken(token)
    
    // Store auth status without triggering UI updates
    this.lastTokenStatus = isValid
    
    return {
      isAuthenticated: isValid,
      token: token,
      needsLogin: !isValid
    }
  }

  /**
   * Enhanced login with input preservation
   */
  async login(credentials) {
    try {
      // Preserve current input states before login
      if (this.isWindowsElectron) {
        this.preserveInputStates()
      }
      
      const response = await fetch('/api/token/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials)
      })
      
      if (!response.ok) {
        throw new Error('Login failed')
      }
      
      const data = await response.json()
      const decoded = jwtDecode(data.access)
      
      localStorage.setItem('token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
      localStorage.setItem('username', decoded.username)
      localStorage.setItem('role', decoded.role)
      
      // Restore input states after successful login
      if (this.isWindowsElectron) {
        setTimeout(() => this.restoreInputStates(), 100)
      }
      
      console.log('✅ Login successful')
      return { success: true, user: decoded }
      
    } catch (error) {
      console.error('❌ Login failed:', error)
      
      // Ensure inputs remain enabled even on login failure
      if (this.isWindowsElectron) {
        setTimeout(() => this.restoreInputStates(), 100)
      }
      
      return { success: false, error: error.message }
    }
  }

  /**
   * Safe logout without DOM side effects
   */
  logout() {
    // Clear auth data
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('username')
    localStorage.removeItem('role')
    
    // Ensure inputs remain functional during logout
    if (this.isWindowsElectron) {
      setTimeout(() => this.restoreInputStates(), 50)
    }
    
    console.log('🔓 Logged out successfully')
  }

  /**
   * Preserve current input states
   */
  preserveInputStates() {
    const inputs = document.querySelectorAll('input, textarea, select')
    this.savedInputStates = Array.from(inputs).map(input => ({
      element: input,
      disabled: input.disabled,
      readonly: input.readOnly,
      value: input.value,
      pointerEvents: input.style.pointerEvents,
      userSelect: input.style.userSelect
    }))
  }

  /**
   * Restore preserved input states
   */
  restoreInputStates() {
    if (!this.savedInputStates) {
      // Fallback: enable all inputs
      this.enableAllInputs('auth-fallback')
      return
    }
    
    this.savedInputStates.forEach(state => {
      if (state.element && state.element.parentNode) {
        if (!state.element.hasAttribute('data-keep-disabled')) {
          state.element.disabled = false
          state.element.style.pointerEvents = 'auto'
          state.element.style.userSelect = 'text'
          state.element.style.webkitUserSelect = 'text'
        }
      }
    })
    
    console.log('🔓 AuthManager: Restored input states')
  }

  /**
   * Force enable all inputs (fallback method)
   */
  enableAllInputs(source = 'auth-manager') {
    const inputs = document.querySelectorAll('input, textarea, select, button')
    let enabledCount = 0
    
    inputs.forEach(input => {
      if (!input.hasAttribute('data-keep-disabled')) {
        input.removeAttribute('disabled')
        input.style.pointerEvents = 'auto'
        input.style.userSelect = 'text'
        input.style.webkitUserSelect = 'text'
        input.tabIndex = input.tabIndex || 0
        enabledCount++
      }
    })
    
    if (enabledCount > 0) {
      console.log(`🔓 AuthManager: Enabled ${enabledCount} inputs (${source})`)
    }
  }

  /**
   * Monitor token status without affecting UI
   */
  initTokenMonitoring() {
    this.tokenCheckInterval = setInterval(() => {
      const currentStatus = this.isValidToken()
      
      // Only act if status changed and we're not on login page
      if (currentStatus !== this.lastTokenStatus && window.location.pathname !== '/login') {
        this.lastTokenStatus = currentStatus
        
        if (!currentStatus) {
          console.log('🔐 Token expired, but preserving input functionality')
          // Don't automatically redirect, just log
        }
        
        // Ensure inputs remain functional regardless of auth status
        setTimeout(() => this.enableAllInputs('token-monitor'), 100)
      }
    }, 30000) // Check every 30 seconds
    
    console.log('⏰ Token monitoring initialized')
  }

  /**
   * Enhanced route guard that preserves input functionality
   */
  beforeRouteEnter(to, from, next) {
    const auth = this.checkAuth()
    
    if (to.path === '/login' && auth.isAuthenticated) {
      // Preserve inputs before redirect
      if (this.isWindowsElectron) {
        setTimeout(() => this.enableAllInputs('route-redirect'), 100)
      }
      next('/pos')
    }
    else if (to.path !== '/login' && !auth.isAuthenticated) {
      // Preserve inputs before redirect to login
      if (this.isWindowsElectron) {
        setTimeout(() => this.enableAllInputs('route-auth-check'), 100)
      }
      next('/login')
    }
    else {
      next()
    }
  }

  /**
   * Clean up resources
   */
  destroy() {
    if (this.tokenCheckInterval) {
      clearInterval(this.tokenCheckInterval)
      this.tokenCheckInterval = null
    }
    
    console.log('🛑 AuthManager destroyed')
  }
}

// Export singleton instance
const authManager = new AuthManager()
export default authManager

// Global access for debugging
if (typeof window !== 'undefined') {
  window.authManager = authManager
}