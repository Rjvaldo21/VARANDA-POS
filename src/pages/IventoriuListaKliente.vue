<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
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

const customers = ref([])
const loading = ref(false)
const saving = ref(false)
const searchFilter = ref('')
const perPage = ref(10)
const selectedCustomer = ref(null)

const showModal = ref(false)
const isEditing = ref(false)

const customerForm = ref({
  name: '',
  phone: '',
  email: '',
  address: '',
  points: 0
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

const filteredCustomers = computed(() => {
  return customers.value.filter(customer => {
    const searchText = searchFilter.value.toLowerCase()
    return customer.nama?.toLowerCase().includes(searchText) ||
           customer.telepon?.toLowerCase().includes(searchText) ||
           customer.email?.toLowerCase().includes(searchText) ||
           customer.nomor?.toLowerCase().includes(searchText)
  })
})

const clearValidation = () => {
  fieldErrors.value = {}
  fieldValidation.value = {}
  formErrors.value = []
}

const resetForm = () => {
  customerForm.value = {
    name: '',
    phone: '',
    email: '',
    address: '',
    points: 0
  }
  isEditing.value = false
  selectedCustomer.value = null
  clearValidation()
}

const addCustomer = () => {
  resetForm()
  showModal.value = true
}

const editItem = (customer) => {
  if (!customer) {
    alert('⚠️ Please select a customer first')
    return
  }
  selectedCustomer.value = customer
  customerForm.value = {
    name: customer.nama || '',
    phone: customer.telepon || '',
    email: customer.email || '',
    address: customer.alamat || '',
    points: customer.poin || 0
  }
  isEditing.value = true
  clearValidation()
  showModal.value = true
}

const fetchCustomers = async () => {
  loading.value = true 
  await nextTick()
  try {
    console.log('🔄 Loading customers...')
    const response = await api.get('customers/')

    customers.value = (response.data || []).map((item, index) => ({
      id: item.id,
      nomor: item.id.toString().padStart(3, '0'),
      nama: item.name || '',
      telepon: item.phone || '',
      email: item.email || '',
      alamat: item.address || '',
      poin: parseInt(item.points) || 0,
      piutang: 0 
    }))
    selectedCustomer.value = null
    console.log(`✅ Loaded ${customers.value.length} customers`)
  } catch (error) {
    console.error('❌ Failed to fetch customers:', error)
    customers.value = []
  } finally { 
    await nextTick();
    loading.value = false
  }
}

const saveCustomer = async () => {
  // Enhanced validation
  if (!customerForm.value.name || customerForm.value.name.trim() === '') {
    alert('Please fill customer name.')
    return
  }
  
  // Validate email format if provided
  if (customerForm.value.email && customerForm.value.email.trim()) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(customerForm.value.email.trim())) {
      alert('Please enter a valid email address.')
      return
    }
  }
  
  // Validate points if provided
  if (customerForm.value.points && isNaN(parseInt(customerForm.value.points))) {
    alert('Please enter a valid number for points.')
    return
  }

  saving.value = true
  try {
    console.log('📦 Saving customer...', isEditing.value ? 'UPDATE' : 'CREATE')
    
    const payload = {
      name: customerForm.value.name.trim(),
      phone: customerForm.value.phone?.trim() || '',
      email: customerForm.value.email?.trim() || '',
      address: customerForm.value.address?.trim() || '',
      points: parseInt(customerForm.value.points) || 0
    }
    
    console.log('📦 Customer payload:', payload)
    
    const isUpdate = isEditing.value
    
    if (isUpdate) {
      // Update existing customer
      await api.put(`customers/${selectedCustomer.value.id}/`, payload)
      console.log('✅ Customer updated successfully')
      alert('✅ Customer updated successfully')
    } else {
      // Create new customer
      await api.post('customers/', payload)
      console.log('✅ Customer created successfully')
      alert('✅ Customer created successfully')
    }
    
    showModal.value = false
    await refresh()
  } catch (err) {
    console.error('❌ Failed to save customer:', err)
    
    let errorMessage = 'Failed to save customer.'
    
    if (err.response) {
      const { status, data } = err.response
      console.error('🚫 Server error details:', { status, data })
      
      if (status === 400 && data) {
        // Handle validation errors
        const validationErrors = []
        for (const [field, errors] of Object.entries(data)) {
          if (Array.isArray(errors)) {
            validationErrors.push(`${field}: ${errors.join(', ')}`)
          } else {
            validationErrors.push(`${field}: ${errors}`)
          }
        }
        if (validationErrors.length > 0) {
          errorMessage = `Validation errors:\n${validationErrors.join('\n')}`
        }
      } else if (status === 401) {
        errorMessage = 'Authentication failed. Please login again.'
      } else if (status === 403) {
        errorMessage = 'Permission denied. You do not have access to perform this action.'
      } else if (status >= 500) {
        errorMessage = 'Server error. Please try again later.'
      } else {
        errorMessage = `Error (${status}): ${data?.detail || data?.message || 'Unknown error'}`
      }
    } else if (err.request) {
      errorMessage = 'Network error. Please check your connection and try again.'
    } else {
      errorMessage = `Unexpected error: ${err.message}`
    }
    
    alert(errorMessage)
  } finally {
    saving.value = false
  }
}

const deleteItem = async (customer) => {
  if (!customer) {
    alert('⚠️ Please select a customer first')
    return
  }
  if (!confirm(`Are you sure you want to delete "${customer.nama}"?`)) return
  
  try {
    console.log('🗑️ Deleting customer:', customer.id, customer.nama)
    await api.delete(`customers/${customer.id}/`)
    console.log('✅ Customer deleted successfully')
    alert('✅ Customer deleted successfully')
    selectedCustomer.value = null
    await refresh()
  } catch (err) {
    console.error('❌ Failed to delete customer:', err)
    
    let errorMessage = 'Failed to delete customer.'
    
    if (err.response?.status === 400) {
      errorMessage = 'Cannot delete customer. They may have transaction history.'
    } else if (err.response?.status === 404) {
      errorMessage = 'Customer not found. They may have been already deleted.'
    } else if (err.response?.status >= 500) {
      errorMessage = 'Server error. Please try again later.'
    }
    
    alert(errorMessage)
  }
}

const refresh = async () => {
  await fetchCustomers()
}

const formatPrice = val => Number(val || 0).toLocaleString('id-ID')

onMounted(async () => {
  try {
    const res = await api.get('store-profile/')
    if (res.data && res.data.length > 0) {
      store.value = res.data[0]
    }
  } catch (err) {
    console.error('Failed to fetch store profile:', err)
  }
  
  await fetchCustomers()
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
      <h1 class="text-lg font-semibold">CUSTOMER MANAGEMENT</h1>
    </div>

    <div class="p-4">
      <!-- Filters -->
      <div class="mb-6 flex flex-wrap items-center gap-4">
        <div class="form-group mb-0 flex-1">
          <label class="block text-sm font-medium text-gray-700 mb-1">Search Customers</label>
          <input 
            v-model="searchFilter" 
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
            placeholder="Search by name, phone, email, or number..."
          />
        </div>
        <button 
          @click="addCustomer" 
          class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          Add Customer
        </button>
      </div>

      <!-- Customers Table -->
      <div class="overflow-x-auto border border-gray-300 rounded-lg">
        <table class="w-full border-collapse text-sm">
          <thead class="bg-gray-50">
            <tr>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Customer ID</th>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Name</th>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Contact</th>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Address</th>
              <th class="border-b border-gray-200 px-4 py-3 text-right font-medium text-gray-700">Points</th>
              <th class="border-b border-gray-200 px-4 py-3 text-right font-medium text-gray-700">Debt</th>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-if="loading">
              <td colspan="7" class="px-4 py-8 text-center text-gray-500">Loading customers...</td>
            </tr>
            <tr v-else-if="filteredCustomers.length === 0">
              <td colspan="7" class="px-4 py-8 text-center text-gray-500">
                <svg class="mx-auto h-12 w-12 text-gray-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
                <p>No customers found</p>
              </td>
            </tr>
            <tr v-else v-for="customer in filteredCustomers" :key="customer.id" class="hover:bg-gray-50" 
                :class="{ 'bg-blue-50': selectedCustomer?.id === customer.id }"
                @click="selectedCustomer = customer">
              <td class="px-4 py-3">
                <span class="inline-flex px-2 py-1 text-xs font-semibold bg-blue-100 text-blue-800 rounded-full">
                  {{ customer.nomor }}
                </span>
              </td>
              <td class="px-4 py-3">
                <div class="font-medium text-gray-900">{{ customer.nama || 'No name' }}</div>
              </td>
              <td class="px-4 py-3">
                <div class="text-sm text-gray-900">{{ customer.telepon || 'No phone' }}</div>
                <div class="text-sm text-gray-500">{{ customer.email || 'No email' }}</div>
              </td>
              <td class="px-4 py-3 text-sm text-gray-900">{{ customer.alamat || 'No address' }}</td>
              <td class="px-4 py-3 text-sm text-gray-900 text-right font-medium">{{ customer.poin ?? 0 }}</td>
              <td class="px-4 py-3 text-sm text-gray-900 text-right font-medium">{{ formatPrice(customer.piutang ?? 0) }}</td>
              <td class="px-4 py-3">
                <div class="flex space-x-2">
                  <button 
                    @click="editItem(customer)"
                    class="text-blue-600 hover:text-blue-900 transition-colors"
                    title="Edit Customer"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                    </svg>
                  </button>
                  <button 
                    @click="deleteItem(customer)"
                    class="text-red-600 hover:text-red-900 transition-colors"
                    title="Delete Customer"
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

    <!-- Create/Edit Customer Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <!-- Header -->
        <div class="flex items-center justify-between p-6 border-b border-gray-200">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-xl font-semibold text-gray-900">
                {{ isEditing ? 'Edit Customer' : 'Add New Customer' }}
              </h3>
              <p class="text-sm text-gray-500">
                {{ isEditing ? 'Update customer information' : 'Create a new customer profile' }}
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
        <form @submit.prevent="saveCustomer" class="p-6">
          <!-- Basic Information -->
          <div class="mb-8">
            <h4 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <span class="w-7 h-7 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-semibold mr-3">1</span>
              Basic Information
            </h4>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Customer Name -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Customer Name *</label>
                <input 
                  v-model="customerForm.name" 
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="Enter customer name"
                  required
                />
                <p class="text-sm text-gray-500">Full name of the customer</p>
              </div>

              <!-- Phone -->  
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Phone Number</label>
                <input 
                  v-model="customerForm.phone" 
                  type="tel"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="+670 123-4567"
                />
                <p class="text-sm text-gray-500">Contact phone number</p>
              </div>

              <!-- Email -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Email Address</label>
                <input 
                  v-model="customerForm.email" 
                  type="email"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="customer@example.com"
                />
                <p class="text-sm text-gray-500">Email for notifications</p>
              </div>

              <!-- Points -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Loyalty Points</label>
                <input 
                  v-model="customerForm.points" 
                  type="number" 
                  min="0"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="0"
                />
                <p class="text-sm text-gray-500">Current loyalty points balance</p>
              </div>
            </div>
          </div>

          <!-- Address Information -->
          <div class="mb-8">
            <h4 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <span class="w-7 h-7 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-semibold mr-3">2</span>
              Address Information
            </h4>
            
            <div class="space-y-1">
              <label class="block text-sm font-medium text-gray-700">Customer Address</label>
              <textarea 
                v-model="customerForm.address" 
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                placeholder="Enter customer address..."
              ></textarea>
              <p class="text-sm text-gray-500">Full address for delivery</p>
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
              {{ saving ? 'Saving...' : (isEditing ? 'Update Customer' : 'Create Customer') }}
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
