<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useCartStore } from '@/stores/cart'
import { formatCurrency } from '@/utils/format'

const cart = useCartStore()
const items = computed(() => cart.itemsWithTotal)

const selectedId = ref(null)
const selectedIndex = ref(-1)

function removeItem(id) {
  cart.removeItem(id)
}

function clearCart() {
  cart.clearCart()
  selectedId.value = null
  selectedIndex.value = -1
}

function preventInvalidQty(e) {
  const allowedKeys = ['ArrowLeft', 'ArrowRight', 'Tab']
  const isValidNumber = /^[1-9]$/.test(e.key)

  if (!isValidNumber && !allowedKeys.includes(e.key)) {
    e.preventDefault()
  }
}

function handleQtyInput(item) {
  const qty = Number(item.quantity)

  if (!qty || isNaN(qty) || qty < 1) {
    item.quantity = 1
  }

  updateQuantity(item.id, item.quantity)
}

function handleQtyBlur(item) {
  if (!item.quantity || item.quantity < 1) {
    item.quantity = 1
  }
}

const props = defineProps({
  focusBarcode: Function,
  onConfirm: Function
})

const handleKeydown = (event) => {
    if (event.ctrlKey && event.key === 'Delete') {
    event.preventDefault()
    props.onConfirm?.('Hamoos sasán hotu iha karosa?', clearCart)
    return
  }

  if (event.key === 'Delete' && selectedId.value) {
    removeItem(selectedId.value)
    selectedId.value = null
    selectedIndex.value = -1
  }

  if (event.key === 'Enter') {
    props.focusBarcode?.()
  }

  if (event.key === 'ArrowDown' && selectedIndex.value < items.value.length - 1) {
    selectedIndex.value++
    selectedId.value = items.value[selectedIndex.value]?.id || null
  }

  if (event.key === 'ArrowUp' && selectedIndex.value > 0) {
    selectedIndex.value--
    selectedId.value = items.value[selectedIndex.value]?.id || null
  }
}

function selectRow(item, index) {
  selectedId.value = item.id
  selectedIndex.value = index
}

function updateQuantity(id, newQty) {
  const item = cart.items.find(i => i.id === id)
  if (item) {
    item.quantity = newQty
    cart.saveToStorage?.()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})
onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <div class="overflow-x-auto">
    <table class="min-w-full text-sm border border-gray-300 border-collapse table-fixed">
      <thead class="bg-gray-100">
        <tr>
          <th class="px-2 py-1 text-center w-[40px] border border-gray-300">Nu</th>
          <th class="px-2 py-1 text-center w-[180px] border border-gray-300">Barcode</th>
          <th class="px-2 py-1 text-center border border-gray-300">Naran</th>
          <th class="px-2 py-1 text-center w-[60px] border border-gray-300">Qty</th>
          <th class="px-2 py-1 text-center w-[80px] border border-gray-300">Unidade</th>
          <th class="px-2 py-1 text-center w-[100px] border border-gray-300">Presu</th>
          <th class="px-2 py-1 text-center w-[100px] border border-gray-300">Diskontu</th>
          <th class="px-2 py-1 text-center w-[100px] border border-gray-300">Total</th>
        </tr>
        </thead>
          <tbody>
          <tr
            v-for="(item, index) in items"
            :key="item.id"
            tabindex="0"
            :class="[ 
              'cursor-pointer focus:outline-none',
              selectedId === item.id ? 'bg-[#4359E2] text-white' : ''
            ]"
            @click="selectRow(item, index)"
          >
          <td class="px-2 py-1 text-center border border-gray-300 w-[40px]">{{ index + 1 }}</td>
          <td class="px-2 py-1 text-center border border-gray-300 w-[180px]">{{ item.barcode }}</td>
          <td class="px-2 py-1 text-left border border-gray-300">{{ item.name }}</td>
          <td class="px-2 py-1 text-center border border-gray-300">
          <input
            type="number"
            min="1"
            v-model.number="item.quantity"
            @keydown="preventInvalidQty"
            @input="handleQtyInput(item)"
            @blur="handleQtyBlur(item)"
            @click.stop
            @select.prevent
            @contextmenu.prevent
            @paste.prevent
            class="w-full text-center text-sm bg-transparent text-black focus:outline-none focus:ring-0 focus:border-none selection:bg-blue-600 selection:text-white"
            style="appearance: textfield;"
          />
          </td>
          <td class="px-2 py-1 text-center border border-gray-300">{{ item.unit }}</td>
          <td class="px-2 py-1 text-center border border-gray-300">{{ formatCurrency(item.price || 0) }}</td>
          <td class="px-2 py-1 text-center border border-gray-300">{{ item.discount }}%</td>
          <td class="px-2 py-1 text-center border border-gray-300">
          {{ formatCurrency(item.price * item.quantity * (1 - (item.discount || 0) / 100)) }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>







