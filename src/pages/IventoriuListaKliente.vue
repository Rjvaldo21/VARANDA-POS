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

const customers = ref([])
const filter = ref({
  nomor: '',
  nama: '',
  telepon: '',
  email: ''
})
const perPage = ref(10)
const selectedCustomer = ref(null)

const showModal = ref(false)

const customerForm = ref({
  name: '',
  phone: '',
  email: '',
  address: '',
  points: 0
})

const formattedAddress = computed(() =>
  store.value.address ? store.value.address.replace(/\n/g, '<br />') : ''
)

const getLogoUrl = (path) => {
  if (!path) return ''
  return path.startsWith('http') ? path : `http://localhost:8000${path}`
}

const fetchCustomers = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('http://127.0.0.1:8000/api/customers/', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })

    customers.value = response.data.map((item, index) => ({
      id: item.id,
      nomor: item.id.toString().padStart(3, '0'),
      nama: item.name,
      telepon: item.phone || '',
      email: item.email || '',
      alamat: item.address || '',
      poin: item.points || 0,
      piutang: 0 
    }))
  } catch (error) {
    console.error('Gagal mengambil data pelanggan:', error)
  }
}

const saveCustomer = async () => {
  const token = localStorage.getItem('token')

  if (!customerForm.value.name || customerForm.value.points === null) {
    alert('❗ Mohon isi field wajib: Name dan Points')
    return
  }

  const isEdit = !!customerForm.value.id
  const url = isEdit
    ? `http://127.0.0.1:8000/api/customers/${customerForm.value.id}/`
    : 'http://127.0.0.1:8000/api/customers/'
  const method = isEdit ? 'put' : 'post'

  try {
    const res = await axios({
      method,
      url,
      data: customerForm.value,
      headers: { Authorization: `Bearer ${token}` }
    })

    console.log(isEdit ? '✅ Kliente diubah:' : '✅ Kliente disimpan:', res.data)
    showModal.value = false
    selectedCustomer.value = null
    refresh()
  } catch (err) {
    console.error('❌ Gagal simpan/ubah kliente:', err)
    alert('Terjadi kesalahan saat menyimpan kliente.')
  }
}

const addItem = () => {
  customerForm.value = {
    name: '',
    phone: '',
    email: '',
    address: '',
    points: 0
  }
  showModal.value = true
}


const editItem = (customer) => {
  if (!customer) return
  customerForm.value = {
    id: customer.id,
    name: customer.nama,
    phone: customer.telepon,
    email: customer.email,
    address: customer.alamat,
    points: customer.poin
  }
  showModal.value = true
}


const deleteItem = async (customer) => {
  if (!customer) return
  const confirmDelete = confirm(`Hapus kliente ${customer.nama}?`)
  if (!confirmDelete) return

  try {
    const token = localStorage.getItem('token')
    await axios.delete(`http://127.0.0.1:8000/api/customers/${customer.id}/`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    alert('✅ Kliente berhasil dihapus.')
    selectedCustomer.value = null
    refresh()
  } catch (err) {
    console.error('❌ Gagal hapus kliente:', err)
    alert('Terjadi kesalahan saat menghapus kliente.')
  }
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

  await fetchCustomers()
})

const filteredCustomers = computed(() => {
  return customers.value.filter(c =>
    c.nomor.toLowerCase().includes(filter.value.nomor.toLowerCase()) &&
    c.nama.toLowerCase().includes(filter.value.nama.toLowerCase()) &&
    (c.telepon || '').toLowerCase().includes(filter.value.telepon.toLowerCase()) &&
    (c.email || '').toLowerCase().includes(filter.value.email.toLowerCase())
  )
})

const formatPrice = val => Number(val || 0).toLocaleString('id-ID')

const refresh = () => fetchCustomers()

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
      <h1 class="text-lg font-semibold">KLIENTE</h1>
    </div>

    <!-- Modal Tambah Kliente -->
      <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white p-4 rounded shadow w-[400px]">
          <h2 class="text-lg font-semibold mb-2">➕ Kliente Foun</h2>

          <div class="space-y-2">
            <div>
              <label class="block text-sm">Name *</label>
              <input v-model="customerForm.name" type="text" class="w-full border px-2 py-1 rounded" />
            </div>
            <div>
              <label class="block text-sm">Phone</label>
              <input v-model="customerForm.phone" type="text" class="w-full border px-2 py-1 rounded" />
            </div>
            <div>
              <label class="block text-sm">Email</label>
              <input v-model="customerForm.email" type="email" class="w-full border px-2 py-1 rounded" />
            </div>
            <div>
              <label class="block text-sm">Address</label>
              <textarea v-model="customerForm.address" class="w-full border px-2 py-1 rounded"></textarea>
            </div>
            <div>
              <label class="block text-sm">Points *</label>
              <input v-model="customerForm.points" type="number" min="0" class="w-full border px-2 py-1 rounded" />
            </div>
          </div>

          <div class="flex justify-end gap-2 mt-4">
            <button @click="showModal = false" class="px-3 py-1 border rounded hover:bg-gray-100">❌ Kansela</button>
            <button @click="saveCustomer" class="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">💾 Submete</button>
          </div>
        </div>
      </div>

    <!-- Table + Filter -->
    <div class="p-2 flex flex-col flex-1 overflow-hidden">
      <div class="flex-1 overflow-x-auto border border-gray-300 rounded-sm scrollbar-stable">
        <table class="w-full min-w-[1000px] xl:min-w-0 border-collapse text-sm table-fixed">
          <colgroup>
            <col style="width:12%" /> 
            <col style="width:20%" /> 
            <col style="width:15%" /> 
            <col style="width:20%" /> 
            <col style="width:19%" /> 
            <col style="width:7%; min-width:90px" /> 
            <col style="width:7%; min-width:90px" />
          </colgroup>

          <thead class="bg-gradient-to-b from-white to-gray-100">
            <tr>
              <th class="th text-left">Numeru</th>
              <th class="th text-left">Naran</th>
              <th class="th text-left">Telemovel</th>
              <th class="th text-left">Email</th>
              <th class="th text-left">Enderesu</th>
              <th class="th text-right">Pontus</th>
              <th class="th text-right">Piutang</th>
            </tr>

            <tr>
              <th class="th">
                <input v-model="filter.nomor"   type="text" placeholder="Numeru"   class="f-input" />
              </th>
              <th class="th">
                <input v-model="filter.nama"    type="text" placeholder="Naran"    class="f-input" />
              </th>
              <th class="th">
                <input v-model="filter.telepon" type="text" placeholder="Telemovel" class="f-input" />
              </th>
              <th class="th">
                <input v-model="filter.email"   type="text" placeholder="Email"    class="f-input" />
              </th>
              <th class="th"></th>
              <th class="th"></th>
              <th class="th"></th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="item in filteredCustomers"
              :key="item.nomor"
              class="hover:bg-gray-50 cursor-pointer"
              :class="{ 'bg-blue-50': selectedCustomer?.nomor === item.nomor }"
              @click="selectedCustomer = item"
            >
              <td class="td"      :title="item.nomor">{{ item.nomor || '-' }}</td>
              <td class="td"      :title="item.nama">{{ item.nama || '-' }}</td>
              <td class="td"      :title="item.telepon">{{ item.telepon || '-' }}</td>
              <td class="td"      :title="item.email">{{ item.email || '-' }}</td>
              <td class="td"      :title="item.alamat">{{ item.alamat || '-' }}</td>
              <td class="td td-num">{{ item.poin ?? 0 }}</td>
              <td class="td td-num">{{ formatPrice(item.piutang ?? 0) }}</td>
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
        <!-- Action Buttons -->
        <div class="space-x-2 text-base">
          <button @click="refresh" class="hover:text-blue-600">🔄</button>
          <button @click="addItem" class="hover:text-green-600">➕</button>
          <button
            @click="editItem(selectedCustomer)"
            :disabled="!selectedCustomer"
            class="hover:text-gray-600"
          >
            ✏️
          </button>
          <button
            @click="deleteItem(selectedCustomer)"
            :disabled="!selectedCustomer"
            class="hover:text-red-600"
          >
            ❌
          </button>
        </div>
      </div>
    </div>
  </div>
  <FooterActions />
</template>

<style scoped>

table { border-collapse: collapse; table-layout: fixed; }

.th, .td {
  font-size: 13px;
  white-space: nowrap;      
  overflow: hidden;         
  text-overflow: ellipsis;  
  vertical-align: middle;
  padding: 0.25rem 0.5rem; 
  border: 1px solid #e5e7eb;
}

.td-num { text-align: right; font-variant-numeric: tabular-nums; }

.f-input {
  width: 100%;
  padding: 0.25rem 0.375rem;
  border: 1px solid #d1d5db;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  line-height: 1.25rem;
  background: #fff;
}
</style>
