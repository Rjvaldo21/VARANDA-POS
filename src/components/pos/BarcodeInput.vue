<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useCartStore } from '@/stores/cart'

const props = defineProps(['onError'])
const barcode = ref('')
const cart = useCartStore()

async function searchProduct(barcode) {
  const res = await axios.get(`/api/products/?barcode=${barcode}`)
  return res.data
}

const fetchProduct = async () => {
  const trimmed = barcode.value.trim()
  if (!trimmed) {
    props.onError?.('Favor scan ka hatama uluk barcode.')
    return
  }

  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/products/?barcode=${trimmed}`)
    const product = response.data

    cart.addItem({
      id: product.id,
      name: product.name,
      barcode: product.sku,
      price: parseFloat(product.price),
      quantity: 1,
      discount: parseFloat(product.discount) || 0,
      unit: product.unit || 'pcs',
      price_after_discount: parseFloat(product.price_after_discount) || parseFloat(product.price)
    })

    barcode.value = ''
  } catch (error) {
    console.error('Produtu la hetan:', error)
    props.onError?.('⚠️ Produtu la hetan.')
  }
}
</script>

<template>
  <input
    v-model="barcode"
    type="text"
    placeholder="Scan Barcode"
    @keyup.enter="fetchProduct"
    class="w-full h-11 px-3 py-2 border border-gray-300 rounded text-sm 
    focus:outline-none focus:ring-0 focus:border-gray-300"
  />
</template>