<template>
  <footer class="bg-gray-100 border-t border-gray-300 text-sm text-gray-500 py-2 mt-auto px-4 flex justify-between">
    <div>{{ currentDate }}</div>
    <div>👤 {{ username }} <span v-if="role">— {{ role }}</span></div>
  </footer>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { jwtDecode } from 'jwt-decode'

const currentDate = ref('')
const username = ref('')
const role = ref('')

function updateDate() {
  const now = new Date()
  const hari = ['Domingu','Segunda','Terca','Quarta','Quinta','Sesta','Sabadu']
  const bulan = ['Janeiru','Fevereiru','Marsu','Abril','Maiu','Junhu','Julhu','Agostu','Setembru','Outubru','Novembru','Dezembru']
  const formatted = `${hari[now.getDay()]}, ${now.getDate()} ${bulan[now.getMonth()]} ${now.getFullYear()} ${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  currentDate.value = formatted
}

onMounted(() => {
  updateDate()
  setInterval(updateDate, 60000)

  const token = localStorage.getItem('token')
  if (token) {
    try {
      const decoded = jwtDecode(token)
      username.value = decoded.username || 'Unknown'
      role.value = decoded.role || 'Unknown'
    } catch (err) {
      console.error('❌ Token invalid:', err)
    }
  }
})
</script>


