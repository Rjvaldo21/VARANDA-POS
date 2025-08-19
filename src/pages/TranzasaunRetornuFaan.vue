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
  activeDateField.value = field // 'return' | 'trans'
  // ambil rentang terakhir utk field ini
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
    // minggu berjalan: senin–hari ini
    const d = new Date()
    const day = d.getDay() || 7 // Minggu=0 → 7
    const monday = new Date(d); monday.setDate(d.getDate() - (day - 1))
    start = fmtDate(monday); end = fmtDate(today)
  }
  if (v === 'month') {
    const d = new Date()
    const first = new Date(d.getFullYear(), d.getMonth(), 1)
    start = fmtDate(first); end = fmtDate(today)
  }
  if (v === '') {
    // pilih di kalender (popup)
    openCalendarFor(field === 'return' ? 'return' : 'trans')
    return
  }
  // set ke rentang
  if (field === 'return') {
    rangeReturn.value = { start, end }
    filter.value.tanggal = ''
  } else {
    rangeTrans.value = { start, end }
    filter.value.tanggalTransaksi = ''
  }
}

// helper banding tanggal yyyy-mm-dd
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
  // kosongkan filter single-date agar pakai rentang
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
          <table class="w-auto max-w-none min-w-[1100px] lg:min-w-[1300px] xl:min-w-0 border-collapse text-sm table-fixed">
            <colgroup>
              <col style="width:7.5rem" />  
              <col style="width:9rem"  />   
              <col style="width:8rem"  />   
              <col style="width:16rem" />   
              <col style="width:13rem" />   
              <col style="width:9rem"  />   
              <col style="width:8rem"  />   
              <col style="width:6rem"  />   
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
                <th class="th text-center">Qty</th>
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
                  <select v-model="filter.status" class="f-input">
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
          <div v-if="showDatePopup" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center">
            <div class="bg-white rounded shadow p-4 w-full max-w-md">
              <div class="text-base font-semibold mb-3">Hili rentang data</div>
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="text-xs text-gray-600">Desde (YYYY-MM-DD)</label>
                  <input type="date" v-model="manualStart" class="w-full border rounded px-2 py-1" />
                </div>
                <div>
                  <label class="text-xs text-gray-600">To’o (YYYY-MM-DD)</label>
                  <input type="date" v-model="manualEnd" class="w-full border rounded px-2 py-1" />
                </div>
              </div>
              <div class="mt-4 flex justify-end gap-2">
                <button class="px-3 py-1 rounded border hover:bg-gray-50" @click="showDatePopup=false">Kansela</button>
                <button class="px-3 py-1 rounded bg-blue-600 text-white hover:bg-blue-700" @click="applyManualRange">Aplika</button>
              </div>
            </div>
          </div>

      <!-- Footer -->
      <div class="flex justify-between items-center mt-2 text-xs">
        <div>
          <select v-model="perPage" class="border px-1 py-0.5 rounded-sm">
            <option v-for="n in [10, 20, 50]" :key="n" :value="n">{{ n }}/pagina</option>
          </select>
        </div>
        <div class="space-x-2 text-base">
          <button @click="refresh" class="hover:text-blue-600 hover:cursor-pointer">🔄</button>
          <button @click="addItem" class="hover:text-green-600 hover:cursor-pointer">➕</button>
          <button @click="editItem" class="hover:text-gray-600 hover:cursor-pointer">✏️</button>
          <button @click="deleteItem" class="hover:text-red-600 hover:cursor-pointer">❌</button>
        </div>
      </div>

      <!-- ✅ Modal form -->
      <div v-if="showForm" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
        <div class="bg-white w-full max-w-2xl p-4 rounded shadow relative">
          <h1 class="text-lg font-bold mb-4">🧾 Retornu Fa’an</h1>
          <button @click="closeForm" class="absolute top-2 right-2 text-gray-600 hover:text-black">✖</button>

          <div class="grid grid-cols-1 gap-4">
            <div>
              <label class="font-medium">Transaction *</label>
              <select v-model="form.transaction_id" class="input">
                <option value="">-- Pilih Transaction --</option>
                <option v-for="t in transactions" :key="t.id" :value="t.id">
                  Invoice #{{ t.invoice_number || t.invoice_id || '—' }} - ${{ formatPrice(t.total) || '0.00' }}
                </option>
              </select>
            </div>

            <div v-if="selectedTransactionSummary" class="mt-2 text-sm bg-gray-50 border rounded px-2 py-1">
              <p><strong>🧾 Invoice:</strong> {{ selectedTransactionSummary.invoice_id }}</p>
              <p><strong>💰 Total:</strong> {{ formatPrice(selectedTransactionSummary.total) }}</p>
              <p><strong>💵 Sudah Dibayar:</strong> {{ formatPrice(selectedTransactionSummary.amount_paid) }}</p>
              <p><strong>📌 Hutang Awal:</strong> {{ formatPrice(selectedTransactionSummary.amount_due) }}</p>
              <p><strong>🔁 Total Retur:</strong> {{ formatPrice(selectedTransactionSummary.total_refunded) }}</p>
              <p><strong>💼 Sisa Hutang Setelah Retur:</strong> {{ formatPrice(selectedTransactionSummary.remaining_due) }}</p>
              <p v-if="selectedTransactionSummary.refund_excess > 0" class="text-red-600">
                <strong>🎁 Uang Kembali:</strong> {{ formatPrice(selectedTransactionSummary.refund_excess) }}
              </p>
            </div>

            <div>
              <label class="font-medium">Product *</label>
              <select v-model="form.product_id" class="input">
                <option value="">-- Pilih Produk --</option>
                <option v-for="p in products" :key="p.id" :value="p.id">
                  {{ p.name }} ({{ p.barcode }})
                </option>
              </select>
            </div>

            <div>
              <label class="font-medium">Quantity *</label>
              <input type="number" v-model="form.quantity" class="input" min="1" />
            </div>

            <div>
              <label class="font-medium">Refunded Amount *</label>
              <input type="number" v-model="form.refunded_amount" class="input" step="0.01" />
            </div>

            <div>
              <label class="font-medium">Reason</label>
              <textarea v-model="form.reason" class="input"></textarea>
            </div>

            <div>
              <label class="font-medium">Status *</label>
              <select v-model="form.status" class="input">
                <option value="">-- Pilih Status --</option>
                <option v-for="s in statusOptions" :key="s.value" :value="s.value">{{ s.label }}</option>
              </select>
            </div>

            <div>
              <label class="font-medium">User *</label>
              <select v-model="form.user" class="input">
                <option value="">-- Pilih User --</option>
                <option v-for="u in users" :key="u.id" :value="u.id">{{ u.username }}</option>
              </select>
            </div>
          </div>

          <div class="mt-6 text-right">
            <button @click="handleSubmit" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
              💾 Submit
            </button>
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

</style>