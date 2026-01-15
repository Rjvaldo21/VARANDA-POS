<script setup>
import { ref, computed, onMounted } from 'vue'
import FooterActions from '@/components/pos/FooterActions.vue'
import axios from 'axios'

const store = ref({
  name: '',
  address: '',
  logo: '',
  version: '',
  location: ''
})

const units = ref([])
const filter = ref({ nama: '' })
const perPage = ref(10)

const showModal = ref(false)
const selectedUnit = ref(null)

const unitForm = ref({
  name: ''
})

const addItem = () => {
  selectedUnit.value = null
  unitForm.value = { name: '' }
  showModal.value = true
}

const editItem = () => {
  if (!selectedUnit.value) return
  unitForm.value = { name: selectedUnit.value.name }
  showModal.value = true
}

const deleteItem = async () => {
  if (!selectedUnit.value) return
  const confirmDelete = confirm(`Hamoos unidade "${selectedUnit.value.name}"?`)
  if (!confirmDelete) return

  try {
    const token = localStorage.getItem('token')
    await axios.delete(`http://localhost:8000/api/units/${selectedUnit.value.id}/`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    selectedUnit.value = null
    refresh()
  } catch (err) {
    console.error('❌ Falha Hamoos unidade:', err)
    alert('Falha Hamoos unidade.')
  }
}

const formattedAddress = computed(() =>
  store.value.address ? store.value.address.replace(/\n/g, '<br />') : ''
)

const getLogoUrl = (path) => {
  if (!path) return ''
  return path.startsWith('http') ? path : `http://localhost:8000${path}`
}

const filteredUnits = computed(() =>
  units.value.filter(u =>
    (u.name || '').toLowerCase().includes(filter.value.nama.toLowerCase())
  )
)

const fetchUnits = async () => {
  const token = localStorage.getItem('token')
  try {
    const res = await axios.get('http://localhost:8000/api/units/', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    units.value = res.data
  } catch (error) {
    console.error('❌ Falha fetch unidade:', error)
    alert('La konsege hetan fali dadus unidade. Favor verifika ita-boot nia ligasaun ka login fali.')
  }
}

const saveUnit = async () => {
  const token = localStorage.getItem('token')
  if (!unitForm.value.name) {
    alert('❗ Naran kampu obrigatoriu..')
    return
  }

  const isEdit = !!selectedUnit.value
  const url = isEdit
    ? `http://localhost:8000/api/units/${selectedUnit.value.id}/`
    : 'http://localhost:8000/api/units/'
  const method = isEdit ? 'put' : 'post'

  try {
    await axios({
      method,
      url,
      data: unitForm.value,
      headers: { Authorization: `Bearer ${token}` }
    })
    showModal.value = false
    selectedUnit.value = null
    refresh()
  } catch (err) {
    console.error('❌ Falha salva unidade:', err)
    alert('Erru ida akontese bainhira salva unidade.')
  }
}


onMounted(async () => {
  try {
    const res = await axios.get('http://localhost:8000/api/store-profile/')
    if (res.data && res.data.length > 0) {
      store.value = res.data[0]
    }
  } catch (err) {
    console.error('Falha fetch perfil loja:', err)
  }

  await fetchUnits()
})

const refresh = fetchUnits
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
      <h1 class="text-lg font-semibold">UNIDADE</h1>
    </div>

    <!-- Table + Filter -->
    <div class="p-2 flex flex-col flex-1 overflow-hidden pb-2">
      <div class="flex-1 overflow-x-auto border border-gray-300">
        <table class="min-w-[400px] w-full border-collapse text-sm table-fixed">
          <thead class="bg-gradient-to-b from-white to-gray-100">
            <!-- Filter Row -->
            <tr>
              <th class="border border-gray-300 px-2 py-1 w-full">
                <input
                  v-model="filter.nama"
                  type="text"
                  placeholder="Buka Unidade..."
                  class="w-full border px-2 py-1 rounded-sm"
                />
                </th>
              </tr>
            </thead>
          <tbody>
            <tr
              v-for="item in filteredUnits"
              :key="item.id"
              :class="{ 'bg-blue-50': selectedUnit?.id === item.id }"
              class="hover:bg-gray-50 cursor-pointer"
              @click="selectedUnit = item"
            >
              <td class="border px-2 py-1">{{ item.name }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Footer -->
      <div class="flex justify-between items-center mt-2 text-xs">
        <!-- Pagination -->
        <div>
          <select v-model="perPage" class="border px-1 py-0.5 rounded-sm">
            <option v-for="n in [10, 20, 50]" :key="n" :value="n">{{ n }}/pagina</option>
          </select>
        </div>

        <!-- Modal Tambah/Edit Unit -->
        <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div class="bg-white p-4 rounded shadow w-[400px]">
            <h2 class="text-lg font-semibold mb-2">
              {{ selectedUnit ? '✏️ Edit Unidade' : '➕ Unidade Foun' }}
            </h2>
            <div>
              <label class="block text-sm mb-1">Name *</label>
              <input v-model="unitForm.name" type="text" class="w-full border px-2 py-1 rounded" />
            </div>
            <div class="flex justify-end gap-2 mt-4">
              <button @click="showModal = false" class="px-3 py-1 border rounded hover:bg-gray-100">❌ Kansela</button>
              <button @click="saveUnit" class="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">💾 Submete</button>
            </div>
          </div>
        </div>
        
        <!-- Action Buttons -->
        <div class="space-x-2 text-base">
          <button @click="refresh" class="hover:text-blue-600">🔄</button>
          <button @click="addItem" class="hover:text-green-600">➕</button>
          <button @click="editItem" class="hover:text-gray-600">✏️</button>
          <button @click="deleteItem" class="hover:text-red-600">❌</button>
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