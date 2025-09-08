<script setup>
import { ref, computed, onMounted } from 'vue'
import api, { baseURL } from '@/axios'
import FooterActions from '@/components/pos/FooterActions.vue'

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
  if (!logoUrl.value) return 'http://127.0.0.1:8000/media/logos/default.jpg'
  const sep = logoUrl.value.includes('?') ? '&' : '?'
  return `${logoUrl.value}${sep}v=${logoVer.value}`
})

const resetLogo = () => {
  logoUrl.value = ''
  selectedLogoFile.value = null
}

const onLogoSelected = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedLogoFile.value = file
    logoUrl.value = URL.createObjectURL(file)
    logoVer.value = Date.now()
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

const saveProfile = async () => {
  try {
    const res = await api.get('store-profile/')
    const data = res.data
    const formData = new FormData()

    formData.append('name', storeName.value)
    formData.append('address', storeAddress.value)
    formData.append('location', storeLocation.value)
    formData.append('version', storeVersion.value)
    if (selectedLogoFile.value) {
      formData.append('logo', selectedLogoFile.value)
    }

    if (Array.isArray(data) && data.length > 0) {
      const id = data[0].id
      await api.put(`store-profile/${id}/`, formData)
    } else {
      await api.post('store-profile/', formData)
    }

    await fetchStoreProfile()

    alert('Store profile saved!')
  } catch (error) {
    console.error('Gagal simpan profil:', error)
    alert('Gagal simpan profil.')
  }
}

const buildLogoUrl = (path) => {
  if (!path) return ''
  if (/^https?:\/\//i.test(path)) return path
  const BASE = 'http://127.0.0.1:8000'
  return new URL(path, BASE).href
}

</script>


<template>
  <div v-bind="$attrs" class="bg-white h-screen flex flex-col text-sm border border-gray-50 rounded-sm shadow-sm">
    <!-- Title Bar -->
    <div class="flex items-center gap-2 px-2 py-1 border-b bg-gray-100">
    <img
          :src="logoSrc"
          @error="e => e.target.src = 'http://127.0.0.1:8000/media/logos/default.jpg'"
          class="w-6 h-6 rounded object-contain"
          width="24" height="24"
          decoding="async"
          fetchpriority="high"
        />
      <h1 class="font-semibold text-base">KONFIGURA</h1>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 px-2 pt-1 border-b bg-white">
      <button
        v-for="name in ['Aplikasaun','Printer','Customer Display']"
        :key="name"
        @click="tab = name"
        class="px-3 py-1 border rounded-t text-xs"
        :class="tab === name ? 'bg-white border-b-0' : 'bg-gray-100'"
      >
        {{ name }}
      </button>
    </div>

    <!-- Content Area -->
    <div class="flex-1 overflow-auto p-4 flex flex-col">
      <template v-if="tab === 'Aplikasaun'">
        <!-- Aplikasaun Content -->
        <table class="w-full border border-gray-300 text-sm table-fixed">
          <tbody>
            <tr>
              <!-- Kiri -->
              <td class="align-top w-1/2 p-3 border-r">
                <div class="flex items-center gap-3 mb-2">
                  <img
                      :src="logoSrc"
                      @error="e => e.target.src = 'http://127.0.0.1:8000/media/logos/default.jpg'"
                      class="w-24 h-24 border rounded bg-white object-contain"
                      width="96" height="96"
                      loading="lazy"
                      decoding="async"
                    />
                  <input ref="logoInput" type="file" accept="image/*" class="hidden" @change="onLogoSelected" />
                  <div class="flex flex-col gap-1">
                    <button @click="triggerLogoPicker" class="px-2 py-1 border rounded text-xs">Change Logo</button>
                    <button @click="resetLogo" class="px-2 py-1 border rounded text-xs">Reset</button>
                    <p class="text-[11px] text-gray-500">Logo must be square. Max size is 512x512.</p>
                  </div>
                </div>
                <div class="space-y-1">
                  <label class="block text-sm font-medium text-gray-700">Store Name *</label>
                  <input 
                    v-model="storeName" 
                    type="text"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                    placeholder="Enter store name"
                  />
                  <p class="text-sm text-gray-500">Display name for your store</p>
                </div>
                <div class="space-y-1">
                  <label class="block text-sm font-medium text-gray-700">Store Address</label>
                  <textarea 
                    v-model="storeAddress" 
                    rows="3"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                    placeholder="Enter store address..."
                  ></textarea>
                  <p class="text-sm text-gray-500">Full business address</p>
                </div>
                <div class="space-y-1">
                  <label class="block text-sm font-medium text-gray-700">Location</label>
                  <select 
                    v-model="storeLocation" 
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  >
                    <option disabled value="">-- Select Location --</option>
                    <option v-for="loc in locationOptions" :key="loc.id" :value="loc.name">
                      {{ loc.name }}
                    </option>
                  </select>
                  <p class="text-sm text-gray-500">Business location</p>
                </div>
                <div class="space-y-1">
                  <label class="block text-sm font-medium text-gray-700">Version</label>
                  <input 
                    v-model="storeVersion" 
                    type="text"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                    placeholder="e.g., 1.0.0"
                  />
                  <p class="text-sm text-gray-500">System version</p>
                </div>
                <div class="space-y-1">
                  <label class="block text-sm font-medium text-gray-700">Machine ID</label>
                  <select 
                    v-model="machineId" 
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  >
                    <option value="Cashier 1">Cashier 1</option>
                    <option value="Cashier 2">Cashier 2</option>
                  </select>
                  <p class="text-sm text-gray-500">Unique cashier station identifier</p>
                </div>
                <div class="space-y-3">
                  <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <h5 class="font-medium text-gray-900">Tax System</h5>
                      <p class="text-sm text-gray-600">Enable tax calculations</p>
                    </div>
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input v-model="taxEnabled" type="checkbox" class="sr-only">
                      <div class="w-11 h-6 bg-gray-200 rounded-full transition-colors" :class="taxEnabled ? 'bg-blue-600' : ''">
                        <div class="w-4 h-4 bg-white rounded-full shadow transform transition-transform" :class="taxEnabled ? 'translate-x-6' : 'translate-x-1'"></div>
                      </div>
                    </label>
                  </div>
                  <div v-if="taxEnabled" class="space-y-1">
                    <label class="block text-sm font-medium text-gray-700">Tax Rate</label>
                    <input
                      v-model="taxRate"
                      type="text"
                      placeholder="e.g., 10%"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                    />
                    <p class="text-sm text-gray-500">Tax percentage (e.g., 10%)</p>
                  </div>
                </div>
              </td>

              <!-- Kanan -->
              <td class="align-top w-1/2 p-3">
                <div class="space-y-4">
                  <h4 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
                    <span class="w-7 h-7 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-semibold mr-3">⚙️</span>
                    System Settings
                  </h4>
                  
                  <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <h5 class="font-medium text-gray-900">Use Customer Names</h5>
                      <p class="text-sm text-gray-600">Enable customer name feature at cashier</p>
                    </div>
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input v-model="useName" type="checkbox" class="sr-only">
                      <div class="w-11 h-6 bg-gray-200 rounded-full transition-colors" :class="useName ? 'bg-blue-600' : ''">
                        <div class="w-4 h-4 bg-white rounded-full shadow transform transition-transform" :class="useName ? 'translate-x-6' : 'translate-x-1'"></div>
                      </div>
                    </label>
                  </div>
                  
                  <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <h5 class="font-medium text-gray-900">Auto Capitalize</h5>
                      <p class="text-sm text-gray-600">Automatically capitalize all text inputs</p>
                    </div>
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input v-model="autoCapitalize" type="checkbox" class="sr-only">
                      <div class="w-11 h-6 bg-gray-200 rounded-full transition-colors" :class="autoCapitalize ? 'bg-blue-600' : ''">
                        <div class="w-4 h-4 bg-white rounded-full shadow transform transition-transform" :class="autoCapitalize ? 'translate-x-6' : 'translate-x-1'"></div>
                      </div>
                    </label>
                  </div>
                  
                  <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <h5 class="font-medium text-gray-900">Minimum Order</h5>
                      <p class="text-sm text-gray-600">Enable multi-pricing with minimum order quantities</p>
                    </div>
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input v-model="useMinOrder" type="checkbox" class="sr-only">
                      <div class="w-11 h-6 bg-gray-200 rounded-full transition-colors" :class="useMinOrder ? 'bg-blue-600' : ''">
                        <div class="w-4 h-4 bg-white rounded-full shadow transform transition-transform" :class="useMinOrder ? 'translate-x-6' : 'translate-x-1'"></div>
                      </div>
                    </label>
                  </div>
                  
                  <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <h5 class="font-medium text-gray-900">Allow Zero Stock Sales</h5>
                      <p class="text-sm text-gray-600">Continue selling products even when stock is zero</p>
                    </div>
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input v-model="allowZeroStock" type="checkbox" class="sr-only">
                      <div class="w-11 h-6 bg-gray-200 rounded-full transition-colors" :class="allowZeroStock ? 'bg-blue-600' : ''">
                        <div class="w-4 h-4 bg-white rounded-full shadow transform transition-transform" :class="allowZeroStock ? 'translate-x-6' : 'translate-x-1'"></div>
                      </div>
                    </label>
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </template>

      <!-- Printer -->
      <template v-if="tab === 'Printer'">
        <div class="bg-gray-50 border rounded-sm p-4 space-y-4">
          <h2 class="font-semibold text-sm border-b pb-1">Printer kasir</h2>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="text-xs block mb-1">Tipu Printer</label>
              <select class="w-full border px-2 py-1 rounded-sm text-sm">
                <option>Spool Printer</option>
              </select>
              <label class="text-xs block mt-2 mb-1">Printer</label>
              <input type="text" class="w-full border px-2 py-1 rounded-sm text-sm" />
              <label class="text-xs block mt-2 mb-1">Device Printer</label>
              <input type="text" placeholder="/dev/usb/p0" class="w-full border px-2 py-1 rounded-sm text-sm" />
              <div class="grid grid-cols-2 gap-2 mt-2">
                <div>
                  <label class="text-xs block mb-1">Luan CPI 10</label>
                  <input type="number" class="w-full border px-2 py-1 rounded-sm text-sm" />
                </div>
                <div>
                  <label class="text-xs block mb-1">Luan CPI 12</label>
                  <input type="number" class="w-full border px-2 py-1 rounded-sm text-sm" />
                </div>
              </div>
              <div class="mt-2 text-xs space-y-1">
                <label><input type="checkbox" /> Hela CPI 10</label><br />
                <label><input type="checkbox" /> Enter depois ikus</label><br />
                <label><input type="checkbox" /> Loke Gaveta</label><br />
                <label><input type="checkbox" /> Auto Tesi</label>
              </div>
            </div>
            <div>
              <label class="text-xs block mb-1">Titulu</label>
              <input type="text" class="w-full border px-2 py-1 rounded-sm text-sm" />
              <label class="text-xs block mt-2 mb-1">Subtítulu</label>
              <textarea class="w-full border px-2 py-1 rounded-sm text-sm"></textarea>
              <label class="text-xs block mt-2 mb-1">Footer</label>
              <textarea class="w-full border px-2 py-1 rounded-sm text-sm"></textarea>
              <div class="mt-2 text-xs space-y-1">
                <label><input type="checkbox" /> Hamosu barcode</label><br />
                <label class="block mt-1">Max Barcode</label>
                <input type="number" class="w-full border px-2 py-1 rounded-sm text-sm" />
              </div>
            </div>
          </div>
          <div class="flex justify-end mt-4 gap-2">
            <button class="px-4 py-1 bg-gray-100 border rounded hover:bg-gray-200 text-sm">Print Koko Pagina</button>
          </div>
        </div>
      </template>

      <!-- Customer Display -->
      <template v-if="tab === 'Customer Display'">
        <div class="bg-gray-50 border rounded-sm p-4">
          <div class="grid grid-cols-1 gap-3">
            <div>
              <label class="text-xs block mb-1">Device</label>
              <select class="w-full border px-2 py-1 rounded-sm text-sm">
                <option>Komunikasaun Port</option>
              </select>
            </div>
            <div>
              <label class="text-xs block mb-1">Postu Inisiál</label>
              <input type="text" class="w-full border px-2 py-1 rounded-sm text-sm" value="BemVindo" />
            </div>
            <div>
              <input type="text" class="w-full border px-2 py-1 rounded-sm text-sm" value="iha Varanda POS" />
            </div>
            <div class="text-right">
              <button class="px-3 py-1 border rounded text-xs">Koko Customer Display</button>
            </div>
          </div>
        </div>
      </template>
    </div>

    <!-- Footer -->
    <div class="flex items-center justify-end px-4 py-3 border-t bg-white">
      <button 
        @click="saveProfile" 
        class="px-6 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors flex items-center"
      >
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"></path>
        </svg>
        Save Configuration
      </button>
    </div>
  </div>

  <FooterActions @save="saveProfile" />
</template>

<style scoped>
textarea {
  white-space: pre-line;
}
</style>
