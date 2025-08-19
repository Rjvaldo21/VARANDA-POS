<script setup>
import axios from 'axios'
import { ref, computed, onMounted } from 'vue'
import FooterActions from '@/components/pos/FooterActions.vue'

const store = ref({
  name: '',
  address: '',
  logo: '',
  version: '',
  location: ''
})

const todayFormatted = new Date().toLocaleDateString('en-GB')

const showDatePopup = ref(false)
const manualStart = ref('')
const manualEnd = ref('')


const authHeader = () => {
  const t =
    localStorage.getItem('access') ||
    localStorage.getItem('token')  ||
    sessionStorage.getItem('access') ||
    sessionStorage.getItem('token')
  if (!t) return {}
  if (t.startsWith('ey')) return { Authorization: `Bearer ${t}` } 
  if (t.startsWith('Token ')) return { Authorization: t }        
  return { Authorization: `Token ${t}` }                              
}

const formatUSD = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2
  }).format(value)
}

const applyManualDateFilter = () => {
  filter.value.tanggal_awal = manualStart.value
  filter.value.tanggal_akhir = manualEnd.value
  showDatePopup.value = false
  refreshByCurrentFilter()
}


const handleFilterChange = (e) => {
  const value = e.target.value
  if (value === '') {
    showDatePopup.value = true
  } else {
    applyQuickFilter(value)
  }
}

const applyQuickFilter = (range) => {
  const now = new Date()
  const isoNow = now.toISOString().slice(0, 10)

  if (range === 'today') {
    filter.value.tanggal_awal = isoNow
    filter.value.tanggal_akhir = isoNow
  } else if (range === 'week') {
    const start = new Date(now)
    start.setDate(now.getDate() - 6)
    filter.value.tanggal_awal = start.toISOString().slice(0, 10)
    filter.value.tanggal_akhir = isoNow
  } else if (range === 'month') {
    const start = new Date(now.getFullYear(), now.getMonth(), 1)
    filter.value.tanggal_awal = start.toISOString().slice(0, 10)
    filter.value.tanggal_akhir = isoNow
  }
  refreshByCurrentFilter() 
} 

const formattedAddress = computed(() => store.value.address.replace(/\n/g, '<br />'))

onMounted(async () => {
  try {
    const res = await axios.get('http://localhost:8000/api/store-profile/')
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

const totalPenjualanAPI = ref(0)

onMounted(() => {
  refreshByCurrentFilter()
})


const normalizeMoney = (val) => {
  if (val == null) return 0
  if (typeof val === 'number' && Number.isFinite(val)) return val
  if (typeof val === 'string') {
    const cleaned = val.replace(/[^0-9.\-]/g, '')
    const n = parseFloat(cleaned)
    return Number.isFinite(n) ? n : 0
  }
  const n = Number(val)
  return Number.isFinite(n) ? n : 0
}

const totalMarginAPI = ref(0)

const toDateOnly = (s) => (s ? s.slice(0, 10) : '')

const fetchSalesTotal = async ({ period, from, to } = {}) => {
  try {
    const params = {}
    if (from && to) {
      params.date_from = toDateOnly(from)
      params.date_to = toDateOnly(to)
    } else if (period) {
      params.period = period 
    } else {
      params.period = 'today'
    }

    const res = await axios.get(
      'http://127.0.0.1:8000/api/sales/total/',
      { params, headers: { ...authHeader() } } 
    )

    totalPenjualanAPI.value = normalizeMoney(res?.data?.totals?.total_sales)
    totalMarginAPI.value = normalizeMoney(res?.data?.margin?.gross_profit)
  } catch (err) {
    console.error('Gagal ambil /api/sales/total/:', err)
  }
}

const refreshByCurrentFilter = () => {
  const from = filter.value.tanggal_awal
  const to = filter.value.tanggal_akhir
  if (from && to) {
    fetchSalesTotal({ from, to })
  } else {
    fetchSalesTotal({ period: 'today' })
  }
}

const filter = ref({
  tanggal_awal: '',
  tanggal_akhir: '',
  barcode: '',
  nama: ''
})

const perPage = ref(10)

const items = ref([
  // {
  //   id: 1,
  //   tanggal: '2025-07-06 10:00',
  //   barcode: '12345678',
  //   nama: 'Contoh Produk',
  //   qty: 5,
  //   satuan: 'pcs',
  //   total: 50000,
  //   harga_beli: 30000,
  //   margin: 20000
  // }
])

const filteredData = computed(() =>
  items.value.filter(i =>
    (!filter.value.tanggal_awal || i.tanggal >= filter.value.tanggal_awal) &&
    (!filter.value.tanggal_akhir || i.tanggal <= filter.value.tanggal_akhir) &&
    i.barcode.toLowerCase().includes(filter.value.barcode.toLowerCase()) &&
    i.nama.toLowerCase().includes(filter.value.nama.toLowerCase())
  )
)

const totalPenjualan = computed(() =>
  filteredData.value.reduce((sum, i) => sum + i.total, 0)
)

const totalMargin = computed(() =>
  filteredData.value.reduce((sum, i) => sum + i.margin, 0)
)
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
      <h1 class="text-lg font-semibold">RELATORIU FA'AN</h1>
    </div>

    <!-- Summary -->
    <div class="flex gap-4 px-2 pt-3">
  <div class="border rounded-sm px-3 py-2 w-40 text-right">
    <div class="text-xs text-gray-500 text-left">Total Fa'an</div>
    <div class="text-lg font-bold">{{ formatUSD(totalPenjualanAPI) }}</div>
  </div>
  <div class="border rounded-sm px-3 py-2 w-40 text-right">
    <div class="text-xs text-gray-500 text-left">Marjen</div>
    <div class="text-lg font-bold">{{ formatUSD(totalMarginAPI) }}</div>
  </div>
</div>

    <!-- Table -->
    <div class="flex-1 overflow-auto border border-gray-300 mx-2 mt-2">
      <table class="w-full table-auto border-collapse text-sm">
        <thead class="bg-gradient-to-b from-white to-gray-100">
          <tr>
            <th class="border px-2 py-1 w-56 align-top">
              <select @change="handleFilterChange($event)" class="border px-2 py-1 text-sm rounded-sm w-full">
                <option :value="'today'">📅 {{ todayFormatted }}</option>
                <option value="">🗓️ Hili kalendariu</option>
              </select>
            </th>

            <th class="border px-2 py-1 w-32">
              <input v-model="filter.barcode" type="text" placeholder="Barcode"
                class="border px-1 py-0.5 rounded-sm w-full" />
            </th>
            <th class="border px-2 py-1 w-48">
              <input v-model="filter.nama" type="text" placeholder="Naran"
                class="border px-1 py-0.5 rounded-sm w-full" />
            </th>
            <th class="border px-2 py-1 text-right w-16">Qty</th>
            <th class="border px-2 py-1 text-right w-20">Unidade</th>
            <th class="border px-2 py-1 text-right w-24">Total</th>
            <th class="border px-2 py-1 text-right w-24">Presu Kompra</th>
            <th class="border px-2 py-1 text-right w-24">Margin</th>
          </tr>
        </thead>

        <!-- 📅 Modal Kalendariu Manual -->
          <div v-if="showDatePopup" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
            <div class="bg-white p-4 rounded shadow w-[300px]">
              <h2 class="text-sm font-semibold mb-2">Hili Data Manual</h2>
              <div class="mb-2">
                <label class="text-xs">Data Inísiu:</label>
                <input v-model="manualStart" type="datetime-local" class="border px-1 py-0.5 w-full rounded-sm" />
              </div>
              <div class="mb-2">
                <label class="text-xs">Data Final:</label>
                <input v-model="manualEnd" type="datetime-local" class="border px-1 py-0.5 w-full rounded-sm" />
              </div>
              <div class="flex justify-end gap-2 mt-2 text-xs">
                <button @click="showDatePopup = false" class="px-2 py-1 border rounded hover:bg-gray-100">Kansela</button>
                <button @click="applyManualDateFilter" class="px-2 py-1 border bg-blue-600 text-white rounded hover:bg-blue-700">
                  Ok
                </button>
              </div>
            </div>
          </div>

        <tbody>
          <tr v-for="item in filteredData" :key="item.id" class="hover:bg-gray-50">
            <td class="border px-2 py-1">{{ item.tanggal }}</td>
            <td class="border px-2 py-1">{{ item.barcode }}</td>
            <td class="border px-2 py-1">{{ item.nama }}</td>
            <td class="border px-2 py-1 text-right">{{ item.qty }}</td>
            <td class="border px-2 py-1 text-right">{{ item.satuan }}</td>
            <td class="border px-2 py-1 text-right">{{ item.total }}</td>
            <td class="border px-2 py-1 text-right">{{ item.harga_beli }}</td>
            <td class="border px-2 py-1 text-right">{{ item.margin }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Footer -->
    <div class="flex justify-between items-center mt-2 text-xs px-2 pb-2">
      <div>
        <select v-model="perPage" class="border px-1 py-0.5 rounded-sm">
          <option v-for="n in [10, 20, 50]" :key="n" :value="n">{{ n }}/pagina</option>
        </select>
      </div>
      <div class="space-x-2 text-base">
        <button @click="refresh" class="hover:text-blue-600">🔄</button>
        <button @click="downloadLaporan" class="hover:text-green-600">⬇</button>
      </div>
    </div>
  </div>
  <FooterActions />
</template>


<style scoped>
table {
  border-collapse: collapse;
}
th, td {
  font-size: 13px;
}
</style>
