<script setup>
import api, { baseURL } from '@/axios'
import { ref, computed, onMounted } from 'vue'
import FooterActions from '@/components/pos/FooterActions.vue'

const authHeader = () => {
  const t =
    localStorage.getItem('access') ||
    localStorage.getItem('token')  ||
    sessionStorage.getItem('access') ||
    sessionStorage.getItem('token')
  if (!t) return {}
  if (t.startsWith('ey')) return { Authorization: `Bearer ${t}` }
  if (t.startsWith('Token ')) return { Authorization: t }
  return { Authorization: `Token ${t}` }
}

const activeTab = ref('products')
const uploadProgress = ref(0)
const isUploading = ref(false)
const uploadMessage = ref('')
const uploadStatus = ref('') // success, error, warning

const store = ref({
  name: '',
  address: '',
  logo: '',
  version: '',
  location: ''
})

// File input refs
const fileInputs = {
  products: ref(null),
  customers: ref(null),
  suppliers: ref(null),
  categories: ref(null)
}

// Example data for downloads
const exampleData = {
  products: [
    { barcode: 'PROD001', name: 'Sample Product 1', category: 'Electronics', buy_price: 100, sell_price: 150, unit: 'pcs', stock: 50, supplier: 'Supplier A' },
    { barcode: 'PROD002', name: 'Sample Product 2', category: 'Clothing', buy_price: 50, sell_price: 80, unit: 'pcs', stock: 25, supplier: 'Supplier B' },
    { barcode: 'PROD003', name: 'Sample Product 3', category: 'Food', buy_price: 20, sell_price: 35, unit: 'kg', stock: 100, supplier: 'Supplier C' }
  ],
  customers: [
    { name: 'John Doe', email: 'john@example.com', phone: '+1234567890', address: '123 Main St, City' },
    { name: 'Jane Smith', email: 'jane@example.com', phone: '+1234567891', address: '456 Oak St, City' },
    { name: 'Bob Johnson', email: 'bob@example.com', phone: '+1234567892', address: '789 Pine St, City' }
  ],
  suppliers: [
    { name: 'Supplier A', contact_person: 'Alice Cooper', phone: '+1111111111', email: 'alice@suppliera.com', address: '100 Business Ave' },
    { name: 'Supplier B', contact_person: 'Bob Wilson', phone: '+2222222222', email: 'bob@supplierb.com', address: '200 Commerce St' },
    { name: 'Supplier C', contact_person: 'Carol Davis', phone: '+3333333333', email: 'carol@supplierc.com', address: '300 Trade Blvd' }
  ],
  categories: [
    { name: 'Electronics', description: 'Electronic devices and accessories' },
    { name: 'Clothing', description: 'Apparel and fashion items' },
    { name: 'Food', description: 'Food and beverage products' },
    { name: 'Books', description: 'Books and educational materials' }
  ]
}

// Generate CSV content
const generateCSV = (data, headers) => {
  const csvHeaders = headers.join(',')
  const csvRows = data.map(row => 
    headers.map(header => {
      const value = row[header] || ''
      // Escape commas and quotes in CSV
      return typeof value === 'string' && (value.includes(',') || value.includes('"')) 
        ? `"${value.replace(/"/g, '""')}"` 
        : value
    }).join(',')
  ).join('\n')
  return `${csvHeaders}\n${csvRows}`
}

// Download example files
const downloadExample = (type) => {
  const data = exampleData[type]
  const headers = Object.keys(data[0])
  const csv = generateCSV(data, headers)
  
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${type}_example.csv`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

// Handle file upload
const handleFileUpload = async (type) => {
  const fileInput = fileInputs[type].value
  const file = fileInput?.files[0]
  
  if (!file) {
    uploadMessage.value = 'Please select a file to upload'
    uploadStatus.value = 'error'
    return
  }

  if (!file.name.endsWith('.csv')) {
    uploadMessage.value = 'Please select a CSV file'
    uploadStatus.value = 'error'
    return
  }

  isUploading.value = true 
  await nextTick()
  uploadProgress.value = 0
  uploadMessage.value = 'Uploading file...'
  uploadStatus.value = ''

  try {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('type', type)

    // Simulate progress
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += 10
      }
    }, 200)

    const response = await api.post('import-data/', formData, {
      headers: {
        ...authHeader(),
        'Content-Type': 'multipart/form-data'
      }
    })

    clearInterval(progressInterval)
    uploadProgress.value = 100

    if (response.data.success) {
      uploadMessage.value = `Successfully imported ${response.data.imported_count || 0} ${type} records`
      uploadStatus.value = 'success'
      if (response.data.errors && response.data.errors.length > 0) {
        uploadMessage.value += `. ${response.data.errors.length} errors encountered.`
        uploadStatus.value = 'warning'
      }
    } else {
      uploadMessage.value = response.data.message || 'Import failed'
      uploadStatus.value = 'error'
    }

    // Clear file input
    if (fileInput) {
      fileInput.value = ''
    }

  } catch (error) {
    uploadMessage.value = error.response?.data?.message || 'Error uploading file'
    uploadStatus.value = 'error'
  } finally {
    isUploading.value = false
    setTimeout(() => {
      uploadMessage.value = ''
      uploadStatus.value = ''
      uploadProgress.value = 0
    }, 5000)
  }
}

// Tab configuration
const tabs = [
  { key: 'products', label: 'Products', icon: '📦' },
  { key: 'customers', label: 'Customers', icon: '👥' },
  { key: 'suppliers', label: 'Suppliers', icon: '🏢' },
  { key: 'categories', label: 'Categories', icon: '📂' }
]

onMounted(async () => {
  try {
    const res = await api.get('store-profile/')
    if (res.data && res.data.length > 0) {
      store.value = res.data[0]
    }
  } catch (err) {
    console.error('Failed to fetch store profile:', err)
  }
})

const getLogoUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `${baseURL.replace("/api/", "")}${path}`
}
</script>

<template>
  <div class="bg-white border border-gray-200 rounded-sm shadow text-sm flex flex-col h-full">
    <!-- Header -->
    <div class="flex items-center gap-2 p-4 border-b border-gray-300 bg-gray-50">
      <img
        :src="store.logo_base64 || getLogoUrl(store.logo)"
        @error="e => e.target.src = baseURL.replace('/api/', '') + '/media/logos/default.jpg'"
        class="h-8 w-8 rounded"
      />
      <h1 class="text-xl font-semibold">📥 Import Data</h1>
    </div>

    <!-- Instructions -->
    <div class="p-4 bg-blue-50 border-b border-blue-200">
      <div class="flex items-start gap-3">
        <div class="text-blue-600 text-xl">💡</div>
        <div class="text-sm text-blue-800">
          <p class="font-medium mb-1">How to import data:</p>
          <ol class="list-decimal list-inside space-y-1 text-xs">
            <li>Download the example CSV file for the data type you want to import</li>
            <li>Open the file in Excel or any spreadsheet application</li>
            <li>Replace the example data with your actual data (keep the headers unchanged)</li>
            <li>Save the file as CSV format</li>
            <li>Upload the file using the upload button below</li>
          </ol>
        </div>
      </div>
    </div>

    <!-- Upload Progress -->
    <div v-if="uploadMessage" class="mx-4 mt-4">
      <div class="p-3 rounded-md" :class="{
        'bg-green-50 border border-green-200': uploadStatus === 'success',
        'bg-red-50 border border-red-200': uploadStatus === 'error',
        'bg-yellow-50 border border-yellow-200': uploadStatus === 'warning',
        'bg-blue-50 border border-blue-200': !uploadStatus
      }">
        <div class="flex items-center gap-2 text-sm">
          <span v-if="uploadStatus === 'success'" class="text-green-600">✅</span>
          <span v-else-if="uploadStatus === 'error'" class="text-red-600">❌</span>
          <span v-else-if="uploadStatus === 'warning'" class="text-yellow-600">⚠️</span>
          <span v-else class="text-blue-600">⏳</span>
          <span :class="{
            'text-green-800': uploadStatus === 'success',
            'text-red-800': uploadStatus === 'error',
            'text-yellow-800': uploadStatus === 'warning',
            'text-blue-800': !uploadStatus
          }">{{ uploadMessage }}</span>
        </div>
        <div v-if="isUploading" class="mt-2">
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div class="bg-blue-600 h-2 rounded-full transition-all duration-300" :style="`width: ${uploadProgress}%`"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="flex space-x-8 px-4" aria-label="Tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="activeTab = tab.key"
          class="py-2 px-1 border-b-2 font-medium text-sm focus:outline-none"
          :class="activeTab === tab.key
            ? 'border-blue-500 text-blue-600'
            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
        >
          {{ tab.icon }} {{ tab.label }}
        </button>
      </nav>
    </div>

    <!-- Content -->
    <div class="flex-1 p-6">
      <!-- Products Tab -->
      <div v-if="activeTab === 'products'" class="space-y-6">
        <div>
          <h3 class="text-lg font-medium text-gray-900 mb-2">Import Products</h3>
          <p class="text-sm text-gray-600 mb-4">Upload a CSV file containing product information including barcode, name, category, prices, and stock levels.</p>
          
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Step 1: Download Example File
                </label>
                <button
                  @click="downloadExample('products')"
                  class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <span class="mr-2">📥</span>
                  Download Products Example
                </button>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Step 2: Upload Your File
                </label>
                <div class="space-y-2">
                  <input
                    ref="fileInputs.products"
                    type="file"
                    accept=".csv"
                    class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  />
                  <button
                    @click="handleFileUpload('products')"
                    :disabled="isUploading"
                    class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm bg-blue-600 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <span class="mr-2">📤</span>
                    {{ isUploading ? 'Uploading...' : 'Upload Products' }}
                  </button>
                </div>
              </div>
            </div>
            
            <div class="bg-gray-50 p-4 rounded-lg">
              <h4 class="text-sm font-medium text-gray-900 mb-2">CSV Format Requirements:</h4>
              <ul class="text-xs text-gray-600 space-y-1">
                <li>• <strong>barcode</strong>: Unique product identifier</li>
                <li>• <strong>name</strong>: Product name</li>
                <li>• <strong>category</strong>: Product category</li>
                <li>• <strong>buy_price</strong>: Purchase price (number)</li>
                <li>• <strong>sell_price</strong>: Selling price (number)</li>
                <li>• <strong>unit</strong>: Unit of measurement (pcs, kg, etc.)</li>
                <li>• <strong>stock</strong>: Initial stock quantity (number)</li>
                <li>• <strong>supplier</strong>: Supplier name</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- Customers Tab -->
      <div v-if="activeTab === 'customers'" class="space-y-6">
        <div>
          <h3 class="text-lg font-medium text-gray-900 mb-2">Import Customers</h3>
          <p class="text-sm text-gray-600 mb-4">Upload a CSV file containing customer information including name, contact details, and address.</p>
          
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Step 1: Download Example File
                </label>
                <button
                  @click="downloadExample('customers')"
                  class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <span class="mr-2">📥</span>
                  Download Customers Example
                </button>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Step 2: Upload Your File
                </label>
                <div class="space-y-2">
                  <input
                    ref="fileInputs.customers"
                    type="file"
                    accept=".csv"
                    class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  />
                  <button
                    @click="handleFileUpload('customers')"
                    :disabled="isUploading"
                    class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm bg-blue-600 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <span class="mr-2">📤</span>
                    {{ isUploading ? 'Uploading...' : 'Upload Customers' }}
                  </button>
                </div>
              </div>
            </div>
            
            <div class="bg-gray-50 p-4 rounded-lg">
              <h4 class="text-sm font-medium text-gray-900 mb-2">CSV Format Requirements:</h4>
              <ul class="text-xs text-gray-600 space-y-1">
                <li>• <strong>name</strong>: Customer name</li>
                <li>• <strong>email</strong>: Email address</li>
                <li>• <strong>phone</strong>: Phone number</li>
                <li>• <strong>address</strong>: Customer address</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- Suppliers Tab -->
      <div v-if="activeTab === 'suppliers'" class="space-y-6">
        <div>
          <h3 class="text-lg font-medium text-gray-900 mb-2">Import Suppliers</h3>
          <p class="text-sm text-gray-600 mb-4">Upload a CSV file containing supplier information including company details and contact information.</p>
          
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Step 1: Download Example File
                </label>
                <button
                  @click="downloadExample('suppliers')"
                  class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <span class="mr-2">📥</span>
                  Download Suppliers Example
                </button>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Step 2: Upload Your File
                </label>
                <div class="space-y-2">
                  <input
                    ref="fileInputs.suppliers"
                    type="file"
                    accept=".csv"
                    class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  />
                  <button
                    @click="handleFileUpload('suppliers')"
                    :disabled="isUploading"
                    class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm bg-blue-600 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <span class="mr-2">📤</span>
                    {{ isUploading ? 'Uploading...' : 'Upload Suppliers' }}
                  </button>
                </div>
              </div>
            </div>
            
            <div class="bg-gray-50 p-4 rounded-lg">
              <h4 class="text-sm font-medium text-gray-900 mb-2">CSV Format Requirements:</h4>
              <ul class="text-xs text-gray-600 space-y-1">
                <li>• <strong>name</strong>: Company name</li>
                <li>• <strong>contact_person</strong>: Contact person name</li>
                <li>• <strong>phone</strong>: Phone number</li>
                <li>• <strong>email</strong>: Email address</li>
                <li>• <strong>address</strong>: Company address</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- Categories Tab -->
      <div v-if="activeTab === 'categories'" class="space-y-6">
        <div>
          <h3 class="text-lg font-medium text-gray-900 mb-2">Import Categories</h3>
          <p class="text-sm text-gray-600 mb-4">Upload a CSV file containing product category information.</p>
          
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Step 1: Download Example File
                </label>
                <button
                  @click="downloadExample('categories')"
                  class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <span class="mr-2">📥</span>
                  Download Categories Example
                </button>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Step 2: Upload Your File
                </label>
                <div class="space-y-2">
                  <input
                    ref="fileInputs.categories"
                    type="file"
                    accept=".csv"
                    class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  />
                  <button
                    @click="handleFileUpload('categories')"
                    :disabled="isUploading"
                    class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm bg-blue-600 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <span class="mr-2">📤</span>
                    {{ isUploading ? 'Uploading...' : 'Upload Categories' }}
                  </button>
                </div>
              </div>
            </div>
            
            <div class="bg-gray-50 p-4 rounded-lg">
              <h4 class="text-sm font-medium text-gray-900 mb-2">CSV Format Requirements:</h4>
              <ul class="text-xs text-gray-600 space-y-1">
                <li>• <strong>name</strong>: Category name</li>
                <li>• <strong>description</strong>: Category description</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>

    <FooterActions />
  </div>
</template>

<style scoped>
.file-input {
  @apply block w-full text-sm text-gray-500;
}

.file-input::file-selector-button {
  @apply mr-4 py-2 px-4 rounded-md border-0 text-sm font-medium bg-blue-50 text-blue-700;
}

.file-input:hover::file-selector-button {
  @apply bg-blue-100;
}
</style>