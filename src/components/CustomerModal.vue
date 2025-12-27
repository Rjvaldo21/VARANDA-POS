<script setup>
import { ref, watch, computed } from 'vue'

const props = defineProps({
  show: Boolean
})
const emit = defineEmits(['close', 'selected'])

const searchQuery = ref('')
const customers = ref([])
const loading = ref(false)

const filteredCustomers = computed(() => {
  return customers.value.filter(c =>
    c.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const searchCustomers = async () => {
  loading.value = true 
  await nextTick()
  try {
    const res = await api.get('/customers/')
    customers.value = res.data
  } catch (err) {
    console.error('Falha buka kliente:', err)
  }
  loading.value = false
}

function selectCustomer(customer) {
  emit('selected', customer)
  emit('close')
}

watch(() => props.show, val => {
  if (val) {
    searchQuery.value = ''
    searchCustomers()
  }
})
</script>

<style scoped>
input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 1px #3b82f6;
}
</style>

<template>
  <div v-if="show" class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
    <div class="bg-white w-full max-w-md p-6 rounded-lg shadow-lg relative">
      
      <button
        class="absolute top-2 right-3 text-gray-500 hover:text-red-500 text-3xl font-extrabold leading-none"
        @click="$emit('close')"
        aria-label="Close"
      >
        ×
      </button>

      <h2 class="text-lg font-bold mb-4 text-left">Naran Kliente</h2>

      <input
        v-model="searchQuery"
        @input="searchCustomers"
        type="text"
        placeholder="Buka kliente..."
        class="w-full border px-3 py-2 mb-4 rounded focus:outline-none focus:ring focus:ring-blue-200"
      />

      <ul v-if="searchQuery.trim().length > 0">
        <li
          v-for="customer in filteredCustomers"
          :key="customer.id"
          @click="selectCustomer(customer)"
          class="px-3 py-2 hover:bg-blue-100 cursor-pointer border-b"
        >
          <strong>{{ customer.name }}</strong>
          <p class="text-sm text-gray-600">Pontus: {{ customer.points }}</p>
        </li>
      </ul>

      <div v-if="loading" class="text-center text-sm text-gray-500 mt-2">
        Prosesu... buka dadus kliente
      </div>
    </div>
  </div>
</template>


