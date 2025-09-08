<script setup>
import { ref, computed, onMounted } from 'vue'
import FooterActions from '@/components/pos/FooterActions.vue'
import api from '@/axios'

const store = ref({
  name: '',
  address: '',
  logo: '',
  logo_base64: '',
  version: '',
  location: ''
})

const transferList = ref([])
const warehouses = ref([])
const products = ref([])

const filter = ref({
  from: '',
  to: '',
  product: ''
})

const perPage = ref(10)
const isLoading = ref(false)

const showTransferModal = ref(false)
const modalMode = ref('add')

const transferForm = ref({
  from_warehouse: '',
  to_warehouse: '',
  product: '',
  quantity: ''
})

const getLogoUrl = (path) => {
  if (!path) return ''
  return path.startsWith('http') ? path : `http://localhost:8000${path}`
}

const fetchStoreProfile = async () => {
  const res = await api.get('store-profile/')
  if (res.data.length > 0) store.value = res.data[0]
}

const fetchWarehouses = async () => {
  const res = await api.get('warehouses/')
  warehouses.value = res.data
}

const fetchProducts = async () => {
  const res = await api.get('products/')
  products.value = res.data
}

const fetchTransfers = async () => {
  const res = await api.get('stock-transfers/')
  console.log('📦 Transfers:', res.data)
  transferList.value = res.data
}

const refresh = async () => {
  await fetchTransfers()
  alert('🔄 Dadus perpindahan atualiza ona')
}

const openAddModal = () => {
  modalMode.value = 'add'
  transferForm.value = { from_warehouse: '', to_warehouse: '', product: '', quantity: '' }
  showTransferModal.value = true
}

const saveTransfer = async () => {
  if (!transferForm.value.from_warehouse || !transferForm.value.to_warehouse || !transferForm.value.product || !transferForm.value.quantity) {
    alert('⚠️ Favor kompletadu formu transferénsia')
    return
  }

  try {
    await api.post('stock-transfers/', transferForm.value)
    showTransferModal.value = false
    await fetchTransfers()
    alert('✅ Perpindahan rai ho susesu')
  } catch (err) {
    console.error('❌ Erro salva:', err)
    alert('Erro salva transferénsia')
  }
}

onMounted(async () => {
  isLoading.value = true
  await fetchStoreProfile()
  await fetchWarehouses()
  await fetchProducts()
  await fetchTransfers()
  isLoading.value = false
})

const filteredTransfers = computed(() => {
  return transferList.value.filter(t =>
    t.from_warehouse_name?.toLowerCase().includes(filter.value.from.toLowerCase()) &&
    t.to_warehouse_name?.toLowerCase().includes(filter.value.to.toLowerCase()) &&
    t.product_name?.toLowerCase().includes(filter.value.product.toLowerCase())
  )
})

</script>


<template>
  <div class="bg-white border border-gray-100 rounded-sm shadow text-sm flex flex-col h-full">
    <!-- Header -->
    <div class="flex items-center gap-2 p-2 border-b border-gray-300 bg-gray-50">
      <img
        :src="store.logo_base64 || getLogoUrl(store.logo)"
        @error="e => e.target.src = 'http://127.0.0.1:8000/media/logos/default.jpg'"
        class="h-6 w-6 rounded"
      />
      <h1 class="text-lg font-semibold">TRANSFERÉNSIA STOK</h1>
    </div>

    <!-- Main Content -->
    <div class="p-2 flex-1 overflow-hidden flex flex-col">
      <!-- Table -->
      <div class="flex-1 overflow-x-auto border border-gray-300">
        <table class="min-w-[700px] w-full table-fixed border-collapse">
          <thead class="bg-gradient-to-b from-white to-gray-100">
            <tr>
              <th class="border px-2 py-1 text-left w-[18%]">Husi Armazén</th>
              <th class="border px-2 py-1 text-left w-[18%]">Ba Armazén</th>
              <th class="border px-2 py-1 text-left w-[32%]">Produtu</th>
              <th class="border px-2 py-1 text-left">Kuantidade</th>
              <th class="border px-2 py-1 text-left">Deskrisaun</th>
            </tr>
            <tr>
              <th class="border px-2 py-1">
                <input v-model="filter.from" type="text" class="w-full border rounded-sm px-1 py-0.5" placeholder="Filtru husi" />
              </th>
              <th class="border px-2 py-1">
                <input v-model="filter.to" type="text" class="w-full border rounded-sm px-1 py-0.5" placeholder="Filtru ba" />
              </th>
              <th class="border px-2 py-1">
                <input v-model="filter.product" type="text" class="w-full border rounded-sm px-1 py-0.5" placeholder="Filtru produtu" />
              </th>
              <th class="border px-2 py-1"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(t, idx) in filteredTransfers" :key="idx" class="hover:bg-gray-50">
              <td class="border px-2 py-1">{{ t.from_warehouse_name }}</td>
              <td class="border px-2 py-1">{{ t.to_warehouse_name }}</td>
              <td class="border px-2 py-1">{{ t.product_name }}</td>
              <td class="border px-2 py-1">{{ t.quantity }}</td>
              <td class="border px-2 py-1">{{ t.note }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Modal -->
      <div v-if="showTransferModal" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
        <div class="bg-white p-4 rounded shadow w-full max-w-md space-y-3">
          <h2 class="text-lg font-semibold">➕ Transferénsia Stok</h2>

          <select v-model="transferForm.from_warehouse" class="w-full border p-1 rounded-sm">
            <option disabled value="">Hili Husi Armazén</option>
            <option v-for="w in warehouses" :key="w.id" :value="w.id">{{ w.name }}</option>
          </select>

          <select v-model="transferForm.to_warehouse" class="w-full border p-1 rounded-sm">
            <option disabled value="">Hili Ba Armazén</option>
            <option v-for="w in warehouses" :key="w.id" :value="w.id">{{ w.name }}</option>
          </select>

          <select v-model="transferForm.product" class="w-full border p-1 rounded-sm">
            <option disabled value="">Hili Produtu</option>
            <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>

          <input type="number" v-model="transferForm.quantity" placeholder="Kuantidade" class="w-full border p-1 rounded-sm" />

          <div class="flex justify-end gap-2">
            <button @click="showTransferModal = false" class="px-3 py-1 border rounded hover:bg-gray-100">Kansela</button>
            <button @click="saveTransfer" class="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">Submete</button>
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
          <button @click="refresh" class="hover:text-blue-600">🔄</button>
          <button @click="openAddModal" class="hover:text-green-600">➕</button>
        </div>
      </div>
    </div>
  </div>
  <FooterActions />
</template>

