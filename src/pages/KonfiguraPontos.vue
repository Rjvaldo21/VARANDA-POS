<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import api, { baseURL } from '@/axios'
import FooterActions from '@/components/pos/FooterActions.vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

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

// Pastikan ada access token sebelum panggil endpoint protected
const ensureAuth = async () => {
  let access = getAccessToken()
  const refresh = getRefreshToken()

  if (!access && refresh) {
    try {
      const { data } = await api.post('token/refresh/', { refresh })
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
const getLogoUrl = (path) => (!path ? '' : (path.startsWith('http') ? path : `baseURL.replace("/api/", "")${path}`))
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
           @error="e => e.target.src = baseURL.replace('/api/', '') + '/media/logos/default.jpg'"
           class="h-6 w-6 rounded" />
      <h1 class="text-lg font-semibold">POINTS MANAGEMENT</h1>
    </div>

    <div class="p-4 flex-1 flex overflow-hidden gap-6">
      <!-- LEFT: Redemption Rules -->
      <div class="w-1/2 flex flex-col bg-white border border-gray-200 rounded-lg overflow-hidden shadow-sm">
        <div class="bg-blue-50 px-4 py-3 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
            </svg>
            Points Redemption Rules
          </h3>
          <p class="text-sm text-gray-600">Configure how customers can redeem their points</p>
        </div>
        
        <div class="flex-1 overflow-auto">
          <table class="w-full border-collapse text-sm">
            <thead class="bg-gray-50">
              <tr>
                <th class="border-b border-gray-200 px-3 py-3 text-left font-medium text-gray-700">Rule Name</th>
                <th class="border-b border-gray-200 px-3 py-3 text-left font-medium text-gray-700">Points Required</th>
                <th class="border-b border-gray-200 px-3 py-3 text-left font-medium text-gray-700">Details</th>
                <th class="border-b border-gray-200 px-3 py-3 text-left font-medium text-gray-700">Discount</th>
                <th class="border-b border-gray-200 px-3 py-3 text-center font-medium text-gray-700">Active</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr v-for="row in redeem" :key="row.id" class="hover:bg-gray-50">
                <td class="px-3 py-3 font-medium text-gray-900 truncate" :title="row.name">{{ row.name }}</td>
                <td class="px-3 py-3 text-gray-700">
                  <span class="inline-flex px-2 py-1 text-xs font-semibold bg-blue-100 text-blue-800 rounded-full">{{ row.points_required }} pts</span>
                </td>
                <td class="px-3 py-3 text-sm text-gray-600 truncate" :title="row.detail">{{ row.detail }}</td>
                <td class="px-3 py-3 text-sm font-medium text-green-600">${{ toMoney(row.discount_amount) }}</td>
                <td class="px-3 py-3 text-center">
                  <label class="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" :checked="row.is_active" @change="(e) => { row.is_active = e.target.checked; toggleActive('redeem', row) }" class="sr-only peer" />
                    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="flex justify-between items-center px-4 py-3 border-t border-gray-200 bg-gray-50">
          <div class="text-sm text-gray-600">{{ redeem.length }} rule(s)</div>
          <div class="flex space-x-2">
            <button @click="refresh" class="text-blue-600 hover:text-blue-900 transition-colors" title="Refresh">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
            </button>
            <button @click="add('redeem')" class="text-green-600 hover:text-green-900 transition-colors" title="Add Rule">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
              </svg>
            </button>
            <button @click="edit('redeem')" class="text-gray-600 hover:text-gray-900 transition-colors" title="Edit Rule">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
              </svg>
            </button>
            <button @click="remove('redeem')" class="text-red-600 hover:text-red-900 transition-colors" title="Delete Rule">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- RIGHT: Earning Rules -->
      <div class="w-1/2 flex flex-col bg-white border border-gray-200 rounded-lg overflow-hidden shadow-sm">
        <div class="bg-green-50 px-4 py-3 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center">
            <svg class="w-5 h-5 mr-2 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
            </svg>
            Points Earning Rules
          </h3>
          <p class="text-sm text-gray-600">Configure how customers earn points from purchases</p>
        </div>
        
        <div class="flex-1 overflow-auto">
          <table class="w-full border-collapse text-sm">
            <thead class="bg-gray-50">
              <tr>
                <th class="border-b border-gray-200 px-3 py-3 text-left font-medium text-gray-700">Rule Name</th>
                <th class="border-b border-gray-200 px-3 py-3 text-left font-medium text-gray-700">Minimum Purchase</th>
                <th class="border-b border-gray-200 px-3 py-3 text-left font-medium text-gray-700">Points Awarded</th>
                <th class="border-b border-gray-200 px-3 py-3 text-center font-medium text-gray-700">Active</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr v-for="row in earning" :key="row.id" class="hover:bg-gray-50">
                <td class="px-3 py-3 font-medium text-gray-900 truncate" :title="row.name">{{ row.name }}</td>
                <td class="px-3 py-3 text-sm font-medium text-gray-700">${{ toMoney(row.min_total) }}</td>
                <td class="px-3 py-3 text-gray-700">
                  <span class="inline-flex px-2 py-1 text-xs font-semibold bg-green-100 text-green-800 rounded-full">{{ row.points_awarded }} pts</span>
                </td>
                <td class="px-3 py-3 text-center">
                  <label class="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" :checked="row.is_active" @change="(e) => { row.is_active = e.target.checked; toggleActive('earn', row) }" class="sr-only peer" />
                    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="flex justify-between items-center px-4 py-3 border-t border-gray-200 bg-gray-50">
          <div class="text-sm text-gray-600">{{ earning.length }} rule(s)</div>
          <div class="flex space-x-2">
            <button @click="refresh" class="text-blue-600 hover:text-blue-900 transition-colors" title="Refresh">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
            </button>
            <button @click="add('earn')" class="text-green-600 hover:text-green-900 transition-colors" title="Add Rule">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
              </svg>
            </button>
            <button @click="edit('earn')" class="text-gray-600 hover:text-gray-900 transition-colors" title="Edit Rule">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
              </svg>
            </button>
            <button @click="remove('earn')" class="text-red-600 hover:text-red-900 transition-colors" title="Delete Rule">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
              </svg>
            </button>
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

