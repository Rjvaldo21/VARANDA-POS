import './style.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import i18n from './locales'
import InputManager from './utils/inputManager.js'
import { InputManagerPlugin } from './plugins/inputManager.js'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(i18n)
app.use(InputManagerPlugin)

// Initialize InputManager for Windows Electron input fix
if (window.electronAPI && navigator.platform.includes('Win')) {
  console.log('🔧 Initializing InputManager for Windows Electron')
  
  // Create global instance
  if (!window.inputManager) {
    window.inputManager = new InputManager()
  }
  
  // Integrate with Vue router
  router.afterEach((to, from) => {
    setTimeout(() => {
      window.inputManager?.enableAllInputs('vue-router-navigation')
    }, 200)
  })
  
  // Add global property to Vue app
  app.config.globalProperties.$inputManager = window.inputManager
  
  // Provide as injectable
  app.provide('inputManager', window.inputManager)
}

app.mount('#app')
