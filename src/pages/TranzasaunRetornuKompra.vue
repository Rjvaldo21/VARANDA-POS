<script setup>
import api, { baseURL } from '@/axios'
import { ref, computed, onMounted } from 'vue'
import FooterActions from '@/components/pos/FooterActions.vue'

const store = ref({
  name: '',
  address: '',
  logo: '',
  version: '',
  location: ''
})

const returns = ref([])
const filter = ref({
  tanggal: '',
  barcode: '',
  nama: '',
  supplier: '',
  status: ''
})

const perPage = ref(10)

const getLogoUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `baseURL.replace("/api/", "")${path}`
}

const formatPrice = (val) => {
  const num = parseFloat(val)
  if (isNaN(num)) return '$0.00'
  return num.toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2
  })
}

const todayOptionLabel = computed(() => {
  const d = new Date()
  const dd = String(d.getDate()).padStart(2, '0')
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const yyyy = d.getFullYear()
  return `📅 ${dd}/${mm}/${yyyy}`
})

const inRange = (dateStr, start, end) => {
  if (!dateStr) return false
  if (!start && !end) return true
  const d = dateStr.slice(0,10)
  return (!start || d >= start) && (!end || d <= end)
}

const showDatePopup = ref(false)
const manualStart = ref('')
const manualEnd   = ref('')
const rangeReturn = ref({ start: '', end: '' }) 


const fmtDate = (d) => {
  const dd = String(d.getDate()).padStart(2, '0')
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const yyyy = d.getFullYear()
  return `${yyyy}-${mm}-${dd}`
}

const openCalendarFor = () => {
  manualStart.value = rangeReturn.value.start || (filter.value.tanggal || '')
  manualEnd.value   = rangeReturn.value.end   || manualStart.value || ''
  showDatePopup.value = true
}

const applyManualRange = () => {
  if (!manualStart.value || !manualEnd.value) {
    showDatePopup.value = false
    return
  }
  rangeReturn.value = { start: manualStart.value, end: manualEnd.value }
  filter.value.tanggal = ''
  showDatePopup.value = false
}

const clearRangeReturn = () => { rangeReturn.value = { start: '', end: '' } }

const handleFilterChangeFor = (field, ev) => {
  const v = ev.target.value
  const today = new Date()
  if (v === 'today') {
    const t = fmtDate(today)
    filter.value.tanggal = t       
    clearRangeReturn()            
    return
  }
  if (v === 'week') {
    const d = new Date()
    const day = d.getDay() || 7 
    const monday = new Date(d); monday.setDate(d.getDate() - (day - 1))
    rangeReturn.value = { start: fmtDate(monday), end: fmtDate(today) }
    filter.value.tanggal = ''   
    return
  }
  if (v === 'month') {
    const d = new Date()
    const first = new Date(d.getFullYear(), d.getMonth(), 1)
    rangeReturn.value = { start: fmtDate(first), end: fmtDate(today) }
    filter.value.tanggal = ''
    return
  }
  openCalendarFor()
}

const filteredReturns = computed(() =>
  returns.value.filter(i => {
    const tanggalMatch =
      filter.value.tanggal
        ? i.returned_at?.slice(0, 10) === filter.value.tanggal
        : inRange(i.returned_at, rangeReturn.value.start, rangeReturn.value.end)

    const barcodeMatch  = !filter.value.barcode  || i.product?.sku?.toLowerCase().includes(filter.value.barcode.toLowerCase())
    const namaMatch     = !filter.value.nama     || i.product?.name?.toLowerCase().includes(filter.value.nama.toLowerCase())
    const supplierMatch = !filter.value.supplier || i.purchase?.supplier?.name?.toLowerCase().includes(filter.value.supplier.toLowerCase())
    const statusMatch   = !filter.value.status   || i.status === filter.value.status

    return tanggalMatch && barcodeMatch && namaMatch && supplierMatch && statusMatch
  })
)

const totalPembelian = computed(() =>
  filteredReturns.value.reduce((sum, item) => sum + (item.refunded_amount || 0), 0)
)

onMounted(async () => {
  try {
    const token = localStorage.getItem('token')
    const [resReturns, resStore] = await Promise.all([
      api.get('purchase-returns/', {
        headers: { Authorization: `Bearer ${token}` }
      }),
      api.get('store-profile/')
    ])

    console.log('🛒 Data Purchase Returns:', resReturns.data)
    returns.value = resReturns.data
    if (resStore.data && resStore.data.length > 0) {
      store.value = resStore.data[0]
    }
  } catch (err) {
    console.error('Gagal fetch data:', err)
  }
})

const refresh = () => console.log('Refresh')
const addItem = () => console.log('Tambah')
const editItem = () => console.log('Edit')
const deleteItem = () => console.log('Hapus')

const dateOnly = (v) => (v ? String(v).slice(0, 10) : '-')

const pricePerItem = (refunded_amount, qty) => {
  const q = Number(qty) || 0
  const amt = Number(refunded_amount) || 0
  return q > 0 ? formatPrice(amt / q) : formatPrice(0)
}

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
      <h1 class="text-lg font-semibold">RETORNU KOMPRA</h1>
    </div>

    <div class="p-2 flex flex-col flex-1 overflow-hidden">
      <div class="border rounded-sm px-3 py-2 w-40 text-right mb-3">
        <div class="text-xs text-gray-500 text-left">Totál Kompra</div>
        <div class="text-lg font-bold">{{ formatPrice(totalPembelian) }}</div>
      </div>

      <!-- Table -->
        <div class="flex-1 border border-gray-300 rounded-sm overflow-x-auto scrollbar-stable">
          <table class="w-auto max-w-none min-w-[1200px] lg:min-w-[1400px] border-collapse text-sm table-fixed">
            <colgroup>
              <col style="width:7.5rem" />  
              <col style="width:12rem" />   
              <col style="width:18rem" />   
              <col style="width:14rem" />   
              <col style="width:10rem" />   
              <col style="width:7rem"  />   
              <col style="width:11rem" />   
              <col style="width:9rem"  />   
              <col style="width:9rem"  />   
              <col style="width:11rem" />   
              <col style="width:16rem" />   
            </colgroup>

            <thead class="bg-gradient-to-b from-white to-gray-100">
              <tr>
                <th class="th">Data</th>
                <th class="th">Barcode / SKU</th>
                <th class="th">Naran</th>
                <th class="th">Fornesedor</th>
                <th class="th">Status</th>
                <th class="th text-center">Qty Fila</th>
                <th class="th text-right">Total (Qty × Preu)</th>
                <th class="th">Data Fila</th>
                <th class="th text-right">Presu Item</th>
                <th class="th text-right">Total Refund Real</th>
                <th class="th">Razaun</th>
              </tr>

              <tr>
                <!-- Data -->
                <th class="th">
                  <div class="flex items-center gap-2">
                    <div class="border rounded-sm px-2 py-1 w-44">
                      <select @change="e => handleFilterChangeFor('return', e)" class="w-full outline-none bg-transparent">
                        <option value="today">{{ todayOptionLabel }}</option>
                        <option value="week">📈 Semana</option>
                        <option value="month">📆 Fulan</option>
                        <option value="">🗓️ Hili kalendariu</option>
                      </select>
                    </div>
                  </div>
                </th>

                <!-- Barcode / SKU -->
                <th class="th">
                  <input v-model="filter.barcode" type="text" placeholder="Barcode/SKU" class="f-input" />
                </th>

                <!-- Naran -->
                <th class="th">
                  <input v-model="filter.nama" type="text" placeholder="Naran" class="f-input" />
                </th>

                <!-- Fornesedor -->
                <th class="th">
                  <input v-model="filter.supplier" type="text" placeholder="Fornesedor" class="f-input" />
                </th>

                <th class="th">
                  <select v-model="filter.status" class="f-input f-select">
                    <option value="">Status</option>
                    <option value="Approved">Aprova</option>
                    <option value="Pending">Pendente</option>
                    <option value="Rejected">Rejeitadu</option>
                  </select>
                </th>

                <th class="th"></th>
                <th class="th"></th>
                <th class="th"></th>
                <th class="th"></th>
                <th class="th"></th>
                <th class="th"></th>
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
              <td class="px-4 py-3 text-sm text-gray-900">{{ dateOnly(item?.returned_at) }}</td>
              <td class="px-4 py-3">
                <div class="font-medium text-gray-900">{{ item?.product?.name || 'No name' }}</div>
                <div class="text-sm text-gray-500">{{ item?.product?.sku || 'No SKU' }}</div>
              </td>
              <td class="px-4 py-3 text-sm text-gray-900">{{ item?.purchase?.supplier?.name || 'No supplier' }}</td>
              <td class="px-4 py-3 text-center">
                <span 
                  class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                  :class="{
                    'bg-green-100 text-green-800': item?.status === 'Approved',
                    'bg-yellow-100 text-yellow-800': item?.status === 'Pending',
                    'bg-red-100 text-red-800': item?.status === 'Rejected'
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
      <div v-if="showForm" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
          <!-- Header -->
          <div class="flex items-center justify-between p-6 border-b border-gray-200">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 15v-1a4 4 0 00-4-4H8m0 0l3 3m-3-3l3-3m5 14v-5a2 2 0 00-2-2H6a2 2 0 00-2 2v5a2 2 0 002 2h14a2 2 0 002-2z"></path>
                </svg>
              </div>
              <div>
                <h3 class="text-xl font-semibold text-gray-900">
                  {{ isEditing ? 'Edit Purchase Return' : 'Add New Purchase Return' }}
                </h3>
                <p class="text-sm text-gray-500">
                  {{ isEditing ? 'Update return information' : 'Create a new purchase return' }}
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
          <form @submit.prevent="saveReturn" class="p-6">
            <!-- Basic Information -->
            <div class="mb-8">
              <h4 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
                <span class="w-7 h-7 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-semibold mr-3">1</span>
                Return Information
              </h4>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Purchase ID -->
                <div class="space-y-1">
                  <label class="block text-sm font-medium text-gray-700">Purchase ID *</label>
                  <input 
                    v-model="returnForm.purchase_id" 
                    type="text"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                    placeholder="Enter purchase ID"
                    required
                  />
                  <p class="text-sm text-gray-500">ID of the original purchase</p>
                </div>

                <!-- Product ID -->
                <div class="space-y-1">
                  <label class="block text-sm font-medium text-gray-700">Product ID *</label>
                  <input 
                    v-model="returnForm.product_id" 
                    type="text"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                    placeholder="Enter product ID"
                    required
                  />
                  <p class="text-sm text-gray-500">ID of the returned product</p>
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
                  <p class="text-sm text-gray-500">Number of items returned</p>
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
                  <p class="text-sm text-gray-500">Amount to be refunded</p>
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
                    <option value="Pending">Pending</option>
                    <option value="Approved">Approved</option>
                    <option value="Rejected">Rejected</option>
                  </select>
                  <p class="text-sm text-gray-500">Current status of the return</p>
                </div>

                <!-- User -->
                <div class="space-y-1">
                  <label class="block text-sm font-medium text-gray-700">User</label>
                  <input 
                    v-model="returnForm.user" 
                    type="text"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                    placeholder="Enter user"
                  />
                  <p class="text-sm text-gray-500">User handling the return</p>
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
                @click="showForm = false" 
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
