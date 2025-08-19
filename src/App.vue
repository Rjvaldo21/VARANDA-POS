<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Header from './components/Header.vue'
import Footer from './components/Footer.vue'

const route = useRoute()

const hideLayout = computed(() => {
  return ['/login', '/customer'].includes(route.path)
})

// onMounted(() => {
//   window.addEventListener('contextmenu', e => e.preventDefault())
// })
</script>

<template>
  <div id="app" class="flex flex-col min-h-screen">
    <Header v-if="!hideLayout" />
    <router-view class="flex-grow" />
    <Footer v-if="!hideLayout" />
  </div>
</template>
