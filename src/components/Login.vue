<script setup>
import { jwtDecode } from 'jwt-decode'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import router from '@/router'
import api from '@/axios'
import LanguageSwitcher from './LanguageSwitcher.vue'

const { t } = useI18n()

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
    error.value = t('auth.loginFailed')
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
        <h1 class="text-2xl font-bold text-white mb-2">{{ t('auth.modernPosSystem') }}</h1>
        <p class="text-white text-[15px] leading-relaxed">
          Sistema POS moderno ne’ebé fasilita prosesu fa’an,<br />
          jeramentu produtu, no relatoriu transasaun iha tempu real.
        </p>
      </div>
      <div class="mt-4">
        <LanguageSwitcher />
      </div>
    </div>

    <div class="w-1/2 bg-[#ffffff] rounded-bl-[60px] flex items-center justify-center px-6 py-12">
      <div class="bg-white rounded-xl shadow-lg p-10 w-full max-w-sm">
        <h2 class="text-3xl font-bold mb-2">{{ t('auth.login') }}!</h2>
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
            :placeholder="t('auth.username')"
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
            :placeholder="t('auth.password')"
            class="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </div>

        <button
          @click="login"
          class="w-full bg-[#007BFF] hover:bg-[#0066d4] text-white font-semibold py-3 rounded-full transition"
        >
          {{ t('auth.login') }}
        </button>

        <!-- <p class="text-sm text-center text-gray-500 mt-4">
          Seidauk iha superuser?
          <a href="#" class="text-blue-600 underline" @click="openCreateSuperuser">Kria Superuser</a>
        </p> -->
        
      </div>
    </div>

    <!-- Superuser Creation Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4">
        <!-- Header -->
        <div class="flex items-center justify-between p-6 border-b border-gray-200">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-xl font-semibold text-gray-900">Create Superuser</h3>
              <p class="text-sm text-gray-500">Create administrator account for system access</p>
            </div>
          </div>
          <button @click="showModal = false" class="text-gray-400 hover:text-gray-600 transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <!-- Form -->
        <form @submit.prevent="submitSuperuser" class="p-6">
          <div class="space-y-6">
            <!-- Username -->
            <div class="space-y-1">
              <label class="block text-sm font-medium text-gray-700">Username *</label>
              <input 
                v-model="suUsername" 
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                placeholder="Enter admin username"
                required
              />
              <p class="text-sm text-gray-500">Administrator login username</p>
            </div>

            <!-- Password -->
            <div class="space-y-1">
              <label class="block text-sm font-medium text-gray-700">Password *</label>
              <input 
                v-model="suPassword" 
                type="password"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                placeholder="Enter secure password"
                required
              />
              <p class="text-sm text-gray-500">Strong password for admin account</p>
            </div>
          </div>

          <!-- Form Actions -->
          <div class="flex items-center justify-between pt-6 border-t border-gray-200 mt-6">
            <button 
              type="button" 
              @click="showModal = false" 
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              class="px-6 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors flex items-center"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"></path>
              </svg>
              Create Superuser
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
