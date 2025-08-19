<script setup>
import { jwtDecode } from 'jwt-decode'
import { ref } from 'vue'
import api from '@/axios'
import router from '@/router'

const username = ref('')
const password = ref('')
const error = ref('')

const emit = defineEmits(['login-success'])

const login = async () => {
  try {
    const res = await api.post('/token/', {
      username: username.value,
      password: password.value
    })

    const token = res.data.access
    const refresh = res.data.refresh
    const decoded = jwtDecode(token)

    localStorage.setItem('token', token)
    localStorage.setItem('refresh_token', refresh)
    localStorage.setItem('username', decoded.username)
    localStorage.setItem('role', decoded.role)

    emit('login-success')
    router.push('/pos')
  } catch (err) {
    error.value = 'Login falha. Hare fali username ka password.'
    console.error(err)
  }
}

const showModal = ref(false)
const suUsername = ref('')
const suPassword = ref('')

const openCreateSuperuser = () => {
  showModal.value = true
}

const submitSuperuser = async () => {
  try {
      await api.post('/create-superuser/', {
      username: suUsername.value,
      password: suPassword.value
    })
    alert('✅ Superuser kria ho sucesso!')
    showModal.value = false
  } catch (err) {
    alert('❌ Erro: ' + (err.response?.data?.error || 'Tente fali'))
    console.error(err)
  }
}
</script>

<template>
  <div class="flex w-full">
    <div class="w-1/2 bg-[#301818] flex flex-col justify-center px-10">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-white mb-2">Sistem POS Modern</h1>
        <p class="text-white text-[15px] leading-relaxed">
          Sistema POS moderno ne’ebé fasilita prosesu fa’an,<br />
          jeramentu produtu, no relatoriu transasaun iha tempu real.
        </p>
      </div>
    </div>

    <div class="w-1/2 bg-[#ffffff] rounded-bl-[60px] flex items-center justify-center px-6 py-12">
      <div class="bg-white rounded-xl shadow-lg p-10 w-full max-w-sm">
        <h2 class="text-3xl font-bold mb-2">Login!</h2>
        <p class="text-gray-600 mb-6">Login hodi komesa halo servisu...</p>

        <div class="mb-4 relative">
          <span class="absolute inset-y-0 left-0 pl-4 flex items-center text-gray-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none"
              viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M16 12H8m0 0l4-4m-4 4l4 4" />
            </svg>
          </span>
          <input
            v-model="username"
            placeholder="Naran Uzuariu"
            class="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </div>

        <div class="mb-6 relative">
          <span class="absolute inset-y-0 left-0 pl-4 flex items-center text-gray-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none"
              viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 11c0-.552-.448-1-1-1s-1 .448-1 1 .448 1 1 1 1-.448 1-1zm4 4v-2a4 4 0 00-8 0v2m12 0a2 2 0 01-2 2H6a2 2 0 01-2-2" />
            </svg>
          </span>
          <input
            v-model="password"
            type="password"
            placeholder="Password"
            class="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </div>

        <button
          @click="login"
          class="w-full bg-[#007BFF] hover:bg-[#0066d4] text-white font-semibold py-3 rounded-full transition"
        >
          Login
        </button>

        <p class="text-sm text-center text-gray-500 mt-4">
          Seidauk iha superuser?
          <a href="#" class="text-blue-600 underline" @click="openCreateSuperuser">Kria Superuser</a>
        </p>
      </div>
    </div>

    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div class="bg-white p-6 rounded-lg shadow-lg w-full max-w-sm">
        <h2 class="text-xl font-semibold mb-4">Kria Superuser</h2>
        <input
          v-model="suUsername"
          placeholder="Naran Uzuariu"
          class="w-full mb-3 px-3 py-2 border border-gray-300 rounded"
        />
        <input
          v-model="suPassword"
          type="password"
          placeholder="Password"
          class="w-full mb-4 px-3 py-2 border border-gray-300 rounded"
        />
        <div class="flex justify-end gap-2">
          <button @click="showModal = false" class="px-4 py-2 bg-gray-200 rounded">Kansela</button>
          <button @click="submitSuperuser" class="px-4 py-2 bg-blue-600 text-white rounded">Kria</button>
        </div>
      </div>
    </div>
  </div>
</template>
