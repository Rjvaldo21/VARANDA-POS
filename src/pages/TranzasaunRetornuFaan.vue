<script setup>
import axios from 'axios'
import { ref, computed, onMounted, watch } from 'vue'
import FooterActions from '@/components/pos/FooterActions.vue'
import api from '@/axios'

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

const totalHutang = computed(() => {
  return filteredReturns.value.reduce((acc, item) => acc + (item.refunded_amount || 0), 0)
})

const getLogoUrl = (path) => {
  if (!path) return ''
  return path.startsWith('http') ? path : `http://localhost:8000${path}`
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
const perPage = ref(10)

const filter = ref({
  tanggal: '',
  barcode: '',
  nama: '',
  nomor: '',
  tanggalTransaksi: '',
  status: '',
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
  try {
    const res = await api.get('product-returns/')
    returns.value = Array.isArray(res.data) ? res.data : res.data.results ?? []
  } catch (err) {
    console.error('Fetch returns error:', err)
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
    const res = await axios.get('http://localhost:8000/api/users/', {
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
    const res = await axios.get('http://localhost:8000/api/store-profile/')
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

const filteredReturns = computed(() =>
  returns.value.filter(i => {
    const retDate = i.returned_at || ''
    const retOK = filter.value.tanggal
      ? retDate.slice(0,10) === filter.value.tanggal
      : inRange(retDate, rangeReturn.value.start, rangeReturn.value.end)

    const trxDate = i.transaction?.created_at || ''
    const trxOK = filter.value.tanggalTransaksi
      ? trxDate.slice(0,10) === filter.value.tanggalTransaksi
      : inRange(trxDate, rangeTrans.value.start, rangeTrans.value.end)

    const barcodeMatch  = !filter.value.barcode  || i.product?.sku?.toLowerCase().includes(filter.value.barcode.toLowerCase())
    const namaMatch     = !filter.value.nama     || i.product?.name?.toLowerCase().includes(filter.value.nama.toLowerCase())
    const supplierMatch = !filter.value.supplier || i.purchase?.supplier?.name?.toLowerCase().includes(filter.value.supplier.toLowerCase())
    const statusMatch   = !filter.value.status   || i.status === filter.value.status

    return retOK && trxOK && barcodeMatch && namaMatch && supplierMatch && statusMatch
  })
)

const refresh = fetchReturns
const addItem = () => (showForm.value = true)
const editItem = () => console.log('Edit retur')
const deleteItem = () => console.log('Hapus retur')
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
      <h1 class="text-lg font-semibold">RETORNU FA’AN</h1>
    </div>

    <!-- Content -->
    <div class="p-2 flex flex-col flex-1 overflow-hidden">
      <!-- Total -->
      <div class="border rounded-sm px-3 py-2 w-40 text-right mb-3">
        <div class="text-xs text-gray-500 text-left">Totál Dívida</div>
        <div class="text-lg font-bold">{{ formatPrice(totalHutang) }}</div>
      </div>

      <!-- Table -->
        <div class="flex-1 border border-gray-300 rounded-sm overflow-x-auto">
          <table class="w-auto max-w-none min-w-[1200px] lg:min-w-[1400px] xl:min-w-0 border-collapse text-sm table-fixed">
            <colgroup>
              <col style="width:7.5rem" />  
              <col style="width:9rem"  />   
              <col style="width:8rem"  />   
              <col style="width:20rem" />   
              <col style="width:13rem" />   
              <col style="width:9rem"  />   
              <col style="width:10rem" />   
              <col style="width:8rem"  />   
              <col style="width:9rem"  />   
              <col style="width:9rem"  />   
              <col style="width:7rem"  />   
              <col style="width:10rem" />   
              <col style="width:16rem" />
            </colgroup>

            <thead class="bg-gradient-to-b from-white to-gray-100">
              <tr>
                <th class="th">Data</th>
                <th class="th">Barcode</th>
                <th class="th">SKU</th>
                <th class="th">Naran</th>
                <th class="th">Numeru Tranzasaun</th>
                <th class="th">Data Tranzasaun</th>
                <th class="th">Status</th>
                <th class="th td-num">Qty</th>
                <th class="th text-right">Total</th>
                <th class="th">Data Fila</th>
                <th class="th text-center">Qty Fila</th>
                <th class="th text-right">Osan Fila</th>
                <th class="th">Razaun</th>
              </tr>

              <tr>
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
                <th class="th">
                  <input v-model="filter.barcode" type="text" placeholder="Barcode" class="f-input" />
                </th>
                <th class="th"></th>
                <th class="th">
                  <input v-model="filter.nama" type="text" placeholder="Naran" class="f-input" />
                </th>
                <th class="th">
                  <input v-model="filter.nomor" type="text" placeholder="Invoice" class="f-input" />
                </th>
                <th class="th">
                    <div class="flex items-center gap-2">
                      <div class="border rounded-sm px-2 py-1 w-44">
                        <select @change="e => handleFilterChangeFor('trans', e)" class="w-full outline-none bg-transparent">
                          <option value="today">{{ todayOptionLabel }}</option>
                          <option value="week">📈 Semana</option>
                          <option value="month">📆 Fulan</option>
                          <option value="">🗓️ Hili kalendariu</option>
                        </select>
                      </div>
                    </div>
                  </th>
                <th class="th">
                  <select v-model="filter.status" class="f-input f-select">

                    <option value="">Status</option>
                    <option value="approved">Aprova</option>
                    <option value="pending">Pendente</option>
                    <option value="rejected">Rejeitadu</option>
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

            <tbody>
              <tr v-for="item in filteredReturns" :key="item.id" class="hover:bg-gray-50">
                <td class="td">{{ item?.returned_at ? String(item.returned_at).slice(0,10) : '-' }}</td>
                <td class="td" :title="item?.product?.barcode || '-'">{{ item?.product?.barcode ?? '-' }}</td>
                <td class="td" :title="item?.product?.sku || '-'">{{ item?.product?.sku ?? '-' }}</td>
                <td class="td" :title="item?.product?.name || '-'">{{ item?.product?.name ?? '-' }}</td>
                <td class="td">{{ item?.transaction?.invoice_id ?? item?.transaction?.invoice_number ?? '-' }}</td>
                <td class="td">{{ item?.transaction?.created_at ? String(item.transaction.created_at).slice(0,10) : '-' }}</td>
                <td class="td">{{ item?.status ?? '-' }}</td>
                <td class="td td-num">{{ item?.quantity ?? 0 }}</td>
                <td class="td td-num">{{ formatPrice(item?.transaction?.total ?? 0) }}</td>
                <td class="td">{{ item?.returned_at ? String(item.returned_at).slice(0,10) : '-' }}</td>
                <td class="td td-num">{{ item?.quantity ?? 0 }}</td>
                <td class="td td-num">{{ formatPrice(item?.refunded_amount ?? 0) }}</td>
                <td class="td" :title="item?.reason || '-'">{{ item?.reason ?? '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Popup pilih rentang tanggal -->
      <div
        v-if="showDatePopup"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
        role="dialog" aria-modal="true"
        @keydown.esc="showDatePopup=false"
        @click.self="showDatePopup=false"
      >
        <div class="bg-white w-full max-w-md rounded-lg shadow-lg">
          <div class="flex items-center justify-between px-4 py-3 border-b">
            <h2 class="text-base font-semibold">Hili rentang data</h2>
            <button class="text-gray-500 hover:text-gray-700" @click="showDatePopup=false">✖</button>
          </div>

          <div class="p-4 space-y-3">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="label">Desde</label>
                <input type="date" v-model="manualStart" class="input" />
              </div>
              <div>
                <label class="label">To’o</label>
                <input type="date" v-model="manualEnd" class="input" />
              </div>
            </div>
          </div>

          <div class="px-4 py-3 border-t flex justify-end gap-2">
            <button class="btn" @click="showDatePopup=false">Kansela</button>
            <button class="btn-primary" @click="applyManualRange">Aplika</button>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="flex justify-between items-center mt-2 text-xs relative z-10">
          <div>
            <select v-model="perPage" class="border px-1 py-0.5 rounded-sm">
              <option v-for="n in [10, 20, 50]" :key="n" :value="n">{{ n }}/pagina</option>
            </select>
          </div>

          <div class="space-x-2 text-base" @submit.prevent>
            <button type="button" @click.stop.prevent="refresh()"   class="hover:text-blue-600 hover:cursor-pointer" aria-label="Refresh">🔄</button>
            <button type="button" @click.stop.prevent="addItem()"   class="hover:text-green-600 hover:cursor-pointer" aria-label="Tambah">➕</button>
            <button type="button" @click.stop.prevent="editItem()"  class="hover:text-gray-600 hover:cursor-pointer" aria-label="Edit">✏️</button>
            <button type="button" @click.stop.prevent="deleteItem()" class="hover:text-red-600 hover:cursor-pointer" aria-label="Hapus">❌</button>
          </div>
        </div>

      <!-- Popup pilih rentang tanggal -->
        <div
          v-if="showDatePopup"
          class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
          role="dialog" aria-modal="true"
          @keydown.esc="showDatePopup=false"
          @click.self="showDatePopup=false"
        >
          <div class="bg-white w-full max-w-md rounded-lg shadow-lg">
            <div class="flex items-center justify-between px-4 py-3 border-b">
              <h2 class="text-base font-semibold">Hili rentang data</h2>
              <button type="button" class="text-gray-500 hover:text-gray-700" @click="showDatePopup=false">✖</button>
            </div>

            <div class="p-4 space-y-3">
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label class="label">Desde</label>
                  <input type="date" v-model="manualStart" class="input" />
                </div>
                <div>
                  <label class="label">To’o</label>
                  <input type="date" v-model="manualEnd" class="input" />
                </div>
              </div>
            </div>

            <div class="px-4 py-3 border-t flex justify-end gap-2">
              <button type="button" class="btn" @click="showDatePopup=false">Kansela</button>
              <button type="button" class="btn-primary" @click="applyManualRange">Aplika</button>
            </div>
          </div>
        </div>
    </div>
  </div>
  <FooterActions />
</template>

<style scoped>
table { border-collapse: collapse; table-layout: fixed; }

.th, .td {
  font-size: 13px;
  white-space: nowrap;      
  overflow: hidden;         
  text-overflow: ellipsis;  
  vertical-align: middle;
  padding: 0.25rem 0.5rem;  
  border: 1px solid #e5e7eb;
}

.f-select { min-width: 9.5rem; }

.td-num { text-align: right; font-variant-numeric: tabular-nums; }

.f-input {
  width: 100%;
  padding: 0.25rem 0.375rem;
  border: 1px solid #d1d5db;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  line-height: 1.25rem;
  background: white;
}

table { border-collapse: collapse; table-layout: fixed; }

.th, .td {
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  vertical-align: middle;
  padding: 0.375rem 0.5rem; /* 6px 8px */
  border: 1px solid #e5e7eb;
}

.td-num { text-align: right; font-variant-numeric: tabular-nums; }

/* form primitives */
.input {
  width: 100%;
  height: 2.25rem;              /* h-9 */
  padding: 0.375rem 0.5rem;     /* px-2 py-1 */
  font-size: 0.875rem;          /* text-sm */
  line-height: 1.25rem;
  border: 1px solid #d1d5db;    /* border-gray-300 */
  border-radius: 0.375rem;      /* rounded-md */
  background: #fff;
  outline: none;
}
.input:focus {
  border-color: #2563eb;        /* blue-600 */
  box-shadow: 0 0 0 3px rgba(37, 99, 235, .15);
}

.label {
  display: block;
  font-size: 0.75rem;           /* text-xs */
  color: #4b5563;               /* gray-600 */
  margin-bottom: 0.25rem;       /* mb-1 */
}

/* buttons */
.btn {
  padding: 0.375rem 0.75rem;    /* px-3 py-1.5 */
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background: #fff;
  font-size: 0.875rem;
}
.btn:hover { background: #f9fafb; }

.btn-primary {
  padding: 0.375rem 0.75rem;
  border-radius: 0.375rem;
  background: #2563eb;          /* blue-600 */
  color: #fff;
  font-size: 0.875rem;
  border: 1px solid #2563eb;
}
.btn-primary:hover { background: #1d4ed8; } /* blue-700 */

</style>