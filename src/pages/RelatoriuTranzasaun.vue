<script setup>
import api, { baseURL } from '@/axios'
import { ref, computed, onMounted, watch } from 'vue'
import FooterActions from '@/components/pos/FooterActions.vue'

const store = ref({
  name: '',
  address: '',
  logo: '',
  version: '',
  location: ''
})

const summary = ref({
  gross_income: 0,
  expenses: 0,
  gross_minus_expenses: 0,
  net_income: 0,
  profit_or_loss: 0
})

const todayFormatted = new Date().toLocaleDateString('en-GB')
const startDate = ref('')
const endDate = ref('')

const filter = ref({
  tipe: '',
  nomor: '',
  detil: '',
})

const props = defineProps({
  class: {
    type: String,
    default: ''
  }
})

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value)
}

const showDatePopup = ref(false)
const manualStart = ref('')
const manualEnd = ref('')

const toggleAdvancedFilter = () => {
  showDatePopup.value = !showDatePopup.value
}

const applyManualDateFilter = () => {
  if (manualStart.value && manualEnd.value) {
    startDate.value = manualStart.value + 'T00:00'
    endDate.value = manualEnd.value + 'T23:59'
    showDatePopup.value = false
  }
}

const handleFilterChange = (e) => {
  const value = e?.target?.value ?? ''
  if (value === '') {
    manualStart.value = startDate.value ? startDate.value.slice(0, 10) : ''
    manualEnd.value   = endDate.value ? endDate.value.slice(0, 10) : ''
    showDatePopup.value = true
  } else {
    applyQuickFilter(value)
  }
}

const perPage = ref(10)

watch([startDate, endDate], async () => {
  if (!startDate.value || !endDate.value) return
  try {
    const res = await api.get('transaction-summary/', {
      params: {
        start: startDate.value,
        end: endDate.value
      }
    })
    summary.value = res.data

    await fetchTableData()
  } catch (error) {
    console.error('❌ Gagal ambil summary:', error)
  }
})

const applyQuickFilter = (value) => {
  const now = new Date()
  const todayStr = now.toISOString().slice(0, 10)

  if (value === '') {
    showDatePopup.value = true
    return
  }

  if (value === 'today') {
    startDate.value = `${todayStr}T00:00`
    endDate.value = `${todayStr}T23:59`
  } else if (value === 'week') {
    const day = now.getDay() || 7
    const start = new Date(now)
    start.setDate(now.getDate() - day + 1)
    const end = new Date(now)

    startDate.value = start.toISOString().slice(0, 10) + 'T00:00'
    endDate.value = end.toISOString().slice(0, 10) + 'T23:59'
  } else if (value === 'month') {
    const start = new Date(now.getFullYear(), now.getMonth(), 1)
    const end = new Date(now.getFullYear(), now.getMonth() + 1, 0)

    startDate.value = start.toISOString().slice(0, 10) + 'T00:00'
    endDate.value = end.toISOString().slice(0, 10) + 'T23:59'
  }
}

const transactions = ref([])


const filteredTransactions = computed(() => {
  return transactions.value.filter(trx => {
    const nomor = trx.nomor?.toLowerCase() || ''
    const detil = trx.detil?.toLowerCase() || ''
    const matchTipe = !filter.value.tipe || trx.tipe === filter.value.tipe
    const matchNomor = nomor.includes(filter.value.nomor.toLowerCase())
    const matchDetil = detil.includes(filter.value.detil.toLowerCase())
    return matchTipe && matchNomor && matchDetil
  })
})

const toRow = (raw) => {
  const tipeRaw = (raw.type || raw.tipe || '').toLowerCase()
  const tipe = ['sale', 'masuk', 'tama'].includes(tipeRaw) ? 'masuk' : 'keluar'

  // Ambil items dari berbagai kemungkinan key
  const itemsSrc = raw.items || raw.order_items || raw.lines || raw.products || []

  const getName = (it) =>
    it.name ??
    it.product_name ??
    it.title ??
    it.description ??
    it.product?.name ??
    it.product?.title ??
    null

  const getQty = (it) =>
    it.qty ?? it.quantity ?? it.qty_sold ?? 1

  const parts = (Array.isArray(itemsSrc) ? itemsSrc : [])
    .map(it => {
      const nm = getName(it)
      const q  = getQty(it)
      return nm ? `${q}x ${nm}` : null
    })
    .filter(Boolean)

  let detil = ''
  if (parts.length) {
    detil = parts.slice(0, 3).join(', ') + (parts.length > 3 ? ', …' : '')
  } else {
    // fallback untuk transaksi tanpa items (expense/return) atau kalau nama item tidak ketemu
    detil = raw.detail || raw.detil || raw.category || raw.reason || '-'
  }

  const formatDate = (s) => {
    const d = new Date(s || raw.date)
    if (Number.isNaN(d.getTime())) return raw.date || ''
    return `${d.toISOString().slice(0,10)} ${d.toTimeString().slice(0,5)}`
  }

  return {
    date:  formatDate(raw.datetime || raw.created_at || raw.date),
    tipe,  // 'masuk' | 'keluar'
    nomor: raw.invoice || raw.nomor || raw.reference || raw.barcode || raw.code || String(raw.id || ''),
    detil,
    total: Number(raw.total ?? raw.amount ?? 0)
  }
}


const fetchTableData = async () => {
  if (!startDate.value || !endDate.value) return
  try {
    const res = await api.get('transactions/', {
      params: { start: startDate.value, end: endDate.value }
    })
    const raw = Array.isArray(res.data) ? res.data : (res.data.results || [])
    transactions.value = raw.map(toRow)
    console.log('✅ rows loaded:', transactions.value.length, transactions.value[0])
  } catch (error) {
    console.error('❌ Gagal ambil data transaksi:', error)
  }
}

const kpiFromTable = computed(() => {
  let income = 0;   // pendapatan (masuk/tama/sale)
  let expense = 0;  // pengeluaran (keluar/sai/expense)

  for (const t of filteredTransactions.value) {
    const val = Math.abs(Number(t.total) || 0)
    const tipe = (t.tipe || '').toLowerCase()

    // map beberapa kemungkinan label
    if (['masuk', 'tama', 'sale'].includes(tipe)) income += val
    if (['keluar', 'sai', 'expense', 'retur', 'return'].includes(tipe)) expense += val
  }

  const gross_minus_expenses = income - expense
  const net_income = gross_minus_expenses        // tanpa diskon/retur/COGS detail
  const profit_or_loss = net_income

  return {
    gross_income: income,
    expenses: expense,
    gross_minus_expenses,
    net_income,
    profit_or_loss
  }
})

// Pakai hasil perhitungan tabel jika ada data; kalau kosong, fallback ke summary API
const displaySummary = computed(() =>
  filteredTransactions.value.length ? kpiFromTable.value : summary.value
)


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
})

const formattedAddress = computed(() => store.value.address.replace(/\n/g, '<br />'))
const getLogoUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `${baseURL.replace("/api/", "")}${path}`
}

// New UI functions
const clearFilters = () => {
  filter.value = {
    tipe: '',
    nomor: '',
    detil: ''
  }
  startDate.value = ''
  endDate.value = ''
}

const exportData = () => {
  const headers = ['Date','Type','Number','Details','Amount']
  const csvData = filteredTransactions.value.map(trx => [
    trx.date || '',
    trx.tipe || '',
    trx.nomor || '',
    trx.detil || '',
    trx.total || 0
  ])
  
  const csv = [headers.join(','), ...csvData.map(row => row.join(','))].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'transaction_report.csv'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const viewTransaction = (transaction) => {
  alert(`View transaction details for: ${transaction?.nomor || 'Unknown Transaction'}`)
}

const editTransaction = (transaction) => {
  alert(`Edit transaction: ${transaction?.nomor || 'Unknown Transaction'}`)
}

// Summary computed properties
const totalTransactions = computed(() => filteredTransactions.value.length)
const totalIncome = computed(() => 
  filteredTransactions.value
    .filter(t => t.tipe === 'masuk')
    .reduce((sum, t) => sum + (Number(t.total) || 0), 0)
)
const totalExpense = computed(() => 
  filteredTransactions.value
    .filter(t => t.tipe === 'keluar')
    .reduce((sum, t) => sum + (Number(t.total) || 0), 0)
)
const netAmount = computed(() => totalIncome.value - totalExpense.value)

</script>


<template>
  <div class="bg-white border border-gray-200 rounded-lg shadow-sm text-sm flex flex-col h-full">
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b border-gray-300 bg-gradient-to-r from-blue-50 to-cyan-50">
      <div class="flex items-center gap-3">
        <img
          :src="store.logo_base64 || getLogoUrl(store.logo)"
          @error="e => e.target.src = baseURL.replace('/api/', '') + '/media/logos/default.jpg'"
          class="h-8 w-8 rounded-lg shadow-sm"
        />
        <div>
          <h1 class="text-xl font-bold text-gray-800">💼 Transaction Report</h1>
          <p class="text-sm text-gray-600">Comprehensive transaction analysis</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button @click="exportData" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg shadow-sm transition-colors">
          <span class="text-sm font-medium">📊 Export Report</span>
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="p-4 bg-gray-50 border-b border-gray-200">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <!-- Total Transactions Card -->
        <div class="bg-gradient-to-r from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-blue-600">Total Transactions</p>
              <p class="text-xl font-bold text-blue-800">{{ totalTransactions }}</p>
            </div>
            <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <span class="text-blue-600 text-lg">💼</span>
            </div>
          </div>
        </div>
        
        <!-- Total Income Card -->
        <div class="bg-gradient-to-r from-green-50 to-green-100 border border-green-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-green-600">Total Income</p>
              <p class="text-xl font-bold text-green-800">{{ formatCurrency(totalIncome) }}</p>
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
              <p class="text-xl font-bold text-red-800">{{ formatCurrency(totalExpense) }}</p>
            </div>
            <div class="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
              <span class="text-red-600 text-lg">📉</span>
            </div>
          </div>
        </div>

        <!-- Net Amount Card -->
        <div class="bg-gradient-to-r from-purple-50 to-purple-100 border border-purple-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-purple-600">Net Amount</p>
              <p class="text-xl font-bold" :class="netAmount >= 0 ? 'text-green-800' : 'text-red-800'">
                {{ formatCurrency(netAmount) }}
              </p>
            </div>
            <div class="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
              <span class="text-purple-600 text-lg">💰</span>
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
          <select @change="handleFilterChange($event)" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
            <option value="today">📅 Today</option>
            <option value="week">📈 This Week</option>
            <option value="month">📆 This Month</option>
            <option value="">🗓️ Custom Range</option>
          </select>
        </div>
        
        <div class="min-w-[140px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Type</label>
          <select v-model="filter.tipe" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
            <option value="">All Types</option>
            <option value="masuk">Income</option>
            <option value="keluar">Expense</option>
          </select>
        </div>
        
        <div class="min-w-[180px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Search by Number</label>
          <input 
            v-model="filter.nomor" 
            type="text" 
            placeholder="Enter transaction number..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Search by Details</label>
          <input 
            v-model="filter.detil" 
            type="text" 
            placeholder="Enter transaction details..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div class="flex items-end gap-2">
          <button @click="clearFilters" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
            Clear Filters
          </button>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="p-4 flex flex-col flex-1 overflow-hidden">

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
                  type="date" 
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                <input 
                  v-model="manualEnd" 
                  type="date" 
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
                />
              </div>
            </div>
          </div>
          
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
              <tr v-if="filteredTransactions.length === 0">
                <td colspan="6" class="px-4 py-12 text-center text-gray-500">
                  <div class="flex flex-col items-center">
                    <span class="text-4xl mb-2">💼</span>
                    <p class="text-lg font-medium mb-1">No transactions found</p>
                    <p class="text-sm">Try adjusting your date range or filters</p>
                  </div>
                </td>
              </tr>
              
              <tr v-else v-for="(trx, index) in filteredTransactions" :key="index" class="hover:bg-gray-50 transition-colors">
                <td class="px-4 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">{{ trx.date || 'N/A' }}</div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap text-center">
                  <span 
                    class="inline-flex px-2 py-1 text-xs font-medium rounded-full capitalize"
                    :class="{
                      'bg-green-100 text-green-800': trx.tipe === 'masuk',
                      'bg-red-100 text-red-800': trx.tipe === 'keluar',
                      'bg-gray-100 text-gray-800': !trx.tipe
                    }"
                  >
                    {{ trx.tipe === 'masuk' ? '📈 Income' : trx.tipe === 'keluar' ? '📉 Expense' : 'Unknown' }}
                  </span>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900">{{ trx.nomor || 'N/A' }}</div>
                </td>
                
                <td class="px-4 py-4">
                  <div class="text-sm text-gray-900 max-w-xs truncate" :title="trx.detil">
                    {{ trx.detil || 'No details' }}
                  </div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap text-right">
                  <div class="text-sm font-bold" 
                       :class="trx.tipe === 'masuk' ? 'text-green-600' : trx.tipe === 'keluar' ? 'text-red-600' : 'text-gray-900'">
                    {{ formatCurrency(parseFloat(trx.total) || 0) }}
                  </div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap text-center">
                  <div class="flex items-center justify-center space-x-2">
                    <button 
                      @click="viewTransaction(trx)"
                      class="text-blue-600 hover:text-blue-800 font-medium text-sm"
                      title="View Details"
                    >
                      👁️
                    </button>
                    <button 
                      @click="editTransaction(trx)"
                      class="text-yellow-600 hover:text-yellow-800 font-medium text-sm"
                      title="Edit Transaction"
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

      <!-- Pagination Footer -->
      <div class="flex justify-between items-center mt-4 px-4 py-3 bg-gray-50 border-t border-gray-200 rounded-b-lg">
        <div class="flex items-center gap-2">
          <span class="text-sm text-gray-700">Show:</span>
          <select v-model="perPage" class="px-2 py-1 border border-gray-300 rounded-md text-sm">
            <option v-for="n in [10, 20, 50, 100]" :key="n" :value="n">{{ n }} per page</option>
          </select>
        </div>
        <div class="text-sm text-gray-700">
          Showing {{ filteredTransactions.length }} transaction{{ filteredTransactions.length !== 1 ? 's' : '' }}
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
  --tw-ring-color: rgb(59 130 246 / 0.5);
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
