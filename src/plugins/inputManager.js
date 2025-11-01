/**
 * Vue Plugin for InputManager
 * Provides easy access to input management functionality in Vue components
 */

import { inject } from 'vue'

export const InputManagerPlugin = {
  install(app, options = {}) {
    // Only install on Windows Electron
    if (!window.electronAPI || !navigator.platform.includes('Win')) {
      console.log('⏭️ InputManager plugin skipped (not Windows Electron)')
      return
    }

    // Global mixin for all components
    app.mixin({
      mounted() {
        // Re-enable inputs when component mounts
        if (window.inputManager) {
          setTimeout(() => {
            window.inputManager.enableAllInputs(`component-mounted-${this.$options.name || 'unknown'}`)
          }, 50)
        }
      },
      
      activated() {
        // Re-enable inputs when keep-alive component activates
        if (window.inputManager) {
          setTimeout(() => {
            window.inputManager.enableAllInputs(`component-activated-${this.$options.name || 'unknown'}`)
          }, 50)
        }
      }
    })

    // Global directive for manual input management
    app.directive('input-fix', {
      mounted(el, binding) {
        // Apply fix to specific element
        const applyFix = () => {
          const inputs = el.querySelectorAll('input, textarea, select, button')
          inputs.forEach(input => {
            input.removeAttribute('disabled')
            input.style.pointerEvents = 'auto'
            input.style.userSelect = 'text'
            input.style.webkitUserSelect = 'text'
            input.tabIndex = input.tabIndex || 0
          })
        }

        // Apply immediately
        setTimeout(applyFix, 10)

        // Store reference for cleanup
        el._inputFixInterval = setInterval(applyFix, 1000)
      },

      unmounted(el) {
        if (el._inputFixInterval) {
          clearInterval(el._inputFixInterval)
        }
      }
    })

    console.log('🔌 InputManager Vue plugin installed')
  }
}

// Composition API helper
export function useInputManager() {
  const inputManager = inject('inputManager', null)
  
  const enableInputs = (source = 'composition-api') => {
    return inputManager?.enableAllInputs(source) || 0
  }
  
  const getStats = () => {
    return inputManager?.getStats() || null
  }
  
  const trigger = (source = 'manual-composition') => {
    return inputManager?.trigger(source) || 0
  }
  
  return {
    inputManager,
    enableInputs,
    getStats,
    trigger,
    isActive: inputManager?.isActive || false
  }
}