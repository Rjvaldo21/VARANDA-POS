/**
 * Global Input Management System for Windows Electron
 * Handles input disable issues across the entire application
 */

class InputManager {
  constructor() {
    this.observers = []
    this.intervalId = null
    this.isElectron = !!window.electronAPI
    this.isWindows = navigator.platform.includes('Win')
    this.isActive = this.isElectron && this.isWindows
    this.eventListeners = []
    
    console.log('🎯 InputManager initialized:', {
      isElectron: this.isElectron,
      isWindows: this.isWindows, 
      isActive: this.isActive
    })
    
    if (this.isActive) {
      this.init()
    }
  }

  /**
   * Force enable all inputs in the document
   */
  enableAllInputs(source = 'manual') {
    if (!this.isActive) return

    const inputs = document.querySelectorAll('input, textarea, select, button')
    let enabledCount = 0
    
    inputs.forEach(input => {
      // Skip if input should remain disabled (has data-keep-disabled attribute)
      if (input.hasAttribute('data-keep-disabled')) return
      
      // Comprehensive input restoration
      input.removeAttribute('disabled')
      input.style.pointerEvents = 'auto'
      input.style.userSelect = 'text'
      input.style.webkitUserSelect = 'text'
      input.style.opacity = ''
      input.style.cursor = ''
      
      // Restore tab navigation
      if (!input.hasAttribute('tabindex') || input.tabIndex < 0) {
        input.tabIndex = 0
      }
      
      // Special handling for different input types
      if (input.type === 'button' || input.type === 'submit') {
        input.style.cursor = 'pointer'
      }
      
      enabledCount++
    })
    
    if (enabledCount > 0) {
      console.log(`🔓 Enabled ${enabledCount} inputs (source: ${source})`)
    }
    
    return enabledCount
  }

  /**
   * Initialize all monitoring systems
   */
  init() {
    this.initDomMonitoring()
    this.initApiMonitoring()
    this.initEventMonitoring()
    this.initPeriodicCheck()
    
    // Initial enable
    setTimeout(() => this.enableAllInputs('initial'), 100)
  }

  /**
   * Monitor DOM changes for dynamic content
   */
  initDomMonitoring() {
    const observer = new MutationObserver((mutations) => {
      let hasInputChanges = false
      
      mutations.forEach((mutation) => {
        if (mutation.type === 'childList') {
          // Check for new input elements
          mutation.addedNodes.forEach((node) => {
            if (node.nodeType === 1) { // Element node
              if (node.matches && node.matches('input, textarea, select, button')) {
                hasInputChanges = true
              } else if (node.querySelector) {
                const inputs = node.querySelectorAll('input, textarea, select, button')
                if (inputs.length > 0) {
                  hasInputChanges = true
                }
              }
            }
          })
        } else if (mutation.type === 'attributes') {
          // Check for disabled attribute changes
          if (mutation.attributeName === 'disabled' && 
              mutation.target.matches && 
              mutation.target.matches('input, textarea, select, button')) {
            hasInputChanges = true
          }
        }
      })
      
      if (hasInputChanges) {
        setTimeout(() => this.enableAllInputs('dom-mutation'), 50)
      }
    })
    
    observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['disabled', 'readonly', 'style']
    })
    
    this.observers.push(observer)
    console.log('📱 DOM monitoring initialized')
  }

  /**
   * Monitor API responses globally
   */
  initApiMonitoring() {
    // Monitor fetch API
    const originalFetch = window.fetch
    window.fetch = async (...args) => {
      try {
        const response = await originalFetch.apply(window, args)
        if (response.ok) {
          setTimeout(() => this.enableAllInputs('fetch-response'), 100)
        }
        return response
      } catch (error) {
        setTimeout(() => this.enableAllInputs('fetch-error'), 100)
        throw error
      }
    }
    
    // Monitor XMLHttpRequest
    const originalXHROpen = XMLHttpRequest.prototype.open
    const originalXHRSend = XMLHttpRequest.prototype.send
    
    XMLHttpRequest.prototype.open = function(...args) {
      this._inputManager_url = args[1]
      return originalXHROpen.apply(this, args)
    }
    
    XMLHttpRequest.prototype.send = function(...args) {
      this.addEventListener('load', () => {
        if (this.status >= 200 && this.status < 300) {
          setTimeout(() => window.inputManager?.enableAllInputs('xhr-response'), 100)
        }
      })
      
      this.addEventListener('error', () => {
        setTimeout(() => window.inputManager?.enableAllInputs('xhr-error'), 100)
      })
      
      return originalXHRSend.apply(this, args)
    }
    
    console.log('🌐 API monitoring initialized')
  }

  /**
   * Monitor various events that might disable inputs
   */
  initEventMonitoring() {
    const events = [
      'submit',
      'reset', 
      'focus',
      'blur',
      'click',
      'change',
      'input'
    ]
    
    events.forEach(eventType => {
      const listener = (event) => {
        // Check if this event might affect input states
        if (event.target.matches && event.target.matches('form, input, textarea, select, button')) {
          setTimeout(() => this.enableAllInputs(`event-${eventType}`), 25)
        }
      }
      
      document.addEventListener(eventType, listener, true)
      this.eventListeners.push({ type: eventType, listener })
    })
    
    // Special handling for form submissions
    document.addEventListener('submit', (event) => {
      setTimeout(() => this.enableAllInputs('form-submit'), 200)
    }, true)
    
    console.log('⚡ Event monitoring initialized')
  }

  /**
   * Periodic fallback check
   */
  initPeriodicCheck() {
    this.intervalId = setInterval(() => {
      this.enableAllInputs('periodic-check')
    }, 2000) // Every 2 seconds
    
    console.log('⏰ Periodic monitoring initialized')
  }

  /**
   * Monitor Vue router changes
   */
  initRouterMonitoring() {
    // Listen to route changes
    window.addEventListener('popstate', () => {
      setTimeout(() => this.enableAllInputs('route-change'), 150)
    })
    
    // Monitor hash changes
    window.addEventListener('hashchange', () => {
      setTimeout(() => this.enableAllInputs('hash-change'), 150)
    })
  }

  /**
   * Cleanup all observers and listeners
   */
  destroy() {
    // Clear observers
    this.observers.forEach(observer => observer.disconnect())
    this.observers = []
    
    // Clear event listeners
    this.eventListeners.forEach(({ type, listener }) => {
      document.removeEventListener(type, listener, true)
    })
    this.eventListeners = []
    
    // Clear interval
    if (this.intervalId) {
      clearInterval(this.intervalId)
      this.intervalId = null
    }
    
    console.log('🛑 InputManager destroyed')
  }

  /**
   * Manual trigger for input enablement
   */
  trigger(source = 'manual-trigger') {
    return this.enableAllInputs(source)
  }

  /**
   * Get statistics about input management
   */
  getStats() {
    const inputs = document.querySelectorAll('input, textarea, select, button')
    const disabled = document.querySelectorAll('input:disabled, textarea:disabled, select:disabled, button:disabled')
    
    return {
      totalInputs: inputs.length,
      disabledInputs: disabled.length,
      isActive: this.isActive,
      observersCount: this.observers.length,
      listenersCount: this.eventListeners.length
    }
  }
}

// Export for use in other modules
export default InputManager

// Auto-initialize if in browser environment
if (typeof window !== 'undefined') {
  window.inputManager = new InputManager()
}