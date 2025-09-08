<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import FooterActions from '@/components/pos/FooterActions.vue'
import api, { baseURL } from '@/axios'

const store = ref({
  name: '',
  address: '',
  logo: '',
  version: '',
  location: ''
})

const formattedAddress = computed(() => store.value.address.replace(/\n/g, '<br />'))

const getLogoUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `${baseURL.replace("/api/", "")}${path}`
}

onMounted(async () => {
  try {
    const res = await api.get('store-profile/')
    if (res.data && res.data.length > 0) {
      store.value = res.data[0]
      console.log('Logo URL:', getLogoUrl(store.value.logo))
    }
  } catch (err) {
    console.error('Gagal fetch store profile:', err)
    console.log('store.logo:', store.value.logo)
  }
  
  fetchProducts()
  fetchAdjustments()
})

const formatDate = (datetimeStr) => {
  const d = new Date(datetimeStr)
  return d.toLocaleString('en-US', {
    dateStyle: 'medium',
    timeStyle: 'short'
  })
}


const startDate = ref('')
const endDate   = ref('')
const showDatePopup = ref(false)
const manualStart = ref('')
const manualEnd = ref('')


const fetchAdjustments = async () => {
  try {
    const params = {}
    if (startDate.value && endDate.value) {
      params.start = startDate.value
      params.end   = endDate.value
    }
    const res = await api.get('stock-adjustments/', { params })
    items.value = res.data
  } catch (err) {
    console.error('❌ Falha foti data hadia stok:', err)
  }
}

watch([startDate, endDate], () => {
  if (startDate.value && endDate.value) {
    fetchAdjustments()
  }
})

// onMounted(() => {
//   const token = localStorage.getItem('token')
//   axios.defaults.headers.common['Authorization'] = `Bearer ${token}`

//   // set default: hari ini → akan memicu watcher & fetchAdjustments
//   applyQuickFilter('today')

//   fetchProducts()
//   // fetchAdjustments() tidak perlu dipanggil di sini karena watcher akan jalan
// })


const filter = ref({
  tanggal_awal: '',
  tanggal_akhir: '',
  barcode: '',
  nama: ''
})

const perPage = ref(10)
const items = ref([])


// Quick filter handler (select)
const handleFilterChange = (e) => {
  const value = e?.target?.value ?? ''
  if (value === '') {
    // buka popup kalender
    manualStart.value = startDate.value ? startDate.value.slice(0,10) : ''
    manualEnd.value   = endDate.value ? endDate.value.slice(0,10) : ''
    showDatePopup.value = true
  } else {
    applyQuickFilter(value)
  }
}

// Quick presets: today / week / month
const applyQuickFilter = (value) => {
  const now = new Date()
  const todayStr = now.toISOString().slice(0,10)

  if (value === 'today') {
    startDate.value = `${todayStr}T00:00`
    endDate.value   = `${todayStr}T23:59`
  } else if (value === 'week') {
    const day = now.getDay() || 7
    const start = new Date(now)
    start.setDate(now.getDate() - day + 1) // Senin
    const end = new Date(now)
    startDate.value = start.toISOString().slice(0,10) + 'T00:00'
    endDate.value   = end.toISOString().slice(0,10) + 'T23:59'
  } else if (value === 'month') {
    const start = new Date(now.getFullYear(), now.getMonth(), 1)
    const end   = new Date(now.getFullYear(), now.getMonth()+1, 0)
    startDate.value = start.toISOString().slice(0,10) + 'T00:00'
    endDate.value   = end.toISOString().slice(0,10) + 'T23:59'
  }
}

// Popup kalender → tombol OK
const applyManualDateFilter = () => {
  if (manualStart.value && manualEnd.value) {
    startDate.value = `${manualStart.value}T00:00`
    endDate.value   = `${manualEnd.value}T23:59`
    showDatePopup.value = false
  }
}

const filteredData = computed(() =>
  items.value.filter(i =>
    (!filter.value.tanggal_awal || i.tanggal >= filter.value.tanggal_awal) &&
    (!filter.value.tanggal_akhir || i.tanggal <= filter.value.tanggal_akhir) &&
    i.barcode.toLowerCase().includes(filter.value.barcode.toLowerCase()) &&
    i.nama.toLowerCase().includes(filter.value.nama.toLowerCase())
  )
)

const todayOptionText = computed(() => {
  const d = new Date(); // ikut tanggal & zona waktu komputer
  const dd = String(d.getDate()).padStart(2, '0');
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const yyyy = d.getFullYear();
  return `📅 ${dd}/${mm}/${yyyy}`
});


const refresh = () => {
  // Placeholder untuk fetch list stock adjustment jika diperlukan
  console.log('Refresh data stok...')
}

// 🔹 Modal state
const showModal = ref(false)
const products = ref([])
const form = ref({
  product: '',
  new_stock: '',
  reason: ''
})

// 🔹 Buka modal
const addItem = () => {
  showModal.value = true
  fetchProducts()
}

// 🔹 Ambil data produk dari API
const fetchProducts = async () => {
  try {
    const res = await api.get('products/')
    products.value = res.data
  } catch (err) {
    console.error('Gagal fetch produk:', err)
  }
}

// 🔹 Submit form
const submitForm = async () => {
  try {
    const payload = {
      product: form.value.product,
      new_stock: parseInt(form.value.new_stock),
      reason: form.value.reason
    }
    await api.post('stock-adjustments/', payload)
    alert('✅ Stock berhasil disesuaikan.')
    showModal.value = false
    form.value = { product: '', new_stock: '', reason: '' }
  } catch (err) {
    console.error('❌ Error submit:', err.response?.data || err)
    alert('Terjadi kesalahan. Silakan periksa kembali.')
  }
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
      <h1 class="text-lg font-semibold">HADIA STOK</h1>
    </div>

    <!-- Filter tanggal -->
      <div class="flex items-center gap-2 p-2">
        <div class="border rounded-sm px-2 py-1 w-48">
          <select @change="handleFilterChange($event)" class="w-full outline-none">
            <option value="today">{{ todayOptionText }}</option>
            <option value="week">📈 Semana</option>
            <option value="month">📆 Fulan</option>
            <option value="">🗓️ Hili kalendariu</option>
          </select>
        </div>
      </div>

      <!-- Popup kalender -->
      <div v-if="showDatePopup" class="fixed inset-0 bg-black/30 z-50 flex items-center justify-center">
        <div class="bg-white shadow border p-5 rounded w-[300px]">
          <div class="text-sm font-semibold mb-3">🛠️ Atur Rentang Tanggal</div>
          <label class="block text-xs mb-1">Data Inisiu</label>
          <input type="date" v-model="manualStart" class="border rounded px-2 py-1 w-full mb-2" />
          <label class="block text-xs mb-1">Data Final</label>
          <input type="date" v-model="manualEnd" class="border rounded px-2 py-1 w-full mb-4" />
          <div class="flex justify-end gap-2 text-xs">
            <button @click="showDatePopup = false" class="px-2 py-1 border rounded">Kansela</button>
            <button @click="applyManualDateFilter" class="px-2 py-1 border rounded text-blue-600">Ok</button>
          </div>
        </div>
      </div>

    <!-- Table -->
    <div class="p-2 flex flex-col flex-1 overflow-hidden">
      <div class="flex-1 overflow-auto border border-gray-300">
        <table class="w-full table-auto border-collapse text-sm">
          <thead class="bg-gradient-to-b from-white to-gray-100">
          <tr>
            <th class="border px-2 py-1">Produtu</th>
            <th class="border px-2 py-1 text-right">Stok Antes</th>
            <th class="border px-2 py-1 text-right">Stok Foun</th>
            <th class="border px-2 py-1">Razaun</th>
            <th class="border px-2 py-1">Adjusted by</th>
            <th class="border px-2 py-1">Adjusted at</th>
          </tr>
        </thead>
          <tbody>
            <tr v-for="item in items" :key="item.id" class="hover:bg-gray-50">
              <td class="border px-2 py-1">
                {{ item.product_name }}
              </td>
              <td class="border px-2 py-1 text-right">
                {{ item.old_stock }}
              </td>
              <td class="border px-2 py-1 text-right">
                {{ item.new_stock }}
              </td>
              <td class="border px-2 py-1">
                {{ item.reason }}
              </td>
              <td class="border px-2 py-1">
                {{ item.adjusted_by }}
              </td>
              <td class="border px-2 py-1">
                {{ formatDate(item.adjusted_at) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Footer -->
      <div class="flex justify-between items-center mt-2 text-xs">
        <div>
          <select v-model="perPage" class="border px-1 py-0.5 rounded-sm">
            <option v-for="n in [10, 20, 50]" :key="n" :value="n">{{ n }}/pagina</option>
          </select>
        </div>
        <div class="space-x-2 text-base">
          <button @click="refresh" class="hover:text-blue-600">🔄</button>
          <button @click="addItem" class="hover:text-green-600">➕</button>
        </div>
      </div>
    </div>

    <!-- 🔶 Modal Input -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
      <div class="bg-white p-4 rounded shadow-md w-[350px] space-y-3">
        <h2 class="text-lg font-bold">Tambah Penyesuaian Stok</h2>

        <div>
          <label class="block text-sm">Produk *</label>
          <select v-model="form.product" class="border w-full px-2 py-1 rounded">
            <option value="">Pilih produk</option>
            <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }} - {{ p.sku }}</option>
          </select>
        </div>

        <div>
          <label class="block text-sm">Stok Baru *</label>
          <input v-model="form.new_stock" type="number" class="border w-full px-2 py-1 rounded" />
        </div>

        <div>
          <label class="block text-sm">Alasan *</label>
          <textarea v-model="form.reason" rows="2" class="border w-full px-2 py-1 rounded"></textarea>
        </div>

        <div class="flex justify-end space-x-2 mt-3">
          <button @click="showModal = false" class="px-3 py-1 border rounded text-gray-600 hover:bg-gray-100">Batal</button>
          <button @click="submitForm" class="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">Simpan</button>
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
