<template>
  <div class="language-switcher">
    <select 
      v-model="currentLocale" 
      @change="changeLanguage"
      class="bg-white border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
    >
      <option value="pt">🇹🇱 Português/Tetum</option>
      <option value="en">🇺🇸 English</option>
    </select>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()
const currentLocale = ref(locale.value)

const changeLanguage = () => {
  locale.value = currentLocale.value
  localStorage.setItem('locale', currentLocale.value)
  console.log('Language changed to:', currentLocale.value)
}

onMounted(() => {
  // Get saved language from localStorage
  const savedLocale = localStorage.getItem('locale')
  if (savedLocale) {
    currentLocale.value = savedLocale
    locale.value = savedLocale
  } else {
    currentLocale.value = locale.value
  }
  console.log('Current locale on mount:', currentLocale.value)
})
</script>

<style scoped>
.language-switcher {
  display: inline-block;
}
</style>