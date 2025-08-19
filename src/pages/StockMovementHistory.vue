<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import FooterActions from '@/components/pos/FooterActions.vue'

const store = ref({
  name: '',
  address: '',
  logo: '',
  logo_base64: '',
  version: '',
  location: ''
})

const selectedMovement = ref(null)

const showModal = ref(false)
const modalMode = ref('add')

const movementForm = ref({
  product: '',
  warehouse: '',
  quantity: '',
  movement_type: 'in',
  note: ''
})

const openAdd = () => {
  modalMode.value = 'add'
  movementForm.value = {
    product: '',
    warehouse: '',
    quantity: '',
    movement_type: 'in',
    note: ''
  }
  showModal.value = true
}

const openEdit = () => {
  if (!selectedMovement.value) {
    alert('⚠️ Favor seleziona movimentu dulu')
    return
  }
  modalMode.value = 'edit'
  movementForm.value = { ...selectedMovement.value }
  showModal.value = true
}

const deleteMovement = async () => {
  if (!selectedMovement.value) {
    alert('⚠️ Favor seleziona movimentu dulu')
    return
  }
  if (!confirm('Apaga movimentu nebee seleziona?')) return

  try {
    await axios.delete(`http://localhost:8000/api/stock-movements/${selectedMovement.value.id}/`)
    await fetchMovements()
    selectedMovement.value = null
    alert('✅ Movimentu apaga ho susesu')
  } catch (err) {
    console.error(err)
    alert('❌ Gagal apaga movimentu')
  }
}

const saveMovement = async () => {
  try {
    if (modalMode.value === 'add') {
      await axios.post('http://localhost:8000/api/stock-movements/', movementForm.value)
    } else {
      await axios.put(`http://localhost:8000/api/stock-movements/${selectedMovement.value.id}/`, movementForm.value)
    }
    await fetchMovements()
    showModal.value = false
    selectedMovement.value = null
    alert('✅ Movimentu rai ho susesu')
  } catch (err) {
    console.error(err)
    alert('❌ Gagal rai movimentu')
  }
}

const movementList = ref([])
const filter = ref({ product: '', warehouse: '', type: '' })
const isLoading = ref(false)
const perPage = ref(10)

const getLogoUrl = (path) => {
  if (!path) return ''
  return path.startsWith('http') ? path : `http://localhost:8000${path}`
}

const fetchStoreProfile = async () => {
  const res = await axios.get('http://localhost:8000/api/store-profile/')
  if (res.data.length > 0) store.value = res.data[0]
}

const fetchMovements = async () => {
  const res = await axios.get('http://localhost:8000/api/stock-movements/')
  movementList.value = res.data
}

const refresh = async () => {
  await fetchMovements()
  alert('🔄 Dadus movimentu atualiza ona')
}

onMounted(async () => {
  isLoading.value = true
  await fetchStoreProfile()
  await fetchMovements()
  isLoading.value = false
})

const filteredMovements = computed(() => {
  return movementList.value.filter(m =>
    m.product_name?.toLowerCase().includes(filter.value.product.toLowerCase()) &&
    m.warehouse_name?.toLowerCase().includes(filter.value.warehouse.toLowerCase()) &&
    m.movement_type?.toLowerCase().includes(filter.value.type.toLowerCase())
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
      <h1 class="text-lg font-semibold">MOVIMENTU STOK</h1>
    </div>

    <!-- Table + Filter -->
    <div class="p-2 flex-1 overflow-hidden flex flex-col">
      <div class="flex-1 overflow-x-auto border border-gray-300">
        <table class="min-w-[700px] w-full table-fixed border-collapse">
          <thead class="bg-gradient-to-b from-white to-gray-100">
            <tr>
              <th class="border px-2 py-1 text-left w-[25%]">Data</th>
              <th class="border px-2 py-1 text-left w-[20%]">Produtu</th>
              <th class="border px-2 py-1 text-left w-[20%]">Armazén</th>
              <th class="border px-2 py-1 text-left w-[15%]">Tipu</th>
              <th class="border px-2 py-1 text-left">Kuantidade</th>
            </tr>
            <tr>
              <th class="border px-2 py-1"></th>
              <th class="border px-2 py-1">
                <input v-model="filter.product" type="text" class="w-full border rounded-sm px-1 py-0.5" placeholder="Filtru produtu" />
              </th>
              <th class="border px-2 py-1">
                <input v-model="filter.warehouse" type="text" class="w-full border rounded-sm px-1 py-0.5" placeholder="Filtru armazén" />
              </th>
              <th class="border px-2 py-1">
                <input v-model="filter.type" type="text" class="w-full border rounded-sm px-1 py-0.5" placeholder="Filtru tipu" />
              </th>
              <th class="border px-2 py-1"></th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(m, idx) in filteredMovements"
                :key="idx"
                :class="[
                  'hover:bg-gray-50 cursor-pointer',
                  selectedMovement?.id === m.id ? 'bg-blue-100' : ''
                ]"
                @click="selectedMovement = m"
              >
              <td class="border px-2 py-1">{{ new Date(m.created_at).toLocaleString() }}</td>
              <td class="border px-2 py-1">{{ m.product_name }}</td>
              <td class="border px-2 py-1">{{ m.warehouse_name }}</td>
              <td class="border px-2 py-1">
              <span :class="m.movement_type === 'in' ? 'text-green-600 font-semibold' : 'text-red-600 font-semibold'">
                {{ m.movement_type === 'in' ? 'Stock In' : 'Stock Out' }}
                </span>
              </td>
              <td class="border px-2 py-1">{{ m.quantity }}</td>
            </tr>
          </tbody>
        </table>
      </div>


      <div v-if="showModal" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40 z-50">
  <div class="bg-white p-4 rounded shadow-md w-[400px]">
    <h2 class="text-lg font-semibold mb-2">
      {{ modalMode === 'add' ? '➕ Tambah Movimentu' : '✏️ Edit Movimentu' }}
    </h2>

    <div class="mb-2">
      <label class="block text-sm mb-1">Product *</label>
      <input v-model="movementForm.product" type="number" class="border w-full px-2 py-1 rounded-sm" />
    </div>

    <div class="mb-2">
      <label class="block text-sm mb-1">Warehouse *</label>
      <input v-model="movementForm.warehouse" type="number" class="border w-full px-2 py-1 rounded-sm" />
    </div>

    <div class="mb-2">
      <label class="block text-sm mb-1">Quantity *</label>
      <input v-model="movementForm.quantity" type="number" class="border w-full px-2 py-1 rounded-sm" />
    </div>

      <div class="mb-2">
        <label class="block text-sm mb-1">Movement Type *</label>
        <select v-model="movementForm.movement_type" class="border w-full px-2 py-1 rounded-sm">
          <option value="in">Stock In</option>
          <option value="out">Stock Out</option>
        </select>
      </div>

        <div class="mb-2">
          <label class="block text-sm mb-1">Note</label>
          <input v-model="movementForm.note" type="text" class="border w-full px-2 py-1 rounded-sm" />
        </div>

        <div class="mt-3 flex justify-end gap-2">
          <button @click="showModal = false" class="px-3 py-1 border rounded hover:bg-gray-100">❌ Kansela</button>
          <button @click="saveMovement" class="px-3 py-1 bg-blue-600 text-white rounded">💾 Rai</button>
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
          <button @click="openAdd" class="hover:text-green-600">➕</button>
          <button @click="openEdit" class="hover:text-gray-600">✏️</button>
          <button @click="deleteMovement" class="hover:text-red-600">❌</button>
        </div>
      </div>
    </div>
  </div>
  <FooterActions />
</template>

