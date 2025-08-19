<script setup>
import { onMounted, ref, computed } from 'vue'
import api from '@/axios'

const store = ref({
  name: '',
  address: '',
  logo: '',
  version: '',
  location: ''
})

const formattedAddress = computed(() => store.value.address.replace(/\n/g, '<br />'))

onMounted(async () => {
  try {
    const res = await api.get('store-profile/')
    if (res.data && res.data.length > 0) {
      store.value = res.data[0]
      console.log('Logo URL:', getLogoUrl(store.value.logo))
    }
  } catch (err) {
    console.error('Gagal fetch store profile:', err)
    console.log('store.logo:', store.value.logo)
  }
})

const getLogoUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `http://localhost:8000${path}`
}

</script>


<template>
  <div class="flex items-center bg-white h-[80px] md:h-[100px] p-3 shadow border rounded">
    <!-- Logo + Versi -->
    <div class="flex flex-col items-center justify-between h-full">
      <img
        :src="store.logo ? getLogoUrl(store.logo) : 'http://localhost:8000/media/logos/default.jpg'"
        alt="Logo"
        class="h-12 w-12 md:h-14 md:w-14 rounded-md"
      />
      <span class="text-[10px] text-gray-600 mt-1">{{ store.version }}</span>
    </div>
    <div class="border-l h-full mx-3"></div>

    <!-- Info toko -->
    <div class="leading-tight">
      <h1 class="text-xl md:text-2xl font-bold">{{ store.name }}</h1>
      <p class="text-xs md:text-sm text-gray-600" v-html="formattedAddress"></p>
      <p class="text-xs md:text-sm text-gray-600 mt-1">{{ store.location }}</p>
    </div>
  </div>
</template>
