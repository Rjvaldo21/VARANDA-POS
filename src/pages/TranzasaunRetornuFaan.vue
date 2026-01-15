<script setup>
import api, { baseURL } from '@/axios'
import { ref, computed, onMounted, watch } from 'vue'
import FooterActions from '@/components/pos/FooterActions.vue'

const store = ref({
  name: '',
  address: '',
  logo: '',
  version: '',
  location: ''
})

const form = ref({
  transaction_id: '',
  product_id: '',
  quantity: 1,
  refunded_amount: 0.0,
  reason: '',
  status: '',
  user: ''
})

const closeForm = () => {
  showForm.value = false
  resetForm()
}

const selectedTransactionSummary = ref(null)

const openPicker = (elRef) => {
  const el = elRef?.value
  if (!el) return
  if (typeof el.showPicker === 'function') {
    try { el.showPicker() } catch { el.focus() }
  } else {
    el.focus()
  }
}

watch(() => form.value.transaction_id, async (newVal) => {
  if (newVal) {
    try {
      const res = await api.get(`transaction/${newVal}/summary/`)
      selectedTransactionSummary.value = res.data
    } catch (err) {
      console.error('❌ Gagal fetch summary transaksi:', err)
      selectedTransactionSummary.value = null
    }
  } else {
    selectedTransactionSummary.value = null
  }
})

const formattedAddress = computed(() =>
  store.value.address ? store.value.address.replace(/\n/g, '<br />') : ''
)

const totalRefunded = computed(() => {
  return filteredReturns.value.reduce((acc, item) => acc + (item.refunded_amount || 0), 0)
})

const totalReturns = computed(() => filteredReturns.value.length)

const approvedReturns = computed(() =>
  filteredReturns.value.filter(item => item.status === 'approved').length
)

const getLogoUrl = (path) => {
  if (!path) return ''
  return path.startsWith('http') ? path : `${baseURL.replace("/api/", "")}${path}`
}

const showDatePopup = ref(false)
const activeDateField = ref(null)
const startDate = ref('')
const manualStart = ref('')
const manualEnd   = ref('')

const openCalendarFor = (field) => {
  activeDateField.value = field 
  const r = field === 'return' ? rangeReturn.value : rangeTrans.value
  manualStart.value = r.start || (field === 'return' ? filter.value.tanggal : filter.value.tanggalTransaksi) || ''
  manualEnd.value   = r.end   || manualStart.value || ''
  startDate.value = manualStart.value
  endDate.value   = manualEnd.value
  showDatePopup.value = true
}


const clearRange = (field) => {
  if (field === 'return') rangeReturn.value = { start: '', end: '' }
  if (field === 'trans')  rangeTrans.value  = { start: '', end: '' }
}

const handleFilterChangeFor = (field, ev) => {
  const v = ev.target.value
  const today = new Date()
  let start = '', end = ''
  if (v === 'today') {
    const t = fmtDate(today)
    if (field === 'return') {
      filter.value.tanggal = t
      clearRange('return')
    } else {
      filter.value.tanggalTransaksi = t
      clearRange('trans')
    }
    return
  }
  if (v === 'week') {
    const d = new Date()
    const day = d.getDay() || 7 
    const monday = new Date(d); monday.setDate(d.getDate() - (day - 1))
    start = fmtDate(monday); end = fmtDate(today)
  }
  if (v === 'month') {
    const d = new Date()
    const first = new Date(d.getFullYear(), d.getMonth(), 1)
    start = fmtDate(first); end = fmtDate(today)
  }
  if (v === '') {
    
    openCalendarFor(field === 'return' ? 'return' : 'trans')
    return
  }
  
  if (field === 'return') {
    rangeReturn.value = { start, end }
    filter.value.tanggal = ''
  } else {
    rangeTrans.value = { start, end }
    filter.value.tanggalTransaksi = ''
  }
}

const inRange = (dateStr, start, end) => {
  if (!dateStr) return false
  if (!start && !end) return true
  const d = dateStr.slice(0,10)
  return (!start || d >= start) && (!end || d <= end)
}


const applyManualRange = () => {
  if (!manualStart.value || !manualEnd.value) {
    showDatePopup.value = false
    return
  }
  const target = activeDateField.value === 'return' ? rangeReturn : rangeTrans
  target.value = { start: manualStart.value, end: manualEnd.value }
  if (activeDateField.value === 'return') {
    filter.value.tanggal = ''
  } else {
    filter.value.tanggalTransaksi = ''
  }
  showDatePopup.value = false
}

const returns = ref([])
const loading = ref(false)
const saving = ref(false)
const searchFilter = ref('')
const statusFilter = ref('')
const showModal = ref(false)
const isEditing = ref(false)
const selectedReturn = ref(null)
const perPage = ref(10)

const filter = ref({
  tanggal: '',
  barcode: '',
  nama: '',
  nomor: '',
  tanggalTransaksi: '',
  status: '',
})

const returnForm = ref({
  transaction_id: '',
  product_id: '',
  quantity: 1,
  refunded_amount: 0,
  reason: '',
  status: 'pending',
  user: ''
})

const transactions = ref([])
const products = ref([])
const users = ref([])
const statusOptions = [
  { value: 'approved', label: 'Approved' },
  { value: 'pending', label: 'Pending' },
  { value: 'rejected', label: 'Rejected' }
]

const showForm = ref(false)

const todayOptionLabel = computed(() => {
  const d = new Date()
  const dd = String(d.getDate()).padStart(2, '0')
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const yyyy = d.getFullYear()
  return `📅 ${dd}/${mm}/${yyyy}`
})

const openCalendar = () => {
  manualStart.value = startDate.value ? startDate.value.slice(0, 10) : ''
  manualEnd.value   = endDate.value ? endDate.value.slice(0, 10) : ''
  showDatePopup.value = true
}

const endDate = ref('') 
const rangeReturn = ref({ start: '', end: '' }) 
const rangeTrans  = ref({ start: '', end: '' })
const fmtDate = (d) => {
  const dd = String(d.getDate()).padStart(2, '0')
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const yyyy = d.getFullYear()
  return `${yyyy}-${mm}-${dd}`
}

const fetchReturns = async () => {
  loading.value = true 
  await nextTick()
  try {
    const res = await api.get('product-returns/')
    returns.value = Array.isArray(res.data) ? res.data : res.data.results ?? []
    selectedReturn.value = null
  } catch (err) {
    console.error('Failed to fetch returns:', err)
  } finally { 
    await nextTick();
    loading.value = false
  }
}

const addReturn = () => {
  returnForm.value = {
    transaction_id: '',
    product_id: '',
    quantity: 1,
    refunded_amount: 0,
    reason: '',
    status: 'pending',
    user: ''
  }
  isEditing.value = false
  showModal.value = true
}

const editReturn = (returnItem) => {
  if (!returnItem) {
    alert('⚠️ Please select a return first')
    return
  }
  selectedReturn.value = returnItem
  returnForm.value = {
    transaction_id: returnItem.transaction?.id || '',
    product_id: returnItem.product?.id || '',
    quantity: returnItem.quantity || 1,
    refunded_amount: returnItem.refunded_amount || 0,
    reason: returnItem.reason || '',
    status: returnItem.status || 'pending',
    user: returnItem.user || ''
  }
  isEditing.value = true
  showModal.value = true
}

const deleteReturn = async (returnItem) => {
  if (!returnItem) {
    alert('⚠️ Please select a return first')
    return
  }
  if (!confirm(`Delete return for "${returnItem.product?.name}"?`)) return
  
  try {
    const token = localStorage.getItem('token')
    await api.delete(`product-returns/${returnItem.id}/`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    alert('✅ Return deleted successfully')
    selectedReturn.value = null
    await fetchReturns()
  } catch (err) {
    console.error('❌ Failed to delete return:', err)
    alert('Failed to delete return')
  }
}

const saveReturn = async () => {
  if (!returnForm.value.transaction_id || !returnForm.value.product_id || !returnForm.value.status) {
    alert('Please fill all required fields')
    return
  }

  saving.value = true
  try {
    const token = localStorage.getItem('token')
    const headers = { Authorization: `Bearer ${token}` }

    if (isEditing.value) {
      await api.put(`product-returns/${selectedReturn.value.id}/`, returnForm.value, { headers })
      alert('✅ Return updated successfully')
    } else {
      await api.post('product-returns/', returnForm.value, { headers })
      alert('✅ Return created successfully')
    }
    
    showModal.value = false
    await fetchReturns()
  } catch (err) {
    console.error('❌ Failed to save return:', err)
    alert('Failed to save return')
  } finally {
    saving.value = false
  }
}

const fetchData = async () => {
  try {
    const [transRes, prodRes] = await Promise.all([
      api.get('invoices/'),
      api.get('products/')
    ])
    transactions.value = transRes.data
    products.value = prodRes.data
  } catch (error) {
    console.error('Fetch data error:', error)
  }
}

const fetchUsers = async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await api.get('users/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    users.value = res.data
  } catch (err) {
    console.error('User fetch error:', err)
  }
}

const handleSubmit = async () => {
  if (!form.value.transaction_id || !form.value.product_id || !form.value.status) {
    alert('❗ Harap lengkapi Transaction, Product, dan Status.')
    return
  }

  console.log('🔍 Data form yang dikirim:', form.value)

  try {
    await api.post('product-returns/', form.value)
    alert('✅ Retornu Fa’an Remata!')
    showForm.value = false
    fetchReturns()
    resetForm()
  } catch (err) {
  console.error('❌ Submit error:', err)

  if (err.response?.data) {
    console.error('🔍 Detail error dari backend:', err.response.data)
    alert('❌ Error:\n' + JSON.stringify(err.response.data, null, 2))
  } else {
    alert('❌ Submit error. Periksa koneksi atau validasi data.')
  }
 }
}

const resetForm = () => {
  form.value = {
    transaction_id: '',
    product_id: '',
    quantity: 1,
    refunded_amount: 0.0,
    reason: '',
    status: '',
    user: ''
  }
}

onMounted(async () => {
  try {
    const res = await api.get('store-profile/')
    if (res.data && res.data.length > 0) {
      store.value = res.data[0]
    }
  } catch (err) {
    console.error('Gagal fetch store profile:', err)
  }

  await fetchReturns()
  await fetchData()
  await fetchUsers()
})

const formatPrice = (val) => {
  const num = parseFloat(val)
  if (isNaN(num)) return '$0.00'
  return num.toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2
  })
}

const filteredReturns = computed(() => {
  return returns.value.filter(item => {
    const searchText = searchFilter.value.toLowerCase()
    const searchMatch = !searchText || 
      item.product?.name?.toLowerCase().includes(searchText) ||
      item.product?.sku?.toLowerCase().includes(searchText) ||
      item.product?.barcode?.toLowerCase().includes(searchText) ||
      item.transaction?.invoice_id?.toLowerCase().includes(searchText) ||
      item.transaction?.invoice_number?.toLowerCase().includes(searchText) ||
      item.reason?.toLowerCase().includes(searchText)

    const statusMatch = !statusFilter.value || item.status === statusFilter.value

    const retDate = item.returned_at || ''
    const retOK = filter.value.tanggal
      ? retDate.slice(0,10) === filter.value.tanggal
      : inRange(retDate, rangeReturn.value.start, rangeReturn.value.end)

    return searchMatch && statusMatch && retOK
  })
})

const refresh = fetchReturns
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
      <h1 class="text-lg font-semibold">RETORNU FA’AN</h1>
    </div>

    <div class="p-4">
      <!-- Summary Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <!-- Total Refunded -->
        <div class="bg-gradient-to-br from-red-50 to-red-100 border border-red-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-red-600">Total Refunded</p>
              <p class="text-2xl font-bold text-red-900">{{ formatPrice(totalRefunded) }}</p>
            </div>
            <div class="p-3 bg-red-200 rounded-full">
              <svg class="w-6 h-6 text-red-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 15v-1a4 4 0 00-4-4H8m0 0l3 3m-3-3l3-3m5 14v-5a2 2 0 00-2-2H6a2 2 0 00-2 2v5a2 2 0 002 2h14a2 2 0 002-2z"></path>
              </svg>
            </div>
          </div>
        </div>

        <!-- Total Returns -->
        <div class="bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-orange-600">Total Returns</p>
              <p class="text-2xl font-bold text-orange-900">{{ totalReturns }}</p>
            </div>
            <div class="p-3 bg-orange-200 rounded-full">
              <svg class="w-6 h-6 text-orange-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
              </svg>
            </div>
          </div>
        </div>

        <!-- Approved Returns -->
        <div class="bg-gradient-to-br from-green-50 to-green-100 border border-green-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-green-600">Approved Returns</p>
              <p class="text-2xl font-bold text-green-900">{{ approvedReturns }}</p>
            </div>
            <div class="p-3 bg-green-200 rounded-full">
              <svg class="w-6 h-6 text-green-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="mb-6 flex flex-wrap items-center gap-4">
        <div class="flex-1 min-w-64">
          <label class="block text-sm font-medium text-gray-700 mb-1">Search Returns</label>
          <input 
            v-model="searchFilter" 
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
            placeholder="Search by product, transaction, or reason..."
          />
        </div>
        <div class="min-w-40">
          <label class="block text-sm font-medium text-gray-700 mb-1">Status Filter</label>
          <select v-model="statusFilter" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent">
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>
        <div class="flex gap-2">
          <button @click="showDatePopup = true" class="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors flex items-center">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
            </svg>
            Date Filter
          </button>
          <button 
            @click="addReturn" 
            class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
            </svg>
            Add Return
          </button>
        </div>
      </div>

      <!-- Table -->
      <div class="overflow-x-auto border border-gray-300 rounded-lg">
        <table class="w-full border-collapse text-sm">
          <thead class="bg-gray-50">
            <tr>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Date</th>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Product</th>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Transaction</th>
              <th class="border-b border-gray-200 px-4 py-3 text-center font-medium text-gray-700">Status</th>
              <th class="border-b border-gray-200 px-4 py-3 text-right font-medium text-gray-700">Return Qty</th>
              <th class="border-b border-gray-200 px-4 py-3 text-right font-medium text-gray-700">Refund Amount</th>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Reason</th>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Actions</th>
            </tr>
          </thead>


          <tbody class="divide-y divide-gray-200">
            <tr v-if="loading">
              <td colspan="8" class="px-4 py-8 text-center text-gray-500">Loading returns...</td>
            </tr>
            <tr v-else-if="filteredReturns.length === 0">
              <td colspan="8" class="px-4 py-8 text-center text-gray-500">
                <svg class="mx-auto h-12 w-12 text-gray-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 15v-1a4 4 0 00-4-4H8m0 0l3 3m-3-3l3-3m5 14v-5a2 2 0 00-2-2H6a2 2 0 00-2 2v5a2 2 0 002 2h14a2 2 0 002-2z"></path>
                </svg>
                <p>No returns found</p>
              </td>
            </tr>
            <tr v-else v-for="item in filteredReturns" :key="item.id" class="hover:bg-gray-50" 
                :class="{ 'bg-blue-50': selectedReturn?.id === item.id }"
                @click="selectedReturn = item">
              <td class="px-4 py-3 text-sm text-gray-900">{{ item?.returned_at ? String(item.returned_at).slice(0,10) : '-' }}</td>
              <td class="px-4 py-3">
                <div class="font-medium text-gray-900">{{ item?.product?.name || 'No name' }}</div>
                <div class="text-sm text-gray-500">{{ item?.product?.sku || 'No SKU' }} | {{ item?.product?.barcode || 'No barcode' }}</div>
              </td>
              <td class="px-4 py-3">
                <div class="font-medium text-gray-900">{{ item?.transaction?.invoice_id ?? item?.transaction?.invoice_number ?? 'No invoice' }}</div>
                <div class="text-sm text-gray-500">{{ item?.transaction?.created_at ? String(item.transaction.created_at).slice(0,10) : 'No date' }}</div>
              </td>
              <td class="px-4 py-3 text-center">
                <span 
                  class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                  :class="{
                    'bg-green-100 text-green-800': item?.status === 'approved',
                    'bg-yellow-100 text-yellow-800': item?.status === 'pending',
                    'bg-red-100 text-red-800': item?.status === 'rejected'
                  }"
                >
                  {{ item?.status || 'Unknown' }}
                </span>
              </td>
              <td class="px-4 py-3 text-sm text-gray-900 text-right font-medium">{{ item?.quantity || 0 }}</td>
              <td class="px-4 py-3 text-sm text-gray-900 text-right font-medium">{{ formatPrice(item?.refunded_amount || 0) }}</td>
              <td class="px-4 py-3 text-sm text-gray-900">{{ item?.reason || 'No reason' }}</td>
              <td class="px-4 py-3">
                <div class="flex space-x-2">
                  <button 
                    @click="editReturn(item)"
                    class="text-blue-600 hover:text-blue-900 transition-colors"
                    title="Edit Return"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                    </svg>
                  </button>
                  <button 
                    @click="deleteReturn(item)"
                    class="text-red-600 hover:text-red-900 transition-colors"
                    title="Delete Return"
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

      <!-- Date Range Modal -->
      <div v-if="showDatePopup" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
          <div class="p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Select Date Range</h3>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                <input type="date" v-model="manualStart" class="w-full border border-gray-300 rounded-lg px-3 py-2" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                <input type="date" v-model="manualEnd" class="w-full border border-gray-300 rounded-lg px-3 py-2" />
              </div>
            </div>
            <div class="flex justify-end gap-3 mt-6">
              <button 
                @click="showDatePopup = false" 
                class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button 
                @click="applyManualRange" 
                class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700"
              >
                Apply
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Return Form Modal -->
      <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
          <!-- Header -->
          <div class="flex items-center justify-between p-6 border-b border-gray-200">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 15v-1a4 4 0 00-4-4H8m0 0l3 3m-3-3l3-3m5 14v-5a2 2 0 00-2-2H6a2 2 0 00-2 2v5a2 2 0 002 2h14a2 2 0 002-2z"></path>
                </svg>
              </div>
              <div>
                <h3 class="text-xl font-semibold text-gray-900">
                  {{ isEditing ? 'Edit Sales Return' : 'Add New Sales Return' }}
                </h3>
                <p class="text-sm text-gray-500">
                  {{ isEditing ? 'Update return information' : 'Create a new sales return' }}
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
          <form @submit.prevent="saveReturn" class="p-6">
            <!-- Basic Information -->
            <div class="mb-8">
              <h4 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
                <span class="w-7 h-7 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-semibold mr-3">1</span>
                Return Information
              </h4>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Transaction -->
                <div class="space-y-1">
                  <label class="block text-sm font-medium text-gray-700">Transaction *</label>
                  <select 
                    v-model="returnForm.transaction_id" 
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                    required
                  >
                    <option value="">-- Select Transaction --</option>
                    <option v-for="t in transactions" :key="t.id" :value="t.id">
                      {{ t.invoice_number || t.invoice_id || 'No Invoice' }} - {{ formatPrice(t.total || 0) }}
                    </option>
                  </select>
                  <p class="text-sm text-gray-500">Original transaction</p>
                </div>

                <!-- Product -->
                <div class="space-y-1">
                  <label class="block text-sm font-medium text-gray-700">Product *</label>
                  <select 
                    v-model="returnForm.product_id" 
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                    required
                  >
                    <option value="">-- Select Product --</option>
                    <option v-for="p in products" :key="p.id" :value="p.id">
                      {{ p.name }} ({{ p.sku || 'No SKU' }})
                    </option>
                  </select>
                  <p class="text-sm text-gray-500">Product to return</p>
                </div>

                <!-- Quantity -->
                <div class="space-y-1">
                  <label class="block text-sm font-medium text-gray-700">Quantity *</label>
                  <input 
                    v-model="returnForm.quantity" 
                    type="number"
                    min="1"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                    placeholder="1"
                    required
                  />
                  <p class="text-sm text-gray-500">Number of items to return</p>
                </div>

                <!-- Refunded Amount -->
                <div class="space-y-1">
                  <label class="block text-sm font-medium text-gray-700">Refunded Amount *</label>
                  <input 
                    v-model="returnForm.refunded_amount" 
                    type="number"
                    step="0.01"
                    min="0"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                    placeholder="0.00"
                    required
                  />
                  <p class="text-sm text-gray-500">Amount to refund</p>
                </div>
              </div>
            </div>

            <!-- Additional Information -->
            <div class="mb-8">
              <h4 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
                <span class="w-7 h-7 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-semibold mr-3">2</span>
                Additional Details
              </h4>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Status -->
                <div class="space-y-1">
                  <label class="block text-sm font-medium text-gray-700">Status *</label>
                  <select 
                    v-model="returnForm.status" 
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                    required
                  >
                    <option value="pending">Pending</option>
                    <option value="approved">Approved</option>
                    <option value="rejected">Rejected</option>
                  </select>
                  <p class="text-sm text-gray-500">Return status</p>
                </div>

                <!-- User -->
                <div class="space-y-1">
                  <label class="block text-sm font-medium text-gray-700">User</label>
                  <select 
                    v-model="returnForm.user" 
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  >
                    <option value="">-- Select User --</option>
                    <option v-for="u in users" :key="u.id" :value="u.id">{{ u.username }}</option>
                  </select>
                  <p class="text-sm text-gray-500">User processing return</p>
                </div>
              </div>
              
              <!-- Reason -->
              <div class="mt-6 space-y-1">
                <label class="block text-sm font-medium text-gray-700">Reason</label>
                <textarea 
                  v-model="returnForm.reason" 
                  rows="3"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="Enter reason for return..."
                ></textarea>
                <p class="text-sm text-gray-500">Explanation for the return</p>
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
                {{ saving ? 'Saving...' : (isEditing ? 'Update Return' : 'Create Return') }}
              </button>
            </div>
          </form>
        </div>
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