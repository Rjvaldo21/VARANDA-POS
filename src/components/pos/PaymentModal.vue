<script setup>
import { ref, watch, computed, onMounted } from 'vue'
import api from '@/axios'
import { useCartStore } from '@/stores/cart'
import { formatCurrency } from '@/utils/format'

const props = defineProps({
  show: Boolean,
  selectedCustomer: Object
})
const emit = defineEmits(['close', 'clear-customer'])

/* =========================
 * Cart & helpers
 * ========================= */
const cart = useCartStore()
const discount = ref(0)
const toFixedFloat = (value) => parseFloat(Number(value || 0).toFixed(2))
const subtotal = computed(() => toFixedFloat((cart.totalPrice || 0) - (discount.value || 0)))

/* =========================
 * Payment method selector
 * ========================= */
const method = ref('cash') // 'cash' | 'transfer' | 'credit' | 'qris'

/* =========================
 * Cash input (tetap seperti sebelumnya)
 * ========================= */
const cashReceived = ref(0)
const cashInputRaw = ref('$0.00')
const inputRef = ref(null)
const onCashInput = (e) => {
  let raw = e.target.value.replace(/[^0-9.]/g, '')
  const parts = raw.split('.')
  if (parts.length > 2) raw = parts[0] + '.' + parts[1]
  raw = raw.replace(/^(\d+)\.(\d{0,2}).*$/, '$1.$2')
  cashInputRaw.value = raw ? `$${raw}` : '$'
  e.target.value = cashInputRaw.value
  const parsed = parseFloat(raw)
  cashReceived.value = isNaN(parsed) ? 0 : parsed
}
const onCashBlur = () => { cashInputRaw.value = formatCurrency(cashReceived.value) }
const change = computed(() => {
  const received = toFixedFloat(cashReceived.value)
  return received > subtotal.value ? toFixedFloat(received - subtotal.value) : 0
})
const isCashValid = computed(() => cashReceived.value > 0)
const isCashEnough = computed(() => toFixedFloat(cashReceived.value) >= subtotal.value)

/* =========================
 * Banks & fee preview (baru)
 * ========================= */
const banks = ref([])
const selectedBankId = ref(null)
const selectedBank = computed(() => banks.value.find(b => b.id === selectedBankId.value) || null)

function computeBankPreview(amount, bank) {
  if (!bank) return { fee: 0, gross: amount, net: amount, fee_paid_by_customer: true }
  const pct = Number(bank.percent_fee || 0) / 100
  let fee = amount * pct + Number(bank.fixed_fee || 0)
  const min = Number(bank.min_fee || 0), max = Number(bank.max_fee || 0)
  if (min > 0 && fee < min) fee = min
  if (max > 0 && fee > max) fee = max
  const byCustomer = !!bank.fee_paid_by_customer
  const gross = byCustomer ? amount + fee : amount
  const net   = byCustomer ? gross - fee : amount - fee
  return {
    fee: toFixedFloat(fee),
    gross: toFixedFloat(gross),
    net: toFixedFloat(net),
    fee_paid_by_customer: byCustomer
  }
}
const bankPreview = computed(() => computeBankPreview(subtotal.value, selectedBank.value))

async function fetchBanks() {
  const res = await api.get('/banks/')
  // filter sesuai metode dipilih
  banks.value = (res.data || []).filter(b => {
    if (!b.is_active) return false
    if (method.value === 'transfer') return b.enable_transfer
    if (method.value === 'credit')   return b.enable_credit
    if (method.value === 'qris')     return b.enable_qris
    return false
  })
  // auto pilih pertama jika kosong
  if (banks.value.length && !selectedBankId.value) {
    selectedBankId.value = banks.value[0].id
  }
}

/* =========================
 * Lifecycle
 * ========================= */
const loading = ref(false)
const loadingQRIS = ref(false)

watch(() => props.show, (val) => {
  if (val) {
    // reset state saat modal dibuka
    method.value = 'cash'
    discount.value = 0
    cashReceived.value = 0
    cashInputRaw.value = formatCurrency(0)
    setTimeout(() => inputRef.value?.focus(), 100)
  }
})

watch(method, async (m) => {
  // saat ganti metode → muat bank jika perlu
  if (m !== 'cash') {
    await fetchBanks()
  }
})

/* =========================
 * Helpers umum
 * ========================= */
const withCustomer = (payload) =>
  (props.selectedCustomer?.id
    ? { ...payload, customer: props.selectedCustomer.id }
    : payload)

const openReceipt = async (transactionId) => {
  const url = `${import.meta.env.VITE_API_URL}/api/receipt/html/${transactionId}/`
  const iframe = document.getElementById('print-frame')
  if (!iframe) return
  iframe.onload = () => {
    setTimeout(() => {
      iframe.contentWindow.focus()
      iframe.contentWindow.print()
    }, 500)
  }
  iframe.src = url
}

const cancel = () => {
  emit('close')
  emit('clear-customer')
}

/* =========================
 * Actions per-metode
 * ========================= */
const payWithQRIS = async () => {
  if (loadingQRIS.value) return
  loadingQRIS.value = true
  try {
    const invoiceId = 'INV' + Date.now()
    const basePayload = {
      invoice_id: invoiceId,
      total: subtotal.value, // bisa juga gross jika mau fee by customer di QRIS (kalau diterapkan)
      payment_method: 'qris',
      items: cart.items.map(item => ({
        product: item.id,
        quantity: item.quantity,
        price: item.price
      }))
    }
    const payload = withCustomer(basePayload)
    await api.post('/transactions/', payload)

    // Simulasi QRIS (placeholder)
    localStorage.setItem('qrisPayment', JSON.stringify({
      invoice: invoiceId,
      total: subtotal.value,
      qrisUrl: `https://qris.merchant-server.tl/${invoiceId}`
    }))

    emit('clear-customer'); emit('close')
    alert('Favor haree QRIS iha tela customer.')
  } catch (err) {
    console.error('Tranzasaun Falha:', err.response?.data || err.message)
    alert('❌ Error Tranzasaun:\n' + JSON.stringify(err.response?.data || err.message, null, 2))
  } finally {
    loadingQRIS.value = false
  }
}

const confirmPayment = async () => {
  // Cash flow lama tetap
  if (method.value === 'cash') {
    if (loading.value) return
    loading.value = true
    try {
      const invoiceId = 'INV' + Date.now()
      const basePayload = {
        invoice_id: invoiceId,
        total: subtotal.value,
        payment_method: 'cash',
        amount_paid: toFixedFloat(cashReceived.value),
        items: cart.items.map(item => ({
          product: item.id,
          quantity: item.quantity,
          price: item.price
        }))
      }
      const payload = withCustomer(basePayload)
      const res = await api.post('/transactions/', payload)
      openReceipt(res.data.id)
      cart.clearCart(); emit('close'); emit('clear-customer')
      alert('Tranzasaun Susesu!')
    } catch (err) {
      console.error('Tranzasaun Falha:', err.response?.data || err.message)
      alert('❌ Error Tranzasaun:\n' + JSON.stringify(err.response?.data || err.message, null, 2))
    } finally {
      loading.value = false
    }
    return
  }

  // Bank (transfer/credit)
  if (method.value === 'transfer' || method.value === 'credit') {
    if (!selectedBank.value) {
      alert('Favor hili banku lai.')
      return
    }
    if (loading.value) return
    loading.value = true
    try {
      const invoiceId = 'INV' + Date.now()
      // Jika fee dibayar customer → total transaksi = gross
      // Jika fee ditanggung toko → total = subtotal
      const totalForTransaction = selectedBank.value.fee_paid_by_customer
        ? bankPreview.value.gross
        : subtotal.value

      // 1) Buat transaksi
      const basePayload = {
        invoice_id: invoiceId,
        total: totalForTransaction,
        payment_method: method.value, // 'transfer' atau 'credit'
        items: cart.items.map(item => ({
          product: item.id,
          quantity: item.quantity,
          price: item.price
        }))
      }
      const payload = withCustomer(basePayload)
      const trxRes = await api.post('/transactions/', payload)
      const trxId = trxRes.data.id

      // 2) Catat Bank Payment (status pending; proof nanti di verifikasi)
      await api.post('/bank-payments/', {
        transaction: trxId,
        bank: selectedBank.value.id,
        gross_amount: String(bankPreview.value.gross.toFixed(2)),
        status: 'pending'
      })

      openReceipt(trxId)
      cart.clearCart(); emit('close'); emit('clear-customer')
      alert('Tranzasaun Banku susesu! Status: pending')
    } catch (err) {
      console.error('Tranzasaun Falha:', err.response?.data || err.message)
      alert('❌ Error Tranzasaun:\n' + JSON.stringify(err.response?.data || err.message, null, 2))
    } finally {
      loading.value = false
    }
  }
}
</script>

<template>
  <div
    v-if="show"
    class="fixed inset-0 bg-black bg-opacity-30 flex justify-center items-center z-50 select-none"
    @contextmenu.prevent
  >
    <div class="relative bg-white px-6 py-5 w-[28rem] rounded-[15px] shadow-lg border border-gray-300">
      <button
        class="absolute top-2 right-3 text-gray-500 hover:text-red-500 text-3xl font-bold"
        @click="cancel"
        aria-label="Close"
      >×</button>

      <!-- TOTAL -->
      <div class="mb-2 text-center">
        <p class="text-2xl font-bold text-green-700">
          {{ formatCurrency(subtotal) }}
        </p>
      </div>

      <!-- Selector metode -->
      <div class="mb-3 flex flex-wrap gap-4 text-sm">
        <label class="inline-flex items-center gap-2">
          <input type="radio" value="cash" v-model="method"> Cash
        </label>
        <label class="inline-flex items-center gap-2">
          <input type="radio" value="transfer" v-model="method"> Banku
        </label>
        <label class="inline-flex items-center gap-2">
          <input type="radio" value="credit" v-model="method"> Kreditu
        </label>
        <label class="inline-flex items-center gap-2">
          <input type="radio" value="qris" v-model="method"> QRIS
        </label>
      </div>

      <!-- CASH -->
      <div v-if="method==='cash'" class="mb-3">
        <label class="block text-sm font-medium mb-1">Montante Osan</label>
        <input
          ref="inputRef"
          :value="cashInputRaw"
          @input="onCashInput"
          @blur="onCashBlur"
          @keyup.enter.prevent="isCashValid && isCashEnough && confirmPayment()"
          class="w-full border px-3 py-2 text-sm rounded focus:outline-none focus:ring focus:ring-blue-200"
          type="text"
        />
        <div class="mt-3 text-right">
          <p class="text-sm text-gray-600">Troka / Osan Volta</p>
          <p class="text-xl font-semibold text-blue-600">{{ formatCurrency(change) }}</p>
        </div>
      </div>

      <!-- BANK (Transfer/Credit) -->
      <div v-if="method==='transfer' || method==='credit'" class="mb-4 space-y-3">
        <div>
          <label class="block text-sm font-medium mb-1">Bank *</label>
          <select
            class="w-full border px-2 py-2 rounded text-sm"
            v-model.number="selectedBankId"
          >
            <option :value="null" disabled>Hili banku…</option>
            <option v-for="b in banks" :key="b.id" :value="b.id">
              {{ b.name }} ({{ b.code || '—' }})
            </option>
          </select>
        </div>

        <div v-if="selectedBank" class="grid grid-cols-2 gap-3 text-sm bg-gray-50 p-3 rounded border">
          <div>
            <div class="text-gray-600">Percent fee</div>
            <div class="font-semibold">{{ Number(selectedBank.percent_fee||0).toFixed(2) }}%</div>
          </div>
          <div>
            <div class="text-gray-600">Fixed fee</div>
            <div class="font-semibold">{{ Number(selectedBank.fixed_fee||0).toFixed(2) }}</div>
          </div>
          <div>
            <div class="text-gray-600">Fee dibayar oleh</div>
            <div class="font-semibold">{{ selectedBank.fee_paid_by_customer ? 'Pelanggan' : 'Toko' }}</div>
          </div>
          <div>
            <div class="text-gray-600">Status</div>
            <div class="font-semibold">pending</div>
          </div>

          <div class="col-span-2 border-t pt-2 grid grid-cols-3 gap-3 text-center">
            <div>
              <div class="text-gray-600">Gross</div>
              <div class="font-semibold">{{ formatCurrency(bankPreview.gross) }}</div>
            </div>
            <div>
              <div class="text-gray-600">Fee</div>
              <div class="font-semibold">{{ formatCurrency(bankPreview.fee) }}</div>
            </div>
            <div>
              <div class="text-gray-600">Net</div>
              <div class="font-semibold">{{ formatCurrency(bankPreview.net) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer actions -->
      <div class="flex justify-end gap-2">
        <button @click="cancel" class="text-sm px-4 py-1 border rounded hover:bg-gray-100">Kansela</button>

        <!-- QRIS tetap (seperti sebelumnya) -->
        <button
          v-if="method==='qris'"
          @click="payWithQRIS"
          :disabled="loadingQRIS"
          class="text-sm px-4 py-1 border border-blue-400 bg-gradient-to-b from-white to-blue-100 hover:bg-blue-200 rounded text-blue-800 flex items-center gap-2 justify-center"
          :class="{ 'opacity-50 cursor-not-allowed': loadingQRIS }"
        >
          <span v-if="loadingQRIS" class="animate-spin h-4 w-4 border-t-2 border-blue-600 rounded-full"></span>
          <span>{{ loadingQRIS ? 'QRIS...' : 'QRIS' }}</span>
        </button>

        <!-- Cash: tombol Selu lama -->
        <button
          v-if="method==='cash'"
          @click="confirmPayment"
          :disabled="!isCashValid || !isCashEnough || loading"
          class="text-sm px-4 py-1 border border-gray-300 bg-gradient-to-b from-white to-gray-200 hover:bg-gray-300 rounded flex items-center gap-2 justify-center"
          :class="{ 'opacity-50 cursor-not-allowed': !isCashValid || !isCashEnough || loading }"
        >
          <span v-if="loading" class="animate-spin h-4 w-4 border-t-2 border-gray-600 rounded-full"></span>
          <span>{{ loading ? 'Proses...' : 'Selu' }}</span>
        </button>

        <!-- Bank: tombol baru -->
        <button
          v-if="method==='transfer' || method==='credit'"
          @click="confirmPayment"
          :disabled="loading || !selectedBank"
          class="text-sm px-4 py-1 border border-emerald-300 bg-gradient-to-b from-white to-emerald-100 hover:bg-emerald-200 rounded text-emerald-800 flex items-center gap-2 justify-center"
          :class="{ 'opacity-50 cursor-not-allowed': loading || !selectedBank }"
        >
          <span v-if="loading" class="animate-spin h-4 w-4 border-t-2 border-emerald-600 rounded-full"></span>
          <span>{{ loading ? 'Proses...' : 'Selu Banku' }}</span>
        </button>
      </div>
    </div>
  </div>

  <iframe id="print-frame" style="display: none;"></iframe>
</template>
