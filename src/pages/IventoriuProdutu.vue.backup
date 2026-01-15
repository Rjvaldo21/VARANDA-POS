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

const showModal = ref(false)

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
  const token = localStorage.getItem('token')
  try {
    const [catRes, unitRes, supRes] = await Promise.all([
      axios.get('http://localhost:8000/api/categories/', { headers: { Authorization: `Bearer ${token}` }}),
      axios.get('http://localhost:8000/api/units/', { headers: { Authorization: `Bearer ${token}` }}),
      axios.get('http://localhost:8000/api/suppliers/', { headers: { Authorization: `Bearer ${token}` }})
    ])
    categories.value = catRes.data
    units.value = unitRes.data
    suppliers.value = supRes.data
  } catch (err) {
    console.error('❌ Gagal ambil data dropdown:', err)
  }
}

const addItem = async () => {
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
    const response = await axios.get('http://127.0.0.1:8000/api/products/', {
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
  const token = localStorage.getItem('token')

  // 🛡️ Validasi field wajib
  if (
    !productForm.value.name ||
    !productForm.value.sku ||
    !productForm.value.price ||
    !productForm.value.cost_price
  ) {
    alert('❗ Mohon isi semua field wajib: Naran, SKU, Presu Kompra, Presu Fa\'an.')
    return
  }

  try {
    const payload = {
      name: productForm.value.name,
      sku: productForm.value.sku,
      barcode: productForm.value.barcode,
      category: productForm.value.category,
      variant: productForm.value.variant,
      unit: productForm.value.unit,
      price: parseFloat(productForm.value.price),
      cost_price: parseFloat(productForm.value.cost_price),
      discount: parseFloat(productForm.value.discount),
      stock: productForm.value.stock,
      min_stock: productForm.value.min_stock,
      supplier: productForm.value.supplier
    }

    const res = await axios.post('http://127.0.0.1:8000/api/products/', payload, {
      headers: { Authorization: `Bearer ${token}` }
    })

    console.log('✅ Produk berhasil disimpan:', res.data)
    showModal.value = false
    selectedItem.value = null // ✅ reset jika sebelumnya edit
    refresh()
  } catch (err) {
    console.error('❌ Gagal menyimpan produk:', err)
    if (err.response && err.response.data) {
      alert('Gagal simpan produk:\n' + JSON.stringify(err.response.data, null, 2))
    } else {
      alert('Gagal menyimpan produk. Coba cek data atau koneksi.')
    }
  }
}

const editItem = async (item) => {
  if (!item) return
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
  if (!confirm(`Ita-boot iha serteza hakarak atu hamoos? ${item.name}?`)) return

  const token = localStorage.getItem('token')
  try {
    await axios.delete(`http://localhost:8000/api/products/${item.id}/`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    alert('✅ Produtu halakon ho susesu.')
    refresh()
    selectedItem.value = null
  } catch (err) {
    console.error('❌ Falha halakon produtu:', err)
    alert('Akontese erru bainhira halakon produtu.')
  }
}

const loadProducts = async () => {
  const token = localStorage.getItem('token')
  const response = await axios.get('http://127.0.0.1:8000/api/products/', {
    headers: { Authorization: `Bearer ${token}` }
  })

  items.value = response.data.map(p => ({
    id: p.id,
    name: p.name,
    sku: p.sku,
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
        @error="e => e.target.src = 'http://127.0.0.1:8000/media/logos/default.jpg'"
        class="h-6 w-6 rounded"
      />
      <h1 class="text-lg font-semibold">PRODUTU</h1>
    </div>

    <!-- Table + Filter -->
    <div class="p-2 flex flex-col flex-1 overflow-hidden">
      <div class="flex-1 overflow-x-auto border border-gray-300 rounded-sm scrollbar-stable">
        <table class="w-auto max-w-none min-w-[1000px] lg:min-w-[1200px] xl:min-w-0 border-collapse text-sm table-fixed">
          <colgroup>
            <col style="width:14%" /> 
            <col style="width:22%" /> 
            <col style="width:12%" /> 
            <col style="width:12%" /> 
            <col style="width:9%"  /> 
            <col style="width:9%"  /> 
            <col style="width:12%" /> 
            <col style="width:20%" />
          </colgroup>

          <thead class="bg-gradient-to-b from-white to-gray-100">
            <!-- Header Row -->
            <tr>
              <th class="th text-left">Barcode</th>
              <th class="th text-left">Naran</th>
              <th class="th text-right">Presu Kompra</th>
              <th class="th text-right">Presu Fa'an</th>
              <th class="th text-right">Stok</th>
              <th class="th text-center">Unidade</th>
              <th class="th text-left">Kategoria</th>
              <th class="th text-left">Supplier</th>
            </tr>

            <tr>
              <th class="th">
                <input v-model="filter.barcode" type="text" placeholder="Barcode" class="f-input" />
              </th>
              <th class="th">
                <input v-model="filter.nama" type="text" placeholder="Naran" class="f-input" />
              </th>
              <th colspan="2" class="th text-center text-gray-400">Presu</th>
              <th colspan="2" class="th text-center text-gray-400">Stok</th>
              <th class="th">
                <select v-model="filter.kategori" class="f-input">
                  <option value="">-- Hili Kategoria --</option>
                  <option>Food</option>
                  <option>Snack</option>
                  <option>Drink</option>
                </select>
              </th>
              <th class="th">
                <input v-model="filter.supplier" type="text" placeholder="Supplier" class="f-input" />
              </th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="item in filteredItems"
              :key="item.barcode"
              class="hover:bg-gray-50 cursor-pointer"
              @click="selectedItem = item"
              :class="{ 'bg-blue-50': selectedItem?.sku === item.sku }"
            >
              <td class="td"      :title="item.barcode">{{ item.barcode || '-' }}</td>
              <td class="td"      :title="item.name">{{ item.name || '-' }}</td>
              <td class="td td-num">{{ formatPrice(item.cost_price) }}</td>
              <td class="td td-num">{{ formatPrice(item.price) }}</td>
              <td class="td td-num">{{ item.stock ?? 0 }}</td>
              <td class="td td-center">{{ item.satuan || '-' }}</td>
              <td class="td"      :title="item.kategori">{{ item.kategori || '-' }}</td>
              <td class="td"      :title="item.supplier_name">{{ item.supplier_name || '-' }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Modal Form -->
      <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-40 z-50 flex items-center justify-center">
        <div class="bg-white rounded shadow-md p-4 w-[400px]">
          <h2 class="text-lg font-semibold mb-2">Formuláriu Produtu</h2>

          <div class="space-y-2 text-sm">
            <input v-model="productForm.name" placeholder="Naran *" class="w-full border px-2 py-1 rounded-sm" />
            <input v-model="productForm.sku" placeholder="SKU *" class="w-full border px-2 py-1 rounded-sm" />
            <input v-model="productForm.barcode" placeholder="Barcode" class="w-full border px-2 py-1 rounded-sm" />

            <select v-model="productForm.category" class="w-full border px-2 py-1 rounded-sm">
              <option value="">-- Kategoria --</option>
              <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>

            <input v-model="productForm.variant" placeholder="Variant" class="w-full border px-2 py-1 rounded-sm" />

            <select v-model="productForm.unit" class="w-full border px-2 py-1 rounded-sm">
              <option value="">-- Unidade --</option>
              <option v-for="u in units" :key="u.id" :value="u.id">{{ u.name }}</option>
            </select>

          <input
              v-model="productForm.price"
              type="text"
              inputmode="decimal"
              placeholder="Presu Fa'an *"
              class="w-full border px-2 py-1 rounded-sm"
              @focus="handleFocus('price')"
              @blur="formatDecimal('price')"
            />
                        <input
              v-model="productForm.cost_price"
              type="text"
              inputmode="decimal"
              placeholder="Presu Kompra *"
              class="w-full border px-2 py-1 rounded-sm"
              @focus="handleFocus('cost_price')"
              @blur="formatDecimal('cost_price')"
            />
                        <input
              v-model="productForm.discount"
              type="text"
              inputmode="decimal"
              placeholder="Diskontu"
              class="w-full border px-2 py-1 rounded-sm"
              @focus="handleFocus('discount')"
              @blur="formatDecimal('discount')"
            />
            <input v-model="productForm.stock" type="number" placeholder="Stok" class="w-full border px-2 py-1 rounded-sm" />
            <input v-model="productForm.min_stock" type="number" placeholder="Stok Minimum" class="w-full border px-2 py-1 rounded-sm" />
            <select v-model="productForm.supplier" class="w-full border px-2 py-1 rounded-sm">
            <option value="">-- Fornesedór --</option>
            <option v-for="s in suppliers" :key="s.id" :value="s.id">{{ s.name }}</option>
          </select>
        </div>

          <div class="mt-4 flex justify-end gap-2 text-sm">
            <button @click="showModal = false" class="px-3 py-1 bg-gray-200 hover:bg-gray-300 rounded">Taka</button>
            <button @click="saveProduct" class="px-3 py-1 bg-blue-600 text-white hover:bg-blue-700 rounded">Rai</button>
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
          <button @click="addItem" class="hover:text-green-600">➕</button>
          <button
            @click="editItem(selectedItem)"
            :disabled="!selectedItem"
            class="hover:text-gray-600"
          >
            ✏️
          </button>
          <button
            @click="deleteItem(selectedItem)"
            :disabled="!selectedItem"
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