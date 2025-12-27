<script setup>
import api, { baseURL } from '@/axios'
import { ref, computed, onMounted, nextTick } from 'vue'
import FooterActions from '@/components/pos/FooterActions.vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

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
  return `${baseURL.replace("/api/", "")}${path}`
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

    const res = await api.get(
      'sales/total/',
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
  <div class="bg-white border border-gray-200 rounded-sm shadow text-sm flex flex-col h-full">
    <!-- Header -->
    <div class="flex items-center gap-2 p-2 border-b border-gray-300 bg-gray-50">
      <img
        :src="store.logo_base64 || getLogoUrl(store.logo)"
        @error="e => e.target.src = baseURL.replace('/api/', '') + '/media/logos/default.jpg'"
        class="h-6 w-6 rounded"
      />
      <h1 class="text-lg font-semibold">SALES REPORT</h1>
    </div>

    <div class="p-4">
      <!-- Summary Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div class="bg-gradient-to-r from-blue-50 to-blue-100 border border-blue-200 rounded-lg px-4 py-3">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-sm font-medium text-blue-600">Total Sales</div>
              <div class="text-2xl font-bold text-blue-900">{{ formatUSD(totalPenjualanAPI) }}</div>
            </div>
            <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
              </svg>
            </div>
          </div>
        </div>
        
        <div class="bg-gradient-to-r from-green-50 to-green-100 border border-green-200 rounded-lg px-4 py-3">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-sm font-medium text-green-600">Profit Margin</div>
              <div class="text-2xl font-bold text-green-900">{{ formatUSD(totalMarginAPI) }}</div>
            </div>
            <div class="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
              </svg>
            </div>
          </div>
        </div>
        
        <div class="bg-gradient-to-r from-purple-50 to-purple-100 border border-purple-200 rounded-lg px-4 py-3">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-sm font-medium text-purple-600">Transactions</div>
              <div class="text-2xl font-bold text-purple-900">{{ filteredData.length }}</div>
            </div>
            <div class="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
              </svg>
            </div>
          </div>
        </div>
        
        <div class="bg-gradient-to-r from-orange-50 to-orange-100 border border-orange-200 rounded-lg px-4 py-3">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-sm font-medium text-orange-600">Average Sale</div>
              <div class="text-2xl font-bold text-orange-900">{{ filteredData.length > 0 ? formatUSD(totalPenjualan / filteredData.length) : '$0.00' }}</div>
            </div>
            <div class="w-10 h-10 bg-orange-100 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="mb-6 flex flex-wrap items-center gap-4">
        <div class="form-group mb-0">
          <label class="block text-sm font-medium text-gray-700 mb-1">Date Range</label>
          <select @change="handleFilterChange($event)" class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent">
            <option :value="'today'">📅 {{ todayFormatted }}</option>
            <option value="">🗓️ Custom Date Range</option>
          </select>
        </div>
        <div class="form-group mb-0">
          <label class="block text-sm font-medium text-gray-700 mb-1">Barcode</label>
          <input 
            v-model="filter.barcode" 
            class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
            placeholder="Search by barcode..."
          />
        </div>
        <div class="form-group mb-0">
          <label class="block text-sm font-medium text-gray-700 mb-1">Product Name</label>
          <input 
            v-model="filter.nama" 
            class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
            placeholder="Search by product name..."
          />
        </div>
      </div>

      <!-- Sales Table -->
      <div class="overflow-x-auto border border-gray-300 rounded-lg">
        <table class="w-full border-collapse text-sm">
          <thead class="bg-gray-50">
            <tr>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Date</th>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Product</th>
              <th class="border-b border-gray-200 px-4 py-3 text-right font-medium text-gray-700">Qty</th>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Unit</th>
              <th class="border-b border-gray-200 px-4 py-3 text-right font-medium text-gray-700">Cost Price</th>
              <th class="border-b border-gray-200 px-4 py-3 text-right font-medium text-gray-700">Total</th>
              <th class="border-b border-gray-200 px-4 py-3 text-right font-medium text-gray-700">Margin</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="item in filteredData" :key="item.id" class="hover:bg-gray-50">
              <td class="px-4 py-3 text-sm text-gray-900">{{ item.tanggal }}</td>
              <td class="px-4 py-3">
                <div class="font-medium text-gray-900">{{ item.nama }}</div>
                <div class="text-sm text-gray-500">{{ item.barcode }}</div>
              </td>
              <td class="px-4 py-3 text-sm text-gray-900 text-right">{{ item.qty }}</td>
              <td class="px-4 py-3 text-sm text-gray-900">{{ item.satuan }}</td>
              <td class="px-4 py-3 text-sm text-gray-900 text-right font-medium">{{ formatUSD(item.harga_beli) }}</td>
              <td class="px-4 py-3 text-sm text-gray-900 text-right font-bold">{{ formatUSD(item.total) }}</td>
              <td class="px-4 py-3 text-sm text-right">
                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                      :class="item.margin >= 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                  {{ formatUSD(item.margin) }}
                </span>
              </td>
            </tr>
            <tr v-if="filteredData.length === 0" class="hover:bg-gray-50">
              <td colspan="7" class="px-4 py-8 text-center text-gray-500">
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                </svg>
                <p class="mt-2">No sales data found for the selected criteria</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>

    <!-- Custom Date Range Modal -->
    <div v-if="showDatePopup" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <!-- Header -->
        <div class="flex items-center justify-between p-6 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">Custom Date Range</h3>
          <button @click="showDatePopup = false" class="text-gray-400 hover:text-gray-600 transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        
        <!-- Form -->
        <div class="p-6">
          <div class="grid grid-cols-1 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
              <input 
                v-model="manualStart" 
                type="datetime-local" 
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
              <input 
                v-model="manualEnd" 
                type="datetime-local" 
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
              />
            </div>
          </div>
        </div>
        
        <!-- Actions -->
        <div class="flex items-center justify-end p-6 border-t border-gray-200 space-x-3">
          <button 
            @click="showDatePopup = false" 
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
          >
            Cancel
          </button>
          <button 
            @click="applyManualDateFilter" 
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
          >
            Apply Filter
          </button>
        </div>
      </div>
    </div>

  <FooterActions />
</template>


<style scoped>
th,
td {
  font-size: 13px;
  padding: 6px 8px;
  border: 1px solid #d1d5db;
}

.th {
  text-align: left;
  background: #f9fafb;
  font-weight: 600;
  white-space: normal; 
  word-break: break-word;
}

.td {
  font-size: 13px;
}
</style>

