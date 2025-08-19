<script setup>
import { useCartStore } from '@/stores/cart'
import { formatCurrency } from '@/utils/format'

const cart = useCartStore()
</script>

<template>
  <div class="bg-white h-[80px] md:h-[100px] px-3 md:px-4 py-2 md:py-3 border rounded shadow w-full flex flex-col justify-between">
    <div class="flex justify-between text-sm md:text-base font-normal text-black">
      <span>Total</span>
    </div>
    <div class="flex justify-end">
      <p class="text-2xl md:text-3xl font-normal text-black leading-none">
        {{ formatCurrency(cart.totalPrice) }}
      </p>
    </div>
  </div>
</template>






