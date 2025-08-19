<template>
  <div class="fixed inset-0 bg-black bg-opacity-30 flex justify-center items-center z-50">
    <div class="bg-white p-6 rounded-lg shadow-md w-[450px] relative">
      <!-- Tombol X -->
      <button
        class="absolute top-2 right-3 text-gray-500 hover:text-red-500 text-3xl font-bold"
        @click="$emit('close')"
      >
        ×
      </button>

      <h2 class="text-xl font-bold mb-4 text-center">🆘 Ajuda Kasir</h2>

      <!-- Tabela Ajuda -->
      <table class="w-full text-sm border border-gray-200">
        <thead>
          <tr class="bg-gray-100 text-left">
            <th class="px-2 py-1 border border-gray-200 w-[120px]">Tecla</th>
            <th class="px-2 py-1 border border-gray-200">Funsaun</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="px-2 py-1 border border-gray-200"><strong>F1</strong></td>
            <td class="px-2 py-1 border border-gray-200">Ajuda</td>
          </tr>
          <tr>
            <td class="px-2 py-1 border border-gray-200"><strong>Enter</strong></td>
            <td class="px-2 py-1 border border-gray-200">Foka ba input barcode</td>
          </tr>
          <tr>
            <td class="px-2 py-1 border border-gray-200"><strong>↑ / ↓</strong></td>
            <td class="px-2 py-1 border border-gray-200">Navega entre produtu sira iha karosa</td>
          </tr>
          <tr>
            <td class="px-2 py-1 border border-gray-200"><strong>Delete</strong></td>
            <td class="px-2 py-1 border border-gray-200">Hamo'os produtu nebe maka ita hili</td>
          </tr>
          <tr>
            <td class="px-2 py-1 border border-gray-200"><strong>Ctrl + Delete</strong></td>
            <td class="px-2 py-1 border border-gray-200">Halakon produtu sira hotu iha karosa</td>
          </tr>
          <tr>
            <td class="px-2 py-1 border border-gray-200"><strong>Ctrl + M</strong></td>
            <td class="px-2 py-1 border border-gray-200">Buka kliente</td>
          </tr>
          <tr>
            <td class="px-2 py-1 border border-gray-200"><strong>Ctrl + D</strong></td>
            <td class="px-2 py-1 border border-gray-200">Hamos kliente</td>
          </tr>
          <tr>
            <td class="px-2 py-1 border border-gray-200"><strong>Shift + Delete</strong></td>
            <td class="px-2 py-1 border border-gray-200">Hamos produtu preview</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

