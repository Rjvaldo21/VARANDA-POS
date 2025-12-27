<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import api, { baseURL } from '@/axios'
import FooterActions from '@/components/pos/FooterActions.vue'

const { t } = useI18n()

const store = ref({
  name: '',
  address: '',
  logo: '',
  logo_base64: '',
  version: '',
  location: ''
})

const selectedMovement = ref(null)

const showModal = ref(false)
const modalMode = ref('add')

const movementForm = ref({
  product: '',
  warehouse: '',
  quantity: '',
  movement_type: 'in',
  note: ''
})

const openAdd = () => {
  modalMode.value = 'add'
  movementForm.value = {
    product: '',
    warehouse: '',
    quantity: '',
    movement_type: 'in',
    note: ''
  }
  showModal.value = true
}

const openEdit = () => {
  if (!selectedMovement.value) {
    alert('⚠️ Favor seleziona movimentu dulu')
    return
  }
  modalMode.value = 'edit'
  movementForm.value = { ...selectedMovement.value }
  showModal.value = true
}

const deleteMovement = async () => {
  if (!selectedMovement.value) {
    alert('⚠️ Favor seleziona movimentu dulu')
    return
  }
  if (!confirm('Apaga movimentu nebee seleziona?')) return

  try {
    await api.delete(`stock-movements/${selectedMovement.value.id}/`)
    await fetchMovements()
    selectedMovement.value = null
    alert('✅ Movimentu apaga ho susesu')
  } catch (err) {
    console.error(err)
    alert('❌ Gagal apaga movimentu')
  }
}

const saveMovement = async () => {
  try {
    if (modalMode.value === 'add') {
      await api.post('stock-movements/', movementForm.value)
    } else {
      await api.put(`stock-movements/${selectedMovement.value.id}/`, movementForm.value)
    }
    await fetchMovements()
    showModal.value = false
    selectedMovement.value = null
    alert('✅ Movimentu rai ho susesu')
  } catch (err) {
    console.error(err)
    alert('❌ Gagal rai movimentu')
  }
}

const movementList = ref([])
const filter = ref({ product: '', warehouse: '', type: '' })
const isLoading = ref(false)
const perPage = ref(10)

const getLogoUrl = (path) => {
  if (!path) return ''
  return path.startsWith('http') ? path : `baseURL.replace("/api/", "")${path}`
}

const fetchStoreProfile = async () => {
  const res = await api.get('store-profile/')
  if (res.data.length > 0) store.value = res.data[0]
}

const fetchMovements = async () => {
  const res = await api.get('stock-movements/')
  movementList.value = res.data
}

const refresh = async () => {
  await fetchMovements()
}

// New UI functions
const clearFilters = () => {
  filter.value = { product: '', warehouse: '', type: '' }
}

const exportData = () => {
  const headers = ['Date','Product','Warehouse','Movement Type','Quantity','Notes']
  const csvData = filteredMovements.value.map(movement => [
    new Date(movement.created_at).toLocaleString(),
    movement.product_name || '',
    movement.warehouse_name || '',
    movement.movement_type === 'in' ? 'Stock In' : 'Stock Out',
    movement.quantity || 0,
    movement.note || ''
  ])
  
  const csv = [headers.join(','), ...csvData.map(row => row.join(','))].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'stock_movements_report.csv'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const viewMovement = (movement) => {
  selectedMovement.value = movement
  alert(`Movement details: ${movement?.product_name || 'Unknown Product'} - ${movement?.movement_type === 'in' ? 'Stock In' : 'Stock Out'}`)
}

// Summary computed properties
const totalMovements = computed(() => filteredMovements.value.length)
const stockInMovements = computed(() => 
  filteredMovements.value.filter(m => m.movement_type === 'in').length
)
const stockOutMovements = computed(() => 
  filteredMovements.value.filter(m => m.movement_type === 'out').length
)
const totalQuantityMoved = computed(() => 
  filteredMovements.value.reduce((sum, m) => sum + (Number(m.quantity) || 0), 0)
)

onMounted(async () => {
  isloading.value = true 
  await nextTick()
  await fetchStoreProfile()
  await fetchMovements()
  isLoading.value = false
})

const filteredMovements = computed(() => {
  return movementList.value.filter(m =>
    m.product_name?.toLowerCase().includes(filter.value.product.toLowerCase()) &&
    m.warehouse_name?.toLowerCase().includes(filter.value.warehouse.toLowerCase()) &&
    m.movement_type?.toLowerCase().includes(filter.value.type.toLowerCase())
  )
})
</script>


<template>
  <div class="bg-white border border-gray-200 rounded-lg shadow-sm text-sm flex flex-col h-full">
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b border-gray-300 bg-gradient-to-r from-indigo-50 to-purple-50">
      <div class="flex items-center gap-3">
        <img
          :src="store.logo_base64 || getLogoUrl(store.logo)"
          @error="e => e.target.src = baseURL.replace('/api/', '') + '/media/logos/default.jpg'"
          class="h-8 w-8 rounded-lg shadow-sm"
        />
        <div>
          <h1 class="text-xl font-bold text-gray-800">📊 {{ t('inventory.stockMovements') }}</h1>
          <p class="text-sm text-gray-600">{{ t('inventory.stockMovements') }}</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button @click="openAdd" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg shadow-sm transition-colors">
          <span class="text-sm font-medium">➕ {{ t('inventory.newMovement') }}</span>
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="p-4 bg-gray-50 border-b border-gray-200">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <!-- Total Movements Card -->
        <div class="bg-gradient-to-r from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-blue-600">{{ t('inventory.totalMovements') }}</p>
              <p class="text-xl font-bold text-blue-800">{{ totalMovements }}</p>
            </div>
            <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <span class="text-blue-600 text-lg">📊</span>
            </div>
          </div>
        </div>
        
        <!-- Stock In Movements Card -->
        <div class="bg-gradient-to-r from-green-50 to-green-100 border border-green-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-green-600">{{ t('inventory.stockIn') }}</p>
              <p class="text-xl font-bold text-green-800">{{ stockInMovements }}</p>
            </div>
            <div class="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
              <span class="text-green-600 text-lg">⬆️</span>
            </div>
          </div>
        </div>

        <!-- Stock Out Movements Card -->
        <div class="bg-gradient-to-r from-red-50 to-red-100 border border-red-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-red-600">{{ t('inventory.stockOut') }}</p>
              <p class="text-xl font-bold text-red-800">{{ stockOutMovements }}</p>
            </div>
            <div class="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
              <span class="text-red-600 text-lg">⬇️</span>
            </div>
          </div>
        </div>

        <!-- Total Quantity Card -->
        <div class="bg-gradient-to-r from-purple-50 to-purple-100 border border-purple-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-purple-600">{{ t('inventory.totalQuantity') }}</p>
              <p class="text-xl font-bold text-purple-800">{{ totalQuantityMoved.toLocaleString() }}</p>
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
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Search by Product</label>
          <input 
            v-model="filter.product" 
            type="text" 
            placeholder="Enter product name..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
        </div>
        
        <div class="min-w-[180px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Search by Warehouse</label>
          <input 
            v-model="filter.warehouse" 
            type="text" 
            placeholder="Enter warehouse name..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
        </div>
        
        <div class="min-w-[140px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Movement Type</label>
          <select v-model="filter.type" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
            <option value="">All Types</option>
            <option value="in">Stock In</option>
            <option value="out">Stock Out</option>
          </select>
        </div>

        <div class="flex items-end gap-2">
          <button @click="clearFilters" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
            Clear Filters
          </button>
          <button @click="exportData" class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors">
            📊 Export
          </button>
          <button @click="refresh" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors">
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
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Product</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Warehouse</th>
                <th class="px-4 py-3 text-center text-xs font-semibold text-gray-700 uppercase tracking-wider">Movement Type</th>
                <th class="px-4 py-3 text-center text-xs font-semibold text-gray-700 uppercase tracking-wider">Quantity</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Notes</th>
                <th class="px-4 py-3 text-center text-xs font-semibold text-gray-700 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>

            <tbody class="divide-y divide-gray-200">
              <tr v-if="isLoading">
                <td colspan="7" class="px-4 py-12 text-center text-gray-500">
                  <div class="flex flex-col items-center">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mb-2"></div>
                    <p>Loading movements...</p>
                  </div>
                </td>
              </tr>
              
              <tr v-else-if="filteredMovements.length === 0">
                <td colspan="7" class="px-4 py-12 text-center text-gray-500">
                  <div class="flex flex-col items-center">
                    <span class="text-4xl mb-2">📊</span>
                    <p class="text-lg font-medium mb-1">No stock movements found</p>
                    <p class="text-sm">Try adjusting your filters or create a new movement</p>
                  </div>
                </td>
              </tr>
              
              <tr v-else v-for="(m, idx) in filteredMovements" :key="idx" 
                  class="hover:bg-gray-50 transition-colors cursor-pointer"
                  :class="{ 'bg-indigo-50 border-l-4 border-l-indigo-400': selectedMovement?.id === m.id }"
                  @click="selectedMovement = m">
                <td class="px-4 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">{{ new Date(m.created_at).toLocaleString() }}</div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900">{{ m.product_name || 'Unknown Product' }}</div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">{{ m.warehouse_name || 'Unknown Warehouse' }}</div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap text-center">
                  <span 
                    class="inline-flex px-2 py-1 text-xs font-medium rounded-full"
                    :class="{
                      'bg-green-100 text-green-800': m.movement_type === 'in',
                      'bg-red-100 text-red-800': m.movement_type === 'out'
                    }"
                  >
                    {{ m.movement_type === 'in' ? '⬆️ Stock In' : '⬇️ Stock Out' }}
                  </span>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap text-center">
                  <span class="inline-flex px-2 py-1 text-sm font-semibold rounded-full bg-gray-100 text-gray-800">
                    {{ (m.quantity || 0).toLocaleString() }}
                  </span>
                </td>
                
                <td class="px-4 py-4">
                  <div class="text-sm text-gray-900 max-w-xs truncate" :title="m.note">
                    {{ m.note || 'No notes' }}
                  </div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap text-center">
                  <div class="flex items-center justify-center space-x-2">
                    <button 
                      @click.stop="viewMovement(m)"
                      class="text-blue-600 hover:text-blue-800 font-medium text-sm"
                      title="View Details"
                    >
                      👁️
                    </button>
                    <button 
                      @click.stop="openEdit(); selectedMovement = m"
                      class="text-yellow-600 hover:text-yellow-800 font-medium text-sm"
                      title="Edit Movement"
                    >
                      ✏️
                    </button>
                    <button 
                      @click.stop="selectedMovement = m; deleteMovement()"
                      class="text-red-600 hover:text-red-800 font-medium text-sm"
                      title="Delete Movement"
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


    <!-- New Movement Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div class="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4">
        <div class="flex items-center justify-between p-6 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">
            {{ modalMode === 'add' ? '📊 New Stock Movement' : '✏️ Edit Stock Movement' }}
          </h3>
          <button @click="showModal = false" class="text-gray-400 hover:text-gray-600 transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        
        <div class="p-6">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Product ID *</label>
              <input 
                v-model="movementForm.product" 
                type="number" 
                min="1" 
                placeholder="Enter product ID..."
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent" 
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Warehouse ID *</label>
              <input 
                v-model="movementForm.warehouse" 
                type="number" 
                min="1" 
                placeholder="Enter warehouse ID..."
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent" 
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Quantity *</label>
              <input 
                v-model="movementForm.quantity" 
                type="number" 
                min="1" 
                placeholder="Enter quantity..."
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent" 
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Movement Type *</label>
              <select v-model="movementForm.movement_type" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
                <option value="in">⬆️ Stock In</option>
                <option value="out">⬇️ Stock Out</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Notes</label>
              <textarea 
                v-model="movementForm.note" 
                rows="3" 
                placeholder="Enter movement notes (optional)..."
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
              ></textarea>
            </div>
          </div>
        </div>
        
        <div class="flex items-center justify-end p-6 border-t border-gray-200 space-x-3">
          <button 
            @click="showModal = false" 
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
          >
            Cancel
          </button>
          <button 
            @click="saveMovement" 
            class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
            :disabled="!movementForm.product || !movementForm.warehouse || !movementForm.quantity"
          >
            {{ modalMode === 'add' ? 'Create Movement' : 'Update Movement' }}
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
          Showing {{ filteredMovements.length }} movement{{ filteredMovements.length !== 1 ? 's' : '' }}
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
  --tw-ring-color: rgb(99 102 241 / 0.5);
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

