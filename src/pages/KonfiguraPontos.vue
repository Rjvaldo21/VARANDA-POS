<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import FooterActions from '@/components/pos/FooterActions.vue'

/* ================= AXIOS + JWT ================= */
const api = axios.create({ baseURL: 'http://localhost:8000/api' })

// Helper ambil token dari berbagai kemungkinan key & storage
const getFromStores = (keys) => {
  for (const key of keys) {
    const v1 = localStorage.getItem(key)
    if (v1) return v1
    const v2 = sessionStorage.getItem(key)
    if (v2) return v2
  }
  return null
}
const getAccessToken = () =>
  getFromStores(['access', 'token', 'access_token'])
const getRefreshToken = () =>
  getFromStores(['refresh', 'refresh_token'])

// Selalu sisipkan access token terbaru
api.interceptors.request.use((config) => {
  const t = getAccessToken()
  config.headers = config.headers || {}
  if (t) config.headers.Authorization = `Bearer ${t}`
  return config
})

// Auto refresh saat 401 lalu retry request
let refreshingPromise = null
api.interceptors.response.use(
  (r) => r,
  async (err) => {
    const resp = err.response
    const original = resp?.config

    if (resp?.status === 401 && original && !original._retry) {
      const refresh = getRefreshToken()
      if (!refresh) {
        console.warn('[auth] 401 & no refresh token found')
        return Promise.reject(err)
      }
      try {
        original._retry = true
        refreshingPromise =
          refreshingPromise || axios.post('http://localhost:8000/api/token/refresh/', { refresh })
        const { data } = await refreshingPromise
        refreshingPromise = null
        // simpan access baru
        localStorage.setItem('access', data.access)
        // retry request sebelumnya
        original.headers = original.headers || {}
        original.headers.Authorization = `Bearer ${data.access}`
        return api(original)
      } catch (e) {
        refreshingPromise = null
        console.error('[auth] refresh gagal, hapus token')
        localStorage.removeItem('access')
        localStorage.removeItem('refresh')
        sessionStorage.removeItem('access')
        sessionStorage.removeItem('refresh')
        return Promise.reject(e)
      }
    }

    // Error lain -> tampilkan ringkas
    const status = resp?.status
    const msg = typeof resp?.data === 'string' ? resp.data : JSON.stringify(resp?.data)
    console.error('API ERROR', status, msg)
    alert(`API error ${status || ''}: ${msg}`)
    return Promise.reject(err)
  }
)

// Pastikan ada access token sebelum panggil endpoint protected
const ensureAuth = async () => {
  let access = getAccessToken()
  const refresh = getRefreshToken()

  if (!access && refresh) {
    try {
      const { data } = await axios.post('http://localhost:8000/api/token/refresh/', { refresh })
      access = data.access
      localStorage.setItem('access', access)
    } catch (e) {
      localStorage.removeItem('access'); localStorage.removeItem('refresh')
      sessionStorage.removeItem('access'); sessionStorage.removeItem('refresh')
      return false
    }
  }
  // Debug ringkas di console supaya tahu kenapa gagal
  if (!access) {
    console.warn('[auth] ensureAuth: tidak menemukan access token di local/sessionStorage')
  }
  return !!access
}

/* ================= Header toko ================= */
const store = ref({ name: '', address: '', logo: '', version: '', location: '' })
const getLogoUrl = (path) => (!path ? '' : (path.startsWith('http') ? path : `http://localhost:8000${path}`))
const formattedAddress = computed(() => (store.value.address ? store.value.address.replace(/\n/g, '<br />') : ''))

/* ================= State poin ================= */
const earning = ref([])   // PointsEarningRule
const redeem  = ref([])   // PointsRedemptionRule
const perPageLeft = ref(10)
const perPageRight = ref(10)

/* ================= Helpers ================= */
const toMoney = (v) => (v == null ? '0.00' : Number(v).toFixed(2))
const asInt = (v) => {
  const n = parseInt(String(v).trim(), 10)
  return Number.isFinite(n) ? n : 0
}
const asMoney = (v) => {
  const n = Number(String(v).trim().replace(',', '.'))
  return Number.isFinite(n) ? n.toFixed(2) : '0.00'
}
const asBool = (v, def=true) => {
  if (v == null || v === '') return def
  const s = String(v).trim().toLowerCase()
  return ['y','ya','yes','true','1'].some(k => s.startsWith(k))
}

/* ================= Fetchers ================= */
const fetchStore = async () => {
  try {
    const res = await api.get('/store-profile/')
    if (Array.isArray(res.data) && res.data.length > 0) store.value = res.data[0]
  } catch (e) {
    console.error('Gagal fetch store profile:', e)
  }
}

const fetchPoints = async () => {
  try {
    const ok = await ensureAuth()
    if (!ok) { alert('Silakan login terlebih dahulu untuk melihat konfigurasi poin.'); return }

    const [earnRes, redeemRes] = await Promise.all([
      api.get('/points/earning-rules/'),
      api.get('/points/redemption-rules/')
    ])

    earning.value = (earnRes.data || []).map(r => ({
      id: r.id,
      name: r.name ?? '',
      min_total: r.min_total,
      points_awarded: r.points_awarded,
      is_active: !!r.is_active
    }))

    redeem.value = (redeemRes.data || []).map(r => ({
      id: r.id,
      name: r.name ?? '',
      points_required: r.points_required,
      detail: r.detail ?? '',
      discount_amount: r.discount_amount ?? '0.00',
      is_active: !!r.is_active
    }))
  } catch (e) {
    console.error('Gagal fetch poin:', e)
  }
}

onMounted(async () => {
  await fetchStore()
  await fetchPoints()
})

/* ================= Actions ================= */
const refresh = async () => { await fetchPoints() }

/* Toggle is_active via PATCH */
const toggleActive = async (ctx, row) => {
  try {
    const url = ctx === 'redeem'
      ? `/points/redemption-rules/${row.id}/`
      : `/points/earning-rules/${row.id}/`
    await api.patch(url, { is_active: row.is_active })
  } catch (e) {
    console.error('Gagal ubah status aktif:', e)
    alert('Gagal ubah status aktif')
    row.is_active = !row.is_active // revert
  }
}

/* Tambah rule */
const add = async (ctx) => {
  try {
    if (!(await ensureAuth())) { alert('Silakan login terlebih dahulu.'); return }

    if (ctx === 'redeem') {
      const name = window.prompt('Name?', '') ?? ''
      const points_required = window.prompt('Points required? (angka)', '100'); if (points_required === null) return
      const detail = window.prompt('Detail? (mis. Diskon $5)', '') ?? ''
      const discount_amount = window.prompt('Discount amount? (mis. 5.00, kosongkan jika tidak)', '0.00') ?? '0.00'
      const is_active = asBool(window.prompt('Aktif? (y/n)', 'y'), true)

      await api.post('/points/redemption-rules/', {
        name,
        points_required: asInt(points_required),
        detail,
        discount_amount: asMoney(discount_amount),
        is_active
      }, { headers: { 'Content-Type': 'application/json' } })
    } else {
      const name = window.prompt('Name?', '') ?? ''
      const min_total = window.prompt('Min total? (mis. 100.00)', '100.00'); if (min_total === null) return
      const points_awarded = window.prompt('Points awarded?', '5'); if (points_awarded === null) return
      const is_active = asBool(window.prompt('Aktif? (y/n)', 'y'), true)

      await api.post('/points/earning-rules/', {
        name,
        min_total: asMoney(min_total),
        points_awarded: asInt(points_awarded),
        is_active
      }, { headers: { 'Content-Type': 'application/json' } })
    }
    await fetchPoints()
  } catch (e) {}
}

/* Edit rule */
const edit = async (ctx) => {
  try {
    if (!(await ensureAuth())) { alert('Silakan login terlebih dahulu.'); return }

    if (ctx === 'redeem') {
      if (redeem.value.length === 0) return alert('Belum ada data')
      const id = window.prompt('ID rule yang mau diedit?', redeem.value[0]?.id || ''); if (!id) return
      const row = redeem.value.find(r => String(r.id) === String(id)); if (!row) return alert('ID tidak ditemukan')

      const name = window.prompt('Name?', row.name ?? '') ?? row.name
      const points_required = window.prompt('Points required?', String(row.points_required)); if (points_required === null) return
      const detail = window.prompt('Detail?', row.detail || '') ?? row.detail
      const discount_amount = window.prompt('Discount amount?', String(row.discount_amount ?? '0.00')) ?? row.discount_amount

      await api.put(`/points/redemption-rules/${id}/`, {
        name,
        points_required: Number(points_required || 0),
        detail,
        discount_amount
      }, { headers: { 'Content-Type': 'application/json' } })
    } else {
      if (earning.value.length === 0) return alert('Belum ada data')
      const id = window.prompt('ID rule yang mau diedit?', earning.value[0]?.id || ''); if (!id) return
      const row = earning.value.find(r => String(r.id) === String(id)); if (!row) return alert('ID tidak ditemukan')

      const name = window.prompt('Name?', row.name ?? '') ?? row.name
      const min_total = window.prompt('Min total?', String(row.min_total)); if (min_total === null) return
      const points_awarded = window.prompt('Points awarded?', String(row.points_awarded)); if (points_awarded === null) return

      await api.put(`/points/earning-rules/${id}/`, {
        name,
        min_total: min_total || '0.00',
        points_awarded: Number(points_awarded || 0)
      }, { headers: { 'Content-Type': 'application/json' } })
    }
    await fetchPoints()
  } catch (e) {
    console.error('Gagal edit rule:', e)
    alert('Gagal edit rule')
  }
}

/* Hapus rule */
const remove = async (ctx) => {
  try {
    if (!(await ensureAuth())) { alert('Silakan login terlebih dahulu.'); return }

    const arr = ctx === 'redeem' ? redeem.value : earning.value
    if (arr.length === 0) return alert('Belum ada data')
    const id = window.prompt('ID rule yang mau dihapus?', arr[0]?.id || ''); if (!id) return
    if (!confirm('Yakin hapus rule ini?')) return
    await api.delete(ctx === 'redeem' ? `/points/redemption-rules/${id}/` : `/points/earning-rules/${id}/`)
    await fetchPoints()
  } catch (e) {
    console.error('Gagal hapus rule:', e)
    alert('Gagal hapus rule')
  }
}
</script>

<template>
  <div class="bg-white border border-gray-50 rounded-sm shadow text-sm flex flex-col h-full">
    <!-- Header -->
    <div class="flex items-center gap-2 p-2 border-b border-gray-300 bg-gray-50">
      <img :src="store.logo_base64 || getLogoUrl(store.logo)"
           @error="e => e.target.src = 'http://127.0.0.1:8000/media/logos/default.jpg'"
           class="h-6 w-6 rounded" />
      <h1 class="text-lg font-semibold">PONTUS</h1>
    </div>

    <div class="p-2 flex-1 flex overflow-hidden gap-2">
      <!-- LEFT: Redemption Rules -->
      <div class="w-1/2 flex flex-col border border-gray-300 rounded-sm overflow-hidden">
        <div class="text-sm font-semibold px-2 py-1 border-b bg-gray-100">Points redemption rules</div>
        <div class="flex-1 overflow-auto">
          <table class="min-w-[700px] w-full border-collapse text-sm table-fixed">
            <thead class="bg-gradient-to-b from-white to-gray-100">
              <tr>
                <th class="border px-2 py-1 w-[20%] text-left">Name</th>
                <th class="border px-2 py-1 w-[15%] text-left">Points required</th>
                <th class="border px-2 py-1 w-[30%] text-left">Detail</th>
                <th class="border px-2 py-1 w-[15%] text-left">Discount amount</th>
                <th class="border px-2 py-1 w-[12%] text-center">Is active</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in redeem" :key="row.id" class="hover:bg-gray-50">
                <td class="border px-2 py-1 truncate" :title="row.name">{{ row.name }}</td>
                <td class="border px-2 py-1">{{ row.points_required }}</td>
                <td class="border px-2 py-1 truncate" :title="row.detail">{{ row.detail }}</td>
                <td class="border px-2 py-1">${{ toMoney(row.discount_amount) }}</td>
                <td class="border px-2 py-1 text-center">
                  <input type="checkbox" :checked="row.is_active" @change="(e) => { row.is_active = e.target.checked; toggleActive('redeem', row) }" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="flex justify-between items-center px-2 py-1 border-t text-xs bg-white">
          <div class="flex items-center gap-1">
            <span>1 / 1</span>
            <select v-model="perPageLeft" class="border px-1 py-0.5 rounded-sm">
              <option v-for="n in [10, 20, 50]" :key="n" :value="n">{{ n }}/page</option>
            </select>
          </div>
          <div class="space-x-2 text-base">
            <button @click="refresh" class="hover:text-blue-600">🔄</button>
            <button @click="add('redeem')" class="hover:text-green-600">➕</button>
            <button @click="edit('redeem')" class="hover:text-gray-600">✏️</button>
            <button @click="remove('redeem')" class="hover:text-red-600">❌</button>
          </div>
        </div>
      </div>

      <!-- RIGHT: Earning Rules -->
      <div class="w-1/2 flex flex-col border border-gray-300 rounded-sm overflow-hidden">
        <div class="text-sm font-semibold px-2 py-1 border-b bg-gray-100">Points earning rules</div>
        <div class="flex-1 overflow-auto">
          <table class="min-w-[650px] w-full border-collapse text-sm table-fixed">
            <thead class="bg-gradient-to-b from-white to-gray-100">
              <tr>
                <th class="border px-2 py-1 w-[30%] text-left">Name</th>
                <th class="border px-2 py-1 w-[20%] text-left">Min total</th>
                <th class="border px-2 py-1 w-[20%] text-left">Points awarded</th>
                <th class="border px-2 py-1 w-[12%] text-center">Is active</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in earning" :key="row.id" class="hover:bg-gray-50">
                <td class="border px-2 py-1 truncate" :title="row.name">{{ row.name }}</td>
                <td class="border px-2 py-1">${{ toMoney(row.min_total) }}</td>
                <td class="border px-2 py-1">{{ row.points_awarded }}</td>
                <td class="border px-2 py-1 text-center">
                  <input type="checkbox" :checked="row.is_active" @change="(e) => { row.is_active = e.target.checked; toggleActive('earn', row) }" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="flex justify-between items-center px-2 py-1 border-t text-xs bg-white">
          <div class="flex items-center gap-1">
            <span>1 / 1</span>
            <select v-model="perPageRight" class="border px-1 py-0.5 rounded-sm">
              <option v-for="n in [10, 20, 50]" :key="n" :value="n">{{ n }}/page</option>
            </select>
          </div>
          <div class="space-x-2 text-base">
            <button @click="refresh" class="hover:text-blue-600">🔄</button>
            <button @click="add('earn')" class="hover:text-green-600">➕</button>
            <button @click="edit('earn')" class="hover:text-gray-600">✏️</button>
            <button @click="remove('earn')" class="hover:text-red-600">❌</button>
          </div>
        </div>
      </div>
    </div>
  </div>
  <FooterActions />
</template>

<style scoped>
table { border-collapse: collapse; }
th, td { font-size: 13px; }
</style>

