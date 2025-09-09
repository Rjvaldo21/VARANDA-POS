<script setup>
import { ref, computed, onMounted } from 'vue'
import api, { baseURL } from '@/axios'
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
  return path.startsWith('http') ? path : `${baseURL.replace('/api/', '')}${path}`
}

const fetchStoreProfile = async () => {
  try {
    const res = await api.get('store-profile/')
    if (res.data && res.data.length > 0) {
      store.value = res.data[0]
    }
  } catch (err) {
    console.error('❌ Gagal fetch profil loja:', err)
  }
}

const fetchStockData = async () => {
  try {
    const res = await api.get('stocks/')
    stocks.value = res.data
  } catch (err) {
    console.error('❌ Gagal fetch stok gudang:', err)
  }
}

const refresh = async () => {
  await fetchStockData()
}

// New UI functions
const clearFilters = () => {
  filter.value = { warehouse: '', product: '', barcode: '' }
}

const exportData = () => {
  const headers = ['Warehouse','Product Name','SKU/Barcode','Category','Unit','Current Stock','Minimum Stock','Stock Status']
  const csvData = filteredStock.value.map(item => [
    item.warehouse_name || '',
    item.product_name || '',
    item.barcode || '',
    item.category || '',
    item.unit || '',
    item.current_stock || 0,
    item.min_stock || 0,
    (item.current_stock || 0) <= (item.min_stock || 0) ? 'Low Stock' : 'In Stock'
  ])
  
  const csv = [headers.join(','), ...csvData.map(row => row.join(','))].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'warehouse_stock_report.csv'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const viewStock = (item) => {
  selectedStock.value = item
  alert(`Stock details for: ${item?.product_name || 'Unknown Product'}`)
}

const adjustStock = (item) => {
  alert(`Adjust stock for: ${item?.product_name || 'Unknown Product'}`)
}

// Summary computed properties
const totalProducts = computed(() => filteredStock.value.length)
const lowStockItems = computed(() => 
  filteredStock.value.filter(item => (item.current_stock || 0) <= (item.min_stock || 0))
)
const totalStockValue = computed(() => 
  filteredStock.value.reduce((sum, item) => sum + (item.current_stock || 0), 0)
)
const warehouses = computed(() => 
  [...new Set(filteredStock.value.map(item => item.warehouse_name))]
)

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
  <div class="bg-white border border-gray-200 rounded-lg shadow-sm text-sm flex flex-col h-full">
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b border-gray-300 bg-gradient-to-r from-orange-50 to-amber-50">
      <div class="flex items-center gap-3">
        <img
          :src="store.logo_base64 || getLogoUrl(store.logo)"
          @error="e => e.target.src = baseURL.replace('/api/', '') + '/media/logos/default.jpg'"
          class="h-8 w-8 rounded-lg shadow-sm"
        />
        <div>
          <h1 class="text-xl font-bold text-gray-800">📦 Warehouse Stock</h1>
          <p class="text-sm text-gray-600">Monitor stock levels across warehouses</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button @click="exportData" class="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg shadow-sm transition-colors">
          <span class="text-sm font-medium">📊 Export Stock</span>
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="p-4 bg-gray-50 border-b border-gray-200">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <!-- Total Products Card -->
        <div class="bg-gradient-to-r from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-blue-600">Total Products</p>
              <p class="text-xl font-bold text-blue-800">{{ totalProducts }}</p>
            </div>
            <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <span class="text-blue-600 text-lg">📦</span>
            </div>
          </div>
        </div>
        
        <!-- Low Stock Items Card -->
        <div class="bg-gradient-to-r from-red-50 to-red-100 border border-red-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-red-600">Low Stock Items</p>
              <p class="text-xl font-bold text-red-800">{{ lowStockItems.length }}</p>
            </div>
            <div class="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
              <span class="text-red-600 text-lg">⚠️</span>
            </div>
          </div>
        </div>

        <!-- Total Stock Units Card -->
        <div class="bg-gradient-to-r from-green-50 to-green-100 border border-green-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-green-600">Total Stock Units</p>
              <p class="text-xl font-bold text-green-800">{{ totalStockValue.toLocaleString() }}</p>
            </div>
            <div class="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
              <span class="text-green-600 text-lg">📊</span>
            </div>
          </div>
        </div>

        <!-- Active Warehouses Card -->
        <div class="bg-gradient-to-r from-purple-50 to-purple-100 border border-purple-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-purple-600">Active Warehouses</p>
              <p class="text-xl font-bold text-purple-800">{{ warehouses.length }}</p>
            </div>
            <div class="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
              <span class="text-purple-600 text-lg">🏢</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="p-4 bg-white border-b border-gray-200">
      <div class="flex flex-wrap items-center gap-3">
        <div class="min-w-[180px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Search by Warehouse</label>
          <input 
            v-model="filter.warehouse" 
            type="text" 
            placeholder="Enter warehouse name..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
          />
        </div>
        
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Search by Product</label>
          <input 
            v-model="filter.product" 
            type="text" 
            placeholder="Enter product name..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
          />
        </div>
        
        <div class="min-w-[180px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Search by SKU/Barcode</label>
          <input 
            v-model="filter.barcode" 
            type="text" 
            placeholder="Enter SKU or barcode..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
          />
        </div>

        <div class="flex items-end gap-2">
          <button @click="clearFilters" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
            Clear Filters
          </button>
          <button @click="refresh" class="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg transition-colors">
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
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Warehouse</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Product</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">SKU/Barcode</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Category</th>
                <th class="px-4 py-3 text-center text-xs font-semibold text-gray-700 uppercase tracking-wider">Current Stock</th>
                <th class="px-4 py-3 text-center text-xs font-semibold text-gray-700 uppercase tracking-wider">Min Stock</th>
                <th class="px-4 py-3 text-center text-xs font-semibold text-gray-700 uppercase tracking-wider">Status</th>
                <th class="px-4 py-3 text-center text-xs font-semibold text-gray-700 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>

            <tbody class="divide-y divide-gray-200">
              <tr v-if="isLoading">
                <td colspan="8" class="px-4 py-12 text-center text-gray-500">
                  <div class="flex flex-col items-center">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600 mb-2"></div>
                    <p>Loading stock data...</p>
                  </div>
                </td>
              </tr>
              
              <tr v-else-if="filteredStock.length === 0">
                <td colspan="8" class="px-4 py-12 text-center text-gray-500">
                  <div class="flex flex-col items-center">
                    <span class="text-4xl mb-2">📦</span>
                    <p class="text-lg font-medium mb-1">No stock data found</p>
                    <p class="text-sm">Try adjusting your filters or refresh the data</p>
                  </div>
                </td>
              </tr>
              
              <tr v-else v-for="item in filteredStock" :key="item.id" 
                  class="hover:bg-gray-50 transition-colors cursor-pointer"
                  :class="{ 'bg-yellow-50 border-l-4 border-l-yellow-400': selectedStock?.id === item.id }"
                  @click="selectedStock = item">
                <td class="px-4 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="w-2 h-2 rounded-full mr-2" :class="(item.current_stock || 0) <= (item.min_stock || 0) ? 'bg-red-500' : 'bg-green-500'"></div>
                    <div class="text-sm font-medium text-gray-900">{{ item.warehouse_name || 'Unknown' }}</div>
                  </div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap">
                  <div>
                    <div class="text-sm font-medium text-gray-900">{{ item.product_name || 'No name' }}</div>
                    <div class="text-xs text-gray-500">Unit: {{ item.unit || 'N/A' }}</div>
                  </div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900 font-mono">{{ item.barcode || 'N/A' }}</div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">{{ item.category || 'Uncategorized' }}</div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap text-center">
                  <span class="inline-flex px-2 py-1 text-sm font-semibold rounded-full" 
                        :class="(item.current_stock || 0) > (item.min_stock || 0) ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                    {{ (item.current_stock || 0).toLocaleString() }}
                  </span>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap text-center">
                  <div class="text-sm text-gray-900">{{ (item.min_stock || 0).toLocaleString() }}</div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap text-center">
                  <span 
                    class="inline-flex px-2 py-1 text-xs font-medium rounded-full"
                    :class="{
                      'bg-green-100 text-green-800': (item.current_stock || 0) > (item.min_stock || 0),
                      'bg-red-100 text-red-800': (item.current_stock || 0) <= (item.min_stock || 0)
                    }"
                  >
                    {{ (item.current_stock || 0) <= (item.min_stock || 0) ? '⚠️ Low Stock' : '✅ In Stock' }}
                  </span>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap text-center">
                  <div class="flex items-center justify-center space-x-2">
                    <button 
                      @click.stop="viewStock(item)"
                      class="text-blue-600 hover:text-blue-800 font-medium text-sm"
                      title="View Details"
                    >
                      👁️
                    </button>
                    <button 
                      @click.stop="adjustStock(item)"
                      class="text-yellow-600 hover:text-yellow-800 font-medium text-sm"
                      title="Adjust Stock"
                    >
                      📝
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
          Showing {{ filteredStock.length }} stock item{{ filteredStock.length !== 1 ? 's' : '' }}
          <span v-if="lowStockItems.length > 0" class="ml-2 text-red-600 font-medium">
            ({{ lowStockItems.length }} low stock)
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
  --tw-ring-color: rgb(234 88 12 / 0.5);
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
</style>