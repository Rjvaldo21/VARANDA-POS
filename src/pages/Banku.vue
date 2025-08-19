<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'
import FooterActions from '@/components/pos/FooterActions.vue'

const RAW_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const API_BASE = RAW_BASE.replace(/\/+$/, '').endsWith('/api')
  ? RAW_BASE.replace(/\/+$/, '')
  : RAW_BASE.replace(/\/+$/, '') + '/api'

const api = axios.create({ baseURL: API_BASE })


function attachAuth() {
  const raw = localStorage.getItem('access_token') || localStorage.getItem('token') || ''
  const header = raw.includes(' ') ? raw : (raw ? `Bearer ${raw}` : '')
  if (header) api.defaults.headers.common['Authorization'] = header
}

const store = ref({ name: '', address: '', logo: '', version: '', location: '' })

const formattedAddress = computed(() =>
  store.value.address ? store.value.address.replace(/\n/g, '<br />') : ''
)

const ORIGIN_BASE = API_BASE.replace(/\/api\/?$/, '')

const getLogoUrl = (path) => {
  if (!path) return ''
  return path.startsWith('http') ? path : `${ORIGIN_BASE}${path}`
}

const banks = ref([])
const loading = ref(false)
const perPage = ref(10)
const page = ref(1)

const pagedBanks = computed(() => {
  const start = (page.value - 1) * perPage.value
  return banks.value.slice(start, start + perPage.value)
})

const showForm = ref(false)
const isEditing = ref(false)
const currentId = ref(null)

const form = reactive({
  name: '',
  code: '',
  account_name: '',
  account_number: '',
  is_active: true,
  notes: '',
  percent_fee: '0.00',
  fixed_fee: '0.00',
  min_fee: '0.00',
  max_fee: '0.00',
  fee_paid_by_customer: true,
  enable_credit: false,
  enable_transfer: true,
  enable_qris: false,
})

function resetForm() {
  isEditing.value = false
  currentId.value = null
  Object.assign(form, {
    name: '',
    code: '',
    account_name: '',
    account_number: '',
    is_active: true,
    notes: '',
    percent_fee: '0.00',
    fixed_fee: '0.00',
    min_fee: '0.00',
    max_fee: '0.00',
    fee_paid_by_customer: true,
    enable_credit: false,
    enable_transfer: true,
    enable_qris: false,
  })
}

async function fetchStore() {
  try {
    const res = await api.get('/store-profile/')
    if (res.data && res.data.length > 0) store.value = res.data[0]
  } catch (err) {
    console.error('Gagal fetch store profile:', err)
  }
}

async function fetchBanks() {
  loading.value = true
  try {
    const res = await api.get('/banks/')
    banks.value = Array.isArray(res.data) ? res.data : res.data?.results || []
  } catch (err) {
    console.error('Gagal fetch banks:', err)
  } finally {
    loading.value = false
  }
}

async function createBank() {
  try {
    const payload = { ...form }
    await api.post('/banks/', payload)
    showForm.value = false
    await fetchBanks()
  } catch (err) {
    console.error('Gagal membuat bank:', err?.response?.data || err)
  }
}

async function updateBank() {
  try {
    const payload = { ...form }
    await api.put(`/banks/${currentId.value}/`, payload)
    showForm.value = false
    await fetchBanks()
  } catch (err) {
    console.error('Gagal update bank:', err?.response?.data || err)
  }
}

async function removeBank(item) {
  const ok = window.confirm(`Hapus bank "${item.name}"?`)
  if (!ok) return
  try {
    await api.delete(`/banks/${item.id}/`)
    await fetchBanks()
  } catch (err) {
    console.error('Gagal hapus bank:', err?.response?.data || err)
  }
}

function refresh() {
  fetchBanks()
}

function addBank() {
  resetForm()
  isEditing.value = false
  showForm.value = true
}

function editBank(item) {
  resetForm()
  isEditing.value = true
  currentId.value = item.id
  Object.assign(form, {
    name: item.name || '',
    code: item.code || '',
    account_name: item.account_name || '',
    account_number: item.account_number || '',
    is_active: !!item.is_active,
    notes: item.notes || '',
    percent_fee: String(item.percent_fee ?? '0.00'),
    fixed_fee: String(item.fixed_fee ?? '0.00'),
    min_fee: String(item.min_fee ?? '0.00'),
    max_fee: String(item.max_fee ?? '0.00'),
    fee_paid_by_customer: !!item.fee_paid_by_customer,
    enable_credit: !!item.enable_credit,
    enable_transfer: !!item.enable_transfer,
    enable_qris: !!item.enable_qris,
  })
  showForm.value = true
}

function submitForm() {
  if (isEditing.value) return updateBank()
  return createBank()
}

onMounted(async () => {
  attachAuth()
  await fetchStore()
  await fetchBanks()
})
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
      <h1 class="text-lg font-semibold">BANKU</h1>

      <div class="ml-auto flex items-center gap-2">
        <button @click="refresh" class="px-2 py-1 border rounded hover:bg-gray-100">🔄 Refresh</button>
        <button @click="addBank" class="px-2 py-1 border rounded hover:bg-gray-100">➕ Tambah</button>
      </div>
    </div>

    <!-- Table -->
    <div class="p-2 flex flex-col flex-1 overflow-hidden">
      <div class="flex-1 overflow-x-auto border border-gray-300">
        <table class="min-w-[800px] w-full border-collapse text-sm">
          <thead class="bg-gradient-to-b from-white to-gray-100">
            <tr>
              <th class="border px-2 py-1 text-left w-[22%]">Banku</th>
              <th class="border px-2 py-1 text-left w-[12%]">Kódigu</th>
              <th class="border px-2 py-1 text-left w-[20%]">Konta Bankaria</th>
              <th class="border px-2 py-1 text-left w-[12%]">% Taxa</th>
              <th class="border px-2 py-1 text-left w-[12%]">Taxa Fixu</th>
              <th class="border px-2 py-1 text-left w-[8%]">Ativu</th>
              <th class="border px-2 py-1 text-left w-[14%]">Asaun</th>
            </tr>
          </thead>

          <tbody v-if="!loading">
            <tr v-for="b in pagedBanks" :key="b.id" class="hover:bg-gray-50">
              <td class="border px-2 py-1">{{ b.name }}</td>
              <td class="border px-2 py-1">{{ b.code || '-' }}</td>
              <td class="border px-2 py-1">
                <div class="leading-tight">
                  <div class="font-medium">{{ b.account_name || '-' }}</div>
                  <div class="text-xs text-gray-600">{{ b.account_number || '-' }}</div>
                </div>
              </td>
              <td class="border px-2 py-1">{{ b.percent_fee ?? '0.00' }}%</td>
              <td class="border px-2 py-1">{{ b.fixed_fee ?? '0.00' }}</td>
              <td class="border px-2 py-1">
                <span class="px-2 py-0.5 rounded text-xs" :class="b.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'">
                  {{ b.is_active ? 'ON' : 'OFF' }}
                </span>
              </td>
              <td class="border px-2 py-1">
                <div class="flex items-center gap-2">
                  <button @click="editBank(b)" class="hover:text-gray-700" title="Edit">✏️</button>
                  <button @click="removeBank(b)" class="hover:text-red-600" title="Hapus">❌</button>
                </div>
              </td>
            </tr>
          </tbody>

          <tbody v-else>
            <tr>
              <td colspan="7" class="border px-2 py-3 text-center text-gray-600">Memuat data…</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Footer -->
      <div class="flex justify-between items-center mt-2 text-xs">
        <div class="flex items-center gap-2">
          <label>Rows:</label>
          <select v-model="perPage" class="border px-1 py-0.5 rounded-sm">
            <option v-for="n in [10, 20, 50]" :key="n" :value="n">{{ n }}/hal</option>
          </select>
        </div>

        <div class="flex items-center gap-2">
          <button class="border rounded px-2 py-0.5" :disabled="page<=1" @click="page--">Prev</button>
          <span>Hal {{ page }}</span>
          <button class="border rounded px-2 py-0.5" :disabled="page*perPage >= banks.length" @click="page++">Next</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Modal Form -->
  <div v-if="showForm" class="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
    <div class="bg-white w-full max-w-2xl rounded shadow-lg">
      <div class="flex items-center justify-between border-b px-4 py-2">
        <h3 class="text-base font-semibold">{{ isEditing ? 'Edit Bank' : 'Tambah Bank' }}</h3>
        <button class="text-lg" @click="showForm=false">✖</button>
      </div>

      <div class="p-4 grid grid-cols-2 gap-3 text-sm">
        <div>
          <label class="block mb-1">Name *</label>
          <input v-model="form.name" type="text" class="w-full border px-2 py-1 rounded" />
        </div>
        <div>
          <label class="block mb-1">Code</label>
          <input v-model="form.code" type="text" class="w-full border px-2 py-1 rounded" />
        </div>

        <div>
          <label class="block mb-1">Account name</label>
          <input v-model="form.account_name" type="text" class="w-full border px-2 py-1 rounded" />
        </div>
        <div>
          <label class="block mb-1">Account number</label>
          <input v-model="form.account_number" type="text" class="w-full border px-2 py-1 rounded" />
        </div>

        <div>
          <label class="block mb-1">Percent fee *</label>
          <input v-model="form.percent_fee" type="number" step="0.01" class="w-full border px-2 py-1 rounded" />
        </div>
        <div>
          <label class="block mb-1">Fixed fee *</label>
          <input v-model="form.fixed_fee" type="number" step="0.01" class="w-full border px-2 py-1 rounded" />
        </div>

        <div>
          <label class="block mb-1">Min fee *</label>
          <input v-model="form.min_fee" type="number" step="0.01" class="w-full border px-2 py-1 rounded" />
        </div>
        <div>
          <label class="block mb-1">Max fee *</label>
          <input v-model="form.max_fee" type="number" step="0.01" class="w-full border px-2 py-1 rounded" />
        </div>

        <div class="col-span-2">
          <label class="inline-flex items-center gap-2 mr-4">
            <input type="checkbox" v-model="form.is_active" /> <span>Is active</span>
          </label>
          <label class="inline-flex items-center gap-2 mr-4">
            <input type="checkbox" v-model="form.fee_paid_by_customer" /> <span>Fee paid by customer</span>
          </label>
          <label class="inline-flex items-center gap-2 mr-4">
            <input type="checkbox" v-model="form.enable_credit" /> <span>Enable credit</span>
          </label>
          <label class="inline-flex items-center gap-2 mr-4">
            <input type="checkbox" v-model="form.enable_transfer" /> <span>Enable transfer</span>
          </label>
          <label class="inline-flex items-center gap-2">
            <input type="checkbox" v-model="form.enable_qris" /> <span>Enable qris</span>
          </label>
        </div>

        <div class="col-span-2">
          <label class="block mb-1">Notes</label>
          <textarea v-model="form.notes" rows="3" class="w-full border px-2 py-1 rounded"></textarea>
        </div>
      </div>

      <div class="flex justify-end gap-2 border-t px-4 py-2">
        <button class="px-3 py-1 border rounded" @click="showForm=false">Batal</button>
        <button class="px-3 py-1 border rounded bg-gray-100 hover:bg-gray-200" @click="submitForm">
          {{ isEditing ? 'Simpan Perubahan' : 'Simpan' }}
        </button>
      </div>
    </div>
  </div>

  <FooterActions />
</template>

<style scoped>
table { border-collapse: collapse; }
th, td { font-size: 13px; }
</style>
