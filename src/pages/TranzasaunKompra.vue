<script setup>
import { ref, computed, onMounted } from 'vue'
import FooterActions from '@/components/pos/FooterActions.vue'
import api, { baseURL } from '@/axios'

const store = ref({
  name: '',
  address: '',
  logo: '',
  logo_base64: '',
  version: '',
  location: ''
})

const users = ref([])
const purchases = ref([])
// const filter = ref({ username: '', name: '', email: '' })
const perPage = ref(10)
const selectedUser = ref(null)
const selectedTransactionSummary = ref(null)
const isLoading = ref(true)


const filter = ref({
  nomor: '',
  supplier: '',
  tipe: 'all',     
  status: 'all',   
  tanggalAwal: '',
  tanggalAkhir: '',
  jatuhTempoAwal: '',
  jatuhTempoAkhir: '',
})

const showUserModal = ref(false)
const modalMode = ref('add') 
const userForm = ref({ username: '', first_name: '', last_name: '', email: '' })

const formattedAddress = computed(() =>
  store.value.address ? store.value.address.replace(/\n/g, '<br />') : ''
)

const getLogoUrl = (path) => {
  if (!path) return ''
  return path.startsWith('http') ? path : `${baseURL.replace("/api/", "")}${path}`
}

const formatPrice = (value) => {
  const number = Number(value)
  return isNaN(number)
    ? '$0.00'
    : new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(number)
}

const fetchUsers = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await api.get('users/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    users.value = response.data
  } catch (error) {
    console.error('❌ Falha fetch uzuariu:', error)
  }
}

const filteredPurchases = computed(() =>
  purchases.value.filter(p => {
    const tipeOk   = filter.value.tipe === 'all'   || p.payment_type === filter.value.tipe
    const statusOk = filter.value.status === 'all' || p.status === filter.value.status
    const nomorOk  = !filter.value.nomor    || (p.invoice_number || '').toLowerCase().includes(filter.value.nomor.toLowerCase())
    const supOk    = !filter.value.supplier || (p.supplier?.name || '').toLowerCase().includes(filter.value.supplier.toLowerCase())

    const inRange = (s, a, b) => {
      if (!a && !b) return true
      if (!s) return false
      const d = String(s).slice(0,10)
      return (!a || d >= a) && (!b || d <= b)
    }
    const tglOk  = inRange(p.date,     filter.value.tanggalAwal,      filter.value.tanggalAkhir)
    const dueOk  = inRange(p.due_date, filter.value.jatuhTempoAwal,   filter.value.jatuhTempoAkhir)

    return tipeOk && statusOk && nomorOk && supOk && tglOk && dueOk
  })
)

const totalHutang = computed(() =>
  filteredPurchases.value.reduce((sum, p) => {
    const amount = Number(p.amount_due || p.total || 0)
    return sum + amount
  }, 0)
)


const todayFormatted = new Date().toLocaleDateString('en-GB')


const showDatePopup = ref(false)
const datePickerMode = ref('date')
const manualStart = ref('')
const manualEnd = ref('')
const toDateOnly = s => (s ? String(s).slice(0,10) : '')

const applyQuickFilter = (range, mode) => {
  const now = new Date()
  const today = now.toISOString().slice(0,10)

  const setRange = (from, to) => {
    if (mode === 'date') {
      filter.value.tanggalAwal = from
      filter.value.tanggalAkhir = to
    } else {
      filter.value.jatuhTempoAwal = from
      filter.value.jatuhTempoAkhir = to
    }
  }

  if (range === 'today') {
    setRange(today, today)
  }
}

const handleFilterChange = (mode, e) => {
  const v = e.target.value
  if (v === '') {
    datePickerMode.value = mode
    manualStart.value = ''
    manualEnd.value = ''
    showDatePopup.value = true
  } else {
    applyQuickFilter(v, mode)
  }
}

const applyManualDateFilter = () => {
  const from = toDateOnly(manualStart.value)
  const to   = toDateOnly(manualEnd.value)
  if (datePickerMode.value === 'date') {
    filter.value.tanggalAwal = from
    filter.value.tanggalAkhir = to
  } else {
    filter.value.jatuhTempoAwal = from
    filter.value.jatuhTempoAkhir = to
  }
  showDatePopup.value = false
}


const fetchStoreProfile = async () => {
  try {
    const res = await api.get('store-profile/')
    if (res.data && res.data.length > 0) {
      store.value = res.data[0]
      console.log('Logo URL:', getLogoUrl(store.value.logo))
    }
  } catch (err) {
    console.error('❌ Falha fetch perfil loja:', err)
  }
}

const fetchPurchases = async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await api.get('purchases/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    purchases.value = res.data
  } catch (err) {
    console.error('❌ Falha fetch kompras:', err)
  }
}

const saveUser = async () => {
  const token = localStorage.getItem('token')
  const headers = { Authorization: `Bearer ${token}` }

  try {
    if (modalMode.value === 'add') {
      await api.post('users/', userForm.value, { headers })
    } else {
      await api.put(`users/${selectedUser.value.id}/`, userForm.value, { headers })
    }

    showUserModal.value = false
    await fetchUsers()
    alert('✅ Uzuariu salva ho susesu')
  } catch (err) {
    console.error('❌ Falha salva uzuariu:', err)
    alert('Akontese erru ida bainhira salva utilizadór.')
  }
}

const deleteUser = async () => {
  if (!selectedUser.value) return alert('⚠️ Hili utilizadór ne\'ebé ita-boot hakarak atu hamoos')
  const konfirmasi = confirm(`Ita iha serteza katak hakarak atu hamoos utilizadór?: ${selectedUser.value.username}?`)
  if (!konfirmasi) return

  try {
    const token = localStorage.getItem('token')
    await api.delete(`users/${selectedUser.value.id}/`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    await fetchUsers()
    selectedUser.value = null
    alert('❌ Utilizadór hamoos ho susesu')
  } catch (err) {
    console.error('❌ La konsege hamoos utilizadór:', err)
    alert('Erru ida akontese bainhira hamoos utilizadór')
  }
}

const resetPassword = () => {
  if (!selectedUser.value) return alert('⚠️ Hili uluk utilizadór')
  alert(`🔑 Reset senha ba: ${selectedUser.value.username}`)
}

const lockUser = async () => {
  if (!selectedUser.value) return alert('⚠️ Hili uluk utilizadór')

  try {
    const token = localStorage.getItem('token')
    await api.patch(`users/${selectedUser.value.id}/`, {
      is_active: false
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })
    await fetchUsers()
    alert('🔒 Uzuáriu dezativa ho susesu')
  } catch (err) {
    console.error('❌ La konsege dezativa utilizadór:', err)
    alert('La konsege dezativa utilizadór')
  }
}

onMounted(async () => {
  await Promise.all([
    fetchStoreProfile(),
    fetchPurchases(),
    fetchUsers()
  ])
  isLoading.value = false
})
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
      <h1 class="text-lg font-semibold">KOMPRA</h1>
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
        <table class="w-max lg:w-full min-w-[1100px] lg:min-w-[1300px] border-collapse text-sm table-fixed">
          <colgroup>
            <col style="width:9rem"  />  
            <col style="width:12rem" /> 
            <col style="width:16rem" />  
            <col style="width:9rem"  /> 
            <col style="width:10rem" />  
            <col style="width:10rem" />  
            <col style="width:10rem" />  
            <col style="width:10rem" />  
            <col style="width:10rem" />  
            <col style="width:11rem" />  
          </colgroup>

          <thead class="bg-gradient-to-b from-white to-gray-100">
            <tr>
              <th class="th text-left">Data</th>
              <th class="th text-left">Numeru</th>
              <th class="th text-left">Fornesedór</th>
              <th class="th text-left">Tipu</th>
              <th class="th text-left">Data Remata</th>
              <th class="th text-left">Status</th>
              <th class="th text-right">Subtotal</th>
              <th class="th text-right">Disc. Form</th>
              <th class="th text-right">Diskontu</th>
              <th class="th text-right">Total</th>
            </tr>

            <!-- Baris Filter -->
            <tr>
              <th class="th">
                <select @change="handleFilterChange($event)" class="f-input">
                  <option :value="'today'">📅 {{ todayFormatted }}</option>
                  <option value="">🗓️ Hili kalendariu</option>
                </select>
              </th>
              <th class="th">
                <input v-model="filter.nomor" type="text" placeholder="Numeru" class="f-input" />
              </th>
              <th class="th">
                <input v-model="filter.supplier" type="text" placeholder="Fornesedór" class="f-input" />
              </th>
              <th class="th">
                <select v-model="filter.tipe" class="f-input">
                  <option value="">Kompletu</option>
                  <option value="tunai">Cash</option>
                  <option value="kredit">Kreditu</option>
                </select>
              </th>
              <th class="th">
                <select @change="handleFilterChange($event)" class="f-input">
                  <option :value="'today'">📅 {{ todayFormatted }}</option>
                  <option value="">🗓️ Hili kalendariu</option>
                </select>
              </th>
              <th class="th">
                <select v-model="filter.status" class="f-input">
                  <option value="all">Kompletu</option>
                  <option value="lunas">Lunas</option>
                  <option value="belum_lunas">Belum Lunas</option>
                </select>
              </th>
              <th class="th"></th>
              <th class="th"></th>
              <th class="th"></th>
              <th class="th"></th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="p in filteredPurchases" :key="p.id" class="hover:bg-gray-50">
              <td class="td">{{ formatDate(p.date) }}</td>
              <td class="td" :title="p.invoice_number">{{ p.invoice_number }}</td>
              <td class="td" :title="p.supplier?.name">{{ p.supplier?.name }}</td>
              <td class="td">{{ p.payment_type }}</td>
              <td class="td">{{ formatDate(p.due_date) }}</td>
              <td class="td">{{ p.status }}</td>
              <td class="td td-num">{{ formatPrice(p.subtotal) }}</td>
              <td class="td td-num">{{ formatPrice(p.discount_fixed) }}</td>
              <td class="td td-num">{{ formatPrice(p.discount_percent) }}</td>
              <td class="td td-num font-bold">{{ formatPrice(p.total) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="showDatePopup" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
        <div class="bg-white p-4 rounded shadow w-[320px]">
          <h2 class="text-sm font-semibold mb-2">
            {{ datePickerMode === 'date' ? 'Hili Data Transasaun' : 'Hili Data Vensimentu' }}
          </h2>
          <div class="mb-2">
            <label class="text-xs">Data Inísiu:</label>
            <input v-model="manualStart" type="date" class="border px-1 py-0.5 w-full rounded-sm" />
          </div>
          <div class="mb-2">
            <label class="text-xs">Data Final:</label>
            <input v-model="manualEnd" type="date" class="border px-1 py-0.5 w-full rounded-sm" />
          </div>
          <div class="flex justify-end gap-2 mt-2 text-xs">
            <button @click="showDatePopup = false" class="px-2 py-1 border rounded hover:bg-gray-100">Kansela</button>
            <button @click="applyManualDateFilter" class="px-2 py-1 border bg-blue-600 text-white rounded hover:bg-blue-700">
              Ok
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
          <button @click="refresh" class="hover:text-blue-600 hover:cursor-pointer">🔄</button>
          <button @click="addItem" class="hover:text-green-600 hover:cursor-pointer">➕</button>
          <button @click="editItem" class="hover:text-gray-600 hover:cursor-pointer">✏️</button>
          <button @click="deleteItem" class="hover:text-red-600 hover:cursor-pointer">❌</button>
        </div>
      </div>

      <!-- ✅ Modal form dipindahkan ke sini -->
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
table {
  border-collapse: collapse;
}
th, td {
  font-size: 13px;
}
</style>
