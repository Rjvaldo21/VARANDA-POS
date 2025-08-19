<script setup>
import { ref, computed, onMounted } from 'vue'
import FooterActions from '@/components/pos/FooterActions.vue'
import axios from 'axios'

const store = ref({
  name: '',
  address: '',
  logo: '',
  logo_base64: '',
  version: '',
  location: ''
})

const users = ref([])
const filter = ref({ username: '', name: '', email: '' })
const perPage = ref(10)
const selectedUser = ref(null)
const isLoading = ref(true)


const showUserModal = ref(false)
const modalMode = ref('add') 
const userForm = ref({ username: '', first_name: '', last_name: '', email: '' })

const formattedAddress = computed(() =>
  store.value.address ? store.value.address.replace(/\n/g, '<br />') : ''
)

const getLogoUrl = (path) => {
  if (!path) return ''
  return path.startsWith('http') ? path : `http://localhost:8000${path}`
}

const fetchUsers = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('http://localhost:8000/api/users/', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    users.value = response.data
  } catch (error) {
    console.error('❌ Falha fetch uzuariu:', error)
  }
}

const fetchStoreProfile = async () => {
  try {
    const res = await axios.get('http://localhost:8000/api/store-profile/')
    if (res.data && res.data.length > 0) {
      store.value = res.data[0]
      console.log('Logo URL:', getLogoUrl(store.value.logo))
    }
  } catch (err) {
    console.error('❌ Falha fetch perfil loja:', err)
  }
}

onMounted(async () => {
  isLoading.value = true
  await fetchStoreProfile()
  await fetchUsers()
  isLoading.value = false
})


const filteredUsers = computed(() => {
  return users.value.filter(u =>
    u.username?.toLowerCase().includes(filter.value.username.toLowerCase()) &&
    `${u.first_name || ''} ${u.last_name || ''}`.toLowerCase().includes(filter.value.name.toLowerCase()) &&
    u.email?.toLowerCase().includes(filter.value.email.toLowerCase())
  )
})

const selectUser = (user) => {
  selectedUser.value = user
}

const refresh = async () => {
  await fetchUsers()
  alert('🔄 Dadus utilizadór nian atualiza ona')
}

const addUser = () => {
  modalMode.value = 'add'
  userForm.value = { username: '', first_name: '', last_name: '', email: '' }
  showUserModal.value = true
}

const editUser = () => {
  if (!selectedUser.value) return alert('⚠️ Hili uzuariu uluk')
  modalMode.value = 'edit'
  userForm.value = {
    username: selectedUser.value.username,
    first_name: selectedUser.value.first_name,
    last_name: selectedUser.value.last_name,
    email: selectedUser.value.email
  }
  showUserModal.value = true
}

const saveUser = async () => {
  if (!userForm.value.username || !userForm.value.first_name || !userForm.value.email) {
    alert('⚠️ Favor prenxe hotu field nebe obrigatóriu (username, naran, email)')
    return
  }

  const token = localStorage.getItem('token')
  const headers = { Authorization: `Bearer ${token}` }

  try {
    if (modalMode.value === 'add') {
      await axios.post('http://localhost:8000/api/users/', userForm.value, { headers })
    } else {
      await axios.put(`http://localhost:8000/api/users/${selectedUser.value.id}/`, userForm.value, { headers })
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
    await axios.delete(`http://localhost:8000/api/users/${selectedUser.value.id}/`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
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
    await axios.patch(`http://localhost:8000/api/users/${selectedUser.value.id}/`, {
      is_active: false
    }, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    await fetchUsers()
    alert('🔒 Uzuáriu dezativa ho susesu')
  } catch (err) {
    console.error('❌ La konsege dezativa utilizadór:', err)
    alert('La konsege dezativa utilizadór')
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
      <h1 class="text-lg font-semibold">UZUARIU</h1>
    </div>

    <!-- Table + Filter -->
    <div class="p-2 flex flex-col flex-1 overflow-hidden">
      <div class="flex-1 overflow-x-auto border border-gray-300">
        <table class="min-w-[600px] w-full border-collapse text-sm table-fixed">
          <thead class="bg-gradient-to-b from-white to-gray-100">
            <tr>
              <th class="border border-gray-300 px-2 py-1 text-left w-[20%]">Naran Uzuariu</th>
              <th class="border border-gray-300 px-2 py-1 text-left w-[25%]">Naran</th>
              <th class="border border-gray-300 px-2 py-1 text-left">Email</th>
            </tr>
            <!-- Filter Inputs -->
            <tr>
              <th class="border border-gray-300 px-2 py-1">
                <input v-model="filter.username" type="text" placeholder="Naran Uzuariu" class="w-full border border-gray-300 px-2 py-1 rounded-sm" />
              </th>
              <th class="border border-gray-300 px-2 py-1">
                <input v-model="filter.name" type="text" placeholder="Naran" class="w-full border border-gray-300 px-2 py-1 rounded-sm" />
              </th>
              <th class="border border-gray-300 px-2 py-1">
                <input v-model="filter.email" type="text" placeholder="Email" class="w-full border border-gray-300 px-2 py-1 rounded-sm" />
              </th>
            </tr>
          </thead>
          <tbody>
          <tr
            v-for="user in filteredUsers"
            :key="user.id"
            @click="selectUser(user)"
            class="hover:bg-gray-50 cursor-pointer"
            :class="{ 'bg-yellow-100': selectedUser?.id === user.id }"
          >
            <td class="border border-gray-300 px-2 py-1">{{ user.username }}</td>
            <td class="border border-gray-300 px-2 py-1">{{ user.first_name }} {{ user.last_name }}</td>
            <td class="border border-gray-300 px-2 py-1">{{ user.email }}</td>
          </tr>
        </tbody>
        </table>
      </div>

      <div v-if="isLoading" class="flex justify-center items-center h-full">
        <div class="text-center space-y-2">
          <svg class="animate-spin h-6 w-6 text-gray-500 mx-auto" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor"
              d="M4 12a8 8 0 018-8v8H4z" />
          </svg>
          <p>Loading data...</p>
        </div>
      </div>

      <!-- Modal Form -->
        <div v-if="showUserModal" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div class="bg-white p-4 rounded shadow w-full max-w-md space-y-3">
            <h2 class="text-lg font-semibold">{{ modalMode === 'add' ? '➕ Tambah User' : '✏️ Edit User' }}</h2>
            <input v-model="userForm.username" placeholder="Username" class="w-full border p-1 rounded-sm" />
            <input v-model="userForm.first_name" placeholder="Naran Propriu" class="w-full border p-1 rounded-sm" />
            <input v-model="userForm.last_name" placeholder="Apelidu" class="w-full border p-1 rounded-sm" />
            <input v-model="userForm.email" placeholder="Email" class="w-full border p-1 rounded-sm" />

            <div class="flex justify-end gap-2 pt-2">
              <button @click="showUserModal = false" class="px-3 py-1 border rounded hover:bg-gray-100">Kansela</button>
              <button @click="saveUser" class="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">
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
          <button @click="addUser" class="hover:text-green-600">➕</button>
          <button @click="editUser" class="hover:text-gray-600">✏️</button>
          <button @click="deleteUser" class="hover:text-red-600">❌</button>
          <button @click="resetPassword" class="hover:text-yellow-600">🔑</button>
          <button @click="lockUser" class="hover:text-orange-600">🔒</button>
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
tr.bg-yellow-100 {
  background-color: #fef9c3;
}
</style>
