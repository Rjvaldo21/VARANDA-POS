<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n' 
import api, { baseURL } from '@/axios'
import FooterActions from '@/components/pos/FooterActions.vue'

const { t } = useI18n()

const logoUrl = ref('')
const storeName = ref('')
const storeAddress = ref('')
const storeLocation = ref('')
const storeVersion = ref('')

const tab = ref('Aplikasaun')
const machineId = ref('Cashier 1')
const taxEnabled = ref(false)
const taxRate = ref('')
const useName = ref(false)
const autoCapitalize = ref(false)
const useMinOrder = ref(false)
const allowZeroStock = ref(false)

const logoInput = ref(null)
const selectedLogoFile = ref(null)

const triggerLogoPicker = () => {
  logoInput.value?.click()
}

const logoVer = ref(0) 

const setLogoFromPath = (path) => {
  logoUrl.value = buildLogoUrl(path)
  logoVer.value = Date.now() 
}

const logoSrc = computed(() => {
  if (!logoUrl.value) return `${baseURL.replace('/api/', '')}/media/logos/default.jpg`
  const sep = logoUrl.value.includes('?') ? '&' : '?'
  return `${logoUrl.value}${sep}v=${logoVer.value}`
})

const resetLogo = () => {
  // Use cancel image upload to restore state properly
  cancelImageUpload()
}

const cancelImageUpload = () => {
  // Reset image upload state completely
  selectedLogoFile.value = null
  logoUrl.value = ''
  logoVer.value = Date.now()
  
  // Reset file input
  if (logoInput.value) {
    logoInput.value.value = ''
  }
  
  console.log('🔄 Image upload cancelled - state restored')
}

const clearForm = () => {
  // Reset all form fields to initial state
  storeName.value = ''
  storeAddress.value = ''
  storeLocation.value = ''
  storeVersion.value = ''
  
  // Cancel any image upload to restore state
  cancelImageUpload()
  
  // Reset other settings
  taxEnabled.value = false
  taxRate.value = ''
  useName.value = false
  autoCapitalize.value = false
  useMinOrder.value = false
  allowZeroStock.value = false
  machineId.value = 'Cashier 1'
  
  // Reset saving state
  saving.value = false
  
  console.log('🔄 Form cleared to initial state')
}

const onLogoSelected = (event) => {
  const file = event.target.files[0]
  if (file) {
    // File validation
    const maxSize = 5 * 1024 * 1024 // 5MB
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    
    console.log('📸 Selected file:', {
      name: file.name,
      size: file.size,
      type: file.type
    })
    
    // Check file size
    if (file.size > maxSize) {
      alert('❌ File too large! Please select an image smaller than 5MB.')
      event.target.value = '' // Clear the input
      return
    }
    
    // Check file type
    if (!allowedTypes.includes(file.type)) {
      alert('❌ Invalid file type! Please select a valid image file (JPG, PNG, GIF, WebP).')
      event.target.value = '' // Clear the input
      return
    }
    
    // Check if it's actually an image by trying to load it
    const img = new Image()
    img.onload = () => {
      console.log('✅ Valid image file:', {
        width: img.width,
        height: img.height,
        name: file.name,
        size: file.size
      })
      
      selectedLogoFile.value = file
      logoUrl.value = URL.createObjectURL(file)
      logoVer.value = Date.now()
    }
    
    img.onerror = () => {
      console.error('❌ Invalid image file')
      alert('❌ Invalid image file! Please select a valid image.')
      event.target.value = '' // Clear the input
    }
    
    img.src = URL.createObjectURL(file)
  }
}

const locationOptions = ref([])

const fetchLocations = async () => {
  try {
    const res = await api.get('locations/')
    locationOptions.value = res.data
  } catch (e) {
    console.error('Gagal ambil lokasi:', e)
  }
}

const fetchStoreProfile = async () => {
  try {
    const res = await api.get('store-profile/')
    if (res.data && res.data.length > 0) {
      const data = res.data[0]
      setLogoFromPath(data.logo)       
      storeName.value = data.name
      storeAddress.value = data.address
      storeLocation.value = data.location
      storeVersion.value = data.version
    }
  } catch (error) {
    console.error('Gagal fetch store profile:', error)
  }
}

onMounted(() => {
  fetchStoreProfile()
  fetchLocations()
})

const saving = ref(false)

const saveProfile = async () => {
  // Enhanced validation
  if (!storeName.value || storeName.value.trim() === '') {
    alert('⚠️ Store name is required!')
    return
  }

  saving.value = true
  try {
    console.log('🔄 Saving store profile...')
    
    // Get current store profile
    const res = await api.get('store-profile/')
    const data = res.data
    
    // Create FormData for multipart upload
    const formData = new FormData()
    formData.append('name', storeName.value.trim())
    formData.append('address', storeAddress.value.trim())
    formData.append('location', storeLocation.value.trim())
    formData.append('version', storeVersion.value.trim())
    
    // Add logo file if selected
    if (selectedLogoFile.value) {
      console.log('📸 Adding logo file to upload:', {
        name: selectedLogoFile.value.name,
        size: selectedLogoFile.value.size,
        type: selectedLogoFile.value.type,
        lastModified: selectedLogoFile.value.lastModified
      })
      
      // Ensure the file is properly appended
      formData.append('logo', selectedLogoFile.value, selectedLogoFile.value.name)
      
      // Verify the file was added to FormData
      console.log('📸 File added to FormData:', formData.has('logo'))
    }

    console.log('📦 FormData contents:')
    for (let [key, value] of formData.entries()) {
      if (value instanceof File) {
        console.log(`  ${key}: ${value.name} (${value.size} bytes)`)
      } else {
        console.log(`  ${key}: ${value}`)
      }
    }

    let response
    if (Array.isArray(data) && data.length > 0) {
      // Update existing profile
      const id = data[0].id
      console.log(`🔄 Updating store profile ID: ${id}`)
      response = await api.put(`store-profile/${id}/`, formData)
    } else {
      // Create new profile
      console.log('🔄 Creating new store profile')
      response = await api.post('store-profile/', formData)
    }

    console.log('✅ Store profile saved successfully')
    
    // Show success message first
    alert('✅ Store profile saved successfully!')
    
    // Cancel image upload to restore form state like after cancel
    cancelImageUpload()
    
    // Refresh profile data to reload from server (this will restore form values)
    await fetchStoreProfile()
    
  } catch (error) {
    console.error('❌ Failed to save store profile:', error)
    
    let errorMessage = 'Failed to save store profile.'
    
    if (error.response) {
      const { status, data } = error.response
      console.error('🚫 Server error details:', { status, data })
      
      if (status === 400 && data) {
        // Handle validation errors
        const validationErrors = []
        for (const [field, errors] of Object.entries(data)) {
          if (Array.isArray(errors)) {
            validationErrors.push(`${field}: ${errors.join(', ')}`)
          } else {
            validationErrors.push(`${field}: ${errors}`)
          }
        }
        if (validationErrors.length > 0) {
          errorMessage = `Validation errors:\n${validationErrors.join('\n')}`
        }
      } else if (status === 413) {
        errorMessage = 'File too large. Please select a smaller image.'
      } else if (status === 415) {
        errorMessage = 'Unsupported file type. Please select a valid image file (JPG, PNG).'
      } else if (status === 401) {
        errorMessage = 'Authentication failed. Please login again.'
      } else if (status === 403) {
        errorMessage = 'Permission denied. You do not have access to perform this action.'
      } else if (status >= 500) {
        errorMessage = 'Server error. Please try again later.'
      } else {
        errorMessage = `Error (${status}): ${data?.detail || data?.message || 'Unknown error'}`
      }
    } else if (error.request) {
      errorMessage = 'Network error. Please check your connection and try again.'
    } else {
      errorMessage = `Unexpected error: ${error.message}`
    }
    
    alert(`❌ ${errorMessage}`)
    
    // Cancel image upload to restore state
    cancelImageUpload()
  } finally {
    saving.value = false
  }
}

const buildLogoUrl = (path) => {
  if (!path) return ''
  if (/^https?:\/\//i.test(path)) return path
  const BASE = baseURL.replace('/api/', '')
  return `${BASE}${path.startsWith('/') ? '' : '/'}${path}`
}

</script>


<template>
  <div v-bind="$attrs" class="bg-white h-screen flex flex-col text-sm border border-gray-200 rounded-lg shadow-sm">
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b border-gray-300 bg-gradient-to-r from-slate-50 to-gray-50">
      <div class="flex items-center gap-3">
        <img
          :src="logoSrc"
          @error="e => e.target.src = baseURL.replace('/api/', '') + '/media/logos/default.jpg'"
          class="w-8 h-8 rounded-lg object-contain shadow-sm"
          width="32" height="32"
          decoding="async"
          fetchpriority="high"
        />
        <div>
          <h1 class="text-xl font-bold text-gray-800">⚙️ {{ t('navigation.systemConfiguration') }}</h1>
          <p class="text-sm text-gray-600">{{ t('settings.title') }}</p>
        </div>
      </div>
      <div class="flex gap-2">
        <button 
          @click="clearForm" 
          :disabled="saving"
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors flex items-center"
          :class="saving ? 'opacity-50 cursor-not-allowed' : ''"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
          {{ t('common.clear') || 'Clear' }}
        </button>
        <button 
          @click="saveProfile" 
          :disabled="saving"
          class="px-4 py-2 text-sm font-medium text-white border border-transparent rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors flex items-center"
          :class="saving 
            ? 'bg-gray-400 cursor-not-allowed' 
            : 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500'"
        >
          <svg v-if="saving" class="animate-spin w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <svg v-else class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"></path>
          </svg>
          {{ saving ? 'Saving...' : t('settings.saveChanges') }}
        </button>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="flex border-b bg-white px-4">
      <button
        v-for="(config, key) in {
          'general': { name: t('settings.general'), icon: '🏪', value: 'Aplikasaun' },
          'printer': { name: t('settings.printer'), icon: '🖨️', value: 'Printer' },
          'display': { name: t('settings.display'), icon: '📺', value: 'Customer Display' }
        }"
        :key="key"
        @click="tab = config.value"
        class="flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors"
        :class="tab === config.value
          ? 'border-blue-500 text-blue-600 bg-blue-50' 
          : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'"
      >
        <span class="text-lg">{{ config.icon }}</span>
        {{ config.name }}
      </button>
    </div>

    <!-- Content Area -->
    <div class="flex-1 overflow-auto">
      <template v-if="tab === 'Aplikasaun'">
        <!-- General Settings Content -->
        <div class="max-w-7xl mx-auto p-6">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <!-- Store Information -->
            <div class="bg-white border border-gray-200 rounded-lg p-6">
              <div class="flex items-center gap-3 mb-6">
                <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <span class="text-blue-600 text-xl">🏪</span>
                </div>
                <div>
                  <h3 class="text-lg font-semibold text-gray-900">{{ t('settings.storeInformation') }}</h3>
                  <p class="text-sm text-gray-600">{{ t('settings.storeInformation') }}</p>
                </div>
              </div>
              
              <!-- Logo Section -->
              <div class="flex items-start gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
                <img
                  :src="logoSrc"
                  @error="e => e.target.src = baseURL.replace('/api/', '') + '/media/logos/default.jpg'"
                  class="w-20 h-20 border-2 border-gray-200 rounded-lg bg-white object-contain"
                  width="80" height="80"
                  loading="lazy"
                  decoding="async"
                />
                <input ref="logoInput" type="file" accept="image/*" class="hidden" @change="onLogoSelected" />
                <div class="flex-1">
                  <h4 class="text-sm font-medium text-gray-900 mb-2">Logo Loja</h4>
                  <div class="flex gap-2 mb-2">
                    <button @click="triggerLogoPicker" class="px-3 py-1.5 text-xs font-medium text-blue-600 bg-blue-50 border border-blue-200 rounded-md hover:bg-blue-100 transition-colors">{{ t('common.edit') }}</button>
                    <button @click="resetLogo" class="px-3 py-1.5 text-xs font-medium text-gray-600 bg-gray-50 border border-gray-200 rounded-md hover:bg-gray-100 transition-colors">{{ t('common.reset') }}</button>
                    <button v-if="selectedLogoFile" @click="cancelImageUpload" class="px-3 py-1.5 text-xs font-medium text-red-600 bg-red-50 border border-red-200 rounded-md hover:bg-red-100 transition-colors">Cancel Upload</button>
                  </div>
                  <p class="text-xs text-gray-500">Square logo recommended. Max size: 512x512px</p>
                </div>
              </div>
              <!-- Store Details Form -->
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Store Name *</label>
                  <input 
                    v-model="storeName" 
                    type="text"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                    placeholder="Enter store name"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Store Address</label>
                  <textarea 
                    v-model="storeAddress" 
                    rows="2"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors resize-none"
                    placeholder="Enter store address..."
                  ></textarea>
                </div>
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Location</label>
                    <select 
                      v-model="storeLocation" 
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                    >
                      <option disabled value="">Select Location</option>
                      <option v-for="loc in locationOptions" :key="loc.id" :value="loc.name">
                        {{ loc.name }}
                      </option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Version</label>
                    <input 
                      v-model="storeVersion" 
                      type="text"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                      placeholder="e.g., 1.0.0"
                    />
                  </div>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Machine ID</label>
                  <select 
                    v-model="machineId" 
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  >
                    <option value="Cashier 1">💻 Cashier 1</option>
                    <option value="Cashier 2">💻 Cashier 2</option>
                  </select>
                </div>
                <!-- Tax Configuration -->
                <div class="border-t pt-4">
                  <div class="flex items-center justify-between p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <div>
                      <h5 class="font-medium text-gray-900 flex items-center gap-2">
                        <span>💰</span> Tax System
                      </h5>
                      <p class="text-sm text-gray-600">Enable automatic tax calculations</p>
                    </div>
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input v-model="taxEnabled" type="checkbox" class="sr-only">
                      <div class="w-11 h-6 bg-gray-200 rounded-full transition-colors" :class="taxEnabled ? 'bg-blue-600' : ''">
                        <div class="w-4 h-4 bg-white rounded-full shadow transform transition-transform" :class="taxEnabled ? 'translate-x-6' : 'translate-x-1'"></div>
                      </div>
                    </label>
                  </div>
                  <div v-if="taxEnabled" class="mt-3">
                    <label class="block text-sm font-medium text-gray-700 mb-1">Tax Rate</label>
                    <input
                      v-model="taxRate"
                      type="text"
                      placeholder="e.g., 10%"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- System Settings -->
            <div class="bg-white border border-gray-200 rounded-lg p-6">
              <div class="flex items-center gap-3 mb-6">
                <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                  <span class="text-green-600 text-xl">⚙️</span>
                </div>
                <div>
                  <h3 class="text-lg font-semibold text-gray-900">System Preferences</h3>
                  <p class="text-sm text-gray-600">Configure operational settings</p>
                </div>
              </div>
              
              <div class="space-y-4">
                <div class="flex items-center justify-between p-3 bg-gray-50 border border-gray-200 rounded-lg">
                  <div>
                    <h5 class="font-medium text-gray-900 flex items-center gap-2">
                      <span>👤</span> Customer Names
                    </h5>
                    <p class="text-sm text-gray-600">Enable customer name input</p>
                  </div>
                  <label class="relative inline-flex items-center cursor-pointer">
                    <input v-model="useName" type="checkbox" class="sr-only">
                    <div class="w-11 h-6 bg-gray-200 rounded-full transition-colors" :class="useName ? 'bg-green-600' : ''">
                      <div class="w-4 h-4 bg-white rounded-full shadow transform transition-transform" :class="useName ? 'translate-x-6' : 'translate-x-1'"></div>
                    </div>
                  </label>
                </div>
                
                <div class="flex items-center justify-between p-3 bg-gray-50 border border-gray-200 rounded-lg">
                  <div>
                    <h5 class="font-medium text-gray-900 flex items-center gap-2">
                      <span>🔤</span> Auto Capitalize
                    </h5>
                    <p class="text-sm text-gray-600">Automatically capitalize text inputs</p>
                  </div>
                  <label class="relative inline-flex items-center cursor-pointer">
                    <input v-model="autoCapitalize" type="checkbox" class="sr-only">
                    <div class="w-11 h-6 bg-gray-200 rounded-full transition-colors" :class="autoCapitalize ? 'bg-green-600' : ''">
                      <div class="w-4 h-4 bg-white rounded-full shadow transform transition-transform" :class="autoCapitalize ? 'translate-x-6' : 'translate-x-1'"></div>
                    </div>
                  </label>
                </div>
                
                <div class="flex items-center justify-between p-3 bg-gray-50 border border-gray-200 rounded-lg">
                  <div>
                    <h5 class="font-medium text-gray-900 flex items-center gap-2">
                      <span>📦</span> Minimum Order
                    </h5>
                    <p class="text-sm text-gray-600">Enable quantity-based pricing</p>
                  </div>
                  <label class="relative inline-flex items-center cursor-pointer">
                    <input v-model="useMinOrder" type="checkbox" class="sr-only">
                    <div class="w-11 h-6 bg-gray-200 rounded-full transition-colors" :class="useMinOrder ? 'bg-green-600' : ''">
                      <div class="w-4 h-4 bg-white rounded-full shadow transform transition-transform" :class="useMinOrder ? 'translate-x-6' : 'translate-x-1'"></div>
                    </div>
                  </label>
                </div>
                
                <div class="flex items-center justify-between p-3 bg-gray-50 border border-gray-200 rounded-lg">
                  <div>
                    <h5 class="font-medium text-gray-900 flex items-center gap-2">
                      <span>🚫</span> Zero Stock Sales
                    </h5>
                    <p class="text-sm text-gray-600">Allow sales with zero inventory</p>
                  </div>
                  <label class="relative inline-flex items-center cursor-pointer">
                    <input v-model="allowZeroStock" type="checkbox" class="sr-only">
                    <div class="w-11 h-6 bg-gray-200 rounded-full transition-colors" :class="allowZeroStock ? 'bg-green-600' : ''">
                      <div class="w-4 h-4 bg-white rounded-full shadow transform transition-transform" :class="allowZeroStock ? 'translate-x-6' : 'translate-x-1'"></div>
                    </div>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Printer Settings -->
      <template v-if="tab === 'Printer'">
        <div class="max-w-6xl mx-auto p-6">
          <div class="bg-white border border-gray-200 rounded-lg p-6">
            <div class="flex items-center gap-3 mb-6">
              <div class="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <span class="text-purple-600 text-xl">🖨️</span>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900">Printer Configuration</h3>
                <p class="text-sm text-gray-600">Configure receipt printer settings</p>
              </div>
            </div>
            
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <!-- Printer Hardware Settings -->
              <div>
                <h4 class="text-md font-medium text-gray-900 mb-4 flex items-center gap-2">
                  <span>⚙️</span> Hardware Settings
                </h4>
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Printer Type</label>
                    <select class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent">
                      <option>Spool Printer</option>
                      <option>Direct Printer</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Printer Name</label>
                    <input type="text" placeholder="Printer name" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Device Path</label>
                    <input type="text" placeholder="/dev/usb/p0" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                  </div>
                  <div class="grid grid-cols-2 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Width CPI 10</label>
                      <input type="number" placeholder="42" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Width CPI 12</label>
                      <input type="number" placeholder="35" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                    </div>
                  </div>
                  
                  <!-- Printer Options -->
                  <div class="space-y-3 pt-4 border-t">
                    <h5 class="text-sm font-medium text-gray-900">Print Options</h5>
                    <div class="space-y-2">
                      <label class="flex items-center gap-2 text-sm text-gray-700">
                        <input type="checkbox" class="rounded border-gray-300 text-purple-600 focus:ring-purple-500" />
                        Use CPI 10 font size
                      </label>
                      <label class="flex items-center gap-2 text-sm text-gray-700">
                        <input type="checkbox" class="rounded border-gray-300 text-purple-600 focus:ring-purple-500" />
                        Add line break after print
                      </label>
                      <label class="flex items-center gap-2 text-sm text-gray-700">
                        <input type="checkbox" class="rounded border-gray-300 text-purple-600 focus:ring-purple-500" />
                        Open cash drawer
                      </label>
                      <label class="flex items-center gap-2 text-sm text-gray-700">
                        <input type="checkbox" class="rounded border-gray-300 text-purple-600 focus:ring-purple-500" />
                        Auto test print
                      </label>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Receipt Layout -->
              <div>
                <h4 class="text-md font-medium text-gray-900 mb-4 flex items-center gap-2">
                  <span>📄</span> Receipt Layout
                </h4>
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Receipt Title</label>
                    <input type="text" placeholder="Store Name" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Subtitle</label>
                    <textarea rows="2" placeholder="Store address and details" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"></textarea>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Footer Message</label>
                    <textarea rows="2" placeholder="Thank you message" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"></textarea>
                  </div>
                  
                  <!-- Barcode Settings -->
                  <div class="space-y-3 pt-4 border-t">
                    <h5 class="text-sm font-medium text-gray-900">Barcode Settings</h5>
                    <label class="flex items-center gap-2 text-sm text-gray-700">
                      <input type="checkbox" class="rounded border-gray-300 text-purple-600 focus:ring-purple-500" />
                      Print barcode on receipt
                    </label>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Max Barcode Length</label>
                      <input type="number" placeholder="13" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Test Print Button -->
            <div class="flex justify-end mt-6 pt-6 border-t">
              <button class="px-4 py-2 text-sm font-medium text-purple-600 bg-purple-50 border border-purple-200 rounded-lg hover:bg-purple-100 transition-colors flex items-center gap-2">
                <span>🖨️</span> Test Print
              </button>
            </div>
          </div>
        </div>
      </template>

      <!-- Customer Display Settings -->
      <template v-if="tab === 'Customer Display'">
        <div class="max-w-4xl mx-auto p-6">
          <div class="bg-white border border-gray-200 rounded-lg p-6">
            <div class="flex items-center gap-3 mb-6">
              <div class="w-10 h-10 bg-teal-100 rounded-lg flex items-center justify-center">
                <span class="text-teal-600 text-xl">📺</span>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900">Customer Display</h3>
                <p class="text-sm text-gray-600">Configure external customer display settings</p>
              </div>
            </div>
            
            <div class="max-w-md space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Display Device</label>
                <select class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent">
                  <option>Communication Port</option>
                  <option>USB Display</option>
                  <option>Network Display</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Welcome Message (Line 1)</label>
                <input type="text" value="Welcome" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Welcome Message (Line 2)</label>
                <input type="text" value="to Varanda POS" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent" />
              </div>
              
              <!-- Test Display Button -->
              <div class="pt-4 border-t">
                <button class="w-full px-4 py-2 text-sm font-medium text-teal-600 bg-teal-50 border border-teal-200 rounded-lg hover:bg-teal-100 transition-colors flex items-center justify-center gap-2">
                  <span>📺</span> Test Customer Display
                </button>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>

  </div>

  <FooterActions />
</template>

<style scoped>
textarea {
  white-space: pre-line;
}
</style>
