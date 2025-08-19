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

const suppliers = ref([])
const filter = ref({ name: '', kode: '', phone: '', email: '' })
const perPage = ref(10)

const showModal = ref(false)
const selectedSupplier = ref(null)
const supplierForm = ref({
  name: '',
  phone: '',
  email: '',
  address: ''
})

const addSupplier = () => {
  selectedSupplier.value = null
  supplierForm.value = { name: '', phone: '', email: '', address: '' }
  showModal.value = true
}

const editSupplier = () => {
  if (!selectedSupplier.value) {
    alert('⚠️ Hili fornesédor dulu')
    return
  }
  supplierForm.value = { ...selectedSupplier.value }
  showModal.value = true
}

const deleteSupplier = async () => {
  if (!selectedSupplier.value) {
    alert('⚠️ Hili fornesédor dulu')
    return
  }
  const konfirmasi = confirm(`Apaga fornesédor: ${selectedSupplier.value.name}?`)
  if (!konfirmasi) return

  try {
    const token = localStorage.getItem('token')
    await axios.delete(`http://localhost:8000/api/suppliers/${selectedSupplier.value.id}/`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    await refresh()
    selectedSupplier.value = null
    alert('🗑️ Fornesédor apaga ho susesu')
  } catch (error) {
    console.error('Gagal apaga:', error)
    alert('Erro ao apaga fornesédor')
  }
}

const saveSupplier = async () => {
  if (!supplierForm.value.name) {
    alert('⚠️ Naran fornesédor wajib')
    return
  }

  const token = localStorage.getItem('token')
  try {
    if (selectedSupplier.value) {
      // Edit
      await axios.put(`http://localhost:8000/api/suppliers/${selectedSupplier.value.id}/`, supplierForm.value, {
        headers: { Authorization: `Bearer ${token}` }
      })
    } else {
      // Tambah
      await axios.post('http://localhost:8000/api/suppliers/', supplierForm.value, {
        headers: { Authorization: `Bearer ${token}` }
      })
    }

    await refresh()
    showModal.value = false
    selectedSupplier.value = null
    alert('✅ Rai fornesédor ho susesu')
  } catch (error) {
    console.error('Gagal simpan:', error)
    alert('Erro ao rai fornesédor')
  }
}


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
    const response = await axios.get('http://localhost:8000/api/suppliers/', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })

    // Tambahkan kode dummy jika tidak tersedia
    suppliers.value = response.data.map((s, index) => ({
      ...s,
      kode: s.kode || `SUP-${index + 1}`
    }))
  } catch (error) {
    console.error('Gagal fetch suppliers:', error)
  }
})

const filteredSuppliers = computed(() => {
  return suppliers.value.filter(s =>
    s.name?.toLowerCase().includes(filter.value.name.toLowerCase()) &&
    s.kode?.toLowerCase().includes(filter.value.kode.toLowerCase()) &&
    (s.phone || '').toLowerCase().includes(filter.value.phone.toLowerCase()) &&
    (s.email || '').toLowerCase().includes(filter.value.email.toLowerCase())
  )
})

const refresh = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('http://localhost:8000/api/suppliers/', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    suppliers.value = response.data.map((s, index) => ({
      ...s,
      kode: s.kode || `SUP-${index + 1}`
    }))
    selectedSupplier.value = null
  } catch (error) {
    console.error('Gagal refresh suppliers:', error)
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
      <h1 class="text-lg font-semibold">FORNESEDÓR</h1>
    </div>

    <!-- Table + Filter -->
    <div class="p-2 flex flex-col flex-1 overflow-hidden">
      <div class="flex-1 overflow-x-auto border border-gray-300">
        <table class="min-w-[800px] w-full border-collapse text-sm table-fixed">
          <thead class="bg-gradient-to-b from-white to-gray-100">
            <tr>
              <th class="border border-gray-300 px-2 py-1 text-left w-[25%]">Naran</th>
              <th class="border border-gray-300 px-2 py-1 text-left w-[10%]">Kodigu</th>
              <th class="border border-gray-300 px-2 py-1 text-left w-[25%]">Telemovel</th>
              <th class="border border-gray-300 px-2 py-1 text-left w-[25%]">Email</th>
              <th class="border border-gray-300 px-2 py-1 text-left">Enderesu</th>
            </tr>
            <!-- Filter Inputs -->
            <tr>
              <th class="border border-gray-300 px-2 py-1">
                <input v-model="filter.name" type="text" placeholder="Nama" class="w-full border border-gray-300 px-2 py-1 rounded-sm" />
              </th>
              <th class="border border-gray-300 px-2 py-1">
                <input v-model="filter.kode" type="text" placeholder="Kode" class="w-full border border-gray-300 px-2 py-1 rounded-sm" />
              </th>
              <th class="border border-gray-300 px-2 py-1">
                <input v-model="filter.phone" type="text" placeholder="Telepon" class="w-full border border-gray-300 px-2 py-1 rounded-sm" />
              </th>
              <th class="border border-gray-300 px-2 py-1">
                <input v-model="filter.email" type="text" placeholder="Email" class="w-full border border-gray-300 px-2 py-1 rounded-sm" />
              </th>
              <th class="border border-gray-300 px-2 py-1"></th>
            </tr>
          </thead>
          <tbody>
            <tr
                v-for="supplier in filteredSuppliers"
                :key="supplier.id"
                :class="[
                  'cursor-pointer',
                  selectedSupplier?.id === supplier.id ? 'bg-blue-50' : 'hover:bg-gray-50'
                ]"
                @click="selectedSupplier = supplier"
              >
              <td class="border border-gray-300 px-2 py-1">{{ supplier.name }}</td>
              <td class="border border-gray-300 px-2 py-1">{{ supplier.kode }}</td>
              <td class="border border-gray-300 px-2 py-1">{{ supplier.phone }}</td>
              <td class="border border-gray-300 px-2 py-1">{{ supplier.email }}</td>
              <td class="border border-gray-300 px-2 py-1">{{ supplier.address }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Footer -->
      <div class="flex justify-between items-center mt-2 text-xs">
        <!-- Modal Tambah/Edit Supplier -->
        <div v-if="showModal" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center">
          <div class="bg-white p-4 rounded shadow w-full max-w-md space-y-3">
            <h2 class="text-lg font-semibold">{{ selectedSupplier ? '✏️ Edit Fornesédor' : '➕ Tambah Fornesédor' }}</h2>
            <input v-model="supplierForm.name" placeholder="Naran" class="w-full border p-1 rounded-sm" />
            <input v-model="supplierForm.phone" placeholder="Telemovel" class="w-full border p-1 rounded-sm" />
            <input v-model="supplierForm.email" placeholder="Email" class="w-full border p-1 rounded-sm" />
            <textarea v-model="supplierForm.address" placeholder="Enderesu" class="w-full border p-1 rounded-sm"></textarea>
            <div class="flex justify-end gap-2 pt-2">
              <button @click="showModal = false" class="px-3 py-1 border rounded hover:bg-gray-100">Kansela</button>
              <button @click="saveSupplier" class="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700">
                {{ selectedSupplier ? 'Atualiza' : 'Rai' }}
              </button>
            </div>
          </div>
        </div>

        <div>
          <select v-model="perPage" class="border px-1 py-0.5 rounded-sm">
            <option v-for="n in [10, 20, 50]" :key="n" :value="n">{{ n }}/pagina</option>
          </select>
        </div>
        <div class="space-x-2 text-base">
          <button @click="refresh" class="hover:text-blue-600">🔄</button>
          <button @click="addSupplier" class="hover:text-green-600">➕</button>
          <button @click="editSupplier" class="hover:text-gray-600">✏️</button>
          <button @click="deleteSupplier" class="hover:text-red-600">❌</button>
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