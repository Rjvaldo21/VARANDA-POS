<script setup>
import axios from 'axios'
import { ref, computed, onMounted } from 'vue'
import FooterActions from '@/components/pos/FooterActions.vue'

/* ========= Store header ========= */
const store = ref({ name:'', address:'', logo:'', version:'', location:'' })
const formattedAddress = computed(() => (store.value.address || '').replace(/\n/g, '<br />'))
const getLogoUrl = (path) => !path ? '' : (path.startsWith('http') ? path : `http://localhost:8000${path}`)

onMounted(async () => {
  try {
    const res = await axios.get('http://localhost:8000/api/store-profile/')
    if (res.data && res.data.length > 0) {
      store.value = res.data[0]
      console.log('Logo URL:', getLogoUrl(store.value.logo))
    }
  } catch (err) {
    console.error('Gagal fetch store profile:', err)
  }
})

/* ========= Auth helper ========= */
const authHeader = () => {
  const t =
    localStorage.getItem('access') ||
    localStorage.getItem('token')  ||
    sessionStorage.getItem('access') ||
    sessionStorage.getItem('token')
  if (!t) return {}
  if (t.startsWith('ey')) return { Authorization: `Bearer ${t}` } // JWT
  if (t.startsWith('Token ')) return { Authorization: t }         // DRF Token (sudah ada prefix)
  return { Authorization: `Token ${t}` }                          // DRF Token mentah
}

/* ========= Filters & UI ========= */
const todayFormatted = new Date().toLocaleDateString('en-GB')
const showDatePopup = ref(false)
const manualStart = ref('')
const manualEnd   = ref('')

const filter = ref({
  tanggal_awal: '',
  tanggal_akhir: '',
  barcode: '',
  nama: ''
})
const perPage = ref(10)

/* ========= Data dari API ========= */
const rows = ref([]) // hasil dari /api/reports/item-sales/

/* angka -> $xx.xx */
const formatPrice = (value) => {
  const n = Number(value)
  return Number.isFinite(n)
    ? new Intl.NumberFormat('en-US', { style:'currency', currency:'USD', minimumFractionDigits:2 }).format(n)
    : '$0.00'
}

/* ========= Fetcher ========= */
const fetchItemSales = async () => {
  try {
    const params = {}
    if (filter.value.tanggal_awal) params.date_from = filter.value.tanggal_awal.slice(0,10)
    if (filter.value.tanggal_akhir) params.date_to   = filter.value.tanggal_akhir.slice(0,10)

    const { data } = await axios.get('http://127.0.0.1:8000/api/reports/item-sales/', {
      params,
      headers: { ...authHeader() }
    })
    rows.value = data?.results || []
  } catch (e) {
    console.error('❌ Gagal ambil item-sales:', e)
  }
}

/* ========= Quick filter (today/week/month) + popup ========= */
const handleFilterChange = async (e) => {
  const value = e.target.value
  if (value === '') {
    showDatePopup.value = true
    return
  }
  applyQuickFilter(value)
  await fetchItemSales()
}

const applyQuickFilter = (range) => {
  const now = new Date()
  const toISODate = (d) => d.toISOString().slice(0,10)

  if (range === 'today') {
    const d = toISODate(now)
    filter.value.tanggal_awal = d + 'T00:00'
    filter.value.tanggal_akhir = d + 'T23:59'
  } else if (range === 'week') {
    const end = new Date(now)
    const start = new Date(now)
    const day = now.getDay() || 7     // Senin = 1
    start.setDate(now.getDate() - day + 1)
    filter.value.tanggal_awal = toISODate(start) + 'T00:00'
    filter.value.tanggal_akhir = toISODate(end) + 'T23:59'
  } else if (range === 'month') {
    const start = new Date(now.getFullYear(), now.getMonth(), 1)
    const end   = new Date(now.getFullYear(), now.getMonth()+1, 0)
    filter.value.tanggal_awal = toISODate(start) + 'T00:00'
    filter.value.tanggal_akhir = toISODate(end)   + 'T23:59'
  }
}

const applyManualDateFilter = async () => {
  if (!manualStart.value || !manualEnd.value) return
  filter.value.tanggal_awal = manualStart.value
  filter.value.tanggal_akhir = manualEnd.value
  showDatePopup.value = false
  await fetchItemSales()
}

/* ========= Client-side filter barcode/nama ========= */
const filteredData = computed(() => {
  const bc = filter.value.barcode.toLowerCase()
  const nm = filter.value.nama.toLowerCase()
  return rows.value.filter(r =>
    (!bc || (r.barcode || '').toLowerCase().includes(bc)) &&
    (!nm || (r.name    || '').toLowerCase().includes(nm))
  )
})

/* ========= Init: default hari ini ========= */
onMounted(async () => {
  applyQuickFilter('today')
  await fetchItemSales()
})

/* ========= Optional: refresh button ========= */
const refresh = async () => {
  await fetchItemSales()
}

/* ========= (opsional) unduh CSV sederhana ========= */
const downloadLaporan = () => {
  const headers = ['Barcode','Nama','Kasir','Qty Terjual','Unit','Kategori','Supplier','Stok','Harga Beli','Harga Jual','Total Penjualan','Margin']
  const lines = filteredData.value.map(r => [
    r.barcode, r.name, r.cashier, r.qty_sold, r.unit, r.category, r.supplier, r.stock,
    r.buy_price, r.sell_price, r.total_sales, r.margin
  ].join(','))
  const csv = [headers.join(','), ...lines].join('\n')
  const blob = new Blob([csv], { type:'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'laporan-penjualan-per-item.csv'
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <div class="bg-white border border-gray-200 rounded-sm shadow text-sm flex flex-col h-full">
    <!-- Header -->
    <div class="flex items-center gap-2 p-2 border-b border-gray-300 bg-gray-50">
      <img
        :src="store.logo_base64 || getLogoUrl(store.logo)"
        @error="e => e.target.src = 'http://127.0.0.1:8000/media/logos/default.jpg'"
        class="h-6 w-6 rounded"
      />
      <h1 class="text-lg font-semibold">RELATORIU PRODUTU</h1>
    </div>

    <!-- Filter rentang waktu -->
    <div class="flex items-center gap-2 mx-2 mt-2">
      <select @change="handleFilterChange($event)" class="border px-2 py-1 text-sm rounded-sm">
        <option :value="'today'">📅 {{ todayFormatted }}</option>
        <option value="week">📈 Semana</option>
        <option value="month">📆 Fulan</option>
        <option value="">🗓️ Hili kalendariu</option>
      </select>
    </div>

    <!-- Table -->
    <div class="flex-1 overflow-auto border border-gray-300 mx-2 mt-2">
      <table class="w-full table-fixed border-collapse text-sm">
        <thead class="bg-gradient-to-b from-white to-gray-100">
          <tr>
            <th class="border px-2 py-1 w-32">Barcode</th> 
            <th class="border px-2 py-1 w-48">Naran</th> 
            <th class="border px-2 py-1 w-28 text-center">Kasir</th> 
            <th class="border px-2 py-1 w-20 text-right">Terjual</th> 
            <th class="border px-2 py-1 w-20 text-center">Unidade</th> 
            <th class="border px-2 py-1 w-28 text-center">Kategoria</th> 
            <th class="border px-2 py-1 w-40 text-center">Fornesedór</th> 
            <th class="border px-2 py-1 w-20 text-right">Stok</th> 
            <th class="border px-2 py-1 w-28 text-right">Presu Kompra</th> 
            <th class="border px-2 py-1 w-28 text-right">Presu Fa'an</th> 
            <th class="border px-2 py-1 w-32 text-right">Total Fa'an</th> 
            <th class="border px-2 py-1 w-24 text-right">Margin</th> </tr>
          <tr>
            <th class="th">
              <input
                v-model="filter.barcode"
                type="text"
                placeholder="Barcode"
                class="border px-2 py-1 rounded-sm w-full text-sm"
              />
            </th>
            <th class="th">
              <input
                v-model="filter.nama"
                type="text"
                placeholder="Naran"
                class="border px-2 py-1 rounded-sm w-full text-sm"
              />
            </th>
            <th class="th"></th>
            <th class="th"></th>
            <th class="th"></th>
            <th class="th"></th>
            <th class="th"></th>
            <th class="th"></th>
            <th class="th"></th>
            <th class="th"></th>
            <th class="th"></th>
            <th class="th"></th>
          </tr>
        </thead>

        <tbody>
          <tr v-if="filteredData.length === 0">
          </tr>

          <tr v-for="(r, idx) in filteredData" :key="idx" class="hover:bg-gray-50">
            <td class="td">{{ r.barcode }}</td>
            <td class="td">{{ r.name }}</td>
            <td class="td text-center">{{ r.cashier || '-' }}</td>
            <td class="td text-right">{{ r.qty_sold }}</td>
            <td class="td text-center">{{ r.unit || '-' }}</td>
            <td class="td text-center">{{ r.category || '-' }}</td>
            <td class="td text-center">{{ r.supplier || '-' }}</td>
            <td class="td text-right">{{ r.stock }}</td>
            <td class="td text-right">{{ formatPrice(r.buy_price) }}</td>
            <td class="td text-right">{{ formatPrice(r.sell_price) }}</td>
            <td class="td text-right font-semibold">{{ formatPrice(r.total_sales) }}</td>
            <td class="td text-right">{{ formatPrice(r.margin) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Footer -->
    <div class="flex justify-between items-center mt-2 text-xs mx-2 pb-2">
      <div>
        <select v-model="perPage" class="border px-2 py-1 rounded-sm text-sm">
          <option v-for="n in [10, 20, 50]" :key="n" :value="n">{{ n }}/pagina</option>
        </select>
      </div>
      <div class="space-x-2 text-base">
        <button @click="refresh" class="hover:text-blue-600">🔄</button>
        <button @click="downloadLaporan" class="hover:text-green-600">⬇</button>
      </div>
    </div>
  </div>

  <!-- 📅 Modal Kalendariu Manual -->
  <div v-if="showDatePopup" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
    <div class="bg-white p-4 rounded shadow w-[300px]">
      <h2 class="text-sm font-semibold mb-2">Hili Data Manual</h2>
      <div class="mb-2">
        <label class="text-xs">Data Inísiu:</label>
        <input v-model="manualStart" type="date" class="border px-2 py-1 w-full rounded-sm text-sm" />
      </div>
      <div class="mb-2">
        <label class="text-xs">Data Final:</label>
        <input v-model="manualEnd" type="date" class="border px-2 py-1 w-full rounded-sm text-sm" />
      </div>
      <div class="flex justify-end gap-2 mt-2 text-xs">
        <button @click="showDatePopup = false" class="px-2 py-1 border rounded">Kansela</button>
        <button @click="applyManualDateFilter" class="px-2 py-1 border bg-blue-600 text-white rounded">Ok</button>
      </div>
    </div>
  </div>

  <FooterActions />
</template>

<style scoped>
th,
td {
  font-size: 13px;
  padding: 6px 8px;
  border: 1px solid #d1d5db;
}
.th {
  text-align: left;
  background: #f9fafb;
  font-weight: 600;
  white-space: normal;   /* header panjang auto-wrap */
  word-break: break-word;
}
.td {
  font-size: 13px;
}
</style>
