<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import FooterActions from '@/components/pos/FooterActions.vue'

const store = ref({
  name: '',
  address: '',
  logo: '',
  logo_base64: '',
  version: '',
  location: ''
})

const stocks = ref([])
const selectedStock = ref(null)
const perPage = ref(10)
const isLoading = ref(true)
const filter = ref({ warehouse: '', product: '', barcode: '' })

const getLogoUrl = (path) => {
  if (!path) return ''
  return path.startsWith('http') ? path : `http://localhost:8000${path}`
}

const fetchStoreProfile = async () => {
  try {
    const res = await axios.get('http://localhost:8000/api/store-profile/')
    if (res.data && res.data.length > 0) {
      store.value = res.data[0]
    }
  } catch (err) {
    console.error('❌ Gagal fetch profil loja:', err)
  }
}

const fetchStockData = async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get('http://localhost:8000/api/stocks/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    stocks.value = res.data
  } catch (err) {
    console.error('❌ Gagal fetch stok gudang:', err)
  }
}

const refresh = async () => {
  await fetchStockData()
  alert('🔄 Dadus Stok atualiza ona')
}

const filteredStock = computed(() => {
  return stocks.value.filter(item =>
    item.warehouse_name.toLowerCase().includes(filter.value.warehouse.toLowerCase())&&
    item.product_name.toLowerCase().includes(filter.value.product.toLowerCase()) &&
    item.barcode.toLowerCase().includes(filter.value.barcode.toLowerCase())
  )
})

onMounted(async () => {
  isLoading.value = true
  await fetchStoreProfile()
  await fetchStockData()
  isLoading.value = false
})
</script>

<template>
  <div class="bg-white border border-gray-50 rounded-sm shadow text-sm flex flex-col h-full">
    <!-- Header -->
    <div class="flex items-center gap-2 p-2 border-b border-gray-300 bg-gray-50">
      <img
        :src="store.logo_base64 || getLogoUrl(store.logo)"
        @error="e => e.target.src = 'http://127.0.0.1:8000/media/logos/default.jpg'"
        class="h-6 w-6 rounded"
      />
      <h1 class="text-lg font-semibold">STOK ARMAZÉN</h1>
    </div>

    <!-- Table + Filter -->
    <div class="p-2 flex-1 overflow-hidden flex flex-col">
      <div class="flex-1 overflow-x-auto border border-gray-300 rounded-sm">
        <table class="min-w-[1000px] w-full border-collapse text-sm table-fixed">
          <thead class="bg-gradient-to-b from-white to-gray-100">
            <tr>
              <th class="border px-2 py-1 text-left">Armazén</th>
              <th class="border px-2 py-1 text-left">Produtu</th>
              <th class="border px-2 py-1 text-left">SKU / Barcode</th>
              <th class="border px-2 py-1 text-left">Kategoria</th>
              <th class="border px-2 py-1 text-left">Unidade</th>
              <th class="border px-2 py-1 text-right">Stok Atual</th>
              <th class="border px-2 py-1 text-right">Stok Mínimu</th>
            </tr>
            <!-- Filter -->
            <tr>
              <th class="border px-2 py-1">
                <input v-model="filter.warehouse" placeholder="Armazén" class="w-full px-2 py-1 border rounded-sm" />
              </th>
              <th class="border px-2 py-1">
                <input v-model="filter.product" placeholder="Produtu" class="w-full px-2 py-1 border rounded-sm" />
              </th>
              <th class="border px-2 py-1">
                <input v-model="filter.barcode" placeholder="SKU / Barcode" class="w-full px-2 py-1 border rounded-sm" />
              </th>
              <th colspan="4" class="border px-2 py-1"></th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in filteredStock"
              :key="item.id"
              class="hover:bg-gray-50"
              :class="{ 'bg-yellow-100': selectedStock?.id === item.id }"
              @click="selectedStock = item"
            >
              <td class="border px-2 py-1">{{ item.warehouse_name }}</td>
              <td class="border px-2 py-1">{{ item.product_name }}</td>
              <td class="border px-2 py-1">{{ item.barcode }}</td>
              <td class="border px-2 py-1">{{ item.category }}</td>
              <td class="border px-2 py-1">{{ item.unit }}</td>
              <td class="border px-2 py-1 text-right">{{ item.current_stock }}</td>
              <td class="border px-2 py-1 text-right">{{ item.min_stock }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Loading -->
      <div v-if="isLoading" class="flex justify-center items-center h-full mt-4">
        <div class="text-center space-y-2">
          <svg class="animate-spin h-6 w-6 text-gray-500 mx-auto" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
          </svg>
          <p>Loading data...</p>
        </div>
      </div>

      <!-- Footer -->
      <div class="flex justify-between items-center mt-2 text-xs">
        <div>
          <select v-model="perPage" class="border px-1 py-0.5 rounded-sm">
            <option v-for="n in [10, 20, 50]" :key="n" :value="n">{{ n }}/pagina</option>
          </select>
        </div>
        <div class="space-x-2 text-base">
          <button @click="refresh" class="hover:text-blue-600">🔄</button>
        </div>
      </div>
    </div>
  </div>
  <FooterActions />
</template>


<style scoped>
table {
  border-collapse: collapse;
}
th,
td {
  font-size: 13px;
}
tr.bg-yellow-100 {
  background-color: #fef9c3;
}
</style>
