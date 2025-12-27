<script setup>
import { ref, computed, onMounted } from 'vue'
import api, { baseURL } from '@/axios'
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

const formattedAddress = computed(() =>
  store.value.address ? store.value.address.replace(/\n/g, '<br />') : ''
)

const getLogoUrl = (path) => {
  if (!path) return ''
  return path.startsWith('http') ? path : `${baseURL.replace("/api/", "")}${path}`
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
  }
})

// Cashier stations data
const stationList = ref([
  { 
    id: 1,
    code: 'CASHIER_01', 
    name: 'Cashier Station 1',
    location: 'Main Counter',
    status: 'active',
    last_used: '2025-01-07T10:30:00Z',
    user_assigned: 'John Doe'
  },
  { 
    id: 2,
    code: 'CASHIER_02', 
    name: 'Cashier Station 2',
    location: 'Secondary Counter',
    status: 'inactive',
    last_used: '2025-01-06T16:45:00Z',
    user_assigned: null
  }
])

const currentUser = ref({})
const loading = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const perPage = ref(10)
const selectedStation = ref(null)

// Modal states
const showStationModal = ref(false)
const editingStation = ref(null)

// Form data
const stationForm = ref({
  code: '',
  name: '',
  location: '',
  status: 'active',
  user_assigned: ''
})

// Computed properties
const filteredStations = computed(() => {
  let filtered = stationList.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(station => 
      station.name?.toLowerCase().includes(query) ||
      station.code?.toLowerCase().includes(query) ||
      station.location?.toLowerCase().includes(query)
    )
  }

  if (statusFilter.value) {
    filtered = filtered.filter(station => station.status === statusFilter.value)
  }

  return filtered
})

const canManageStations = computed(() => {
  return currentUser.value.profile?.can_manage_stations || true
})

// Methods
const loadStations = async () => {
  try {
    loading.value = true 
  await nextTick()
    // In a real app, this would be an API call
    // const response = await api.get('cashier-stations/')
    // stationList.value = response.data
  } catch (error) {
    console.error('Error loading stations:', error)
    alert('Error loading stations')
  } finally { 
    await nextTick();
    loading.value = false
  }
}

const openCreateModal = () => {
  editingStation.value = null
  resetForm()
  showStationModal.value = true
}

const openEditModal = (station) => {
  editingStation.value = station
  populateForm(station)
  showStationModal.value = true
}

const closeStationModal = () => {
  showStationModal.value = false
  editingStation.value = null
  resetForm()
}

const resetForm = () => {
  stationForm.value = {
    code: '',
    name: '',
    location: '',
    status: 'active',
    user_assigned: ''
  }
}

const populateForm = (station) => {
  stationForm.value = {
    code: station.code,
    name: station.name,
    location: station.location || '',
    status: station.status,
    user_assigned: station.user_assigned || ''
  }
}

const saveStation = async () => {
  try {
    loading.value = true 
  await nextTick()
    
    if (editingStation.value) {
      // Update station
      const index = stationList.value.findIndex(s => s.id === editingStation.value.id)
      stationList.value[index] = { ...editingStation.value, ...stationForm.value }
    } else {
      // Create station
      const newStation = {
        id: Date.now(),
        ...stationForm.value,
        last_used: new Date().toISOString()
      }
      stationList.value.push(newStation)
    }
    
    closeStationModal()
    alert(editingStation.value ? 'Station updated successfully' : 'Station created successfully')
  } catch (error) {
    console.error('Error saving station:', error)
    alert('Error saving station')
  } finally { 
    await nextTick();
    loading.value = false
  }
}

const toggleStationStatus = (station) => {
  station.status = station.status === 'active' ? 'inactive' : 'active'
  alert(`Station ${station.status === 'active' ? 'activated' : 'deactivated'} successfully`)
}

const deleteStation = (station) => {
  if (confirm('Are you sure you want to delete this station?')) {
    const index = stationList.value.findIndex(s => s.id === station.id)
    stationList.value.splice(index, 1)
    selectedStation.value = null
    alert('Station deleted successfully')
  }
}

// Utility methods
const getStatusBadgeClass = (status) => {
  const classes = {
    'active': 'bg-green-100 text-green-800',
    'inactive': 'bg-gray-100 text-gray-800',
    'maintenance': 'bg-yellow-100 text-yellow-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const formatDate = (dateString) => {
  return dateString ? new Date(dateString).toLocaleDateString() + ' ' + new Date(dateString).toLocaleTimeString() : 'Never'
}

const refresh = () => loadStations()
</script>

<style scoped>
table {
  border-collapse: collapse;
}
th, td {
  font-size: 13px;
}
</style>


<template>
  <div class="bg-white border border-gray-50 rounded-sm shadow text-sm flex flex-col h-full">
    <!-- Header -->
    <div class="flex items-center gap-2 p-2 border-b border-gray-300 bg-gray-50">
      <img
        :src="store.logo_base64 || getLogoUrl(store.logo)"
        @error="e => e.target.src = baseURL.replace('/api/', '') + '/media/logos/default.jpg'"
        class="h-6 w-6 rounded"
      />
      <h1 class="text-lg font-semibold">CASHIER STATIONS</h1>
    </div>

    <div class="p-4">
      <!-- Filters -->
      <div class="mb-6 flex flex-wrap items-center gap-4">
        <div class="form-group mb-0">
          <label class="block text-sm font-medium text-gray-700 mb-1">Search Stations</label>
          <input 
            v-model="searchQuery" 
            class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
            placeholder="Search by name, code, or location..."
          />
        </div>
        <div class="form-group mb-0">
          <label class="block text-sm font-medium text-gray-700 mb-1">Filter by Status</label>
          <select v-model="statusFilter" class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent">
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="maintenance">Maintenance</option>
          </select>
        </div>
        <button 
          v-if="canManageStations" 
          @click="openCreateModal" 
          class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          Add Station
        </button>
      </div>

      <!-- Stations Table -->
      <div class="overflow-x-auto border border-gray-300 rounded-lg">
        <table class="w-full border-collapse text-sm">
          <thead class="bg-gray-50">
            <tr>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Station</th>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Location</th>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Status</th>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Assigned User</th>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Last Used</th>
              <th v-if="canManageStations" class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="station in filteredStations" :key="station.id" class="hover:bg-gray-50" 
                :class="{ 'bg-blue-50': selectedStation?.id === station.id }"
                @click="selectedStation = station">
              <td class="px-4 py-3">
                <div>
                  <div class="font-medium text-gray-900">{{ station.name }}</div>
                  <div class="text-sm text-gray-500">{{ station.code }}</div>
                </div>
              </td>
              <td class="px-4 py-3 text-sm text-gray-900">{{ station.location || 'Not specified' }}</td>
              <td class="px-4 py-3">
                <span 
                  class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                  :class="getStatusBadgeClass(station.status)"
                >
                  {{ station.status?.charAt(0).toUpperCase() + station.status?.slice(1) }}
                </span>
              </td>
              <td class="px-4 py-3 text-sm text-gray-900">{{ station.user_assigned || 'Unassigned' }}</td>
              <td class="px-4 py-3 text-sm text-gray-500">{{ formatDate(station.last_used) }}</td>
              <td v-if="canManageStations" class="px-4 py-3">
                <div class="flex space-x-2">
                  <button 
                    @click="openEditModal(station)"
                    class="text-blue-600 hover:text-blue-900 transition-colors"
                    title="Edit Station"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                    </svg>
                  </button>
                  <button 
                    @click="toggleStationStatus(station)"
                    class="transition-colors"
                    :class="station.status === 'active' ? 'text-orange-600 hover:text-orange-900' : 'text-green-600 hover:text-green-900'"
                    :title="station.status === 'active' ? 'Deactivate Station' : 'Activate Station'"
                  >
                    <svg v-if="station.status === 'active'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636M5.636 18.364l12.728-12.728"></path>
                    </svg>
                    <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                  </button>
                  <button 
                    @click="deleteStation(station)"
                    class="text-red-600 hover:text-red-900 transition-colors"
                    title="Delete Station"
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

    <!-- Create/Edit Station Modal -->
    <div v-if="showStationModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <!-- Header -->
        <div class="flex items-center justify-between p-6 border-b border-gray-200">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-xl font-semibold text-gray-900">
                {{ editingStation ? 'Edit Station' : 'Add New Station' }}
              </h3>
              <p class="text-sm text-gray-500">
                {{ editingStation ? 'Update station information' : 'Create a new cashier station' }}
              </p>
            </div>
          </div>
          <button @click="closeStationModal" class="text-gray-400 hover:text-gray-600 transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <!-- Form -->
        <form @submit.prevent="saveStation" class="p-6">
          <!-- Basic Information -->
          <div class="mb-8">
            <h4 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <span class="w-7 h-7 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-semibold mr-3">1</span>
              Station Information
            </h4>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Station Code -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Station Code *</label>
                <input 
                  v-model="stationForm.code" 
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="e.g., CASHIER_01"
                  required
                />
                <p class="text-sm text-gray-500">Unique identifier for the station</p>
              </div>

              <!-- Station Name -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Station Name *</label>
                <input 
                  v-model="stationForm.name" 
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="e.g., Main Counter Station"
                  required
                />
                <p class="text-sm text-gray-500">Display name for the station</p>
              </div>

              <!-- Location -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Location</label>
                <input 
                  v-model="stationForm.location" 
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="e.g., Main Floor, Counter 1"
                />
                <p class="text-sm text-gray-500">Physical location of the station</p>
              </div>

              <!-- User Assignment -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Assigned User</label>
                <input 
                  v-model="stationForm.user_assigned" 
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="e.g., John Doe"
                />
                <p class="text-sm text-gray-500">User currently assigned to this station</p>
              </div>
            </div>
          </div>

          <!-- Status & Settings -->
          <div class="mb-8">
            <h4 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <span class="w-7 h-7 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-semibold mr-3">2</span>
              Status & Settings
            </h4>

            <div class="space-y-4">
              <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <h5 class="font-medium text-gray-900">Station Status</h5>
                  <p class="text-sm text-gray-600">Enable or disable this station</p>
                </div>
                <label class="relative inline-flex items-center cursor-pointer">
                  <input v-model="stationForm.status" type="checkbox" class="sr-only" true-value="active" false-value="inactive">
                  <div class="w-11 h-6 bg-gray-200 rounded-full transition-colors" :class="stationForm.status === 'active' ? 'bg-blue-600' : ''">
                    <div class="w-4 h-4 bg-white rounded-full shadow transform transition-transform" :class="stationForm.status === 'active' ? 'translate-x-6' : 'translate-x-1'"></div>
                  </div>
                </label>
              </div>
            </div>
          </div>

          <!-- Form Actions -->
          <div class="flex items-center justify-between pt-6 border-t border-gray-200">
            <button 
              type="button" 
              @click="closeStationModal" 
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              :disabled="loading"
              class="px-6 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
            >
              <svg v-if="loading" class="w-4 h-4 mr-2 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
              <svg v-else class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"></path>
              </svg>
              {{ loading ? 'Saving...' : (editingStation ? 'Update Station' : 'Create Station') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
  <FooterActions />
</template>
