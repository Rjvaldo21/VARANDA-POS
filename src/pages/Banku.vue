<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'
import FooterActions from '@/components/pos/FooterActions.vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const RAW_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const API_BASE = RAW_BASE.replace(/\/+$/, '').endsWith('/api')
  ? RAW_BASE.replace(/\/+$/, '')
  : RAW_BASE.replace(/\/+$/, '') + '/api'

const api = axios.create({ baseURL: API_BASE })

function attachAuth() {
  const raw = localStorage.getItem('access_token') || localStorage.getItem('token') || ''
  const header = raw.includes(' ') ? raw : (raw ? `Bearer ${raw}` : '')
  if (header) api.defaults.headers.common['Authorization'] = header
}

const store = ref({ name: '', address: '', logo: '', version: '', location: '' })

const formattedAddress = computed(() =>
  store.value.address ? store.value.address.replace(/\n/g, '<br />') : ''
)

const ORIGIN_BASE = API_BASE.replace(/\/api\/?$/, '')

const getLogoUrl = (path) => {
  if (!path) return ''
  return path.startsWith('http') ? path : `${ORIGIN_BASE}${path}`
}

const banks = ref([])
const loading = ref(false)
const perPage = ref(10)
const page = ref(1)
const selectedBank = ref(null)
const searchFilter = ref('')

const filteredBanks = computed(() => {
  return banks.value.filter(bank => {
    const searchText = searchFilter.value.toLowerCase()
    return bank.name?.toLowerCase().includes(searchText) ||
           bank.code?.toLowerCase().includes(searchText) ||
           bank.account_name?.toLowerCase().includes(searchText) ||
           bank.account_number?.toLowerCase().includes(searchText)
  })
})

const pagedBanks = computed(() => {
  const start = (page.value - 1) * perPage.value
  return filteredBanks.value.slice(start, start + perPage.value)
})

const showForm = ref(false)
const isEditing = ref(false)
const currentId = ref(null)
const savingForm = ref(false)

const form = reactive({
  name: '',
  code: '',
  account_name: '',
  account_number: '',
  is_active: true,
  notes: '',
  percent_fee: '0.00',
  fixed_fee: '0.00',
  min_fee: '0.00',
  max_fee: '0.00',
  fee_paid_by_customer: true,
  enable_credit: false,
  enable_transfer: true,
  enable_qris: false,
})

// Validation states
const fieldErrors = ref({})
const fieldValidation = ref({})
const formErrors = ref([])

function resetForm() {
  isEditing.value = false
  currentId.value = null
  fieldErrors.value = {}
  fieldValidation.value = {}
  formErrors.value = []
  Object.assign(form, {
    name: '',
    code: '',
    account_name: '',
    account_number: '',
    is_active: true,
    notes: '',
    percent_fee: '0.00',
    fixed_fee: '0.00',
    min_fee: '0.00',
    max_fee: '0.00',
    fee_paid_by_customer: true,
    enable_credit: false,
    enable_transfer: true,
    enable_qris: false,
  })
}

async function fetchStore() {
  try {
    const res = await api.get('/store-profile/')
    if (res.data && res.data.length > 0) store.value = res.data[0]
  } catch (err) {
    console.error('Failed to fetch store profile:', err)
  }
}

async function fetchBanks() {
  loading.value = true
  try {
    const res = await api.get('/banks/')
    banks.value = Array.isArray(res.data) ? res.data : res.data?.results || []
    selectedBank.value = null
  } catch (err) {
    console.error('Failed to fetch banks:', err)
  } finally {
    loading.value = false
  }
}

async function createBank() {
  // Validation
  if (!form.name) {
    alert('Please fill bank name.')
    return
  }

  savingForm.value = true
  try {
    const payload = { ...form }
    await api.post('/banks/', payload)
    showForm.value = false
    alert('✅ Bank added successfully')
    await fetchBanks()
  } catch (err) {
    console.error('Failed to create bank:', err?.response?.data || err)
    alert('Failed to create bank. Please check your data.')
  } finally {
    savingForm.value = false
  }
}

async function updateBank() {
  savingForm.value = true
  try {
    const payload = { ...form }
    await api.put(`/banks/${currentId.value}/`, payload)
    showForm.value = false
    alert('✅ Bank updated successfully')
    await fetchBanks()
  } catch (err) {
    console.error('Failed to update bank:', err?.response?.data || err)
    alert('Failed to update bank. Please check your data.')
  } finally {
    savingForm.value = false
  }
}

async function removeBank(item) {
  if (!confirm(`Delete bank "${item.name}"?`)) return
  try {
    await api.delete(`/banks/${item.id}/`)
    alert('✅ Bank deleted successfully')
    await fetchBanks()
  } catch (err) {
    console.error('Failed to delete bank:', err?.response?.data || err)
    alert('Failed to delete bank')
  }
}

function refresh() {
  fetchBanks()
}

function addBank() {
  resetForm()
  isEditing.value = false
  showForm.value = true
}

function editBank(item) {
  resetForm()
  isEditing.value = true
  currentId.value = item.id
  selectedBank.value = item
  Object.assign(form, {
    name: item.name || '',
    code: item.code || '',
    account_name: item.account_name || '',
    account_number: item.account_number || '',
    is_active: !!item.is_active,
    notes: item.notes || '',
    percent_fee: String(item.percent_fee ?? '0.00'),
    fixed_fee: String(item.fixed_fee ?? '0.00'),
    min_fee: String(item.min_fee ?? '0.00'),
    max_fee: String(item.max_fee ?? '0.00'),
    fee_paid_by_customer: !!item.fee_paid_by_customer,
    enable_credit: !!item.enable_credit,
    enable_transfer: !!item.enable_transfer,
    enable_qris: !!item.enable_qris,
  })
  showForm.value = true
}

function submitForm() {
  if (isEditing.value) return updateBank()
  return createBank()
}

const formatCurrency = (val) => {
  const num = parseFloat(val)
  if (isNaN(num)) return '$0.00'
  return num.toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2
  })
}

onMounted(async () => {
  attachAuth()
  await fetchStore()
  await fetchBanks()
})
</script>


<template>
  <div class="bg-white border border-gray-50 rounded-sm shadow text-sm flex flex-col h-full">
    <!-- Header -->
    <div class="flex items-center gap-2 p-2 border-b border-gray-300 bg-gray-50">
      <img
        :src="store.logo_base64 || getLogoUrl(store.logo)"
        @error="e => e.target.src = 'http://127.0.0.1:8000/media/logos/default.jpg'"
        class="h-6 w-6 rounded"
      />
      <h1 class="text-lg font-semibold">BANK MANAGEMENT</h1>
    </div>

    <div class="p-4">
      <!-- Filters -->
      <div class="mb-6 flex flex-wrap items-center gap-4">
        <div class="form-group mb-0 flex-1">
          <label class="block text-sm font-medium text-gray-700 mb-1">Search Banks</label>
          <input 
            v-model="searchFilter" 
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
            placeholder="Search by bank name, code, account..."
          />
        </div>
        <button 
          @click="addBank" 
          class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          Add Bank
        </button>
      </div>

      <!-- Banks Table -->
      <div class="overflow-x-auto border border-gray-300 rounded-lg">
        <table class="w-full border-collapse text-sm">
          <thead class="bg-gray-50">
            <tr>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Bank Details</th>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Account</th>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Fees</th>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Features</th>
              <th class="border-b border-gray-200 px-4 py-3 text-center font-medium text-gray-700">Status</th>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-if="loading">
              <td colspan="6" class="px-4 py-8 text-center text-gray-500">Loading banks data...</td>
            </tr>
            <tr v-else-if="pagedBanks.length === 0">
              <td colspan="6" class="px-4 py-8 text-center text-gray-500">
                <svg class="mx-auto h-12 w-12 text-gray-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"></path>
                </svg>
                <p>No banks found</p>
              </td>
            </tr>
            <tr v-else v-for="bank in pagedBanks" :key="bank.id" class="hover:bg-gray-50" 
                :class="{ 'bg-blue-50': selectedBank?.id === bank.id }"
                @click="selectedBank = bank">
              <td class="px-4 py-3">
                <div class="font-medium text-gray-900">{{ bank.name }}</div>
                <div class="text-sm text-gray-500">Code: {{ bank.code || 'N/A' }}</div>
              </td>
              <td class="px-4 py-3">
                <div class="text-sm text-gray-900">{{ bank.account_name || 'No account name' }}</div>
                <div class="text-sm text-gray-500">{{ bank.account_number || 'No account number' }}</div>
              </td>
              <td class="px-4 py-3">
                <div class="space-y-1">
                  <div class="text-sm">
                    <span class="font-medium">Percent:</span> {{ bank.percent_fee || 0 }}%
                  </div>
                  <div class="text-sm">
                    <span class="font-medium">Fixed:</span> {{ formatCurrency(bank.fixed_fee || 0) }}
                  </div>
                  <div class="text-xs text-gray-500">
                    Min: {{ formatCurrency(bank.min_fee || 0) }} | Max: {{ formatCurrency(bank.max_fee || 0) }}
                  </div>
                </div>
              </td>
              <td class="px-4 py-3">
                <div class="flex flex-wrap gap-1">
                  <span v-if="bank.enable_credit" class="inline-flex px-2 py-1 text-xs font-semibold bg-purple-100 text-purple-800 rounded-full">Credit</span>
                  <span v-if="bank.enable_transfer" class="inline-flex px-2 py-1 text-xs font-semibold bg-blue-100 text-blue-800 rounded-full">Transfer</span>
                  <span v-if="bank.enable_qris" class="inline-flex px-2 py-1 text-xs font-semibold bg-green-100 text-green-800 rounded-full">QRIS</span>
                </div>
              </td>
              <td class="px-4 py-3 text-center">
                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                      :class="bank.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'">
                  {{ bank.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="px-4 py-3">
                <div class="flex space-x-2">
                  <button 
                    @click="editBank(bank)"
                    class="text-blue-600 hover:text-blue-900 transition-colors"
                    title="Edit Bank"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                    </svg>
                  </button>
                  <button 
                    @click="removeBank(bank)"
                    class="text-red-600 hover:text-red-900 transition-colors"
                    title="Delete Bank"
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

      <!-- Pagination -->
      <div class="flex justify-between items-center mt-4">
        <div class="text-sm text-gray-600">
          Showing {{ Math.min((page - 1) * perPage + 1, filteredBanks.length) }} to {{ Math.min(page * perPage, filteredBanks.length) }} of {{ filteredBanks.length }} banks
        </div>
        <div class="flex items-center space-x-2">
          <button 
            class="px-3 py-1 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed" 
            :disabled="page <= 1" 
            @click="page--"
          >
            Previous
          </button>
          <span class="text-sm text-gray-600">Page {{ page }}</span>
          <button 
            class="px-3 py-1 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed" 
            :disabled="page * perPage >= filteredBanks.length" 
            @click="page++"
          >
            Next
          </button>
        </div>
      </div>
    </div>

    <!-- Create/Edit Bank Modal -->
    <div v-if="showForm" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <!-- Header -->
        <div class="flex items-center justify-between p-6 border-b border-gray-200">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-xl font-semibold text-gray-900">
                {{ isEditing ? 'Edit Bank' : 'Add New Bank' }}
              </h3>
              <p class="text-sm text-gray-500">
                {{ isEditing ? 'Update bank information and fee settings' : 'Configure a new bank with fee structure' }}
              </p>
            </div>
          </div>
          <button @click="showForm = false" class="text-gray-400 hover:text-gray-600 transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <!-- Form -->
        <form @submit.prevent="submitForm" class="p-6">
          <!-- Basic Information -->
          <div class="mb-8">
            <h4 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <span class="w-7 h-7 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-semibold mr-3">1</span>
              Basic Information
            </h4>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Bank Name -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Bank Name *</label>
                <input 
                  v-model="form.name" 
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="e.g., Bank Mandiri"
                  required
                />
                <p class="text-sm text-gray-500">Full name of the bank</p>
              </div>

              <!-- Bank Code -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Bank Code</label>
                <input 
                  v-model="form.code" 
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="e.g., BMRI"
                />
                <p class="text-sm text-gray-500">Short code or identifier</p>
              </div>

              <!-- Account Name -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Account Name</label>
                <input 
                  v-model="form.account_name" 
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="Account holder name"
                />
                <p class="text-sm text-gray-500">Name on the bank account</p>
              </div>

              <!-- Account Number -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Account Number</label>
                <input 
                  v-model="form.account_number" 
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="Bank account number"
                />
                <p class="text-sm text-gray-500">Your bank account number</p>
              </div>
            </div>
          </div>

          <!-- Fee Configuration -->
          <div class="mb-8">
            <h4 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <span class="w-7 h-7 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-semibold mr-3">2</span>
              Fee Configuration
            </h4>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Percent Fee -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Percentage Fee (%)</label>
                <input 
                  v-model="form.percent_fee" 
                  type="number" 
                  step="0.01"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="0.00"
                />
                <p class="text-sm text-gray-500">Percentage of transaction amount</p>
              </div>

              <!-- Fixed Fee -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Fixed Fee ($)</label>
                <input 
                  v-model="form.fixed_fee" 
                  type="number" 
                  step="0.01"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="0.00"
                />
                <p class="text-sm text-gray-500">Fixed amount per transaction</p>
              </div>

              <!-- Minimum Fee -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Minimum Fee ($)</label>
                <input 
                  v-model="form.min_fee" 
                  type="number" 
                  step="0.01"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="0.00"
                />
                <p class="text-sm text-gray-500">Minimum fee per transaction</p>
              </div>

              <!-- Maximum Fee -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Maximum Fee ($)</label>
                <input 
                  v-model="form.max_fee" 
                  type="number" 
                  step="0.01"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="0.00"
                />
                <p class="text-sm text-gray-500">Maximum fee per transaction</p>
              </div>
            </div>
          </div>

          <!-- Features & Settings -->
          <div class="mb-8">
            <h4 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <span class="w-7 h-7 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-semibold mr-3">3</span>
              Features & Settings
            </h4>
            
            <div class="space-y-4">
              <!-- Toggle Switches -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <label class="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                  <div>
                    <span class="font-medium text-gray-700">Active Status</span>
                    <p class="text-sm text-gray-500">Enable this bank for transactions</p>
                  </div>
                  <label class="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" v-model="form.is_active" class="sr-only peer" />
                    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </label>

                <label class="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                  <div>
                    <span class="font-medium text-gray-700">Customer Pays Fee</span>
                    <p class="text-sm text-gray-500">Add fee to customer's total</p>
                  </div>
                  <label class="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" v-model="form.fee_paid_by_customer" class="sr-only peer" />
                    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </label>

                <label class="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                  <div>
                    <span class="font-medium text-gray-700">Enable Credit</span>
                    <p class="text-sm text-gray-500">Allow credit card payments</p>
                  </div>
                  <label class="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" v-model="form.enable_credit" class="sr-only peer" />
                    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </label>

                <label class="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                  <div>
                    <span class="font-medium text-gray-700">Enable Transfer</span>
                    <p class="text-sm text-gray-500">Allow bank transfer payments</p>
                  </div>
                  <label class="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" v-model="form.enable_transfer" class="sr-only peer" />
                    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </label>

                <label class="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                  <div>
                    <span class="font-medium text-gray-700">Enable QRIS</span>
                    <p class="text-sm text-gray-500">Allow QRIS payments</p>
                  </div>
                  <label class="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" v-model="form.enable_qris" class="sr-only peer" />
                    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </label>
              </div>

              <!-- Notes -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Notes</label>
                <textarea 
                  v-model="form.notes" 
                  rows="3"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="Additional notes or information..."
                ></textarea>
                <p class="text-sm text-gray-500">Any additional information about this bank</p>
              </div>
            </div>
          </div>

          <!-- Form Actions -->
          <div class="flex items-center justify-between pt-6 border-t border-gray-200">
            <button 
              type="button" 
              @click="showForm = false" 
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              :disabled="savingForm"
              class="px-6 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
            >
              <svg v-if="savingForm" class="w-4 h-4 mr-2 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
              <svg v-else class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"></path>
              </svg>
              {{ savingForm ? 'Saving...' : (isEditing ? 'Update Bank' : 'Create Bank') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>

  <FooterActions />
</template>

<style scoped>
table { border-collapse: collapse; }
th, td { font-size: 13px; }
</style>