<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { RouterLink } from 'vue-router'

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
    name: 'File',
    submenu: [
      { label: 'Konfigura', route: '/config' },

      { divider: true },

       { label: 'Importa / Exporta', action: 'modal', modal: 'importExport' },
      { label: 'Hafoun Database', action: 'modal', modal: 'resetDb' },

      { divider: true },

      { label: 'Logout', action: 'logout' }
    ]
  },
  {
    name: 'Administrasaun',
    submenu: [
      {
        label: 'Uzuariu',
        route: '/admin/users',
        group: 'main'
      },
      {
        label: 'Komputador Kasir',
        route: '/admin/komputador',
        group: 'main'
      },
      {
        divider: true
      },
      {
        label: 'Troka Password', action: 'modal', modal: 'password', group: 'secondary'
      }
    ]
  },

  {
  name: 'Inventóriu',
    submenu: [
      { label: 'Ketegoria', route: '/inventory/categories' },
      { label: 'Fornesedór', route: '/inventory/suppliers' },
      { label: 'Produtu', route: '/inventory/products' },

      { divider: true },

      { label: 'Lista Kliente', route: '/inventory/customers' },
      { label: 'Konfigura Pontos', route: '/inventory/points' },

      { divider: true },

      { label: 'Banku', route: '/inventory/banks' },
      { label: 'Unidade', route: '/inventory/units' }
    ]
  },
  {
    name: 'Tranzasaun',
    submenu: [
      { label: 'Kasir Ctrl D', route: '/pos' },
      { label: 'Retornu Fa\'an', route: '/sales/returns' },

      { divider: true },

      { label: 'Kompra', route: '/purchases' },
      { label: 'Retornu Kompra', route: '/purchases/returns' },

      { divider: true },

      { label: 'Hadia Stok', route: '/inventory/adjustment' }
    ]
  },
    {
    name: 'Relatóriu',
    submenu: [
      { label: 'Fa\'an', route: '/reports/sales' },
      { label: 'Produtu', route: '/reports/products' },

      { divider: true },

      { label: 'Tranzasaun', route: '/reports/transactions' },
      { label: 'Finansas', route: '/reports/finance' }
    ]
  },
  {
    name: 'Armazén',
    submenu: [
      { label: 'Lista Armazén', route: '/warehouse/list' },
      { label: 'Stok Armazén', route: '/warehouse/stock' },
      { label: 'Transferénsia Stok', route: '/warehouse/transfer' },
      { label: 'Movimentu Stok', route: '/warehouse/movements' }
    ]
  }
]

</script>


<template>
  <header class="w-full border-b border-gray-300 px-4 py-2 text-sm bg-white z-50 relative">
    <nav class="flex justify-between items-center w-full">
      <div class="flex space-x-0">
        <div
          class="relative"
          v-for="(menu, index) in menus"
          :key="index"
        >
          <div
            class="px-3 py-2 cursor-pointer text-center min-w-[80px] rounded-t"
            @click="toggleMenu(menu.name)"
          >
            {{ menu.name }}
          </div>
          <div
            v-if="activeMenu === menu.name"
            class="absolute left-0 mt-1 bg-white shadow-md border rounded-b text-sm z-50 w-48"
          >
            <ul>
              <template v-for="(sub, idx) in menu.submenu" :key="idx">
                  <li v-if="sub.divider">
                    <hr class="my-1 border-t border-gray-200" />
                  </li>

                  <li v-else-if="sub.action === 'logout'">
                    <button
                      @click="logout"
                      class="block w-full text-left px-4 py-2 hover:[background-color:#4359E2] hover:text-white whitespace-nowrap"
                    >
                      {{ sub.label }}
                    </button>
                  </li>

                  <li v-else-if="sub.action === 'modal'">
                    <button
                      @click="openModal(sub.modal)"
                      class="block w-full text-left px-4 py-2 hover:[background-color:#4359E2] hover:text-white whitespace-nowrap"
                    >
                      {{ sub.label }}
                    </button>
                  </li>

                  <li v-else>
                    <RouterLink
                      :to="sub.route || '#'"
                      class="block w-full px-4 py-2 hover:[background-color:#4359E2] hover:text-white whitespace-nowrap"
                      @click="activeMenu = null"
                    >
                      {{ sub.label }}
                    </RouterLink>
                  </li>
                </template>
              </ul>
            </div>
          </div>
        </div>
    </nav>
    <!-- Modal Popup -->
    <div
      v-if="showModal"
      class="fixed inset-0 z-[100] bg-black/40 flex items-center justify-center"
      @keydown.esc="closeModal"
    >
      <div class="bg-white w-full max-w-lg rounded shadow-lg border relative">
        <!-- Header -->
        <div class="px-4 py-3 border-b flex items-center justify-between">
          <h3 class="font-semibold">
            {{ modalType === 'password' ? 'Troka Password'
              : modalType === 'importExport' ? 'Importa / Exporta Baze-dadus'
              : modalType === 'resetDb' ? 'Hafoun Baze-dadus'
              : '' }}
          </h3>
          <button class="text-gray-500 hover:text-black" @click="closeModal">✖</button>
        </div>

        <!-- Body -->
        <div class="p-4 space-y-4">
          <!-- Troka Password -->
          <div v-if="modalType === 'password'" class="space-y-3">
            <div>
              <label class="text-sm">Password Atual</label>
              <input type="password" class="w-full border rounded px-3 py-2 mt-1" />
            </div>
            <div>
              <label class="text-sm">Password Foun</label>
              <input type="password" class="w-full border rounded px-3 py-2 mt-1" />
            </div>
            <div>
              <label class="text-sm">Konfirma Password Foun</label>
              <input type="password" class="w-full border rounded px-3 py-2 mt-1" />
            </div>
          </div>

          <!-- Import / Export DB -->
            <div v-else-if="modalType === 'importExport'" class="space-y-3">
              <p class="text-sm text-gray-600">
                Importa sei substitui Baze-dadus ho dados foun.
              </p>
              <p class="text-sm text-gray-600">
                Exporta sei dada Baze-dadus ho dados agora.
              </p>
              <div class="flex gap-2">
                <button class="px-4 py-2 border rounded hover:bg-gray-50">
                  ⬆️ Importa Baze-dadus
                </button>
                <button class="px-4 py-2 border rounded hover:bg-gray-50">
                  ⬇️ Exporta Baze-dadus
                </button>
              </div>
            </div>

            <!-- Reset DB -->
            <div v-else-if="modalType === 'resetDb'" class="space-y-3">
              <p class="text-sm text-red-600">
                Atensaun: Aksaun ne’e sei <b>hafoun</b> Baze-dadus. ita iha serteza?
              </p>
            </div>
          </div>

      <!-- Footer -->
        <div class="px-4 py-3 border-t flex justify-end gap-2">
          <button class="px-3 py-1 rounded border hover:bg-gray-50" @click="closeModal">
            Kansela
          </button>
          <button
            v-if="modalType === 'password'"
            class="px-3 py-1 rounded bg-blue-600 text-white hover:bg-blue-700"
            @click="/* TODO: submit ganti password */ closeModal()"
          >
            Rai
          </button>
          <button
            v-else-if="modalType === 'importExport'"
            class="px-3 py-1 rounded bg-blue-600 text-white hover:bg-blue-700"
            @click="closeModal"
          >
            Ok
          </button>
          <button
            v-else-if="modalType === 'resetDb'"
            class="px-3 py-1 rounded bg-red-600 text-white hover:bg-red-700"
            @click="/* TODO: konfirmasi reset */ closeModal()"
          >
            Hafoun Agora
          </button>
        </div>
      </div>
    </div>
  </header>
</template>