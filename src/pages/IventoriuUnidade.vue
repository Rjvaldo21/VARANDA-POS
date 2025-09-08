<script setup>
import { ref, computed, onMounted } from 'vue'
import FooterActions from '@/components/pos/FooterActions.vue'
import api, { baseURL } from '@/axios'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const store = ref({
  name: '',
  address: '',
  logo: '',
  version: '',
  location: ''
})

const units = ref([])
const loading = ref(false)
const saving = ref(false)
const searchFilter = ref('')
const perPage = ref(10)

const showModal = ref(false)
const selectedUnit = ref(null)
const isEditing = ref(false)

const unitForm = ref({
  name: ''
})

// Validation states
const fieldErrors = ref({})
const fieldValidation = ref({})
const formErrors = ref([])

const formattedAddress = computed(() =>
  store.value.address ? store.value.address.replace(/\n/g, '<br />') : ''
)

const getLogoUrl = (path) => {
  if (!path) return ''
  return path.startsWith('http') ? path : `${baseURL.replace("/api/", "")}${path}`
}

const filteredUnits = computed(() => {
  return units.value.filter(unit => {
    const searchText = searchFilter.value.toLowerCase()
    return unit.name?.toLowerCase().includes(searchText)
  })
})

const clearValidation = () => {
  fieldErrors.value = {}
  fieldValidation.value = {}
  formErrors.value = []
}

const resetForm = () => {
  unitForm.value = {
    name: ''
  }
  isEditing.value = false
  selectedUnit.value = null
  clearValidation()
}

const addUnit = () => {
  resetForm()
  showModal.value = true
}

const editItem = (unit) => {
  if (!unit) {
    alert('⚠️ Please select a unit first')
    return
  }
  selectedUnit.value = unit
  unitForm.value = {
    name: unit.name || ''
  }
  isEditing.value = true
  clearValidation()
  showModal.value = true
}

const deleteItem = async (unit) => {
  if (!unit) {
    alert('⚠️ Please select a unit first')
    return
  }
  if (!confirm(`Delete unit "${unit.name}"?`)) return
  
  try {
    const token = localStorage.getItem('token')
    await api.delete(`units/${unit.id}/`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    alert('✅ Unit deleted successfully')
    selectedUnit.value = null
    await refresh()
  } catch (err) {
    console.error('❌ Failed to delete unit:', err)
    alert('Failed to delete unit')
  }
}

const fetchUnits = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await api.get('units/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    units.value = res.data
    selectedUnit.value = null
  } catch (error) {
    console.error('Failed to fetch units:', error)
  } finally {
    loading.value = false
  }
}

const saveUnit = async () => {
  // Validation
  if (!unitForm.value.name) {
    alert('Please fill unit name.')
    return
  }

  saving.value = true
  try {
    const token = localStorage.getItem('token')
    const headers = { Authorization: `Bearer ${token}` }

    if (isEditing.value) {
      // Update existing unit
      await api.put(`units/${selectedUnit.value.id}/`, unitForm.value, { headers })
      alert('✅ Unit updated successfully')
    } else {
      // Create new unit
      await api.post('units/', unitForm.value, { headers })
      alert('✅ Unit created successfully')
    }
    
    showModal.value = false
    await refresh()
  } catch (err) {
    console.error('❌ Failed to save unit:', err)
    if (err.response && err.response.data) {
      alert('Failed to save unit:\n' + JSON.stringify(err.response.data, null, 2))
    } else {
      alert('Failed to save unit. Please check your data.')
    }
  } finally {
    saving.value = false
  }
}

const refresh = async () => {
  await fetchUnits()
}

onMounted(async () => {
  try {
    const res = await api.get('store-profile/')
    if (res.data && res.data.length > 0) {
      store.value = res.data[0]
    }
  } catch (err) {
    console.error('Failed to fetch store profile:', err)
  }
  
  await fetchUnits()
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
      <h1 class="text-lg font-semibold">UNIT MANAGEMENT</h1>
    </div>

    <div class="p-4">
      <!-- Filters -->
      <div class="mb-6 flex flex-wrap items-center gap-4">
        <div class="form-group mb-0 flex-1">
          <label class="block text-sm font-medium text-gray-700 mb-1">Search Units</label>
          <input 
            v-model="searchFilter" 
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
            placeholder="Search by unit name..."
          />
        </div>
        <button 
          @click="addUnit" 
          class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          Add Unit
        </button>
      </div>

      <!-- Units Table -->
      <div class="overflow-x-auto border border-gray-300 rounded-lg">
        <table class="w-full border-collapse text-sm">
          <thead class="bg-gray-50">
            <tr>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Unit Name</th>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-if="loading">
              <td colspan="2" class="px-4 py-8 text-center text-gray-500">Loading units...</td>
            </tr>
            <tr v-else-if="filteredUnits.length === 0">
              <td colspan="2" class="px-4 py-8 text-center text-gray-500">
                <svg class="mx-auto h-12 w-12 text-gray-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>
                </svg>
                <p>No units found</p>
              </td>
            </tr>
            <tr v-else v-for="unit in filteredUnits" :key="unit.id" class="hover:bg-gray-50" 
                :class="{ 'bg-blue-50': selectedUnit?.id === unit.id }"
                @click="selectedUnit = unit">
              <td class="px-4 py-3">
                <div class="font-medium text-gray-900">{{ unit.name }}</div>
              </td>
              <td class="px-4 py-3">
                <div class="flex space-x-2">
                  <button 
                    @click="editItem(unit)"
                    class="text-blue-600 hover:text-blue-900 transition-colors"
                    title="Edit Unit"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                    </svg>
                  </button>
                  <button 
                    @click="deleteItem(unit)"
                    class="text-red-600 hover:text-red-900 transition-colors"
                    title="Delete Unit"
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

    <!-- Create/Edit Unit Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto">
        <!-- Header -->
        <div class="flex items-center justify-between p-6 border-b border-gray-200">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-xl font-semibold text-gray-900">
                {{ isEditing ? 'Edit Unit' : 'Add New Unit' }}
              </h3>
              <p class="text-sm text-gray-500">
                {{ isEditing ? 'Update unit information' : 'Create a new measurement unit' }}
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
        <form @submit.prevent="saveUnit" class="p-6">
          <!-- Unit Information -->
          <div class="mb-8">
            <h4 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <span class="w-7 h-7 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-semibold mr-3">1</span>
              Unit Information
            </h4>
            
            <div class="space-y-6">
              <!-- Unit Name -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Unit Name *</label>
                <input 
                  v-model="unitForm.name" 
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="Enter unit name (e.g., pieces, kg, liter)"
                  required
                />
                <p class="text-sm text-gray-500">Name of the measurement unit</p>
              </div>
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
              {{ saving ? 'Saving...' : (isEditing ? 'Update Unit' : 'Create Unit') }}
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