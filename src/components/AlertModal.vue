<template>
  <div
    v-if="show"
    class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50"
  >
    <div class="bg-white w-[360px] max-w-full rounded-xl p-6 shadow-lg border border-gray-200 text-center">
      <h2 class="text-lg font-semibold text-gray-800 mb-3">
        {{ title || (isConfirm ? '❓ Konfirma' : '⚠️ Atenasaun') }}
      </h2>

      <p class="text-sm text-gray-700 whitespace-pre-line">{{ message }}</p>

      <div class="mt-6 flex justify-center gap-4">
        <button
          v-if="isConfirm"
          @click="$emit('cancel')"
          class="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded"
        >
          Kansela
        </button>

        <button
          @click="() => isConfirm ? $emit('confirm') : $emit('close')"
          class="px-4 py-2 bg-[#4359E2] text-white hover:bg-[#3a4ecc] rounded"
        >
          OK
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  show: Boolean,
  message: String,
  title: String,
  isConfirm: Boolean
})

defineEmits(['close', 'confirm', 'cancel'])
</script>

