<script setup>
import axios from 'axios'
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
  return `http://localhost:8000${path}`
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
      axios.get('http://localhost:8000/api/purchase-returns/', {
        headers: { Authorization: `Bearer ${token}` }
      }),
      axios.get('http://localhost:8000/api/store-profile/')
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
        @error="e => e.target.src = 'http://127.0.0.1:8000/media/logos/default.jpg'"
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

            <tbody>
              <tr v-for="item in filteredReturns" :key="item.id" class="hover:bg-gray-50">
                <td class="td">{{ dateOnly(item?.returned_at) }}</td>
                <td class="td" :title="item?.product?.sku || '-'">{{ item?.product?.sku ?? '-' }}</td>
                <td class="td" :title="item?.product?.name || '-'">{{ item?.product?.name ?? '-' }}</td>
                <td class="td" :title="item?.purchase?.supplier?.name || '-'">{{ item?.purchase?.supplier?.name ?? '-' }}</td>
                <td class="td">{{ item?.status ?? '-' }}</td>
                <td class="td td-num">{{ item?.quantity ?? 0 }}</td>
                <td class="td td-num">{{ formatPrice(item?.total_refund_value ?? 0) }}</td>
                <td class="td">{{ dateOnly(item?.returned_at) }}</td>
                <td class="td td-num">{{ pricePerItem(item?.refunded_amount, item?.quantity) }}</td>
                <td class="td td-num">{{ formatPrice(item?.refunded_amount ?? 0) }}</td>
                <td class="td" :title="item?.reason || '-'">{{ item?.reason ?? '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Popup pilih rentang tanggal -->
        <div v-if="showDatePopup" class="fixed inset-0 bg-black/40 z-[100] flex items-center justify-center">
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

      <div class="flex justify-between items-center mt-2 text-xs">
        <div>
          <select v-model="perPage" class="border px-1 py-0.5 rounded-sm">
            <option v-for="n in [10, 20, 50]" :key="n" :value="n">{{ n }}/pagina</option>
          </select>
        </div>
        <div class="space-x-2 text-base">
          <button @click="refresh" class="hover:text-blue-600">🔄</button>
          <button @click="addItem" class="hover:text-green-600">➕</button>
          <button @click="editItem" class="hover:text-gray-600">✏️</button>
          <button @click="deleteItem" class="hover:text-red-600">❌</button>
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
  background: #fff;
}

.f-select { min-width: 9.5rem; }


</style>
