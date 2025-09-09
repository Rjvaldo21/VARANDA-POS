<script setup>
import { ref, computed, onMounted } from 'vue'
import FooterActions from '@/components/pos/FooterActions.vue'
import api from '@/axios'

const store = ref({
  name: '',
  address: '',
  logo: '',
  logo_base64: '',
  version: '',
  location: ''
})

const transferList = ref([])
const warehouses = ref([])
const products = ref([])

const filter = ref({
  from: '',
  to: '',
  product: ''
})

const perPage = ref(10)
const isLoading = ref(false)

const showTransferModal = ref(false)
const modalMode = ref('add')

const transferForm = ref({
  from_warehouse: '',
  to_warehouse: '',
  product: '',
  quantity: ''
})

const getLogoUrl = (path) => {
  if (!path) return ''
  return path.startsWith('http') ? path : `http://localhost:8000${path}`
}

const fetchStoreProfile = async () => {
  const res = await api.get('store-profile/')
  if (res.data.length > 0) store.value = res.data[0]
}

const fetchWarehouses = async () => {
  const res = await api.get('warehouses/')
  warehouses.value = res.data
}

const fetchProducts = async () => {
  const res = await api.get('products/')
  products.value = res.data
}

const fetchTransfers = async () => {
  const res = await api.get('stock-transfers/')
  console.log('📦 Transfers:', res.data)
  transferList.value = res.data
}

const refresh = async () => {
  await fetchTransfers()
}

// New UI functions
const clearFilters = () => {
  filter.value = { from: '', to: '', product: '' }
}

const exportData = () => {
  const headers = ['Transfer Date','From Warehouse','To Warehouse','Product','Quantity','Status','Notes']
  const csvData = filteredTransfers.value.map(transfer => [
    transfer.created_at ? new Date(transfer.created_at).toLocaleDateString() : '',
    transfer.from_warehouse_name || '',
    transfer.to_warehouse_name || '',
    transfer.product_name || '',
    transfer.quantity || 0,
    transfer.status || 'Pending',
    transfer.note || ''
  ])
  
  const csv = [headers.join(','), ...csvData.map(row => row.join(','))].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'stock_transfers_report.csv'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const viewTransfer = (transfer) => {
  alert(`View transfer details for: ${transfer?.product_name || 'Unknown Product'}`)
}

const editTransfer = (transfer) => {
  alert(`Edit transfer: ${transfer?.product_name || 'Unknown Product'}`)
}

const cancelTransfer = async (transfer) => {
  if (!confirm(`Are you sure you want to cancel the transfer for ${transfer?.product_name || 'this product'}?`)) return
  
  try {
    // Assuming there's a cancel endpoint or status update
    await api.patch(`stock-transfers/${transfer.id}/`, { status: 'cancelled' })
    await fetchTransfers()
    alert('Transfer cancelled successfully')
  } catch (error) {
    console.error('Error cancelling transfer:', error)
    alert('Failed to cancel transfer')
  }
}

// Summary computed properties
const totalTransfers = computed(() => filteredTransfers.value.length)
const pendingTransfers = computed(() => 
  filteredTransfers.value.filter(t => t.status === 'pending' || !t.status).length
)
const completedTransfers = computed(() => 
  filteredTransfers.value.filter(t => t.status === 'completed').length
)
const totalQuantityTransferred = computed(() => 
  filteredTransfers.value.reduce((sum, t) => sum + (Number(t.quantity) || 0), 0)
)

const openAddModal = () => {
  modalMode.value = 'add'
  transferForm.value = { from_warehouse: '', to_warehouse: '', product: '', quantity: '' }
  showTransferModal.value = true
}

const saveTransfer = async () => {
  if (!transferForm.value.from_warehouse || !transferForm.value.to_warehouse || !transferForm.value.product || !transferForm.value.quantity) {
    alert('⚠️ Favor kompletadu formu transferénsia')
    return
  }

  try {
    await api.post('stock-transfers/', transferForm.value)
    showTransferModal.value = false
    await fetchTransfers()
    alert('✅ Perpindahan rai ho susesu')
  } catch (err) {
    console.error('❌ Erro salva:', err)
    alert('Erro salva transferénsia')
  }
}

onMounted(async () => {
  isLoading.value = true
  await fetchStoreProfile()
  await fetchWarehouses()
  await fetchProducts()
  await fetchTransfers()
  isLoading.value = false
})

const filteredTransfers = computed(() => {
  return transferList.value.filter(t =>
    t.from_warehouse_name?.toLowerCase().includes(filter.value.from.toLowerCase()) &&
    t.to_warehouse_name?.toLowerCase().includes(filter.value.to.toLowerCase()) &&
    t.product_name?.toLowerCase().includes(filter.value.product.toLowerCase())
  )
})

</script>


<template>
  <div class="bg-white border border-gray-200 rounded-lg shadow-sm text-sm flex flex-col h-full">
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b border-gray-300 bg-gradient-to-r from-teal-50 to-cyan-50">
      <div class="flex items-center gap-3">
        <img
          :src="store.logo_base64 || getLogoUrl(store.logo)"
          @error="e => e.target.src = 'http://127.0.0.1:8000/media/logos/default.jpg'"
          class="h-8 w-8 rounded-lg shadow-sm"
        />
        <div>
          <h1 class="text-xl font-bold text-gray-800">🔄 Stock Transfers</h1>
          <p class="text-sm text-gray-600">Manage stock transfers between warehouses</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button @click="openAddModal" class="px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-lg shadow-sm transition-colors">
          <span class="text-sm font-medium">➕ New Transfer</span>
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="p-4 bg-gray-50 border-b border-gray-200">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <!-- Total Transfers Card -->
        <div class="bg-gradient-to-r from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-blue-600">Total Transfers</p>
              <p class="text-xl font-bold text-blue-800">{{ totalTransfers }}</p>
            </div>
            <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <span class="text-blue-600 text-lg">🔄</span>
            </div>
          </div>
        </div>
        
        <!-- Pending Transfers Card -->
        <div class="bg-gradient-to-r from-yellow-50 to-yellow-100 border border-yellow-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-yellow-600">Pending Transfers</p>
              <p class="text-xl font-bold text-yellow-800">{{ pendingTransfers }}</p>
            </div>
            <div class="w-10 h-10 bg-yellow-100 rounded-full flex items-center justify-center">
              <span class="text-yellow-600 text-lg">⏳</span>
            </div>
          </div>
        </div>

        <!-- Completed Transfers Card -->
        <div class="bg-gradient-to-r from-green-50 to-green-100 border border-green-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-green-600">Completed Transfers</p>
              <p class="text-xl font-bold text-green-800">{{ completedTransfers }}</p>
            </div>
            <div class="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
              <span class="text-green-600 text-lg">✅</span>
            </div>
          </div>
        </div>

        <!-- Total Quantity Card -->
        <div class="bg-gradient-to-r from-purple-50 to-purple-100 border border-purple-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-purple-600">Total Quantity</p>
              <p class="text-xl font-bold text-purple-800">{{ totalQuantityTransferred.toLocaleString() }}</p>
            </div>
            <div class="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
              <span class="text-purple-600 text-lg">📊</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="p-4 bg-white border-b border-gray-200">
      <div class="flex flex-wrap items-center gap-3">
        <div class="min-w-[180px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">From Warehouse</label>
          <input 
            v-model="filter.from" 
            type="text" 
            placeholder="Search from warehouse..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
          />
        </div>
        
        <div class="min-w-[180px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">To Warehouse</label>
          <input 
            v-model="filter.to" 
            type="text" 
            placeholder="Search to warehouse..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
          />
        </div>
        
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Product</label>
          <input 
            v-model="filter.product" 
            type="text" 
            placeholder="Search product..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
          />
        </div>

        <div class="flex items-end gap-2">
          <button @click="clearFilters" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
            Clear Filters
          </button>
          <button @click="exportData" class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors">
            📊 Export
          </button>
          <button @click="refresh" class="px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-lg transition-colors">
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
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">From Warehouse</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">To Warehouse</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Product</th>
                <th class="px-4 py-3 text-center text-xs font-semibold text-gray-700 uppercase tracking-wider">Quantity</th>
                <th class="px-4 py-3 text-center text-xs font-semibold text-gray-700 uppercase tracking-wider">Status</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Notes</th>
                <th class="px-4 py-3 text-center text-xs font-semibold text-gray-700 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>

            <tbody class="divide-y divide-gray-200">
              <tr v-if="isLoading">
                <td colspan="7" class="px-4 py-12 text-center text-gray-500">
                  <div class="flex flex-col items-center">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600 mb-2"></div>
                    <p>Loading transfers...</p>
                  </div>
                </td>
              </tr>
              
              <tr v-else-if="filteredTransfers.length === 0">
                <td colspan="7" class="px-4 py-12 text-center text-gray-500">
                  <div class="flex flex-col items-center">
                    <span class="text-4xl mb-2">🔄</span>
                    <p class="text-lg font-medium mb-1">No transfers found</p>
                    <p class="text-sm">Try adjusting your filters or create a new transfer</p>
                  </div>
                </td>
              </tr>
              
              <tr v-else v-for="(t, idx) in filteredTransfers" :key="idx" class="hover:bg-gray-50 transition-colors">
                <td class="px-4 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="w-2 h-2 rounded-full bg-red-500 mr-2"></div>
                    <div class="text-sm font-medium text-gray-900">{{ t.from_warehouse_name || 'Unknown' }}</div>
                  </div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="w-2 h-2 rounded-full bg-green-500 mr-2"></div>
                    <div class="text-sm font-medium text-gray-900">{{ t.to_warehouse_name || 'Unknown' }}</div>
                  </div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900">{{ t.product_name || 'No name' }}</div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap text-center">
                  <span class="inline-flex px-2 py-1 text-sm font-semibold rounded-full bg-blue-100 text-blue-800">
                    {{ (t.quantity || 0).toLocaleString() }}
                  </span>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap text-center">
                  <span 
                    class="inline-flex px-2 py-1 text-xs font-medium rounded-full"
                    :class="{
                      'bg-green-100 text-green-800': t.status === 'completed',
                      'bg-yellow-100 text-yellow-800': t.status === 'pending' || !t.status,
                      'bg-red-100 text-red-800': t.status === 'cancelled',
                      'bg-gray-100 text-gray-800': !['completed', 'pending', 'cancelled'].includes(t.status)
                    }"
                  >
                    {{ t.status === 'completed' ? '✅ Completed' : 
                       t.status === 'cancelled' ? '❌ Cancelled' : 
                       '⏳ Pending' }}
                  </span>
                </td>
                
                <td class="px-4 py-4">
                  <div class="text-sm text-gray-900 max-w-xs truncate" :title="t.note">
                    {{ t.note || 'No notes' }}
                  </div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap text-center">
                  <div class="flex items-center justify-center space-x-2">
                    <button 
                      @click="viewTransfer(t)"
                      class="text-blue-600 hover:text-blue-800 font-medium text-sm"
                      title="View Details"
                    >
                      👁️
                    </button>
                    <button 
                      @click="editTransfer(t)"
                      class="text-yellow-600 hover:text-yellow-800 font-medium text-sm"
                      title="Edit Transfer"
                    >
                      ✏️
                    </button>
                    <button 
                      @click="cancelTransfer(t)"
                      class="text-red-600 hover:text-red-800 font-medium text-sm"
                      title="Cancel Transfer"
                      v-if="t.status !== 'completed' && t.status !== 'cancelled'"
                    >
                      ❌
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    <!-- New Transfer Modal -->
    <div v-if="showTransferModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div class="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4">
        <div class="flex items-center justify-between p-6 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">🔄 New Stock Transfer</h3>
          <button @click="showTransferModal = false" class="text-gray-400 hover:text-gray-600 transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        
        <div class="p-6">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">From Warehouse *</label>
              <select v-model="transferForm.from_warehouse" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent">
                <option value="">Select source warehouse...</option>
                <option v-for="w in warehouses" :key="w.id" :value="w.id">{{ w.name }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">To Warehouse *</label>
              <select v-model="transferForm.to_warehouse" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent">
                <option value="">Select destination warehouse...</option>
                <option v-for="w in warehouses" :key="w.id" :value="w.id" :disabled="w.id === transferForm.from_warehouse">{{ w.name }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Product *</label>
              <select v-model="transferForm.product" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent">
                <option value="">Select product to transfer...</option>
                <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }} - {{ p.sku || 'No SKU' }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Quantity *</label>
              <input 
                type="number" 
                v-model="transferForm.quantity" 
                min="1" 
                placeholder="Enter quantity to transfer..."
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent" 
              />
            </div>
          </div>
        </div>
        
        <div class="flex items-center justify-end p-6 border-t border-gray-200 space-x-3">
          <button 
            @click="showTransferModal = false" 
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-teal-500 transition-colors"
          >
            Cancel
          </button>
          <button 
            @click="saveTransfer" 
            class="px-4 py-2 text-sm font-medium text-white bg-teal-600 border border-transparent rounded-lg hover:bg-teal-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-teal-500 transition-colors"
            :disabled="!transferForm.from_warehouse || !transferForm.to_warehouse || !transferForm.product || !transferForm.quantity"
          >
            Create Transfer
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
          Showing {{ filteredTransfers.length }} transfer{{ filteredTransfers.length !== 1 ? 's' : '' }}
          <span v-if="pendingTransfers > 0" class="ml-2 text-yellow-600 font-medium">
            ({{ pendingTransfers }} pending)
          </span>
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
  --tw-ring-color: rgb(20 184 166 / 0.5);
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

