import './style.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import i18n from './locales'
import InputManager from './utils/inputManager.js'
import { InputManagerPlugin } from './plugins/inputManager.js'
import authManager from './utils/authManager.js'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(i18n)
app.use(InputManagerPlugin)

// Initialize Windows Electron fixes
if (window.electronAPI && navigator.platform.includes('Win')) {
  console.log('🔧 Initializing Windows Electron fixes')
  
  // Initialize InputManager
  if (!window.inputManager) {
    window.inputManager = new InputManager()
  }
  
  // AuthManager is already initialized as singleton
  console.log('🔐 AuthManager ready for Windows Electron')
  
  // Integrate with Vue router
  router.afterEach((to, from) => {
    setTimeout(() => {
      window.inputManager?.enableAllInputs('vue-router-navigation')
      window.authManager?.enableAllInputs('router-afterEach')
    }, 200)
  })
  
  // Add global properties to Vue app
  app.config.globalProperties.$inputManager = window.inputManager
  app.config.globalProperties.$authManager = window.authManager
  
  // Provide as injectables
  app.provide('inputManager', window.inputManager)
  app.provide('authManager', window.authManager)
}

app.mount('#app')
