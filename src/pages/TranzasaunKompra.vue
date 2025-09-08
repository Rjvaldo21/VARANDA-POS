<script setup>
import { ref, computed, onMounted } from 'vue'
import FooterActions from '@/components/pos/FooterActions.vue'
import api, { baseURL } from '@/axios'

const store = ref({
  name: '',
  address: '',
  logo: '',
  logo_base64: '',
  version: '',
  location: ''
})

const users = ref([])
const purchases = ref([])
// const filter = ref({ username: '', name: '', email: '' })
const perPage = ref(10)
const selectedUser = ref(null)
const selectedTransactionSummary = ref(null)
const isLoading = ref(true)


const filter = ref({
  nomor: '',
  supplier: '',
  tipe: 'all',     
  status: 'all',   
  tanggalAwal: '',
  tanggalAkhir: '',
  jatuhTempoAwal: '',
  jatuhTempoAkhir: '',
})

const showUserModal = ref(false)
const modalMode = ref('add') 
const userForm = ref({ username: '', first_name: '', last_name: '', email: '' })

// Missing variables for the improved UI
const todayFormatted = new Date().toLocaleDateString('en-GB')
const showDatePopup = ref(false)
const manualStart = ref('')
const manualEnd = ref('')
const datePickerMode = ref('date')

const formattedAddress = computed(() =>
  store.value.address ? store.value.address.replace(/\n/g, '<br />') : ''
)

const getLogoUrl = (path) => {
  if (!path) return ''
  return path.startsWith('http') ? path : `${baseURL.replace("/api/", "")}${path}`
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

const fetchUsers = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await api.get('users/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    users.value = response.data
  } catch (error) {
    console.error('❌ Falha fetch uzuariu:', error)
  }
}

const filteredPurchases = computed(() =>
  purchases.value.filter(p => {
    const tipeOk   = filter.value.tipe === 'all'   || p.payment_type === filter.value.tipe
    const statusOk = filter.value.status === 'all' || p.status === filter.value.status
    const nomorOk  = !filter.value.nomor    || (p.invoice_number || '').toLowerCase().includes(filter.value.nomor.toLowerCase())
    const supOk    = !filter.value.supplier || (p.supplier?.name || '').toLowerCase().includes(filter.value.supplier.toLowerCase())

    const inRange = (s, a, b) => {
      if (!a && !b) return true
      if (!s) return false
      const d = String(s).slice(0,10)
      return (!a || d >= a) && (!b || d <= b)
    }
    const tglOk  = inRange(p.date,     filter.value.tanggalAwal,      filter.value.tanggalAkhir)
    const dueOk  = inRange(p.due_date, filter.value.jatuhTempoAwal,   filter.value.jatuhTempoAkhir)

    return tipeOk && statusOk && nomorOk && supOk && tglOk && dueOk
  })
)

const totalHutang = computed(() =>
  filteredPurchases.value.reduce((sum, p) => {
    const amount = Number(p.amount_due || p.total || 0)
    return sum + amount
  }, 0)
)
const toDateOnly = s => (s ? String(s).slice(0,10) : '')

const applyQuickFilter = (range, mode) => {
  const now = new Date()
  const today = now.toISOString().slice(0,10)

  const setRange = (from, to) => {
    if (mode === 'date') {
      filter.value.tanggalAwal = from
      filter.value.tanggalAkhir = to
    } else {
      filter.value.jatuhTempoAwal = from
      filter.value.jatuhTempoAkhir = to
    }
  }

  if (range === 'today') {
    setRange(today, today)
  }
}

const handleFilterChange = (mode, e) => {
  const v = e.target.value
  if (v === '') {
    datePickerMode.value = mode
    manualStart.value = ''
    manualEnd.value = ''
    showDatePopup.value = true
  } else {
    applyQuickFilter(v, mode)
  }
}

const applyManualDateFilter = () => {
  const from = toDateOnly(manualStart.value)
  const to   = toDateOnly(manualEnd.value)
  if (datePickerMode.value === 'date') {
    filter.value.tanggalAwal = from
    filter.value.tanggalAkhir = to
  } else {
    filter.value.jatuhTempoAwal = from
    filter.value.jatuhTempoAkhir = to
  }
  showDatePopup.value = false
}


const fetchStoreProfile = async () => {
  try {
    const res = await api.get('store-profile/')
    if (res.data && res.data.length > 0) {
      store.value = res.data[0]
      console.log('Logo URL:', getLogoUrl(store.value.logo))
    }
  } catch (err) {
    console.error('❌ Falha fetch perfil loja:', err)
  }
}

const fetchPurchases = async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await api.get('purchases/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    purchases.value = res.data
  } catch (err) {
    console.error('❌ Falha fetch kompras:', err)
  }
}

const saveUser = async () => {
  const token = localStorage.getItem('token')
  const headers = { Authorization: `Bearer ${token}` }

  try {
    if (modalMode.value === 'add') {
      await api.post('users/', userForm.value, { headers })
    } else {
      await api.put(`users/${selectedUser.value.id}/`, userForm.value, { headers })
    }

    showUserModal.value = false
    await fetchUsers()
    alert('✅ Uzuariu salva ho susesu')
  } catch (err) {
    console.error('❌ Falha salva uzuariu:', err)
    alert('Akontese erru ida bainhira salva utilizadór.')
  }
}

const deleteUser = async () => {
  if (!selectedUser.value) return alert('⚠️ Hili utilizadór ne\'ebé ita-boot hakarak atu hamoos')
  const konfirmasi = confirm(`Ita iha serteza katak hakarak atu hamoos utilizadór?: ${selectedUser.value.username}?`)
  if (!konfirmasi) return

  try {
    const token = localStorage.getItem('token')
    await api.delete(`users/${selectedUser.value.id}/`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    await fetchUsers()
    selectedUser.value = null
    alert('❌ Utilizadór hamoos ho susesu')
  } catch (err) {
    console.error('❌ La konsege hamoos utilizadór:', err)
    alert('Erru ida akontese bainhira hamoos utilizadór')
  }
}

const resetPassword = () => {
  if (!selectedUser.value) return alert('⚠️ Hili uluk utilizadór')
  alert(`🔑 Reset senha ba: ${selectedUser.value.username}`)
}

const lockUser = async () => {
  if (!selectedUser.value) return alert('⚠️ Hili uluk utilizadór')

  try {
    const token = localStorage.getItem('token')
    await api.patch(`users/${selectedUser.value.id}/`, {
      is_active: false
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })
    await fetchUsers()
    alert('🔒 Uzuáriu dezativa ho susesu')
  } catch (err) {
    console.error('❌ La konsege dezativa utilizadór:', err)
    alert('La konsege dezativa utilizadór')
  }
}

// New functions for improved UI
const clearFilters = () => {
  filter.value = {
    nomor: '',
    supplier: '',
    tipe: 'all',     
    status: 'all',   
    tanggalAwal: '',
    tanggalAkhir: '',
    jatuhTempoAwal: '',
    jatuhTempoAkhir: '',
  }
}

const exportData = () => {
  const headers = ['Date','Invoice','Supplier','Payment Type','Due Date','Status','Subtotal','Total']
  const csvData = filteredPurchases.value.map(p => [
    formatDate(p.date),
    p.invoice_number,
    p.supplier?.name || '',
    p.payment_type,
    formatDate(p.due_date),
    p.status,
    p.subtotal,
    p.total
  ])
  
  const csv = [headers.join(','), ...csvData.map(row => row.join(','))].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'purchases_export.csv'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const viewPurchaseDetails = (purchase) => {
  selectedUser.value = purchase
  selectedTransactionSummary.value = {
    invoice_id: purchase.invoice_number,
    total: purchase.total,
    amount_paid: purchase.amount_paid || 0,
    amount_due: purchase.amount_due || purchase.total,
    total_refunded: purchase.total_refunded || 0,
    remaining_due: (purchase.total - (purchase.amount_paid || 0)),
    refund_excess: purchase.refund_excess || 0
  }
  showUserModal.value = true
}

const editPurchase = (purchase) => {
  // TODO: Implement edit functionality
  alert('Edit functionality to be implemented')
}

const deletePurchase = async (purchase) => {
  if (!confirm(`Are you sure you want to delete purchase ${purchase.invoice_number}?`)) return
  
  try {
    await api.delete(`purchases/${purchase.id}/`)
    await fetchPurchases()
    alert('Purchase deleted successfully')
  } catch (error) {
    console.error('Error deleting purchase:', error)
    alert('Failed to delete purchase')
  }
}

// Date filter functions
const handleFilterChange = (e) => {
  const value = e?.target?.value ?? ''
  if (value === '') {
    showDatePopup.value = true
    datePickerMode.value = 'date'
  } else if (value === 'today') {
    const today = new Date().toISOString().slice(0, 10)
    filter.value.tanggalAwal = today
    filter.value.tanggalAkhir = today
  }
}

const applyManualDateFilter = () => {
  if (manualStart.value && manualEnd.value) {
    filter.value.tanggalAwal = manualStart.value
    filter.value.tanggalAkhir = manualEnd.value
    showDatePopup.value = false
  }
}

onMounted(async () => {
  await Promise.all([
    fetchStoreProfile(),
    fetchPurchases(),
    fetchUsers()
  ])
  isLoading.value = false
})
</script>


<template>
  <div class="bg-white border border-gray-200 rounded-lg shadow-sm text-sm flex flex-col h-full">
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b border-gray-300 bg-gradient-to-r from-blue-50 to-indigo-50">
      <div class="flex items-center gap-3">
        <img
          :src="store.logo_base64 || getLogoUrl(store.logo)"
          @error="e => e.target.src = baseURL.replace('/api/', '') + '/media/logos/default.jpg'"
          class="h-8 w-8 rounded-lg shadow-sm"
        />
        <div>
          <h1 class="text-xl font-bold text-gray-800">🛒 Purchase Orders</h1>
          <p class="text-sm text-gray-600">Manage your purchase transactions</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg shadow-sm transition-colors">
          <span class="text-sm font-medium">➕ New Purchase</span>
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="p-4 bg-gray-50 border-b border-gray-200">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <!-- Total Debt Card -->
        <div class="bg-gradient-to-r from-red-50 to-red-100 border border-red-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-red-600">Total Outstanding</p>
              <p class="text-xl font-bold text-red-800">{{ formatPrice(totalHutang) }}</p>
            </div>
            <div class="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
              <span class="text-red-600 text-lg">💳</span>
            </div>
          </div>
        </div>
        
        <!-- Total Purchases Card -->
        <div class="bg-gradient-to-r from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-blue-600">Total Purchases</p>
              <p class="text-xl font-bold text-blue-800">{{ filteredPurchases.length }}</p>
            </div>
            <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <span class="text-blue-600 text-lg">📦</span>
            </div>
          </div>
        </div>

        <!-- Paid Orders Card -->
        <div class="bg-gradient-to-r from-green-50 to-green-100 border border-green-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-green-600">Paid Orders</p>
              <p class="text-xl font-bold text-green-800">{{ filteredPurchases.filter(p => p.status === 'lunas').length }}</p>
            </div>
            <div class="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
              <span class="text-green-600 text-lg">✅</span>
            </div>
          </div>
        </div>

        <!-- Pending Orders Card -->
        <div class="bg-gradient-to-r from-yellow-50 to-yellow-100 border border-yellow-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-yellow-600">Pending Orders</p>
              <p class="text-xl font-bold text-yellow-800">{{ filteredPurchases.filter(p => p.status === 'belum_lunas').length }}</p>
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
          <label class="block text-sm font-medium text-gray-700 mb-1">Search by Invoice Number</label>
          <input 
            v-model="filter.nomor" 
            type="text" 
            placeholder="Enter invoice number..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        
        <div class="min-w-[180px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Supplier</label>
          <input 
            v-model="filter.supplier" 
            type="text" 
            placeholder="Search supplier..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div class="min-w-[140px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Payment Type</label>
          <select v-model="filter.tipe" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
            <option value="">All Types</option>
            <option value="tunai">Cash</option>
            <option value="kredit">Credit</option>
          </select>
        </div>

        <div class="min-w-[140px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select v-model="filter.status" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
            <option value="all">All Status</option>
            <option value="lunas">Paid</option>
            <option value="belum_lunas">Unpaid</option>
          </select>
        </div>

        <div class="min-w-[160px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Date Range</label>
          <select @change="handleFilterChange($event)" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
            <option :value="'today'">📅 Today</option>
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

      <!-- Table -->
      <div class="bg-white rounded-lg border border-gray-200 overflow-hidden shadow-sm">
        <div class="overflow-x-auto">
          <table class="w-full border-collapse">
            <thead class="bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Purchase Date</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Invoice #</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Supplier</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Payment Type</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Due Date</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Status</th>
                <th class="px-4 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">Amount</th>
                <th class="px-4 py-3 text-center text-xs font-semibold text-gray-700 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>

            <tbody class="divide-y divide-gray-200">
              <tr v-if="filteredPurchases.length === 0">
                <td colspan="8" class="px-4 py-12 text-center text-gray-500">
                  <div class="flex flex-col items-center">
                    <span class="text-4xl mb-2">📦</span>
                    <p class="text-lg font-medium mb-1">No purchases found</p>
                    <p class="text-sm">Try adjusting your filters or create a new purchase order</p>
                  </div>
                </td>
              </tr>
              
              <tr v-for="p in filteredPurchases" :key="p.id" class="hover:bg-gray-50 transition-colors">
                <td class="px-4 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">{{ formatDate(p.date) }}</div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div>
                      <div class="text-sm font-medium text-gray-900">{{ p.invoice_number }}</div>
                      <div class="text-xs text-gray-500">ID: {{ p.id }}</div>
                    </div>
                  </div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">{{ p.supplier?.name || 'N/A' }}</div>
                  <div class="text-xs text-gray-500">{{ p.supplier?.contact_person || '' }}</div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap">
                  <span class="inline-flex px-2 py-1 text-xs font-medium rounded-full" 
                        :class="p.payment_type === 'tunai' ? 'bg-green-100 text-green-800' : 'bg-orange-100 text-orange-800'">
                    {{ p.payment_type === 'tunai' ? '💰 Cash' : '💳 Credit' }}
                  </span>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">{{ formatDate(p.due_date) }}</div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap">
                  <span class="inline-flex px-2 py-1 text-xs font-medium rounded-full"
                        :class="p.status === 'lunas' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                    {{ p.status === 'lunas' ? '✅ Paid' : '⏳ Unpaid' }}
                  </span>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap text-right">
                  <div class="text-sm font-bold text-gray-900">{{ formatPrice(p.total) }}</div>
                  <div class="text-xs text-gray-500">
                    Subtotal: {{ formatPrice(p.subtotal) }}
                  </div>
                </td>
                
                <td class="px-4 py-4 whitespace-nowrap text-center">
                  <div class="flex items-center justify-center space-x-2">
                    <button 
                      @click="viewPurchaseDetails(p)"
                      class="text-blue-600 hover:text-blue-800 font-medium text-sm"
                      title="View Details"
                    >
                      👁️
                    </button>
                    <button 
                      @click="editPurchase(p)"
                      class="text-yellow-600 hover:text-yellow-800 font-medium text-sm"
                      title="Edit"
                    >
                      ✏️
                    </button>
                    <button 
                      @click="deletePurchase(p)"
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
          Showing {{ filteredPurchases.length }} purchase{{ filteredPurchases.length !== 1 ? 's' : '' }}
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
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                <input 
                  v-model="manualEnd" 
                  type="date" 
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
                />
              </div>
            </div>
          </div>
          
          <div class="flex items-center justify-end p-6 border-t border-gray-200 space-x-3">
            <button 
              @click="showDatePopup = false" 
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              Cancel
            </button>
            <button 
              @click="applyManualDateFilter" 
              class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              Apply Filter
            </button>
          </div>
        </div>
      </div>

      <!-- Purchase Details Modal -->
      <div v-if="showUserModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
        <div class="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4">
          <div class="flex items-center justify-between p-6 border-b border-gray-200">
            <h3 class="text-lg font-semibold text-gray-900">Purchase Details</h3>
            <button @click="showUserModal = false" class="text-gray-400 hover:text-gray-600 transition-colors">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
          
          <div class="p-6" v-if="selectedTransactionSummary">
            <div class="space-y-3">
              <div class="flex justify-between items-center py-2 border-b border-gray-100">
                <span class="font-medium text-gray-700">Invoice Number:</span>
                <span class="text-gray-900">{{ selectedTransactionSummary.invoice_id }}</span>
              </div>
              <div class="flex justify-between items-center py-2 border-b border-gray-100">
                <span class="font-medium text-gray-700">Total Amount:</span>
                <span class="text-gray-900 font-bold">{{ formatPrice(selectedTransactionSummary.total) }}</span>
              </div>
              <div class="flex justify-between items-center py-2 border-b border-gray-100">
                <span class="font-medium text-gray-700">Amount Paid:</span>
                <span class="text-green-600 font-medium">{{ formatPrice(selectedTransactionSummary.amount_paid) }}</span>
              </div>
              <div class="flex justify-between items-center py-2 border-b border-gray-100">
                <span class="font-medium text-gray-700">Amount Due:</span>
                <span class="text-red-600 font-medium">{{ formatPrice(selectedTransactionSummary.amount_due) }}</span>
              </div>
              <div class="flex justify-between items-center py-2 border-b border-gray-100">
                <span class="font-medium text-gray-700">Remaining Due:</span>
                <span class="text-red-600 font-bold">{{ formatPrice(selectedTransactionSummary.remaining_due) }}</span>
              </div>
              <div v-if="selectedTransactionSummary.total_refunded > 0" class="flex justify-between items-center py-2 border-b border-gray-100">
                <span class="font-medium text-gray-700">Total Refunded:</span>
                <span class="text-orange-600 font-medium">{{ formatPrice(selectedTransactionSummary.total_refunded) }}</span>
              </div>
              <div v-if="selectedTransactionSummary.refund_excess > 0" class="flex justify-between items-center py-2 border-b border-gray-100">
                <span class="font-medium text-gray-700">Refund Excess:</span>
                <span class="text-purple-600 font-medium">{{ formatPrice(selectedTransactionSummary.refund_excess) }}</span>
              </div>
            </div>
          </div>
          
          <div class="flex items-center justify-end p-6 border-t border-gray-200">
            <button 
              @click="showUserModal = false" 
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              Close
            </button>
          </div>
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
  --tw-ring-color: rgb(59 130 246 / 0.5);
  border-color: transparent;
}

/* Table improvements */
table {
  border-collapse: collapse;
  font-variant-numeric: tabular-nums;
}

/* Loading states */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: .5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
