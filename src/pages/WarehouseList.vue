<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import FooterActions from '@/components/pos/FooterActions.vue'

const warehouses = ref([])
const store = ref({ logo: '', logo_base64: '', name: '' })

const filter = ref({ name: '', location: '' })
const selectedWarehouse = ref(null)
const showModal = ref(false)
const modalMode = ref('add')
const form = ref({ name: '', location: '', description: '' })

const perPage = ref(10)
const isLoading = ref(false)

const getLogoUrl = (path) => {
  if (!path) return ''
  return path.startsWith('http') ? path : `http://localhost:8000${path}`
}

const fetchStore = async () => {
  try {
    const res = await axios.get('http://localhost:8000/api/store-profile/')
    if (res.data?.length > 0) {
      store.value = res.data[0]
    }
  } catch (err) {
    console.error('❌ Error fetch store:', err)
  }
}

const fetchWarehouses = async () => {
  try {
    isLoading.value = true
    const token = localStorage.getItem('token')
    const res = await axios.get('http://localhost:8000/api/warehouses/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    warehouses.value = res.data
  } catch (err) {
    console.error('❌ Error fetch warehouses:', err)
  } finally {
    isLoading.value = false
  }
}

const filteredWarehouses = computed(() => {
  return warehouses.value.filter(w =>
    w.name.toLowerCase().includes(filter.value.name.toLowerCase()) &&
    w.location.toLowerCase().includes(filter.value.location.toLowerCase())
    )
})

const selectWarehouse = (w) => {
  selectedWarehouse.value = w
}

const openAdd = () => {
  modalMode.value = 'add'
  form.value = { name: '', location: '', description: '' }
  showModal.value = true
}

const openEdit = () => {
  if (!selectedWarehouse.value) return alert('⚠️ Hili gudang uluk')
  modalMode.value = 'edit'
  form.value = {
    name: selectedWarehouse.value.name,
    location: selectedWarehouse.value.location,
    // description: selectedWarehouse.value.description
  }
  showModal.value = true
}

const saveWarehouse = async () => {
  const token = localStorage.getItem('token')
  const headers = { Authorization: `Bearer ${token}` }

  try {
    if (modalMode.value === 'add') {
      await axios.post('http://localhost:8000/api/warehouses/', form.value, { headers })
    } else {
      await axios.put(`http://localhost:8000/api/warehouses/${selectedWarehouse.value.id}/`, form.value, { headers })
    }
    showModal.value = false
    await fetchWarehouses()
    alert('✅ Gudang rai ho susesu')
  } catch (err) {
    console.error('❌ Error save:', err)
    alert('Erru bainhira rai gudang')
  }
}

const deleteWarehouse = async () => {
  if (!selectedWarehouse.value) return alert('⚠️ Hili gudang uluk')
  const confirmDelete = confirm(`Ita hakarak hamoos gudang "${selectedWarehouse.value.name}"?`)
  if (!confirmDelete) return

  try {
    const token = localStorage.getItem('token')
    await axios.delete(`http://localhost:8000/api/warehouses/${selectedWarehouse.value.id}/`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    selectedWarehouse.value = null
    await fetchWarehouses()
    alert('❌ Gudang hamoos ho susesu')
  } catch (err) {
    console.error('❌ Error delete:', err)
  }
}

const refresh = async () => {
  await fetchWarehouses()
  alert('🔄 Dados gudang atualiza ona')
}

onMounted(async () => {
  await fetchStore()
  await fetchWarehouses()
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
      <h1 class="text-lg font-semibold">LISTA ARMAZÉN</h1>
    </div>

    <!-- Table + Filter -->
    <div class="p-2 flex flex-col flex-1 overflow-hidden">
      <div class="flex-1 overflow-x-auto border border-gray-300">
        <table class="min-w-[600px] w-full border-collapse text-sm table-fixed">
          <thead class="bg-gradient-to-b from-white to-gray-100">
            <tr>
              <th class="border px-2 py-1 text-left w-[30%]">Naran</th>
              <th class="border px-2 py-1 text-left w-[30%]">Lokasaun</th>
              <th class="border px-2 py-1 text-left">Deskrisaun</th>
            </tr>
            <tr>
              <th class="border px-2 py-1">
                <input v-model="filter.name" placeholder="Naran Armazén" class="w-full border p-1 rounded-sm" />
              </th>
              <th class="border px-2 py-1">
                <input v-model="filter.location" placeholder="Lokasaun" class="w-full border p-1 rounded-sm" />
              </th>
              <th class="border px-2 py-1">
                <input v-model="filter.description" placeholder="Deskrisaun" class="w-full border p-1 rounded-sm" />
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="w in filteredWarehouses"
              :key="w.id"
              @click="selectWarehouse(w)"
              :class="{ 'bg-yellow-100': selectedWarehouse?.id === w.id }"
              class="hover:bg-gray-50 cursor-pointer"
            >
              <td class="border px-2 py-1">{{ w.name }}</td>
              <td class="border px-2 py-1">{{ w.location }}</td>
              <td class="border px-2 py-1">{{ w.description }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Modal -->
      <div v-if="showModal" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
        <div class="bg-white p-4 rounded shadow w-full max-w-md space-y-3">
          <h2 class="text-lg font-semibold">{{ modalMode === 'add' ? '➕ Tambah Gudang' : '✏️ Edit Gudang' }}</h2>
          <input v-model="form.name" placeholder="Naran Armazén" class="w-full border p-1 rounded-sm" />
          <input v-model="form.location" placeholder="Lokasaun" class="w-full border p-1 rounded-sm" />
          <textarea v-model="form.description" placeholder="Deskrisaun" class="w-full border p-1 rounded-sm" />

          <div class="flex justify-end gap-2 pt-2">
            <button @click="showModal = false" class="px-3 py-1 border rounded hover:bg-gray-100">Kansela</button>
            <button @click="saveWarehouse" class="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">
              {{ modalMode === 'add' ? 'Rai' : 'Atualiza' }}
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
          <button @click="refresh" class="hover:text-blue-600">🔄</button>
          <button @click="openAdd" class="hover:text-green-600">➕</button>
          <button @click="openEdit" class="hover:text-gray-600">✏️</button>
          <button @click="deleteWarehouse" class="hover:text-red-600">❌</button>
        </div>
      </div>
    </div>
  </div>
  <FooterActions />
</template>

<style scoped>
tr.bg-yellow-100 {
  background-color: #fef9c3;
}
</style>
