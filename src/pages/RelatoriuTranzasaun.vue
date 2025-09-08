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

const summary = ref({
  gross_income: 0,
  expenses: 0,
  gross_minus_expenses: 0,
  net_income: 0,
  profit_or_loss: 0
})

const todayFormatted = new Date().toLocaleDateString('en-GB')
const startDate = ref('')
const endDate = ref('')

const filter = ref({
  tipe: '',
  nomor: '',
  detil: '',
})

const props = defineProps({
  class: {
    type: String,
    default: ''
  }
})

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value)
}

const showDatePopup = ref(false)
const manualStart = ref('')
const manualEnd = ref('')

const toggleAdvancedFilter = () => {
  showDatePopup.value = !showDatePopup.value
}

const applyManualDateFilter = () => {
  if (manualStart.value && manualEnd.value) {
    startDate.value = manualStart.value + 'T00:00'
    endDate.value = manualEnd.value + 'T23:59'
    showDatePopup.value = false
  }
}

const handleFilterChange = (e) => {
  const value = e?.target?.value ?? ''
  if (value === '') {
    manualStart.value = startDate.value ? startDate.value.slice(0, 10) : ''
    manualEnd.value   = endDate.value ? endDate.value.slice(0, 10) : ''
    showDatePopup.value = true
  } else {
    applyQuickFilter(value)
  }
}

const perPage = ref(10)

watch([startDate, endDate], async () => {
  if (!startDate.value || !endDate.value) return
  try {
    const res = await api.get('transaction-summary/', {
      params: {
        start: startDate.value,
        end: endDate.value
      }
    })
    summary.value = res.data

    await fetchTableData()
  } catch (error) {
    console.error('❌ Gagal ambil summary:', error)
  }
})

const applyQuickFilter = (value) => {
  const now = new Date()
  const todayStr = now.toISOString().slice(0, 10)

  if (value === '') {
    showDatePopup.value = true
    return
  }

  if (value === 'today') {
    startDate.value = `${todayStr}T00:00`
    endDate.value = `${todayStr}T23:59`
  } else if (value === 'week') {
    const day = now.getDay() || 7
    const start = new Date(now)
    start.setDate(now.getDate() - day + 1)
    const end = new Date(now)

    startDate.value = start.toISOString().slice(0, 10) + 'T00:00'
    endDate.value = end.toISOString().slice(0, 10) + 'T23:59'
  } else if (value === 'month') {
    const start = new Date(now.getFullYear(), now.getMonth(), 1)
    const end = new Date(now.getFullYear(), now.getMonth() + 1, 0)

    startDate.value = start.toISOString().slice(0, 10) + 'T00:00'
    endDate.value = end.toISOString().slice(0, 10) + 'T23:59'
  }
}

const transactions = ref([])


const filteredTransactions = computed(() => {
  return transactions.value.filter(trx => {
    const nomor = trx.nomor?.toLowerCase() || ''
    const detil = trx.detil?.toLowerCase() || ''
    const matchTipe = !filter.value.tipe || trx.tipe === filter.value.tipe
    const matchNomor = nomor.includes(filter.value.nomor.toLowerCase())
    const matchDetil = detil.includes(filter.value.detil.toLowerCase())
    return matchTipe && matchNomor && matchDetil
  })
})

const toRow = (raw) => {
  const tipeRaw = (raw.type || raw.tipe || '').toLowerCase()
  const tipe = ['sale', 'masuk', 'tama'].includes(tipeRaw) ? 'masuk' : 'keluar'

  // Ambil items dari berbagai kemungkinan key
  const itemsSrc = raw.items || raw.order_items || raw.lines || raw.products || []

  const getName = (it) =>
    it.name ??
    it.product_name ??
    it.title ??
    it.description ??
    it.product?.name ??
    it.product?.title ??
    null

  const getQty = (it) =>
    it.qty ?? it.quantity ?? it.qty_sold ?? 1

  const parts = (Array.isArray(itemsSrc) ? itemsSrc : [])
    .map(it => {
      const nm = getName(it)
      const q  = getQty(it)
      return nm ? `${q}x ${nm}` : null
    })
    .filter(Boolean)

  let detil = ''
  if (parts.length) {
    detil = parts.slice(0, 3).join(', ') + (parts.length > 3 ? ', …' : '')
  } else {
    // fallback untuk transaksi tanpa items (expense/return) atau kalau nama item tidak ketemu
    detil = raw.detail || raw.detil || raw.category || raw.reason || '-'
  }

  const formatDate = (s) => {
    const d = new Date(s || raw.date)
    if (Number.isNaN(d.getTime())) return raw.date || ''
    return `${d.toISOString().slice(0,10)} ${d.toTimeString().slice(0,5)}`
  }

  return {
    date:  formatDate(raw.datetime || raw.created_at || raw.date),
    tipe,  // 'masuk' | 'keluar'
    nomor: raw.invoice || raw.nomor || raw.reference || raw.barcode || raw.code || String(raw.id || ''),
    detil,
    total: Number(raw.total ?? raw.amount ?? 0)
  }
}


const fetchTableData = async () => {
  if (!startDate.value || !endDate.value) return
  try {
    const res = await api.get('transactions/', {
      params: { start: startDate.value, end: endDate.value }
    })
    const raw = Array.isArray(res.data) ? res.data : (res.data.results || [])
    transactions.value = raw.map(toRow)
    console.log('✅ rows loaded:', transactions.value.length, transactions.value[0])
  } catch (error) {
    console.error('❌ Gagal ambil data transaksi:', error)
  }
}

const kpiFromTable = computed(() => {
  let income = 0;   // pendapatan (masuk/tama/sale)
  let expense = 0;  // pengeluaran (keluar/sai/expense)

  for (const t of filteredTransactions.value) {
    const val = Math.abs(Number(t.total) || 0)
    const tipe = (t.tipe || '').toLowerCase()

    // map beberapa kemungkinan label
    if (['masuk', 'tama', 'sale'].includes(tipe)) income += val
    if (['keluar', 'sai', 'expense', 'retur', 'return'].includes(tipe)) expense += val
  }

  const gross_minus_expenses = income - expense
  const net_income = gross_minus_expenses        // tanpa diskon/retur/COGS detail
  const profit_or_loss = net_income

  return {
    gross_income: income,
    expenses: expense,
    gross_minus_expenses,
    net_income,
    profit_or_loss
  }
})

// Pakai hasil perhitungan tabel jika ada data; kalau kosong, fallback ke summary API
const displaySummary = computed(() =>
  filteredTransactions.value.length ? kpiFromTable.value : summary.value
)


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

const formattedAddress = computed(() => store.value.address.replace(/\n/g, '<br />'))
const getLogoUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `${baseURL.replace(\"/api/\", \"\")}${path}`
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
      <h1 class="text-lg font-semibold">RELATORIU TRANZASAUN</h1>
    </div>

    <!-- Statistic Cards -->
      <div class="flex gap-2 p-2 overflow-x-auto">
        <div class="border rounded-sm px-3 py-2 w-40 text-right">
          <div class="text-xs text-gray-500 text-left">Rendimentu Brutu</div>
          <div class="text-lg font-bold">{{ formatCurrency(summary.gross_income) }}</div>
        </div>
        <div class="border rounded-sm px-3 py-2 w-40 text-right">
          <div class="text-xs text-gray-500 text-left">Despeza</div>
          <div class="text-lg font-bold">{{ formatCurrency(summary.expenses) }}</div>
        </div>
        <div class="border rounded-sm px-3 py-2 w-40 text-right">
          <div class="text-xs text-gray-500 text-left">Brutu - Despeza</div>
          <div class="text-lg font-bold">{{ formatCurrency(summary.gross_minus_expenses) }}</div>
        </div>
        <div class="border rounded-sm px-3 py-2 w-40 text-right">
          <div class="text-xs text-gray-500 text-left">Rendimentu Líkidu</div>
          <div class="text-lg font-bold">{{ formatCurrency(summary.net_income) }}</div>
        </div>
        <div class="border rounded-sm px-3 py-2 w-40 text-right">
          <div class="text-xs text-gray-500 text-left">Lukru/Lakon</div>
          <div class="text-lg font-bold">{{ formatCurrency(summary.profit_or_loss) }}</div>
        </div>
      </div>

    <!-- Table -->
    <div class="p-2 flex flex-col flex-1 overflow-hidden">
      <div class="flex-1 overflow-auto border border-gray-300 rounded-sm">
        <table class="w-full border-collapse text-sm table-fixed">
          <thead class="bg-gradient-to-b from-white to-gray-100">
            <tr>
              <th class="th w-52 align-top">
                <select @change="handleFilterChange($event)" class="border px-2 py-1 rounded-sm w-full">
                  <option :value="'today'">📅 {{ todayFormatted }}</option>
                  <option value="week">📈 Semana</option>
                  <option value="month">📆 Fulan</option>
                  <option value="">🗓️ Hili kalendariu</option>
                </select>

              <!-- Popup Modal di luar table -->
                <div v-if="showDatePopup" class="fixed inset-0 bg-black bg-opacity-30 z-50 flex items-center justify-center">
                  <div class="bg-white shadow border p-5 rounded w-[300px]">
                    <div class="text-sm font-semibold mb-3">🛠️ Atur Rentang Tanggal</div>

                    <label class="block text-xs text-gray-600 mb-1">Data Inisiu</label>
                    <input type="date" v-model="manualStart" class="input w-full mb-2" />

                    <label class="block text-xs text-gray-600 mb-1">Data Final</label>
                    <input type="date" v-model="manualEnd" class="input w-full mb-4" />

                    <div class="flex justify-end gap-2 text-xs">
                      <button @click="showDatePopup = false" class="px-2 py-1 border rounded text-gray-600 hover:bg-gray-100">Kansela</button>
                      <button @click="applyManualDateFilter" class="px-2 py-1 border rounded text-blue-600 hover:bg-blue-50">Ok</button>
                    </div>
                  </div>
                </div>
                </th>
              <th class="th w-28">
                <select v-model="filter.tipe" class="input w-full">
                  <option value="">Kompletu</option>
                  <option value="masuk">Tama</option>
                  <option value="keluar">Sai</option>
                </select>
              </th>
              <th class="th w-36">
                <input v-model="filter.nomor" type="text" placeholder="Numeru" class="input w-full" />
              </th>
              <th class="th">
                <input v-model="filter.detil" type="text" placeholder="Detalle" class="input w-full" />
              </th>
              <th class="th w-24 text-right">Total</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="filteredTransactions.length === 0">
            </tr>
            <tr v-for="(trx, index) in filteredTransactions" :key="index">
              <td class="border px-2 py-1 text-xs">{{ trx.date }}</td>
              <td class="border px-2 py-1 text-xs capitalize">{{ trx.tipe }}</td>
              <td class="border px-2 py-1 text-xs">{{ trx.nomor }}</td>
              <td class="border px-2 py-1 text-xs">{{ trx.detil }}</td>
              <td class="border px-2 py-1 text-xs text-right">{{ parseFloat(trx.total).toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Footer -->
    <div class="flex justify-between items-center px-2 pb-2 text-xs">
      <div class="flex items-center gap-1">
      <select v-model="perPage" class="border px-1 py-0.5 rounded-sm">
      <option v-for="n in [10, 20, 50]" :key="n" :value="n">{{ n }}/pagina</option>
      </select>
    </div>

      <!-- Action Buttons -->
      <div class="space-x-2 text-base">
        <button class="hover:text-blue-600">🔄</button>
        <button class="hover:text-green-600">➕</button>
        <button class="hover:text-gray-600">✏️</button>
        <button class="hover:text-red-600">❌</button>
        <button class="hover:text-purple-600">⏏️</button>
      </div>
    </div>
  </div>
  <FooterActions />
</template>

<style scoped>
.input {
  padding: 6px 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 12px;
}
.th {
  border: 1px solid #ccc;
  padding: 8px;
  text-align: center;
  font-weight: 600;
}
.stat-card {
  background-color: #fefefe;
  border-radius: 4px;
  padding: 8px;
  text-align: left;
  border: 1px solid #999;
  min-width: 120px;
  flex-shrink: 0;
}
.stat-value {
  font-size: 16px;
  font-weight: bold;
  text-align: center;
  margin-top: 4px;
}
</style>
