<script setup>
import { ref, computed, onMounted } from 'vue'
import FooterActions from '@/components/pos/FooterActions.vue'
import api, { baseURL } from '@/axios'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const store = ref({
  name: '',
  address: '',
  logo: '',
  version: '',
  location: ''
})

const showModal = ref(false)
const loading = ref(false)
const currentUser = ref({})
const editingProduct = ref(null)

// Validation states
const fieldErrors = ref({})
const fieldValidation = ref({})
const formErrors = ref([])

const productForm = ref({
  name: '',
  sku: '',
  barcode: '',
  category: '',
  variant: '',
  unit: '',
  price: '',
  cost_price: '',
  discount: '',
  stock: '',
  min_stock: '',
  supplier: ''
})

const categories = ref([])
const units = ref([])
const suppliers = ref([])

const items = ref([])
const productsRaw = ref([])
const selectedItem = ref(null)

const handleFocus = (field) => {
  const val = productForm.value[field]
  if (val === '' || val === null) {
    productForm.value[field] = '0.00'
  } else {
    const num = parseFloat(val)
    if (!isNaN(num)) {
      productForm.value[field] = num.toFixed(2)
    }
  }
}

const formatDecimal = (field) => {
  const val = parseFloat(productForm.value[field])
  productForm.value[field] = isNaN(val) ? '' : val.toFixed(2)
}

const fetchDropdownData = async () => {
  try {
    console.log('🔄 Loading dropdown data...')
    const [catRes, unitRes, supRes] = await Promise.all([
      api.get('categories/'),
      api.get('units/'),
      api.get('suppliers/')
    ])
    categories.value = catRes.data || []
    units.value = unitRes.data || []
    suppliers.value = supRes.data || []
    console.log('✅ Dropdown data loaded:', {
      categories: categories.value.length,
      units: units.value.length,
      suppliers: suppliers.value.length
    })
  } catch (err) {
    console.error('❌ Failed to load dropdown data:', err)
    // Initialize with empty arrays if API fails
    categories.value = []
    units.value = []
    suppliers.value = []
  }
}

const addItem = async () => {
  editingProduct.value = null
  await fetchDropdownData()
  Object.assign(productForm.value, {
    name: '', sku: '', barcode: '', category: '',
    variant: '', unit: '', price: '', cost_price: '',
    discount: '', stock: '', min_stock: '', supplier: ''
  })
  showModal.value = true
}

const formatUSD = (val) => {
  const num = parseFloat(val)
  if (isNaN(num)) return ''
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(num)
}

const filter = ref({ barcode: '', nama: '', kategori: '', supplier: '' })
const perPage = ref(10)

const formattedAddress = computed(() =>
  store.value.address ? store.value.address.replace(/\n/g, '<br />') : ''
)

const getLogoUrl = (path) => {
  if (!path) return ''
  return path.startsWith('http') ? path : `${baseURL.replace("/api/", "")}${path}`
}

onMounted(async () => {
  try {
    const res = await api.get('store-profile/')
    if (res.data && res.data.length > 0) {
      store.value = res.data[0]
    }
  } catch (err) {
    console.error('Gagal fetch store profile:', err)
  }

  try {
    const token = localStorage.getItem('token')
    const response = await api.get('products/', {
      headers: { Authorization: `Bearer ${token}` }
    })

    productsRaw.value = response.data

    items.value = response.data.map(p => ({
      id: p.id,
      sku: p.sku,
      name: p.name,
      barcode: p.barcode,
      category: p.category,
      variant: p.variant,
      unit: p.unit,
      price: parseFloat(p.price),
      cost_price: parseFloat(p.cost_price),
      discount: parseFloat(p.discount),
      stock: p.stock,
      min_stock: p.min_stock,
      supplier: p.supplier,
      satuan: p.unit_name,
      kategori: p.category_name,
      supplier_name: p.supplier_name
    }))
  } catch (error) {
    console.error('Gagal mengambil data produk:', error)
  }
})

const filteredItems = computed(() => {
  return items.value.filter(i =>
    i.barcode?.toLowerCase().includes(filter.value.barcode.toLowerCase()) &&
    i.name?.toLowerCase().includes(filter.value.nama.toLowerCase()) &&
    (i.kategori || '').toLowerCase().includes(filter.value.kategori.toLowerCase()) &&
    (i.supplier_name || '').toLowerCase().includes(filter.value.supplier.toLowerCase())
  )
})

const formatPrice = (val) => {
  const num = parseFloat(val)
  return isNaN(num) ? '$0.00' : num.toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2
  })
}

const saveProduct = async () => {
  // Enhanced validation
  const requiredFields = {
    name: 'Product Name',
    sku: 'SKU',
    price: 'Selling Price',
    cost_price: 'Cost Price'
  }
  
  const missingFields = []
  for (const [field, label] of Object.entries(requiredFields)) {
    if (!productForm.value[field] || productForm.value[field].toString().trim() === '') {
      missingFields.push(label)
    }
  }
  
  if (missingFields.length > 0) {
    alert(`Please fill all required fields: ${missingFields.join(', ')}`)
    return
  }

  // Validate numeric fields
  const priceValue = parseFloat(productForm.value.price)
  const costValue = parseFloat(productForm.value.cost_price)
  
  if (isNaN(priceValue) || priceValue <= 0) {
    alert('Please enter a valid selling price greater than 0')
    return
  }
  
  if (isNaN(costValue) || costValue <= 0) {
    alert('Please enter a valid cost price greater than 0')
    return
  }

  try {
    loading.value = true 
  await nextTick()
    console.log('📦 Saving product...', editingProduct.value ? 'UPDATE' : 'CREATE')
    
    const payload = {
      name: productForm.value.name.trim(),
      sku: productForm.value.sku.trim(),
      barcode: productForm.value.barcode?.trim() || '',
      category: productForm.value.category || null,
      variant: productForm.value.variant?.trim() || '',
      unit: productForm.value.unit || null,
      price: priceValue,
      cost_price: costValue,
      discount: parseFloat(productForm.value.discount) || 0,
      stock: parseInt(productForm.value.stock) || 0,
      min_stock: parseInt(productForm.value.min_stock) || 0,
      supplier: productForm.value.supplier || null
    }
    
    console.log('📦 Product payload:', payload)
    
    let res
    const isUpdate = editingProduct.value
    
    if (isUpdate) {
      // Update product
      res = await api.put(`products/${editingProduct.value.id}/`, payload)
      const index = items.value.findIndex(p => p.id === editingProduct.value.id)
      if (index !== -1) {
        items.value[index] = { ...editingProduct.value, ...res.data }
      }
      console.log('✅ Product updated successfully')
    } else {
      // Create product
      res = await api.post('products/', payload)
      items.value.push(res.data)
      console.log('✅ Product created successfully')
    }

    showModal.value = false
    editingProduct.value = null
    selectedItem.value = null
    alert(`✅ Product ${isUpdate ? 'updated' : 'created'} successfully`)
    await refresh()
  } catch (err) {
    console.error('❌ Error saving product:', err)
    
    let errorMessage = 'Failed to save product.'
    
    if (err.response) {
      const { status, data } = err.response
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
      } else if (status === 401) {
        errorMessage = 'Authentication failed. Please login again.'
      } else if (status === 403) {
        errorMessage = 'Permission denied. You do not have access to perform this action.'
      } else if (status >= 500) {
        errorMessage = 'Server error. Please try again later.'
      } else {
        errorMessage = `Error (${status}): ${data?.detail || data?.message || 'Unknown error'}`
      }
    } else if (err.request) {
      errorMessage = 'Network error. Please check your connection and try again.'
    } else {
      errorMessage = `Unexpected error: ${err.message}`
    }
    
    alert(errorMessage)
  } finally { 
    await nextTick();
    loading.value = false
  }
}

const editItem = async (item) => {
  if (!item) return
  editingProduct.value = item
  await fetchDropdownData()

  productForm.value = {
    name: item.name,
    sku: item.sku,
    barcode: item.barcode,
    category: item.category,
    variant: item.variant,
    unit: item.unit,
    price: item.price,
    cost_price: item.cost_price,
    discount: item.discount,
    stock: item.stock,
    min_stock: item.min_stock,
    supplier: item.supplier,
  }

  showModal.value = true
}

const deleteItem = async (item) => {
  if (!item) return
  if (!confirm(`Are you sure you want to delete "${item.name}"?`)) return

  try {
    console.log('🗑️ Deleting product:', item.id, item.name)
    await api.delete(`products/${item.id}/`)
    console.log('✅ Product deleted successfully')
    alert('✅ Product deleted successfully.')
    await refresh()
    selectedItem.value = null
  } catch (err) {
    console.error('❌ Failed to delete product:', err)
    let errorMessage = 'Failed to delete product.'
    
    if (err.response?.status === 400) {
      errorMessage = 'Cannot delete product. It may be referenced by other records.'
    } else if (err.response?.status === 404) {
      errorMessage = 'Product not found. It may have been already deleted.'
    } else if (err.response?.status >= 500) {
      errorMessage = 'Server error. Please try again later.'
    }
    
    alert(errorMessage)
  }
}

const loadProducts = async () => {
  try {
    console.log('🔄 Loading products...')
    const response = await api.get('products/')
    
    items.value = response.data.map(p => ({
      id: p.id,
      name: p.name,
      sku: p.sku,
      barcode: p.barcode,
      category: p.category,
      variant: p.variant,
      unit: p.unit,
      price: parseFloat(p.price) || 0,
      cost_price: parseFloat(p.cost_price) || 0,
      discount: parseFloat(p.discount) || 0,
      stock: parseInt(p.stock) || 0,
      min_stock: parseInt(p.min_stock) || 0,
      supplier: p.supplier,
      satuan: p.unit_name,
      kategori: p.category_name,
      supplier_name: p.supplier_name
    }))
    
    console.log(`✅ Loaded ${items.value.length} products`)
  } catch (err) {
    console.error('❌ Failed to load products:', err)
    throw err
  }
}

const refresh = async () => {
  try {
    await loadProducts()
  } catch (error) {
    console.error('Falha hafoun data:', error)
  }
}

</script>


<template>
  <div class="bg-white border border-gray-50 rounded-sm shadow text-sm flex flex-col h-full">
    <!-- Header -->
    <div class="flex items-center gap-2 p-2 border-b border-gray-300 bg-gray-50">
      <img
        :src="store.logo_base64 || getLogoUrl(store.logo)"
        @error="e => e.target.src = baseURL.replace('/api/', '') + '/media/logos/default.jpg'"
        class="h-6 w-6 rounded"
      />
      <h1 class="text-lg font-semibold">PRODUCT MANAGEMENT</h1>
    </div>

    <div class="p-4">
      <!-- Filters -->
      <div class="mb-6 flex flex-wrap items-center gap-4">
        <div class="form-group mb-0">
          <label class="block text-sm font-medium text-gray-700 mb-1">Search Products</label>
          <input 
            v-model="filter.nama" 
            class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
            placeholder="Search by product name..."
          />
        </div>
        <div class="form-group mb-0">
          <label class="block text-sm font-medium text-gray-700 mb-1">Barcode</label>
          <input 
            v-model="filter.barcode" 
            class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
            placeholder="Search by barcode..."
          />
        </div>
        <div class="form-group mb-0">
          <label class="block text-sm font-medium text-gray-700 mb-1">Category</label>
          <select v-model="filter.kategori" class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent">
            <option value="">All Categories</option>
            <option value="Food">Food</option>
            <option value="Snack">Snack</option>
            <option value="Drink">Drink</option>
          </select>
        </div>
        <div class="form-group mb-0">
          <label class="block text-sm font-medium text-gray-700 mb-1">Supplier</label>
          <input 
            v-model="filter.supplier" 
            class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
            placeholder="Search by supplier..."
          />
        </div>
        <button 
          @click="addItem" 
          class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          Add Product
        </button>
      </div>

      <!-- Products Table -->
      <div class="overflow-x-auto border border-gray-300 rounded-lg">
        <table class="w-full border-collapse text-sm">
          <thead class="bg-gray-50">
            <tr>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Product</th>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Category</th>
              <th class="border-b border-gray-200 px-4 py-3 text-right font-medium text-gray-700">Cost Price</th>
              <th class="border-b border-gray-200 px-4 py-3 text-right font-medium text-gray-700">Selling Price</th>
              <th class="border-b border-gray-200 px-4 py-3 text-right font-medium text-gray-700">Stock</th>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Unit</th>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Supplier</th>
              <th class="border-b border-gray-200 px-4 py-3 text-left font-medium text-gray-700">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="item in filteredItems" :key="item.id" class="hover:bg-gray-50" 
                :class="{ 'bg-blue-50': selectedItem?.id === item.id }"
                @click="selectedItem = item">
              <td class="px-4 py-3">
                <div>
                  <div class="font-medium text-gray-900">{{ item.name }}</div>
                  <div class="text-sm text-gray-500">{{ item.sku }} • {{ item.barcode || 'No barcode' }}</div>
                </div>
              </td>
              <td class="px-4 py-3 text-sm text-gray-900">{{ item.kategori || 'No category' }}</td>
              <td class="px-4 py-3 text-sm text-gray-900 text-right font-medium">{{ formatPrice(item.cost_price) }}</td>
              <td class="px-4 py-3 text-sm text-gray-900 text-right font-medium">{{ formatPrice(item.price) }}</td>
              <td class="px-4 py-3 text-sm text-right">
                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                      :class="item.stock > item.min_stock ? 'bg-green-100 text-green-800' : item.stock > 0 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'">
                  {{ item.stock ?? 0 }}
                </span>
              </td>
              <td class="px-4 py-3 text-sm text-gray-900">{{ item.satuan || 'No unit' }}</td>
              <td class="px-4 py-3 text-sm text-gray-900">{{ item.supplier_name || 'No supplier' }}</td>
              <td class="px-4 py-3">
                <div class="flex space-x-2">
                  <button 
                    @click="editItem(item)"
                    class="text-blue-600 hover:text-blue-900 transition-colors"
                    title="Edit Product"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                    </svg>
                  </button>
                  <button 
                    @click="deleteItem(item)"
                    class="text-red-600 hover:text-red-900 transition-colors"
                    title="Delete Product"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Product Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <!-- Header -->
        <div class="flex items-center justify-between p-6 border-b border-gray-200">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-xl font-semibold text-gray-900">
                {{ editingProduct ? 'Edit Product' : 'Add New Product' }}
              </h3>
              <p class="text-sm text-gray-500">
                {{ editingProduct ? 'Update product information' : 'Create a new product in inventory' }}
              </p>
            </div>
          </div>
          <button @click="showModal = false" class="text-gray-400 hover:text-gray-600 transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <!-- Form -->
        <form @submit.prevent="saveProduct" class="p-6">
          <!-- Basic Information -->
          <div class="mb-8">
            <h4 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <span class="w-7 h-7 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-semibold mr-3">1</span>
              Basic Information
            </h4>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Product Name -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Product Name *</label>
                <input 
                  v-model="productForm.name" 
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="Enter product name"
                  required
                />
                <p class="text-sm text-gray-500">Display name for the product</p>
              </div>

              <!-- SKU -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">SKU *</label>
                <input 
                  v-model="productForm.sku" 
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="e.g., PRD-001"
                  required
                />
                <p class="text-sm text-gray-500">Unique product identifier</p>
              </div>

              <!-- Barcode -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Barcode</label>
                <input 
                  v-model="productForm.barcode" 
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="Product barcode"
                />
                <p class="text-sm text-gray-500">Scannable barcode for POS</p>
              </div>

              <!-- Category -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Category</label>
                <select 
                  v-model="productForm.category" 
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                >
                  <option value="">Select Category</option>
                  <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
                </select>
                <p class="text-sm text-gray-500">Product category</p>
              </div>

              <!-- Variant -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Variant</label>
                <input 
                  v-model="productForm.variant" 
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="e.g., Large, Small, Red"
                />
                <p class="text-sm text-gray-500">Product variant or size</p>
              </div>

              <!-- Unit -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Unit</label>
                <select 
                  v-model="productForm.unit" 
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                >
                  <option value="">Select Unit</option>
                  <option v-for="u in units" :key="u.id" :value="u.id">{{ u.name }}</option>
                </select>
                <p class="text-sm text-gray-500">Unit of measurement</p>
              </div>
            </div>
          </div>

          <!-- Pricing Information -->
          <div class="mb-8">
            <h4 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <span class="w-7 h-7 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-semibold mr-3">2</span>
              Pricing Information
            </h4>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <!-- Cost Price -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Cost Price *</label>
                <input 
                  v-model="productForm.cost_price" 
                  type="text"
                  inputmode="decimal"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="0.00"
                  @focus="handleFocus('cost_price')"
                  @blur="formatDecimal('cost_price')"
                  required
                />
                <p class="text-sm text-gray-500">Purchase cost per unit</p>
              </div>

              <!-- Selling Price -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Selling Price *</label>
                <input 
                  v-model="productForm.price" 
                  type="text"
                  inputmode="decimal"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="0.00"
                  @focus="handleFocus('price')"
                  @blur="formatDecimal('price')"
                  required
                />
                <p class="text-sm text-gray-500">Retail price per unit</p>
              </div>

              <!-- Discount -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Discount</label>
                <input 
                  v-model="productForm.discount" 
                  type="text"
                  inputmode="decimal"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="0.00"
                  @focus="handleFocus('discount')"
                  @blur="formatDecimal('discount')"
                />
                <p class="text-sm text-gray-500">Discount amount</p>
              </div>
            </div>
          </div>

          <!-- Inventory Information -->
          <div class="mb-8">
            <h4 class="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <span class="w-7 h-7 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-semibold mr-3">3</span>
              Inventory Information
            </h4>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <!-- Stock Quantity -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Current Stock</label>
                <input 
                  v-model="productForm.stock" 
                  type="number"
                  min="0"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="0"
                />
                <p class="text-sm text-gray-500">Current inventory quantity</p>
              </div>

              <!-- Minimum Stock -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Minimum Stock</label>
                <input 
                  v-model="productForm.min_stock" 
                  type="number"
                  min="0"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                  placeholder="0"
                />
                <p class="text-sm text-gray-500">Minimum stock alert level</p>
              </div>

              <!-- Supplier -->
              <div class="space-y-1">
                <label class="block text-sm font-medium text-gray-700">Supplier</label>
                <select 
                  v-model="productForm.supplier" 
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                >
                  <option value="">Select Supplier</option>
                  <option v-for="s in suppliers" :key="s.id" :value="s.id">{{ s.name }}</option>
                </select>
                <p class="text-sm text-gray-500">Primary supplier</p>
              </div>
            </div>
          </div>

          <!-- Form Actions -->
          <div class="flex items-center justify-between pt-6 border-t border-gray-200">
            <button 
              type="button" 
              @click="showModal = false" 
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              :disabled="loading"
              class="px-6 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
            >
              <svg v-if="loading" class="w-4 h-4 mr-2 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
              <svg v-else class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"></path>
              </svg>
              {{ loading ? 'Saving...' : (editingProduct ? 'Update Product' : 'Create Product') }}
            </button>
          </div>
        </form>
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
.td-center { text-align: center; }

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