<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import FooterActions from '@/components/pos/FooterActions.vue'
import api, { baseURL } from '@/axios'

const store = ref({
  name: '',
  address: '',
  logo: '',
  version: '',
  location: ''
})

const formattedAddress = computed(() => store.value.address.replace(/\n/g, '<br />'))

const getLogoUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `${baseURL.replace("/api/", "")}${path}`
}

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
  
  fetchProducts()
  fetchAdjustments()
})

const formatDate = (datetimeStr) => {
  const d = new Date(datetimeStr)
  return d.toLocaleString('en-US', {
    dateStyle: 'medium',
    timeStyle: 'short'
  })
}

const formatPrice = (value) => {
  const number = Number(value)
  return isNaN(number)
    ? '$0.00'
    : new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(number)
}

const startDate = ref('')
const endDate   = ref('')
const showDatePopup = ref(false)
const manualStart = ref('')
const manualEnd = ref('')


const fetchAdjustments = async () => {
  try {
    const params = {}
    if (startDate.value && endDate.value) {
      params.start = startDate.value
      params.end   = endDate.value
    }
    const res = await api.get('stock-adjustments/', { params })
    items.value = res.data
  } catch (err) {
    console.error('❌ Falha foti data hadia stok:', err)
  }
}

watch([startDate, endDate], () => {
  if (startDate.value && endDate.value) {
    fetchAdjustments()
  }
})

// onMounted(() => {
//   const token = localStorage.getItem('token')
//   axios.defaults.headers.common['Authorization'] = `Bearer ${token}`

//   // set default: hari ini → akan memicu watcher & fetchAdjustments
//   applyQuickFilter('today')

//   fetchProducts()
//   // fetchAdjustments() tidak perlu dipanggil di sini karena watcher akan jalan
// })


const filter = ref({
  tanggal_awal: '',
  tanggal_akhir: '',
  barcode: '',
  nama: ''
})

const perPage = ref(10)
const items = ref([])


// Quick filter handler (select)
const handleFilterChange = (e) => {
  const value = e?.target?.value ?? ''
  if (value === '') {
    // buka popup kalender
    manualStart.value = startDate.value ? startDate.value.slice(0,10) : ''
    manualEnd.value   = endDate.value ? endDate.value.slice(0,10) : ''
    showDatePopup.value = true
  } else {
    applyQuickFilter(value)
  }
}

// Quick presets: today / week / month
const applyQuickFilter = (value) => {
  const now = new Date()
  const todayStr = now.toISOString().slice(0,10)

  if (value === 'today') {
    startDate.value = `${todayStr}T00:00`
    endDate.value   = `${todayStr}T23:59`
  } else if (value === 'week') {
    const day = now.getDay() || 7
    const start = new Date(now)
    start.setDate(now.getDate() - day + 1) // Senin
    const end = new Date(now)
    startDate.value = start.toISOString().slice(0,10) + 'T00:00'
    endDate.value   = end.toISOString().slice(0,10) + 'T23:59'
  } else if (value === 'month') {
    const start = new Date(now.getFullYear(), now.getMonth(), 1)
    const end   = new Date(now.getFullYear(), now.getMonth()+1, 0)
    startDate.value = start.toISOString().slice(0,10) + 'T00:00'
    endDate.value   = end.toISOString().slice(0,10) + 'T23:59'
  }
}

// Popup kalender → tombol OK
const applyManualDateFilter = () => {
  if (manualStart.value && manualEnd.value) {
    startDate.value = `${manualStart.value}T00:00`
    endDate.value   = `${manualEnd.value}T23:59`
    showDatePopup.value = false
  }
}

const filteredData = computed(() =>
  items.value.filter(i =>
    (!filter.value.tanggal_awal || i.tanggal >= filter.value.tanggal_awal) &&
    (!filter.value.tanggal_akhir || i.tanggal <= filter.value.tanggal_akhir) &&
    i.barcode.toLowerCase().includes(filter.value.barcode.toLowerCase()) &&
    i.nama.toLowerCase().includes(filter.value.nama.toLowerCase())
  )
)

const todayOptionText = computed(() => {
  const d = new Date(); // ikut tanggal & zona waktu komputer
  const dd = String(d.getDate()).padStart(2, '0');
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const yyyy = d.getFullYear();
  return `📅 ${dd}/${mm}/${yyyy}`
});


const refresh = () => {
  fetchAdjustments()
}

// New functions for improved UI
const clearFilters = () => {
  filter.value = {
    tanggal_awal: '',
    tanggal_akhir: '',
    barcode: '',
    nama: ''
  }
  startDate.value = ''
  endDate.value = ''
}

const exportData = () => {
  const headers = ['Adjustment Date','Product Name','Old Stock','New Stock','Difference','Reason','Adjusted By']
  const csvData = items.value.map(item => [
    formatDate(item.adjusted_at),
    item.product_name || 'No name',
    item.old_stock || 0,
    item.new_stock || 0,
    (item.new_stock || 0) - (item.old_stock || 0),
    item.reason || 'No reason',
    item.adjusted_by || 'Unknown'
  ])
  
  const csv = [headers.join(','), ...csvData.map(row => row.join(','))].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'inventory_adjustments_export.csv'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const viewAdjustment = (item) => {
  alert(`View adjustment details for: ${item?.product_name || 'Unknown Product'}`)
}

const editAdjustment = (item) => {
  alert(`Edit adjustment for: ${item?.product_name || 'Unknown Product'}`)
}

const deleteAdjustment = async (item) => {
  if (!confirm(`Are you sure you want to delete the adjustment for ${item?.product_name || 'this product'}?`)) return
  
  try {
    await api.delete(`stock-adjustments/${item.id}/`)
    await fetchAdjustments()
    alert('Adjustment deleted successfully')
  } catch (error) {
    console.error('Error deleting adjustment:', error)
    alert('Failed to delete adjustment')
  }
}

// Summary computed properties
const totalAdjustments = computed(() => items.value.length)
const totalIncreases = computed(() => 
  items.value.filter(item => (item.new_stock || 0) > (item.old_stock || 0)).length
)
const totalDecreases = computed(() => 
  items.value.filter(item => (item.new_stock || 0) < (item.old_stock || 0)).length
)
const totalStockDifference = computed(() => 
  items.value.reduce((sum, item) => sum + ((item.new_stock || 0) - (item.old_stock || 0)), 0)
)

// 🔹 Modal state
const showModal = ref(false)
const products = ref([])
const form = ref({
  product: '',
  new_stock: '',
  reason: ''
})

// 🔹 Buka modal
const addItem = () => {
  showModal.value = true
  fetchProducts()
}

// 🔹 Ambil data produk dari API
const fetchProducts = async () => {
  try {
    const res = await api.get('products/')
    products.value = res.data
  } catch (err) {
    console.error('Gagal fetch produk:', err)
  }
}

// 🔹 Submit form
const submitForm = async () => {
  try {
    const payload = {
      product: form.value.product,
      new_stock: parseInt(form.value.new_stock),
      reason: form.value.reason
    }
    await api.post('stock-adjustments/', payload)
    alert('✅ Stock berhasil disesuaikan.')
    showModal.value = false
    form.value = { product: '', new_stock: '', reason: '' }
  } catch (err) {
    console.error('❌ Error submit:', err.response?.data || err)
    alert('Terjadi kesalahan. Silakan periksa kembali.')
  }
}
</script>


<template>
  <div class="bg-white border border-gray-200 rounded-lg shadow-sm text-sm flex flex-col h-full">
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b border-gray-300 bg-gradient-to-r from-purple-50 to-indigo-50">
      <div class="flex items-center gap-3">
        <img
          :src="store.logo_base64 || getLogoUrl(store.logo)"
          @error="e => e.target.src = baseURL.replace('/api/', '') + '/media/logos/default.jpg'"
          class="h-8 w-8 rounded-lg shadow-sm"
        />
        <div>
          <h1 class="text-xl font-bold text-gray-800">📊 Inventory Adjustments</h1>
          <p class="text-sm text-gray-600">Track and manage stock adjustments</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button @click="addItem" class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg shadow-sm transition-colors">
          <span class="text-sm font-medium">📝 New Adjustment</span>
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="p-4 bg-gray-50 border-b border-gray-200">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <!-- Total Adjustments Card -->
        <div class="bg-gradient-to-r from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-blue-600">Total Adjustments</p>
              <p class="text-xl font-bold text-blue-800">{{ totalAdjustments }}</p>
            </div>
            <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <span class="text-blue-600 text-lg">📝</span>
            </div>
          </div>
        </div>
        
        <!-- Stock Increases Card -->
        <div class="bg-gradient-to-r from-green-50 to-green-100 border border-green-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-green-600">Stock Increases</p>
              <p class="text-xl font-bold text-green-800">{{ totalIncreases }}</p>
            </div>
            <div class="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
              <span class="text-green-600 text-lg">📈</span>
            </div>
          </div>
        </div>

        <!-- Stock Decreases Card -->
        <div class="bg-gradient-to-r from-red-50 to-red-100 border border-red-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-red-600">Stock Decreases</p>
              <p class="text-xl font-bold text-red-800">{{ totalDecreases }}</p>
            </div>
            <div class="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
              <span class="text-red-600 text-lg">📉</span>
            </div>
          </div>
        </div>

        <!-- Net Stock Change Card -->
        <div class="bg-gradient-to-r from-yellow-50 to-yellow-100 border border-yellow-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-yellow-600">Net Change</p>
              <p class="text-xl font-bold" :class="totalStockDifference >= 0 ? 'text-green-800' : 'text-red-800'">{{ totalStockDifference >= 0 ? '+' : '' }}{{ totalStockDifference }}</p>
            </div>
            <div class="w-10 h-10 bg-yellow-100 rounded-full flex items-center justify-center">
              <span class="text-yellow-600 text-lg">⚖️</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="p-4 bg-white border-b border-gray-200">
      <div class="flex flex-wrap items-center gap-3">
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Search by Product</label>
          <input 
            v-model="filter.nama" 
            type="text" 
            placeholder="Enter product name..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>
        
        <div class="min-w-[160px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Date Range</label>
          <select @change="handleFilterChange($event)" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent">
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
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" 
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                <input 
                  v-model="manualEnd" 
                  type="date" 
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" 
                />
              </div>
            </div>
          </div>
          
          <div class="flex items-center justify-end p-6 border-t border-gray-200 space-x-3">
            <button 
              @click="showDatePopup = false" 
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition-colors"
            >
              Cancel
            </button>
            <button 
              @click="applyManualDateFilter" 
              class="px-4 py-2 text-sm font-medium text-white bg-purple-600 border border-transparent rounded-lg hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition-colors"
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
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Product</th>
                <th class="px-4 py-3 text-center text-xs font-semibold text-gray-700 uppercase tracking-wider">Old Stock</th>
                <th class="px-4 py-3 text-center text-xs font-semibold text-gray-700 uppercase tracking-wider">New Stock</th>
                <th class="px-4 py-3 text-center text-xs font-semibold text-gray-700 uppercase tracking-wider">Difference</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Reason</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Adjusted By</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Date</th>
                <th class="px-4 py-3 text-center text-xs font-semibold text-gray-700 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>

            <tbody class="divide-y divide-gray-200">
              <tr v-if="items.length === 0">
                <td colspan="8" class="px-4 py-12 text-center text-gray-500">
                  <div class="flex flex-col items-center">
                    <span class="text-4xl mb-2">📝</span>
                    <p class="text-lg font-medium mb-1">No adjustments found</p>
                    <p class="text-sm">Try adjusting your filters or create a new adjustment</p>
                  </div>
                </td>
              </tr>
              
              <tr v-else v-for="item in items" :key="item.id" class="hover:bg-gray-50 transition-colors">
                <td class="px-4 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div>
                      <div class="text-sm font-medium text-gray-900">{{ item.product_name || 'No name' }}</div>
                      <div class="text-xs text-gray-500">ID: {{ item.id }}</div>
                    </div>
                  </div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap text-center">
                  <div class="text-sm font-bold text-gray-900">{{ item.old_stock || 0 }}</div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap text-center">
                  <div class="text-sm font-bold text-gray-900">{{ item.new_stock || 0 }}</div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap text-center">
                  <span 
                    class="inline-flex px-2 py-1 text-xs font-medium rounded-full"
                    :class="{
                      'bg-green-100 text-green-800': (item.new_stock || 0) > (item.old_stock || 0),
                      'bg-red-100 text-red-800': (item.new_stock || 0) < (item.old_stock || 0),
                      'bg-gray-100 text-gray-800': (item.new_stock || 0) === (item.old_stock || 0)
                    }"
                  >
                    {{ ((item.new_stock || 0) > (item.old_stock || 0) ? '+' : '') + ((item.new_stock || 0) - (item.old_stock || 0)) }}
                  </span>
                </td>
                
                <td class="px-4 py-4">
                  <div class="text-sm text-gray-900 max-w-xs truncate" :title="item.reason">
                    {{ item.reason || 'No reason provided' }}
                  </div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">{{ item.adjusted_by || 'Unknown' }}</div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">{{ formatDate(item.adjusted_at) }}</div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap text-center">
                  <div class="flex items-center justify-center space-x-2">
                    <button 
                      @click="viewAdjustment(item)"
                      class="text-blue-600 hover:text-blue-800 font-medium text-sm"
                      title="View Details"
                    >
                      👁️
                    </button>
                    <button 
                      @click="editAdjustment(item)"
                      class="text-yellow-600 hover:text-yellow-800 font-medium text-sm"
                      title="Edit"
                    >
                      ✏️
                    </button>
                    <button 
                      @click="deleteAdjustment(item)"
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
          Showing {{ items.length }} adjustment{{ items.length !== 1 ? 's' : '' }}
        </div>
      </div>
    </div>

    <!-- New Adjustment Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div class="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4">
        <div class="flex items-center justify-between p-6 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">📝 New Stock Adjustment</h3>
          <button @click="showModal = false" class="text-gray-400 hover:text-gray-600 transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        
        <div class="p-6">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Product *</label>
              <select v-model="form.product" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent">
                <option value="">Select a product...</option>
                <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }} - {{ p.sku }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">New Stock Quantity *</label>
              <input 
                v-model="form.new_stock" 
                type="number" 
                min="0" 
                placeholder="Enter new stock quantity..."
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" 
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Adjustment Reason *</label>
              <textarea 
                v-model="form.reason" 
                rows="3" 
                placeholder="Explain the reason for this stock adjustment..."
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              ></textarea>
            </div>
          </div>
        </div>
        
        <div class="flex items-center justify-end p-6 border-t border-gray-200 space-x-3">
          <button 
            @click="showModal = false" 
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition-colors"
          >
            Cancel
          </button>
          <button 
            @click="submitForm" 
            class="px-4 py-2 text-sm font-medium text-white bg-purple-600 border border-transparent rounded-lg hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition-colors"
            :disabled="!form.product || !form.new_stock || !form.reason"
          >
            Save Adjustment
          </button>
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
select:focus,
textarea:focus {
  outline: 2px solid transparent;
  outline-offset: 2px;
  --tw-ring-offset-shadow: var(--tw-ring-inset) 0 0 0 var(--tw-ring-offset-width) var(--tw-ring-offset-color);
  --tw-ring-shadow: var(--tw-ring-inset) 0 0 0 calc(2px + var(--tw-ring-offset-width)) var(--tw-ring-color);
  box-shadow: var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow, 0 0 #0000);
  --tw-ring-color: rgb(147 51 234 / 0.5);
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

/* Disabled button styles */
button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

button:disabled:hover {
  background-color: initial;
}
</style>
