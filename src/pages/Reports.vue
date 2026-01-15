<template>
  <div class="bg-white rounded-lg shadow p-6">
    <h2 class="text-2xl font-bold mb-6">📊 Laporan</h2>
    
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <router-link to="/relatoriu-finansas" class="block p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
            <span class="text-blue-600 text-xl">💰</span>
          </div>
          <div>
            <h3 class="font-semibold">Financial Report</h3>
            <p class="text-sm text-gray-600">View financial entries and summaries</p>
          </div>
        </div>
      </router-link>

      <router-link to="/relatoriu-tranzasaun" class="block p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
            <span class="text-green-600 text-xl">📊</span>
          </div>
          <div>
            <h3 class="font-semibold">Transaction Report</h3>
            <p class="text-sm text-gray-600">Track income, expenses, and profit/loss</p>
          </div>
        </div>
      </router-link>

      <router-link to="/relatoriu-produtu" class="block p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
            <span class="text-purple-600 text-xl">📦</span>
          </div>
          <div>
            <h3 class="font-semibold">Product Sales Report</h3>
            <p class="text-sm text-gray-600">Item-wise sales analysis</p>
          </div>
        </div>
      </router-link>

      <router-link to="/relatoriu-faan" class="block p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-orange-100 rounded-full flex items-center justify-center">
            <span class="text-orange-600 text-xl">🛒</span>
          </div>
          <div>
            <h3 class="font-semibold">Sales Report</h3>
            <p class="text-sm text-gray-600">Detailed sales analytics with charts</p>
          </div>
        </div>
      </router-link>

      <router-link to="/import" class="block p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center">
            <span class="text-indigo-600 text-xl">📥</span>
          </div>
          <div>
            <h3 class="font-semibold">Import Data</h3>
            <p class="text-sm text-gray-600">Import products, customers, suppliers, and categories</p>
          </div>
        </div>
      </router-link>
    </div>
  </div>
</template>
