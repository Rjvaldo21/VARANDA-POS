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

const kategoriList = ref([])
const perPage = ref(10)

const formattedAddress = computed(() =>
  store.value.address ? store.value.address.replace(/\n/g, '<br />') : ''
)

const getLogoUrl = (path) => {
  if (!path) return ''
  return path.startsWith('http') ? path : `http://localhost:8000${path}`
}

onMounted(async () => {
  try {
    const res = await axios.get('http://localhost:8000/api/store-profile/')
    if (res.data && res.data.length > 0) {
      store.value = res.data[0]
    }
  } catch (err) {
    console.error('Gagal fetch store profile:', err)
  }

  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('http://localhost:8000/api/categories/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    kategoriList.value = response.data
  } catch (error) {
    console.error('Gagal fetch kategori:', error)
  }
})


const showModal = ref(false)
const kategoriForm = ref({ name: '', code: '' })


const saveKategori = async () => {
  if (!kategoriForm.value.name || !kategoriForm.value.code) {
    alert('⚠️ Naran kategori dan kode wajib diisi')
    return
  }

  try {
    const token = localStorage.getItem('token')
    await axios.post('http://localhost:8000/api/categories/', kategoriForm.value, {
      headers: { Authorization: `Bearer ${token}` }
      }).then(res => {
  console.log('✅ Respon:', res.data)
    })
    showModal.value = false
    await refresh()
    alert('✅ Kategoria rai ho susesu')
  } catch (err) {
    console.error('❌ Gagal rai kategoria:', err)
    alert('Gagal rai kategoria')
  }
}

const refresh = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('http://localhost:8000/api/categories/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    kategoriList.value = response.data
  } catch (error) {
    console.error('Gagal fetch kategori:', error)
  }
}

const selectedKategori = ref(null)

const addKategori = () => {
  kategoriForm.value = { name: '', id: '' }
  selectedKategori.value = null
  showModal.value = true
}

const editKategori = (item) => {
  kategoriForm.value = { name: item.name, code: item.code }
  selectedKategori.value = item
  showModal.value = true
}

const deleteKategori = async (item) => {
  const konfirmasi = confirm(`Hapus kategoria: ${item.name}?`)
  if (!konfirmasi) return

  try {
    const token = localStorage.getItem('token')
    await axios.delete(`http://localhost:8000/api/categories/${item.id}/`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    await refresh()
    alert('🗑️ Kategoria apaga ho susesu')
  } catch (err) {
    console.error('❌ Gagal apaga kategoria:', err)
    alert('Erro ao apaga kategoria')
  }
}

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
      <h1 class="text-lg font-semibold">KATEGORIA</h1>
    </div>

    <!-- Table -->
    <div class="p-2 flex flex-col flex-1 overflow-hidden">
      <div class="flex-1 overflow-x-auto border border-gray-300">
        <table class="min-w-[400px] w-full border-collapse text-sm table-fixed">
          <thead class="bg-gradient-to-b from-white to-gray-100">
            <tr>
              <th class="border border-gray-300 px-2 py-1 text-left w-[50%]">Naran</th>
              <th class="border border-gray-300 px-2 py-1 text-left">Kode</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in kategoriList"
              :key="item.id"
              :class="[
                'cursor-pointer',
                'hover:bg-gray-50',
                selectedKategori && selectedKategori.id === item.id ? 'bg-blue-50' : ''
              ]"
              @click="selectedKategori = item"
            >
              <td class="border border-gray-300 px-2 py-1">{{ item.name }}</td>
              <td class="border border-gray-300 px-2 py-1">{{ item.code }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Modal Tambah/Edit Kategoria -->
      <div v-if="showModal" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
        <div class="bg-white p-4 rounded shadow w-full max-w-md space-y-3">
          <h2 class="text-lg font-semibold">{{ selectedKategori ? '✏️ Edit Kategoria' : '➕ Tambah Kategoria' }}</h2>
          <input v-model="kategoriForm.name" placeholder="Naran Kategoria" class="w-full border p-1 rounded-sm" />
          <input v-model="kategoriForm.code" placeholder="Kode" class="w-full border p-1 rounded-sm" />

          <div class="flex justify-end gap-2 pt-2">
            <button @click="showModal = false" class="px-3 py-1 border rounded hover:bg-gray-100">Kansela</button>
            <button @click="saveKategori" class="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700">
              {{ selectedKategori ? 'Atualiza' : 'Rai' }}
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
          <button @click="addKategori" class="hover:text-green-600">➕</button>
          <button @click="selectedKategori ? editKategori(selectedKategori) : alert('⚠️ Hili kategoria dulu')" class="hover:text-gray-600">✏️</button>
          <button @click="selectedKategori ? deleteKategori(selectedKategori) : alert('⚠️ Hili kategoria dulu')" class="hover:text-red-600">❌</button>
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
