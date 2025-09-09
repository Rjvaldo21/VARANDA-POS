import { createI18n } from 'vue-i18n'
import en from './en.json'
import pt from './pt.json'
import tet from './tet.json'

const messages = {
  en,
  pt,
  tet
}

// Get saved language from localStorage or default to Tetum
const savedLocale = localStorage.getItem('locale') || 'tet'

const i18n = createI18n({
  locale: savedLocale,
  fallbackLocale: 'tet',
  messages,
  legacy: false,
  globalInjection: true
})

export default i18n