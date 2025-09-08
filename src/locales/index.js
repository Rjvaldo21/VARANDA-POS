import { createI18n } from 'vue-i18n'
import en from './en.json'
import pt from './pt.json'

const messages = {
  en,
  pt
}

// Get saved language from localStorage or default to Portuguese
const savedLocale = localStorage.getItem('locale') || 'pt'

const i18n = createI18n({
  locale: savedLocale,
  fallbackLocale: 'pt',
  messages,
  legacy: false,
  globalInjection: true
})

export default i18n