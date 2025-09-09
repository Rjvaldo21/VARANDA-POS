<script setup>
import api, { baseURL } from '@/axios'
import { ref, computed, onMounted } from 'vue'
import FooterActions from '@/components/pos/FooterActions.vue'

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

const store = ref({
  name: '',
  address: '',
  logo: '',
  version: '',
  location: ''
})

const formatPrice = (value) => {
  const number = Number(value)
  return isNaN(number)
    ? '$0.00'
    : new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(number)
}

const formattedAddress = computed(() => store.value.address.replace(/\n/g, '<br />'))

const todayFormatted = new Date().toLocaleDateString('en-GB')

const totalNet = ref(0)        
const breakdown = ref(null)     
const rows = ref([])            

const toDate = (s) => (s ? s.slice(0, 10) : '')

const fetchFinanceSummary = async () => {
  try {
    const params = {}
    if (startDate.value && endDate.value) {
      params.date_from = toDate(startDate.value)
      params.date_to   = toDate(endDate.value)
    }
    const { data } = await api.get(
      'finance/summary/',
      { params, headers: { ...authHeader() } }   
    )
    totalNet.value = Number(data?.total_net) || 0
    breakdown.value = data?.breakdown || null
  } catch (e) {
    console.error('Gagal fetch finance/summary:', e)
  }
}

const fetchFinanceEntries = async () => {
  try {
    const params = {}
    if (startDate.value && endDate.value) {
      params.date_from = toDate(startDate.value)
      params.date_to   = toDate(endDate.value)
    }
    const { data } = await api.get(
      'finance/entries/',
      { params, headers: { ...authHeader() } }   
    )
    rows.value = data?.results || data || []
  } catch (e) {
    console.error('Gagal fetch finance/entries:', e)
  }
}

const refresh = async () => {
  await Promise.all([fetchFinanceSummary(), fetchFinanceEntries()])
}

const handleFilterChange = async (e) => {
  const value = e.target.value
  if (value === '') {
    showDatePopup.value = true
  } else if (value === 'today') {
    const today = new Date().toISOString().slice(0, 10)
    startDate.value = today
    endDate.value = today
    showDatePopup.value = false
    await refresh()
  }
}

const applyManualDateFilter = async () => {
  startDate.value = manualStart.value
  endDate.value = manualEnd.value
  showDatePopup.value = false
  await refresh()
}


const filteredRows = computed(() => {
  const f = filter.value
  return rows.value.filter(r => {
    if (f.tipe === 'masuk'  && Number(r.amount_signed) < 0) return false
    if (f.tipe === 'keluar' && Number(r.amount_signed) > 0) return false

    if (f.nomor && !(r.number || '').toLowerCase().includes(f.nomor.toLowerCase())) return false
    if (f.detil && !(r.note || '').toLowerCase().includes(f.detil.toLowerCase())) return false
    return true
  })
})

onMounted(async () => {
  try {
    const res = await api.get('store-profile/')
    if (res.data && res.data.length > 0) {
      store.value = res.data[0]
      console.log('Logo URL:', getLogoUrl(store.value.logo))
    }
  } catch (err) {
    console.error('Gagal fetch store profile:', err)
  }

  const today = new Date().toISOString().slice(0, 10)
  startDate.value = today
  endDate.value = today
  await refresh()
})

const getLogoUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `${baseURL.replace("/api/", "")}${path}`
}

defineOptions({ inheritAttrs: false })

const startDate = ref('')
const endDate = ref('')

const filter = ref({
  tipe: '',
  nomor: '',
  banku: '',
  mesin: '',
  pengguna: '',
  detil: '',
})

const perPage = ref(10)

const showDatePopup = ref(false)
const manualStart = ref('')
const manualEnd = ref('')

// New UI functions
const clearFilters = () => {
  filter.value = {
    tipe: '',
    nomor: '',
    banku: '',
    mesin: '',
    pengguna: '',
    detil: ''
  }
  startDate.value = ''
  endDate.value = ''
}

const exportData = () => {
  const headers = ['Date','Type','Number','Bank','Computer','User','Details','Amount']
  const csvData = filteredRows.value.map(row => [
    row.entry_date || '',
    row.entry_type || '',
    row.number || '',
    'N/A', // Bank info not available
    'N/A', // Computer info not available  
    'N/A', // User info not available
    row.note || '',
    row.amount_signed || 0
  ])
  
  const csv = [headers.join(','), ...csvData.map(row => row.join(','))].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'finance_report.csv'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const viewEntry = (entry) => {
  alert(`View finance entry details for: ${entry?.number || 'Unknown Entry'}`)
}

const editEntry = (entry) => {
  alert(`Edit finance entry: ${entry?.number || 'Unknown Entry'}`)
}

// Summary computed properties
const totalEntries = computed(() => filteredRows.value.length)
const totalIncome = computed(() => 
  filteredRows.value
    .filter(r => Number(r.amount_signed) > 0)
    .reduce((sum, r) => sum + Number(r.amount_signed), 0)
)
const totalExpenses = computed(() => 
  filteredRows.value
    .filter(r => Number(r.amount_signed) < 0)
    .reduce((sum, r) => sum + Math.abs(Number(r.amount_signed)), 0)
)
const netBalance = computed(() => totalIncome.value - totalExpenses.value)

</script>


<template>
  <div
    class="bg-white border border-gray-200 rounded-lg shadow-sm text-sm flex flex-col h-full"
    v-bind="$attrs"
  >
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b border-gray-300 bg-gradient-to-r from-emerald-50 to-teal-50">
      <div class="flex items-center gap-3">
        <img
          :src="store.logo_base64 || getLogoUrl(store.logo)"
          @error="e => e.target.src = baseURL.replace('/api/', '') + '/media/logos/default.jpg'"
          class="h-8 w-8 rounded-lg shadow-sm"
        />
        <div>
          <h1 class="text-xl font-bold text-gray-800">💰 Finance Report</h1>
          <p class="text-sm text-gray-600">Financial entries and account summary</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button @click="exportData" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg shadow-sm transition-colors">
          <span class="text-sm font-medium">📊 Export Report</span>
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="p-4 bg-gray-50 border-b border-gray-200">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <!-- Total Entries Card -->
        <div class="bg-gradient-to-r from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-blue-600">Total Entries</p>
              <p class="text-xl font-bold text-blue-800">{{ totalEntries }}</p>
            </div>
            <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <span class="text-blue-600 text-lg">📝</span>
            </div>
          </div>
        </div>
        
        <!-- Total Income Card -->
        <div class="bg-gradient-to-r from-green-50 to-green-100 border border-green-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-green-600">Total Income</p>
              <p class="text-xl font-bold text-green-800">{{ formatPrice(totalIncome) }}</p>
            </div>
            <div class="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
              <span class="text-green-600 text-lg">📈</span>
            </div>
          </div>
        </div>

        <!-- Total Expenses Card -->
        <div class="bg-gradient-to-r from-red-50 to-red-100 border border-red-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-red-600">Total Expenses</p>
              <p class="text-xl font-bold text-red-800">{{ formatPrice(totalExpenses) }}</p>
            </div>
            <div class="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
              <span class="text-red-600 text-lg">📉</span>
            </div>
          </div>
        </div>

        <!-- Net Balance Card -->
        <div class="bg-gradient-to-r from-purple-50 to-purple-100 border border-purple-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-purple-600">Net Balance</p>
              <p class="text-xl font-bold" :class="netBalance >= 0 ? 'text-green-800' : 'text-red-800'">
                {{ formatPrice(netBalance) }}
              </p>
            </div>
            <div class="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
              <span class="text-purple-600 text-lg">⚖️</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="p-4 bg-white border-b border-gray-200">
      <div class="flex flex-wrap items-center gap-3">
        <div class="min-w-[160px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Date Range</label>
          <select @change="handleFilterChange($event)" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent">
            <option value="today">📅 Today</option>
            <option value="">🗓️ Custom Range</option>
          </select>
        </div>
        
        <div class="min-w-[140px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Entry Type</label>
          <select v-model="filter.tipe" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent">
            <option value="">All Types</option>
            <option value="masuk">Income</option>
            <option value="keluar">Expense</option>
          </select>
        </div>
        
        <div class="min-w-[160px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Entry Number</label>
          <input 
            v-model="filter.nomor" 
            type="text" 
            placeholder="Enter number..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
          />
        </div>
        
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Search Details</label>
          <input 
            v-model="filter.detil" 
            type="text" 
            placeholder="Enter details..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
          />
        </div>

        <div class="flex items-end gap-2">
          <button @click="clearFilters" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
            Clear Filters
          </button>
          <button @click="refresh" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg transition-colors">
            🔄 Refresh
          </button>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="p-4 flex flex-col flex-1 overflow-hidden">

      <!-- Table -->
      <div class="bg-white rounded-lg border border-gray-200 overflow-hidden shadow-sm">
        <div class="overflow-x-auto">
          <table class="w-full border-collapse">
            <thead class="bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Date</th>
                <th class="px-4 py-3 text-center text-xs font-semibold text-gray-700 uppercase tracking-wider">Type</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Number</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Details</th>
                <th class="px-4 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">Amount</th>
                <th class="px-4 py-3 text-center text-xs font-semibold text-gray-700 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>

            <tbody class="divide-y divide-gray-200">
              <tr v-if="filteredRows.length === 0">
                <td colspan="6" class="px-4 py-12 text-center text-gray-500">
                  <div class="flex flex-col items-center">
                    <span class="text-4xl mb-2">💰</span>
                    <p class="text-lg font-medium mb-1">No finance entries found</p>
                    <p class="text-sm">Try adjusting your date range or filters</p>
                  </div>
                </td>
              </tr>

              <tr v-else v-for="(r, i) in filteredRows" :key="i" class="hover:bg-gray-50 transition-colors">
                <td class="px-4 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">{{ r.entry_date || 'N/A' }}</div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap text-center">
                  <span 
                    class="inline-flex px-2 py-1 text-xs font-medium rounded-full"
                    :class="{
                      'bg-green-100 text-green-800': r.entry_type?.toLowerCase() === 'income' || Number(r.amount_signed) > 0,
                      'bg-red-100 text-red-800': r.entry_type?.toLowerCase() === 'expense' || Number(r.amount_signed) < 0,
                      'bg-gray-100 text-gray-800': !r.entry_type
                    }"
                  >
                    {{ r.entry_type || 'Unknown' }}
                  </span>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900">{{ r.number || 'N/A' }}</div>
                </td>
                
                <td class="px-4 py-4">
                  <div class="text-sm text-gray-900 max-w-xs truncate" :title="r.note">
                    {{ r.note || 'No details' }}
                  </div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap text-right">
                  <div class="text-sm font-bold" 
                       :class="Number(r.amount_signed) >= 0 ? 'text-green-600' : 'text-red-600'">
                    {{ formatPrice(r.amount_signed) }}
                  </div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap text-center">
                  <div class="flex items-center justify-center space-x-2">
                    <button 
                      @click="viewEntry(r)"
                      class="text-blue-600 hover:text-blue-800 font-medium text-sm"
                      title="View Details"
                    >
                      👁️
                    </button>
                    <button 
                      @click="editEntry(r)"
                      class="text-yellow-600 hover:text-yellow-800 font-medium text-sm"
                      title="Edit Entry"
                    >
                      ✏️
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <!-- Custom Date Range Modal -->
      <div v-if="showDatePopup" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
          <div class="flex items-center justify-between p-6 border-b border-gray-200">
            <h3 class="text-lg font-semibold text-gray-900">Select Date Range</h3>
            <button @click="showDatePopup = false" class="text-gray-400 hover:text-gray-600 transition-colors">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
          
          <div class="p-6">
            <div class="grid grid-cols-1 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                <input 
                  v-model="manualStart" 
                  type="datetime-local" 
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent" 
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                <input 
                  v-model="manualEnd" 
                  type="datetime-local" 
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent" 
                />
              </div>
            </div>
          </div>
          
          <div class="flex items-center justify-end p-6 border-t border-gray-200 space-x-3">
            <button 
              @click="showDatePopup = false" 
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition-colors"
            >
              Cancel
            </button>
            <button 
              @click="applyManualDateFilter" 
              class="px-4 py-2 text-sm font-medium text-white bg-emerald-600 border border-transparent rounded-lg hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition-colors"
            >
              Apply Filter
            </button>
          </div>
        </div>
      </div>

      <!-- Pagination Footer -->
      <div class="flex justify-between items-center mt-4 px-4 py-3 bg-gray-50 border-t border-gray-200 rounded-b-lg">
        <div class="flex items-center gap-2">
          <span class="text-sm text-gray-700">Show:</span>
          <select v-model="perPage" class="px-2 py-1 border border-gray-300 rounded-md text-sm">
            <option v-for="n in [10, 20, 50, 100]" :key="n" :value="n">{{ n }} per page</option>
          </select>
        </div>
        <div class="text-sm text-gray-700">
          Showing {{ filteredRows.length }} entr{{ filteredRows.length !== 1 ? 'ies' : 'y' }}
        </div>
      </div>
    </div>
  </div>
  <FooterActions />
</template>

<style scoped>
/* Modern utility styles */
.transition-colors {
  transition-property: color, background-color, border-color;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

.transition-shadow {
  transition-property: box-shadow;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

/* Custom focus states */
input:focus,
select:focus {
  outline: 2px solid transparent;
  outline-offset: 2px;
  --tw-ring-offset-shadow: var(--tw-ring-inset) 0 0 0 var(--tw-ring-offset-width) var(--tw-ring-offset-color);
  --tw-ring-shadow: var(--tw-ring-inset) 0 0 0 calc(2px + var(--tw-ring-offset-width)) var(--tw-ring-color);
  box-shadow: var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow, 0 0 #0000);
  --tw-ring-color: rgb(16 185 129 / 0.5);
  border-color: transparent;
}

/* Table improvements */
table {
  border-collapse: collapse;
  font-variant-numeric: tabular-nums;
}

/* Hover effects */
.hover\:shadow-md:hover {
  --tw-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --tw-shadow-colored: 0 4px 6px -1px var(--tw-shadow-color), 0 2px 4px -2px var(--tw-shadow-color);
  box-shadow: var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000), var(--tw-shadow);
}
</style>
