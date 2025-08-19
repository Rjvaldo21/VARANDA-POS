<script setup>
import { computed, onMounted, onBeforeUnmount } from 'vue'
import { useCartStore } from '@/stores/cart'

const cart = useCartStore()

const selectedProduct = computed(() => cart.lastScannedProduct || { name: '', price: null })

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2
  }).format(amount)
}

function clearPreview() {
  cart.lastScannedProduct = { name: '', price: null }
}

function handleKeyDown(e) {
  if (e.key === 'Delete' && e.shiftKey) {
    clearPreview()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})
onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeyDown)
})
</script>

<template>
  <div class="border p-3 rounded bg-white shadow h-24 flex flex-col justify-center">
    <p class="text-base font-semibold text-black leading-tight">
      {{ selectedProduct?.name || '' }}
    </p>
    <p class="text-xl font-bold text-black leading-tight">
      {{ selectedProduct?.price ? formatCurrency(selectedProduct.price) : '' }}
    </p>
  </div>
</template>
