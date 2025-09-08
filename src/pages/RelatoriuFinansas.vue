<script setup>
import api, { baseURL } from '@/axios'
import { ref, computed, onMounted } from 'vue'
import FooterActions from '@/components/pos/FooterActions.vue'

const authHeader = () => {
  const t =
    localStorage.getItem('access') ||
    localStorage.getItem('token')  ||
    sessionStorage.getItem('access') ||
    sessionStorage.getItem('token')
  if (!t) return {}
  if (t.startsWith('ey')) return { Authorization: `Bearer ${t}` }
  if (t.startsWith('Token ')) return { Authorization: t }
  return { Authorization: `Token ${t}` }
}

const store = ref({
  name: '',
  address: '',
  logo: '',
  version: '',
  location: ''
})

const formatPrice = (value) => {
  const number = Number(value)
  return isNaN(number)
    ? '$0.00'
    : new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(number)
}

const formattedAddress = computed(() => store.value.address.replace(/\n/g, '<br />'))

const todayFormatted = new Date().toLocaleDateString('en-GB')

const totalNet = ref(0)        
const breakdown = ref(null)     
const rows = ref([])            

const toDate = (s) => (s ? s.slice(0, 10) : '')

const fetchFinanceSummary = async () => {
  try {
    const params = {}
    if (startDate.value && endDate.value) {
      params.date_from = toDate(startDate.value)
      params.date_to   = toDate(endDate.value)
    }
    const { data } = await api.get(
      'finance/summary/',
      { params, headers: { ...authHeader() } }   
    )
    totalNet.value = Number(data?.total_net) || 0
    breakdown.value = data?.breakdown || null
  } catch (e) {
    console.error('Gagal fetch finance/summary:', e)
  }
}

const fetchFinanceEntries = async () => {
  try {
    const params = {}
    if (startDate.value && endDate.value) {
      params.date_from = toDate(startDate.value)
      params.date_to   = toDate(endDate.value)
    }
    const { data } = await api.get(
      'finance/entries/',
      { params, headers: { ...authHeader() } }   
    )
    rows.value = data?.results || data || []
  } catch (e) {
    console.error('Gagal fetch finance/entries:', e)
  }
}

const refresh = async () => {
  await Promise.all([fetchFinanceSummary(), fetchFinanceEntries()])
}

const handleFilterChange = async (e) => {
  const value = e.target.value
  if (value === '') {
    showDatePopup.value = true
  } else if (value === 'today') {
    const today = new Date().toISOString().slice(0, 10)
    startDate.value = today
    endDate.value = today
    showDatePopup.value = false
    await refresh()
  }
}

const applyManualDateFilter = async () => {
  startDate.value = manualStart.value
  endDate.value = manualEnd.value
  showDatePopup.value = false
  await refresh()
}


const filteredRows = computed(() => {
  const f = filter.value
  return rows.value.filter(r => {
    if (f.tipe === 'masuk'  && Number(r.amount_signed) < 0) return false
    if (f.tipe === 'keluar' && Number(r.amount_signed) > 0) return false

    if (f.nomor && !(r.number || '').toLowerCase().includes(f.nomor.toLowerCase())) return false
    if (f.detil && !(r.note || '').toLowerCase().includes(f.detil.toLowerCase())) return false
    return true
  })
})

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

  const today = new Date().toISOString().slice(0, 10)
  startDate.value = today
  endDate.value = today
  await refresh()
})

const getLogoUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `${baseURL.replace(\"/api/\", \"\")}${path}`
}

defineOptions({ inheritAttrs: false })

const startDate = ref('')
const endDate = ref('')

const filter = ref({
  tipe: '',
  nomor: '',
  banku: '',
  mesin: '',
  pengguna: '',
  detil: '',
})

const perPage = ref(10)

const showDatePopup = ref(false)
const manualStart = ref('')
const manualEnd = ref('')

</script>


<template>
  <div
    class="bg-white border border-gray-50 rounded-sm shadow text-sm flex flex-col h-full"
    v-bind="$attrs"
  >
    <!-- Header -->
    <div class="flex items-center gap-2 p-2 border-b border-gray-300 bg-gray-50">
      <img
        :src="store.logo_base64 || getLogoUrl(store.logo)"
        @error="e => e.target.src = baseURL.replace('/api/', '') + '/media/logos/default.jpg'"
        class="h-6 w-6 rounded"
      />
      <h1 class="text-lg font-semibold">RELATORIU FINANSAS</h1>
    </div>

    <!-- ✅ Total Box -->
    <div class="px-2 pt-2 pb-1 w-[150px]">
      <div class="border rounded-sm px-3 py-2 w-full text-right">
        <div class="text-xs text-gray-500 text-left">Total</div>
        <div class="text-lg font-bold">{{ formatPrice(totalNet) }}</div>
      </div>
    </div>

    <!-- Table -->
    <div class="p-2 flex flex-col flex-1 overflow-hidden">
      <div class="flex-1 overflow-auto border border-gray-300">
        <table class="w-full table-fixed border-collapse text-sm">
          <thead class="bg-gradient-to-b from-white to-gray-100">
            <!-- Header -->
            <tr>
              <th class="th w-48 text-left">Data</th>
              <th class="th w-32 text-left">Tipu</th>
              <th class="th w-32 text-left">Numeru</th>
              <th class="th w-28 text-left">Banku</th>
              <th class="th w-28 text-left">Komputador</th>
              <th class="th w-32 text-left">Uzuariu</th>
              <th class="th w-[140px] text-left">Detalle</th>
              <th class="th w-[500px] text-right">Total</th>
            </tr>

            <!-- Filter -->
            <tr>
              <!-- Data -->
              <th class="th align-top">
                <div class="flex flex-col gap-1 w-full">
                  <select @change="handleFilterChange($event)" class="border px-2 py-1 text-sm rounded-sm w-full">
                    <option :value="'today'">📅 {{ todayFormatted }}</option>
                    <option value="">🗓️ Hili kalendariu</option>
                  </select>
                </div>
              </th>

              <!-- Tipu -->
              <th class="th">
                <select v-model="filter.tipe" class="border px-2 py-1 rounded-sm w-full text-sm">
                  <option value="">Kompletu</option>
                  <option value="masuk">Tama</option>
                  <option value="keluar">Sai</option>
                </select>
              </th>

              <th class="th">
                <input v-model="filter.nomor" placeholder="Numeru" class="border px-2 py-1 rounded-sm w-full text-sm" />
              </th>

              <th class="th">
                <select v-model="filter.banku" class="border px-2 py-1 rounded-sm w-full text-sm">
                  <option value="">Kompletu</option>
                  <option value="BNCTL">BNCTL</option>
                  <option value="MANDIRI">MANDIRI</option>
                  <option value="BNU">BNU</option>
                </select>
              </th>

              <th class="th">
                <input v-model="filter.mesin" placeholder="Komputador" class="border px-2 py-1 rounded-sm w-full text-sm" />
              </th>

              <th class="th">
                <input v-model="filter.pengguna" placeholder="Uzuariu" class="border px-2 py-1 rounded-sm w-full text-sm" />
              </th>

              <th class="th">
                <input v-model="filter.detil" placeholder="Detalle" class="border px-2 py-1 rounded-sm w-full text-sm" />
              </th>

              <th class="th text-center text-gray-400">Otomatika</th>
            </tr>
          </thead>

          <tbody>
            <tr v-if="filteredRows.length === 0">
            </tr>

            <tr v-for="(r, i) in filteredRows" :key="i" class="hover:bg-gray-50">
              <td class="td">{{ r.entry_date }}</td>
              <td class="td">{{ r.entry_type }}</td>
              <td class="td">{{ r.number || '' }}</td>
              <td class="td">—</td>
              <td class="td">—</td>
              <td class="td">—</td>
              <td class="td">{{ r.note || '-' }}</td>
              <td class="td text-right" :class="Number(r.amount_signed) >= 0 ? 'text-green-600' : 'text-red-600'">
                {{ formatPrice(r.amount_signed) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- 📅 Popup Kalender Manual -->
        <div v-if="showDatePopup" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div class="bg-white rounded shadow-md p-4 w-[300px] text-sm space-y-3">
            <div class="text-base font-semibold mb-1">Hili Data Manual</div>

            <div class="flex flex-col gap-1">
              <label for="start">Tinan Inisiu</label>
              <input id="start" v-model="manualStart" type="datetime-local" class="input" />

              <label for="end">Tinan Remata</label>
              <input id="end" v-model="manualEnd" type="datetime-local" class="input" />
            </div>

            <div class="flex justify-end gap-2 pt-2">
              <button @click="showDatePopup = false" class="px-3 py-1 text-gray-600 hover:underline">Taka</button>
              <button @click="applyManualDateFilter" class="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded">
                Aplika
              </button>
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
          <button class="hover:text-blue-600">🔄</button>
        </div>
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
  width: 100%;
  font-size: 12px;
}
.th {
  border: 1px solid #ccc;
  padding: 8px;
  text-align: center;
  font-weight: 600;
}

th,
td {
  font-size: 13px;
  padding: 6px 8px;
  border: 1px solid #d1d5db;
}
.th {
  text-align: left;
  background: #f9fafb;
  font-weight: bold;
  white-space: normal;
  word-break: break-word;
}
.td {
  font-size: 13px;
}
</style>
