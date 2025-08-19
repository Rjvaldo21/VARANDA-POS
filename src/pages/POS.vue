<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useCartStore } from '@/stores/cart'
import StoreHeader from '@/components/pos/StoreHeader.vue'
import TotalBox from '@/components/pos/TotalBox.vue'
import CartTable from '@/components/pos/CartTable.vue'
import BarcodeInput from '@/components/pos/BarcodeInput.vue'
import ProductPreview from '@/components/pos/ProductPreview.vue'
import FooterActions from '@/components/pos/FooterActions.vue'
import PaymentModal from '@/components/pos/PaymentModal.vue'
import HelpModal from '@/components/pos/HelpModal.vue'
import CustomerModal from '@/components/CustomerModal.vue'
import AlertModal from '@/components/AlertModal.vue'

const showPaymentModal = ref(false)
const barcodeInputRef = ref(null)
const cart = useCartStore()
const showHelpModal = ref(false)

const showAlert = ref(false)
const alertMessage = ref('')

const selectedCustomer = ref(null)
const showCustomerModal = ref(false)

const setCustomer = (customer) => {
  selectedCustomer.value = customer
}

function handleAlert(msg) {
  alertMessage.value = msg
  showAlert.value = true
}

// <===========================>

const props = defineProps({
  focusBarcode: Function,
  onConfirm: Function 
})

const alertTitle = ref('')
const isConfirm = ref(false)
const onConfirmCallback = ref(null)

function showInfo(message) {
  alertTitle.value = ''
  alertMessage.value = message
  isConfirm.value = false
  showAlert.value = true
}

function showConfirm(message, onConfirm) {
  alertTitle.value = ''
  alertMessage.value = message
  isConfirm.value = true
  onConfirmCallback.value = onConfirm
  showAlert.value = true
}

// <===========================>

function handleKeyEvents(e) {
  console.log('🧪 Keyboard Event:', e.key, 'Ctrl:', e.ctrlKey)

    if (e.ctrlKey && e.key.toLowerCase() === 'd') {
    e.preventDefault()
    selectedCustomer.value = null
  }

  if (e.key === 'F5' || (e.ctrlKey && e.key.toLowerCase() === 'r')) {
    e.preventDefault()
  }

  if (e.key === 'F1') {
    e.preventDefault()
    showHelpModal.value = true
  }

  if (e.ctrlKey && e.key.toLowerCase() === 'm') {
    e.preventDefault()
    console.log('✅ Ctrl + M ditekan')
    showCustomerModal.value = true
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyEvents)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyEvents)
})

defineOptions({ inheritAttrs: false })

function handleSeluClick() {
    if (cart.items.length === 0) {
    showInfo('Favor hatama ka scan produtu antes klik selu.')
    return
  }
  showPaymentModal.value = true
}

</script>

<template>
  <div class="w-full min-w-[800px] min-h-[600px] h-screen flex flex-col bg-gray-50">
    <!-- Wrapper untuk POS layout -->
    <div class="flex flex-col flex-1 overflow-hidden">
      <div class="flex px-4 py-2 gap-4">
        <div class="flex-1">
          <StoreHeader />
        </div>
        <div class="max-w-sm w-full">
          <TotalBox />
        </div>
      </div>

      <div class="flex-1 flex flex-col px-4 pb-2 overflow-hidden">
        <div class="flex-1 overflow-y-auto border mb-2">
          <CartTable
            :focusBarcode="() => barcodeInputRef.value?.focus()"
            :onConfirm="showConfirm"
          />
        </div>

        <div class="flex flex-col md:flex-row gap-2 border border-gray-300 p-2 bg-white">
          <div class="md:w-1/4 text-xs leading-tight border-r pr-2">
            <p><em>Membru</em> Kliente</p>
            <p class="ml-4"><em>Naran</em>: {{ selectedCustomer?.name || 'Mamuk' }}</p>
            <p class="ml-4"><em>Pontus</em>: {{ selectedCustomer?.points || 0 }}</p>
            <hr class="my-2" />
            <p>F1 : Ajuda</p>
          </div>

          <div class="flex-1 flex flex-col gap-2">
            <BarcodeInput
              ref="barcodeInputRef"
              :onError="handleAlert"
            />
            <ProductPreview />
          </div>

          <div class="md:w-32 w-full">
            <AlertModal
              :show="showAlert"
              :message="alertMessage"
              :title="alertTitle"
              :isConfirm="isConfirm"
              @close="showAlert = false"
              @cancel="showAlert = false"
              @confirm="onConfirmCallback?.(); showAlert = false"
            />
            <button
              class="w-full h-full border border-gray-300 bg-gradient-to-b from-white to-gray-100 hover:bg-gray-200 text-xs"
              @click="handleSeluClick"
            >
              Selu
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Modals -->
    <PaymentModal
      :show="showPaymentModal"
      :selectedCustomer="selectedCustomer"
      @close="showPaymentModal = false"
      @clear-customer="selectedCustomer = null"
    />
    <HelpModal :show="showHelpModal" @close="showHelpModal = false" v-if="showHelpModal" />
    <CustomerModal :show="showCustomerModal" @selected="setCustomer" @close="showCustomerModal = false" />
    </div>
  <FooterActions />
</template>

