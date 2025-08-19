<template>
  <div class="flex flex-col items-center justify-center h-screen bg-white text-center">
    <h1 class="text-xl font-bold mb-4">SCAN QRIS MOSAN</h1>
    
    <!-- ✅ Tampilkan QR hanya jika data lengkap -->
    <div v-if="qrisData?.qrisUrl && qrisData.qrisUrl.length > 5">

      <p class="text-sm text-gray-600 mb-2">Invoice: {{ qrisData.invoice }}</p>
      <img
        :src="`https://api.qrserver.com/v1/create-qr-code/?data=${qrisData.qrisUrl}&size=200x200`"
        alt="QRIS"
        class="border p-2 bg-white"
      />
      <p class="mt-2 font-semibold text-lg">{{ formatCurrency(qrisData.total || 0) }}</p>
    </div>

    <!-- ❌ Jika data kosong, tampilkan fallback video -->
    <div v-else>
      <p class="text-sm text-gray-600 mb-2">No QRIS data available</p>
      <iframe 
        width="320" 
        height="240" 
        src="https://www.youtube.com/embed/8JMMjCyyznI?si=gsM2q4CZmrqREV5l" 
        frameborder="0" 
        allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" 
        allowfullscreen>
      </iframe>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const qrisData = ref(null)

onMounted(() => {
  const data = localStorage.getItem('qrisPayment')
  if (data) {
    qrisData.value = JSON.parse(data)
    console.log('✅ Loaded qrisData:', qrisData.value)
  } else {
    console.log('❌ No qrisPayment in localStorage')
  }
})


function formatCurrency(amount) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}
</script>
