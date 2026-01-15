<script setup>
import api, { baseURL } from '@/axios'
import { ref, computed, onMounted, nextTick } from 'vue'
import FooterActions from '@/components/pos/FooterActions.vue'

const store = ref({
  name: '',
  address: '',
  logo: '',
  version: '',
  location: ''
})

const returns = ref([])
const filter = ref({
  tanggal: '',
  barcode: '',
  nama: '',
  supplier: '',
  status: ''
})

const perPage = ref(10)
const loading = ref(false)
const selectedReturn = ref(null)

const getLogoUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `${baseURL.replace("/api/", "")}${path}`
}

const formatPrice = (val) => {
  const num = parseFloat(val)
  if (isNaN(num)) return '$0.00'
  return num.toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2
  })
}

const todayOptionLabel = computed(() => {
  const d = new Date()
  const dd = String(d.getDate()).padStart(2, '0')
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const yyyy = d.getFullYear()
  return `📅 ${dd}/${mm}/${yyyy}`
})

const inRange = (dateStr, start, end) => {
  if (!dateStr) return false
  if (!start && !end) return true
  const d = dateStr.slice(0,10)
  return (!start || d >= start) && (!end || d <= end)
}

const showDatePopup = ref(false)
const manualStart = ref('')
const manualEnd   = ref('')
const rangeReturn = ref({ start: '', end: '' }) 


const fmtDate = (d) => {
  const dd = String(d.getDate()).padStart(2, '0')
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const yyyy = d.getFullYear()
  return `${yyyy}-${mm}-${dd}`
}

const openCalendarFor = () => {
  manualStart.value = rangeReturn.value.start || (filter.value.tanggal || '')
  manualEnd.value   = rangeReturn.value.end   || manualStart.value || ''
  showDatePopup.value = true
}

const applyManualRange = () => {
  if (!manualStart.value || !manualEnd.value) {
    showDatePopup.value = false
    return
  }
  rangeReturn.value = { start: manualStart.value, end: manualEnd.value }
  filter.value.tanggal = ''
  showDatePopup.value = false
}

const clearRangeReturn = () => { rangeReturn.value = { start: '', end: '' } }

const handleFilterChangeFor = (field, ev) => {
  const v = ev.target.value
  const today = new Date()
  if (v === 'today') {
    const t = fmtDate(today)
    filter.value.tanggal = t       
    clearRangeReturn()            
    return
  }
  if (v === 'week') {
    const d = new Date()
    const day = d.getDay() || 7 
    const monday = new Date(d); monday.setDate(d.getDate() - (day - 1))
    rangeReturn.value = { start: fmtDate(monday), end: fmtDate(today) }
    filter.value.tanggal = ''   
    return
  }
  if (v === 'month') {
    const d = new Date()
    const first = new Date(d.getFullYear(), d.getMonth(), 1)
    rangeReturn.value = { start: fmtDate(first), end: fmtDate(today) }
    filter.value.tanggal = ''
    return
  }
  openCalendarFor()
}

const filteredReturns = computed(() =>
  returns.value.filter(i => {
    const tanggalMatch =
      filter.value.tanggal
        ? i.returned_at?.slice(0, 10) === filter.value.tanggal
        : inRange(i.returned_at, rangeReturn.value.start, rangeReturn.value.end)

    const barcodeMatch  = !filter.value.barcode  || i.product?.sku?.toLowerCase().includes(filter.value.barcode.toLowerCase())
    const namaMatch     = !filter.value.nama     || i.product?.name?.toLowerCase().includes(filter.value.nama.toLowerCase())
    const supplierMatch = !filter.value.supplier || i.purchase?.supplier?.name?.toLowerCase().includes(filter.value.supplier.toLowerCase())
    const statusMatch   = !filter.value.status   || i.status === filter.value.status

    return tanggalMatch && barcodeMatch && namaMatch && supplierMatch && statusMatch
  })
)

const totalPembelian = computed(() =>
  filteredReturns.value.reduce((sum, item) => sum + (item.refunded_amount || 0), 0)
)

onMounted(async () => {
  try {
    const token = localStorage.getItem('token')
    const [resReturns, resStore] = await Promise.all([
      api.get('purchase-returns/', {
        headers: { Authorization: `Bearer ${token}` }
      }),
      api.get('store-profile/')
    ])

    console.log('🛒 Data Purchase Returns:', resReturns.data)
    returns.value = resReturns.data
    if (resStore.data && resStore.data.length > 0) {
      store.value = resStore.data[0]
    }
  } catch (err) {
    console.error('Gagal fetch data:', err)
  }
})

// New functions for improved UI
const clearFilters = () => {
  filter.value = {
    tanggal: '',
    barcode: '',
    nama: '',
    supplier: '',
    status: ''
  }
  clearRangeReturn()
}

const exportData = () => {
  const headers = ['Return Date','Product','SKU','Supplier','Status','Quantity','Refund Amount','Reason']
  const csvData = filteredReturns.value.map(item => [
    dateOnly(item?.returned_at),
    item?.product?.name || 'No name',
    item?.product?.sku || 'N/A',
    item?.purchase?.supplier?.name || 'No supplier',
    item?.status || 'Unknown',
    item?.quantity || 0,
    item?.refunded_amount || 0,
    item?.reason || 'No reason'
  ])
  
  const csv = [headers.join(','), ...csvData.map(row => row.join(','))].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'purchase_returns_export.csv'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const viewReturn = (item) => {
  // TODO: Implement view functionality
  alert(`View return details for: ${item?.product?.name || 'Unknown Product'}`)
}

const editReturn = (item) => {
  // TODO: Implement edit functionality
  alert(`Edit return for: ${item?.product?.name || 'Unknown Product'}`)
}

const deleteReturn = async (item) => {
  if (!confirm(`Are you sure you want to delete the return for ${item?.product?.name || 'this product'}?`)) return
  
  try {
    await api.delete(`purchase-returns/${item.id}/`)
    // Refresh the data
    await fetchReturns()
    alert('Return deleted successfully')
  } catch (error) {
    console.error('Error deleting return:', error)
    alert('Failed to delete return')
  }
}

const refresh = () => console.log('Refresh')
const addItem = () => console.log('Tambah')
const editItem = () => console.log('Edit')
const deleteItem = () => console.log('Hapus')

const dateOnly = (v) => (v ? String(v).slice(0, 10) : '-')

const pricePerItem = (refunded_amount, qty) => {
  const q = Number(qty) || 0
  const amt = Number(refunded_amount) || 0
  return q > 0 ? formatPrice(amt / q) : formatPrice(0)
}

</script>

<template>
  <div class="bg-white border border-gray-200 rounded-lg shadow-sm text-sm flex flex-col h-full">
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b border-gray-300 bg-gradient-to-r from-red-50 to-orange-50">
      <div class="flex items-center gap-3">
        <img
          :src="store.logo_base64 || getLogoUrl(store.logo)"
          @error="e => e.target.src = baseURL.replace('/api/', '') + '/media/logos/default.jpg'"
          class="h-8 w-8 rounded-lg shadow-sm"
        />
        <div>
          <h1 class="text-xl font-bold text-gray-800">📦 Purchase Returns</h1>
          <p class="text-sm text-gray-600">Manage returned purchase items</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg shadow-sm transition-colors">
          <span class="text-sm font-medium">↩️ New Return</span>
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="p-4 bg-gray-50 border-b border-gray-200">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <!-- Total Returns Card -->
        <div class="bg-gradient-to-r from-red-50 to-red-100 border border-red-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-red-600">Total Returns</p>
              <p class="text-xl font-bold text-red-800">{{ formatPrice(totalPembelian) }}</p>
            </div>
            <div class="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
              <span class="text-red-600 text-lg">↩️</span>
            </div>
          </div>
        </div>
        
        <!-- Return Count Card -->
        <div class="bg-gradient-to-r from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-blue-600">Return Items</p>
              <p class="text-xl font-bold text-blue-800">{{ filteredReturns.length }}</p>
            </div>
            <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <span class="text-blue-600 text-lg">📦</span>
            </div>
          </div>
        </div>

        <!-- Approved Returns Card -->
        <div class="bg-gradient-to-r from-green-50 to-green-100 border border-green-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-green-600">Approved</p>
              <p class="text-xl font-bold text-green-800">{{ filteredReturns.filter(r => r.status === 'Approved').length }}</p>
            </div>
            <div class="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
              <span class="text-green-600 text-lg">✅</span>
            </div>
          </div>
        </div>

        <!-- Pending Returns Card -->
        <div class="bg-gradient-to-r from-yellow-50 to-yellow-100 border border-yellow-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-yellow-600">Pending</p>
              <p class="text-xl font-bold text-yellow-800">{{ filteredReturns.filter(r => r.status === 'Pending').length }}</p>
            </div>
            <div class="w-10 h-10 bg-yellow-100 rounded-full flex items-center justify-center">
              <span class="text-yellow-600 text-lg">⏳</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="p-4 bg-white border-b border-gray-200">
      <div class="flex flex-wrap items-center gap-3">
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Search by Barcode/SKU</label>
          <input 
            v-model="filter.barcode" 
            type="text" 
            placeholder="Enter barcode or SKU..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
          />
        </div>
        
        <div class="min-w-[180px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Product Name</label>
          <input 
            v-model="filter.nama" 
            type="text" 
            placeholder="Search product..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
          />
        </div>

        <div class="min-w-[140px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Supplier</label>
          <input 
            v-model="filter.supplier" 
            type="text" 
            placeholder="Supplier name..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
          />
        </div>

        <div class="min-w-[140px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select v-model="filter.status" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent">
            <option value="">All Status</option>
            <option value="Approved">Approved</option>
            <option value="Pending">Pending</option>
            <option value="Rejected">Rejected</option>
          </select>
        </div>

        <div class="min-w-[160px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Date Range</label>
          <select @change="e => handleFilterChangeFor('return', e)" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent">
            <option value="today">📅 Today</option>
            <option value="week">📈 This Week</option>
            <option value="month">📆 This Month</option>
            <option value="">🗓️ Custom Range</option>
          </select>
        </div>

        <div class="flex items-end gap-2">
          <button @click="clearFilters" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
            Clear Filters
          </button>
          <button @click="exportData" class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors">
            📊 Export
          </button>
        </div>
      </div>
    </div>

    <div class="p-4 flex flex-col flex-1 overflow-hidden">

      <!-- Table -->
      <div class="bg-white rounded-lg border border-gray-200 overflow-hidden shadow-sm">
        <div class="overflow-x-auto">
          <table class="w-full border-collapse">
            <thead class="bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Return Date</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Product</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Supplier</th>
                <th class="px-4 py-3 text-center text-xs font-semibold text-gray-700 uppercase tracking-wider">Status</th>
                <th class="px-4 py-3 text-center text-xs font-semibold text-gray-700 uppercase tracking-wider">Quantity</th>
                <th class="px-4 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">Refund Amount</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Reason</th>
                <th class="px-4 py-3 text-center text-xs font-semibold text-gray-700 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>

            <tbody class="divide-y divide-gray-200">
              <tr v-if="loading">
                <td colspan="8" class="px-4 py-12 text-center text-gray-500">
                  <div class="flex flex-col items-center">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-red-600 mb-2"></div>
                    <p>Loading returns...</p>
                  </div>
                </td>
              </tr>
              
              <tr v-else-if="filteredReturns.length === 0">
                <td colspan="8" class="px-4 py-12 text-center text-gray-500">
                  <div class="flex flex-col items-center">
                    <span class="text-4xl mb-2">↩️</span>
                    <p class="text-lg font-medium mb-1">No returns found</p>
                    <p class="text-sm">Try adjusting your filters or create a new return</p>
                  </div>
                </td>
              </tr>
              
              <tr v-else v-for="item in filteredReturns" :key="item.id" class="hover:bg-gray-50 transition-colors">
                <td class="px-4 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">{{ dateOnly(item?.returned_at) }}</div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div>
                      <div class="text-sm font-medium text-gray-900">{{ item?.product?.name || 'No name' }}</div>
                      <div class="text-xs text-gray-500">SKU: {{ item?.product?.sku || 'N/A' }}</div>
                    </div>
                  </div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">{{ item?.purchase?.supplier?.name || 'No supplier' }}</div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap text-center">
                  <span 
                    class="inline-flex px-2 py-1 text-xs font-medium rounded-full"
                    :class="{
                      'bg-green-100 text-green-800': item?.status === 'Approved',
                      'bg-yellow-100 text-yellow-800': item?.status === 'Pending',
                      'bg-red-100 text-red-800': item?.status === 'Rejected'
                    }"
                  >
                    {{ item?.status === 'Approved' ? '✅ Approved' : item?.status === 'Pending' ? '⏳ Pending' : '❌ Rejected' }}
                  </span>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap text-center">
                  <div class="text-sm font-bold text-gray-900">{{ item?.quantity || 0 }}</div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap text-right">
                  <div class="text-sm font-bold text-gray-900">{{ formatPrice(item?.refunded_amount || 0) }}</div>
                  <div class="text-xs text-gray-500">
                    Per item: {{ pricePerItem(item?.refunded_amount, item?.quantity) }}
                  </div>
                </td>
                
                <td class="px-4 py-4">
                  <div class="text-sm text-gray-900 max-w-xs truncate" :title="item?.reason">
                    {{ item?.reason || 'No reason provided' }}
                  </div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap text-center">
                  <div class="flex items-center justify-center space-x-2">
                    <button 
                      @click="viewReturn(item)"
                      class="text-blue-600 hover:text-blue-800 font-medium text-sm"
                      title="View Details"
                    >
                      👁️
                    </button>
                    <button 
                      @click="editReturn(item)"
                      class="text-yellow-600 hover:text-yellow-800 font-medium text-sm"
                      title="Edit"
                    >
                      ✏️
                    </button>
                    <button 
                      @click="deleteReturn(item)"
                      class="text-red-600 hover:text-red-800 font-medium text-sm"
                      title="Delete"
                    >
                      🗑️
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
          Showing {{ filteredReturns.length }} return{{ filteredReturns.length !== 1 ? 's' : '' }}
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
                  type="date" 
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent" 
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                <input 
                  v-model="manualEnd" 
                  type="date" 
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent" 
                />
              </div>
            </div>
          </div>
          
          <div class="flex items-center justify-end p-6 border-t border-gray-200 space-x-3">
            <button 
              @click="showDatePopup = false" 
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors"
            >
              Cancel
            </button>
            <button 
              @click="applyManualRange" 
              class="px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors"
            >
              Apply Filter
            </button>
          </div>
        </div>
      </div>
    </div>

    <FooterActions />
  </div>
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
  --tw-ring-color: rgb(220 38 38 / 0.5);
  border-color: transparent;
}

/* Table improvements */
table {
  border-collapse: collapse;
  font-variant-numeric: tabular-nums;
}

/* Loading animation */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* Scrollbar styling */
.scrollbar-stable {
  scrollbar-gutter: stable;
}

/* Hover effects */
.hover\:shadow-md:hover {
  --tw-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --tw-shadow-colored: 0 4px 6px -1px var(--tw-shadow-color), 0 2px 4px -2px var(--tw-shadow-color);
  box-shadow: var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000), var(--tw-shadow);
}
</style>
