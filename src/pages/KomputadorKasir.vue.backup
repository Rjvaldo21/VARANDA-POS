<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import FooterActions from '@/components/pos/FooterActions.vue'

const store = ref({
  name: '',
  address: '',
  logo: '',
  version: '',
  location: ''
})

const formattedAddress = computed(() =>
  store.value.address ? store.value.address.replace(/\n/g, '<br />') : ''
)

const getLogoUrl = (path) => {
  if (!path) return ''
  return path.startsWith('http') ? path : `http://localhost:8000${path}`
}

onMounted(async () => {
  try {
    const res = await axios.get('http://localhost:8000/api/store-profile/')
    if (res.data && res.data.length > 0) {
      store.value = res.data[0]
      console.log('Logo URL:', getLogoUrl(store.value.logo))
    }
  } catch (err) {
    console.error('Gagal fetch store profile:', err)
  }
})

// Mesin kasir (sementara hardcoded)
const mesinList = ref([
  { kode: 'Cashier 1', nama: 'Cashier 1' },
])

const perPage = ref(10)

// Aksi tombol
const refresh = () => console.log('Refresh')
const addMesin = () => console.log('Add')
const editMesin = () => console.log('Edit')
const deleteMesin = () => console.log('Delete')
</script>

<style scoped>
table {
  border-collapse: collapse;
}
th, td {
  font-size: 13px;
}
</style>


<template>
  <div class="bg-white border border-gray-50 rounded-sm shadow text-sm flex flex-col h-full">
    <!-- Header -->
    <div class="flex items-center gap-2 p-2 border-b border-gray-300 bg-gray-50">
      <img
        :src="store.logo_base64 || getLogoUrl(store.logo)"
        @error="e => e.target.src = 'http://127.0.0.1:8000/media/logos/default.jpg'"
        class="h-6 w-6 rounded"
      />
      <h1 class="text-lg font-semibold">KOMPUTADOR</h1>
    </div>

    <!-- Table -->
    <div class="p-2 flex flex-col flex-1 overflow-hidden">
      <div class="flex-1 overflow-x-auto border border-gray-300">
        <table class="min-w-[400px] w-full border-collapse text-sm table-fixed">
          <thead class="bg-gradient-to-b from-white to-gray-100">
            <tr>
              <th class="border border-gray-300 px-2 py-1 text-left w-[30%]">Kodigu</th>
              <th class="border border-gray-300 px-2 py-1 text-left">Naran</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="mesin in mesinList" :key="mesin.kode" class="hover:bg-gray-50">
              <td class="border border-gray-300 px-2 py-1">{{ mesin.kode }}</td>
              <td class="border border-gray-300 px-2 py-1 flex justify-between items-center">
                {{ mesin.nama }}
                <span class="space-x-2 text-base">
                  <button @click="editMesin(mesin)" class="hover:text-gray-600">✏️</button>
                  <button @click="deleteMesin(mesin)" class="hover:text-red-600">❌</button>
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Footer -->
      <div class="flex justify-between items-center mt-2 text-xs">
        <!-- Pagination -->
        <div>
          <select v-model="perPage" class="border px-1 py-0.5 rounded-sm">
            <option v-for="n in [10, 20, 50]" :key="n" :value="n">{{ n }}/pagina</option>
          </select>
        </div>
        <!-- Action Buttons -->
        <div class="space-x-2 text-base">
          <button @click="refresh" class="hover:text-blue-600">🔄</button>
          <button @click="addMesin" class="hover:text-green-600">➕</button>
        </div>
      </div>
    </div>
  </div>
  <FooterActions />
</template>
