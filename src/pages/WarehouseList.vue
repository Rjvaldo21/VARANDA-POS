<script setup>
import { ref, computed, onMounted } from 'vue'
import api, { baseURL } from '@/axios'
import FooterActions from '@/components/pos/FooterActions.vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const warehouses = ref([])
const store = ref({ logo: '', logo_base64: '', name: '' })

const loading = ref(false)
const saving = ref(false)
const searchFilter = ref('')
const selectedWarehouse = ref(null)
const showModal = ref(false)
const isEditing = ref(false)
const perPage = ref(10)

const warehouseForm = ref({
  name: '',
  location: '',
  description: ''
})

// Validation states
const fieldErrors = ref({})
const fieldValidation = ref({})
const formErrors = ref([])

const getLogoUrl = (path) => {
  if (!path) return ''
  return path.startsWith('http') ? path : `${baseURL.replace("/api/", "")}${path}`
}

const filteredWarehouses = computed(() => {
  return warehouses.value.filter(warehouse => {
    const searchText = searchFilter.value.toLowerCase()
    return warehouse.name?.toLowerCase().includes(searchText) ||
           warehouse.location?.toLowerCase().includes(searchText) ||
           warehouse.description?.toLowerCase().includes(searchText)
  })
})

const clearValidation = () => {
  fieldErrors.value = {}
  fieldValidation.value = {}
  formErrors.value = []
}

const resetForm = () => {
  warehouseForm.value = {
    name: '',
    location: '',
    description: ''
  }
  isEditing.value = false
  selectedWarehouse.value = null
  clearValidation()
}

const fetchStore = async () => {
  try {
    const res = await api.get('store-profile/')
    if (res.data?.length > 0) {
      store.value = res.data[0]
    }
  } catch (err) {
    console.error('Error fetch store:', err)
  }
}

const fetchWarehouses = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await api.get('warehouses/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    warehouses.value = res.data
    selectedWarehouse.value = null
  } catch (err) {
    console.error('Failed to fetch warehouses:', err)
  } finally {
    loading.value = false
  }
}

const addWarehouse = () => {
  resetForm()
  showModal.value = true
}

const editItem = (warehouse) => {
  if (!warehouse) {
    alert('⚠️ Please select a warehouse first')
    return
  }
  selectedWarehouse.value = warehouse
  warehouseForm.value = {
    name: warehouse.name || '',
    location: warehouse.location || '',
    description: warehouse.description || ''
  }
  isEditing.value = true
  clearValidation()
  showModal.value = true
}

const saveWarehouse = async () => {
  // Validation
  if (!warehouseForm.value.name || !warehouseForm.value.location) {
    alert('Please fill warehouse name and location.')
    return
  }

  saving.value = true
  try {
    const token = localStorage.getItem('token')
    const headers = { Authorization: `Bearer ${token}` }

    if (isEditing.value) {
      // Update existing warehouse
      await api.put(`warehouses/${selectedWarehouse.value.id}/`, warehouseForm.value, { headers })
      alert('✅ Warehouse updated successfully')
    } else {
      // Create new warehouse
      await api.post('warehouses/', warehouseForm.value, { headers })
      alert('✅ Warehouse created successfully')
    }
    
    showModal.value = false
    await refresh()
  } catch (err) {
    console.error('❌ Failed to save warehouse:', err)
    if (err.response && err.response.data) {
      alert('Failed to save warehouse:\n' + JSON.stringify(err.response.data, null, 2))
    } else {
      alert('Failed to save warehouse. Please check your data.')
    }
  } finally {
    saving.value = false
  }
}

const deleteItem = async (warehouse) => {
  if (!warehouse) {
    alert('⚠️ Please select a warehouse first')
    return
  }
  if (!confirm(`Delete warehouse "${warehouse.name}"?`)) return
  
  try {
    const token = localStorage.getItem('token')
    await api.delete(`warehouses/${warehouse.id}/`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    alert('✅ Warehouse deleted successfully')
    selectedWarehouse.value = null
    await refresh()
  } catch (err) {
    console.error('❌ Failed to delete warehouse:', err)
    alert('Failed to delete warehouse')
  }
}

const refresh = async () => {
  await fetchWarehouses()
}

onMounted(async () => {
  await fetchStore()
  await fetchWarehouses()
})
</script>


<template>
  <div class="bg-white border border-gray-50 rounded-sm shadow text-sm flex flex-col h-full">
    <!-- Header -->
    <div class="flex items-center gap-2 p-2 border-b border-gray-300 bg-gray-50">
      <img
        :src="store.logo_base64 || getLogoUrl(store.logo)"
        @error="e => e.target.src = baseURL.replace('/api/', '') + '/media/logos/default.jpg'"
        class="h-6 w-6 rounded"
      />
      <h1 class="text-lg font-semibold">WAREHOUSE MANAGEMENT</h1>
    </div>

    <div class="p-4">
      <!-- Filters -->
      <div class="mb-6 flex flex-wrap items-center gap-4">
        <div class="form-group mb-0 flex-1">
          <label class="block text-sm font-medium text-gray-700 mb-1">Search Warehouses</label>
          <input 
            v-model="searchFilter" 
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
            placeholder="Search by name, location, or description..."
          />
        </div>
        <button 
          @click="addWarehouse" 
          class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          Add Warehouse
        </button>
      </div>

      <!-- Warehouses Table -->
      <div class="overflow-x-auto border border-gray-300 rounded-lg">
        <table class="w-full border-collapse text-sm">
          <thead class="bg-gray-50">
            <tr>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Warehouse Name</th>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Location</th>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Description</th>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-if="loading">
              <td colspan="4" class="px-4 py-8 text-center text-gray-500">Loading warehouses...</td>
            </tr>
            <tr v-else-if="filteredWarehouses.length === 0">
              <td colspan="4" class="px-4 py-8 text-center text-gray-500">
                <svg class="mx-auto h-12 w-12 text-gray-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                </svg>
                <p>No warehouses found</p>
              </td>
            </tr>
            <tr v-else v-for="warehouse in filteredWarehouses" :key="warehouse.id" class="hover:bg-gray-50" 
                :class="{ 'bg-blue-50': selectedWarehouse?.id === warehouse.id }"
                @click="selectedWarehouse = warehouse">
              <td class="px-4 py-3">
                <div class="font-medium text-gray-900">{{ warehouse.name }}</div>
              </td>
              <td class="px-4 py-3 text-sm text-gray-900">{{ warehouse.location || 'No location' }}</td>
              <td class="px-4 py-3 text-sm text-gray-900">{{ warehouse.description || 'No description' }}</td>
              <td class="px-4 py-3">
                <div class="flex space-x-2">
                  <button 
                    @click="editItem(warehouse)"
                    class="text-blue-600 hover:text-blue-900 transition-colors"
                    title="Edit Warehouse"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                    </svg>
                  </button>
                  <button 
                    @click="deleteItem(warehouse)"
                    class="text-red-600 hover:text-red-900 transition-colors"
                    title="Delete Warehouse"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Warehouse Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <!-- Header -->
        <div class="flex items-center justify-between p-6 border-b border-gray-200">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-xl font-semibold text-gray-900">
                {{ isEditing ? 'Edit Warehouse' : 'Add New Warehouse' }}
              </h3>
              <p class="text-sm text-gray-500">
                {{ isEditing ? 'Update warehouse information' : 'Create a new warehouse location' }}
              </p>
            </div>
          </div>
          <button @click="showModal = false" class="text-gray-400 hover:text-gray-600 transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <!-- Form -->
        <form @submit.prevent="saveWarehouse" class="p-6">
          <!-- Basic Information -->
          <div class="mb-8">
            <h4 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <span class="w-7 h-7 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-semibold mr-3">1</span>
              Basic Information
            </h4>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Warehouse Name -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Warehouse Name *</label>
                <input 
                  v-model="warehouseForm.name" 
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="Enter warehouse name"
                  required
                />
                <p class="text-sm text-gray-500">Name of the warehouse</p>
              </div>

              <!-- Location -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Location *</label>
                <input 
                  v-model="warehouseForm.location" 
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="Enter warehouse location"
                  required
                />
                <p class="text-sm text-gray-500">Physical location or address</p>
              </div>
            </div>
          </div>

          <!-- Additional Information -->
          <div class="mb-8">
            <h4 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <span class="w-7 h-7 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-semibold mr-3">2</span>
              Additional Information
            </h4>
            
            <div class="space-y-1">
              <label class="block text-sm font-medium text-gray-700">Description</label>
              <textarea 
                v-model="warehouseForm.description" 
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                placeholder="Enter warehouse description..."
              ></textarea>
              <p class="text-sm text-gray-500">Additional details about the warehouse</p>
            </div>
          </div>

          <!-- Form Actions -->
          <div class="flex items-center justify-between pt-6 border-t border-gray-200">
            <button 
              type="button" 
              @click="showModal = false" 
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              :disabled="saving"
              class="px-6 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
            >
              <svg v-if="saving" class="w-4 h-4 mr-2 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
              <svg v-else class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"></path>
              </svg>
              {{ saving ? 'Saving...' : (isEditing ? 'Update Warehouse' : 'Create Warehouse') }}
            </button>
          </div>
        </form>
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
