<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'
import LanguageSwitcher from './LanguageSwitcher.vue'

const { t } = useI18n()

const activeMenu = ref(null)

const toggleMenu = (menuName) => {
  activeMenu.value = activeMenu.value === menuName ? null : menuName
}

const router = useRouter()
// === Modal state ===
const showModal = ref(false)
const modalType = ref(null) // 'password' | 'importExport' | 'resetDb'

const openModal = (type) => {
  modalType.value = type
  showModal.value = true
  activeMenu.value = null // tutup dropdown saat modal dibuka
}
const closeModal = () => {
  showModal.value = false
  modalType.value = null
}


const logout = () => {
  localStorage.removeItem('token')  
  activeMenu.value = null
  router.push('/login')             
}

const menus = [
  {
    name: t('navigation.file'),
    submenu: [
      { label: t('navigation.configuration'), route: '/config' },

      { divider: true },

       { label: t('navigation.importExport'), action: 'modal', modal: 'importExport' },
      { label: t('navigation.resetDatabase'), action: 'modal', modal: 'resetDb' },

      { divider: true },

      { label: t('navigation.logout'), action: 'logout' }
    ]
  },
  {
    name: t('navigation.administration'),
    submenu: [
      {
        label: t('navigation.users'),
        route: '/admin/users',
        group: 'main'
      },
      {
        label: t('navigation.cashierStation'),
        route: '/admin/komputador',
        group: 'main'
      },
      {
        divider: true
      },
      {
        label: t('navigation.changePassword'), action: 'modal', modal: 'password', group: 'secondary'
      }
    ]
  },

  {
  name: t('navigation.inventory'),
    submenu: [
      { label: t('navigation.categories'), route: '/inventory/categories' },
      { label: t('navigation.suppliers'), route: '/inventory/suppliers' },
      { label: t('navigation.products'), route: '/inventory/products' },

      { divider: true },

      { label: t('navigation.customers'), route: '/inventory/customers' },
      { label: t('navigation.loyaltyPoints'), route: '/inventory/points' },

      { divider: true },

      { label: t('navigation.banks'), route: '/inventory/banks' },
      { label: t('navigation.units'), route: '/inventory/units' }
    ]
  },
  {
    name: t('navigation.transactions'),
    submenu: [
      { label: t('navigation.pos'), route: '/pos' },
      { label: t('navigation.salesReturns'), route: '/sales/returns' },

      { divider: true },

      { label: t('navigation.purchases'), route: '/purchases' },
      { label: t('navigation.purchaseReturns'), route: '/purchases/returns' },

      { divider: true },

      { label: t('navigation.stockAdjustment'), route: '/inventory/adjustment' }
    ]
  },
    {
    name: t('navigation.reports'),
    submenu: [
      { label: t('navigation.salesReport'), route: '/reports/sales' },
      { label: t('navigation.productReport'), route: '/reports/products' },

      { divider: true },

      { label: t('navigation.transactionReport'), route: '/reports/transactions' },
      { label: t('navigation.financeReport'), route: '/reports/finance' }
    ]
  },
  {
    name: t('navigation.warehouse'),
    submenu: [
      { label: t('navigation.warehouseList'), route: '/warehouse/list' },
      { label: t('navigation.warehouseStock'), route: '/warehouse/stock' },
      { label: t('navigation.stockTransfer'), route: '/warehouse/transfer' },
      { label: t('navigation.stockMovements'), route: '/warehouse/movements' }
    ]
  }
]

</script>


<template>
  <header class="header">
    <nav class="header-nav flex justify-between items-center w-full">
      <div class="flex space-x-0">
        <div
          class="relative"
          v-for="(menu, index) in menus"
          :key="index"
        >
          <button
            class="btn btn-secondary"
            :class="{ 'btn-primary': activeMenu === menu.name }"
            @click="toggleMenu(menu.name)"
          >
            {{ menu.name }}
          </button>
          <div
            v-if="activeMenu === menu.name"
            class="absolute left-0 top-full mt-1 bg-white shadow-lg border border-gray-200 rounded-lg text-sm z-50 w-56 py-2"
          >
            <ul>
              <template v-for="(sub, idx) in menu.submenu" :key="idx">
                  <li v-if="sub.divider">
                    <hr class="my-2 border-t border-gray-200" />
                  </li>

                  <li v-else-if="sub.action === 'logout'">
                    <button
                      @click="logout"
                      class="block w-full text-left px-4 py-2 hover:bg-gray-100 rounded-md mx-2 transition-colors duration-150"
                    >
                      <svg class="inline-block w-4 h-4 mr-2 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
                      </svg>
                      {{ sub.label }}
                    </button>
                  </li>

                  <li v-else-if="sub.action === 'modal'">
                    <button
                      @click="openModal(sub.modal)"
                      class="block w-full text-left px-4 py-2 hover:bg-gray-100 rounded-md mx-2 transition-colors duration-150"
                    >
                      <svg class="inline-block w-4 h-4 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                      </svg>
                      {{ sub.label }}
                    </button>
                  </li>

                  <li v-else>
                    <RouterLink
                      :to="sub.route || '#'"
                      class="block w-full px-4 py-2 hover:bg-gray-100 rounded-md mx-2 transition-colors duration-150 flex items-center"
                      :class="{ 'bg-blue-50 text-blue-700': $route.path === sub.route }"
                      @click="activeMenu = null"
                    >
                      <svg class="inline-block w-4 h-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                      </svg>
                      {{ sub.label }}
                    </RouterLink>
                  </li>
                </template>
              </ul>
            </div>
          </div>
        </div>
      <!-- Language Switcher -->
      <div class="ml-4">
        <LanguageSwitcher />
      </div>
    </nav>
    <!-- Modal Popup -->
    <div
      v-if="showModal"
      class="modal-overlay"
      @click.self="closeModal"
      @keydown.esc="closeModal"
    >
      <div class="modal-content w-full max-w-lg">
        <!-- Header -->
        <div class="card-header flex items-center justify-between">
          <h3 class="font-semibold text-lg text-gray-800">
            {{ modalType === 'password' ? t('navigation.changePassword')
              : modalType === 'importExport' ? t('navigation.importExport')
              : modalType === 'resetDb' ? t('navigation.resetDatabase')
              : '' }}
          </h3>
          <button 
            class="text-gray-400 hover:text-gray-600 p-1 rounded-full hover:bg-gray-100 transition-colors" 
            @click="closeModal"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <!-- Body -->
        <div class="card-body space-y-4">
          <!-- Change Password -->
          <div v-if="modalType === 'password'" class="space-y-4">
            <div class="form-group">
              <label class="form-label">{{ t('auth.currentPassword') }}</label>
              <input type="password" class="form-control" :placeholder="t('auth.enterCurrentPassword')" />
            </div>
            <div class="form-group">
              <label class="form-label">{{ t('auth.newPassword') }}</label>
              <input type="password" class="form-control" :placeholder="t('auth.enterNewPassword')" />
            </div>
            <div class="form-group">
              <label class="form-label">{{ t('auth.confirmPassword') }}</label>
              <input type="password" class="form-control" :placeholder="t('auth.confirmNewPassword')" />
            </div>
          </div>

          <!-- Import / Export DB -->
            <div v-else-if="modalType === 'importExport'" class="space-y-3">
              <p class="text-sm text-gray-600">
                {{ t('settings.importWarning') }}
              </p>
              <p class="text-sm text-gray-600">
                {{ t('settings.exportInfo') }}
              </p>
              <div class="flex gap-3">
                <button class="btn btn-secondary flex items-center">
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"></path>
                  </svg>
                  {{ t('settings.importDatabase') }}
                </button>
                <button class="btn btn-primary flex items-center">
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                  </svg>
                  {{ t('settings.exportDatabase') }}
                </button>
              </div>
            </div>

            <!-- Reset DB -->
            <div v-else-if="modalType === 'resetDb'" class="space-y-3">
              <p class="text-sm text-red-600">
                {{ t('settings.resetWarning') }}
              </p>
            </div>
          </div>

      <!-- Footer -->
        <div class="card-footer flex justify-end gap-3">
          <button class="btn btn-secondary" @click="closeModal">
            {{ t('common.cancel') }}
          </button>
          <button
            v-if="modalType === 'password'"
            class="btn btn-primary"
            @click="/* TODO: submit ganti password */ closeModal()"
          >
            {{ t('common.save') }}
          </button>
          <button
            v-else-if="modalType === 'importExport'"
            class="btn btn-primary"
            @click="closeModal"
          >
            {{ t('common.confirm') }}
          </button>
          <button
            v-else-if="modalType === 'resetDb'"
            class="btn btn-danger"
            @click="/* TODO: konfirmasi reset */ closeModal()"
          >
            {{ t('settings.resetNow') }}
          </button>
        </div>
      </div>
    </div>
  </header>
</template>