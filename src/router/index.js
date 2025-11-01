import { createRouter, createWebHistory } from 'vue-router'
import authManager from '@/utils/authManager.js'
import POS from '../pages/POS.vue'
import Konfigura from '@/pages/Konfigura.vue'
import CustomerScreen from '../pages/CustomerScreen.vue'
import Products from '../pages/Products.vue'
import Reports from '../pages/Reports.vue'
import Login from '@/components/Login.vue'
import Administrasaun from '../pages/Administrasaun.vue'
import KomputadorKasir from '@/pages/KomputadorKasir.vue'
import Kategoria from '@/pages/Kategoria.vue'
import Supplier from '@/pages/IventoriuSupplier.vue'
import Produk from '@/pages/IventoriuProdutu.vue'
import ListaKliente from '@/pages/IventoriuListaKliente.vue'
import KonfiguraPontos from '@/pages/KonfiguraPontos.vue'
import Banku from '@/pages/Banku.vue'
import Unidade from '@/pages/IventoriuUnidade.vue'
import TranzasaunRetornuFaan from '@/pages/TranzasaunRetornuFaan.vue'
import Kompra from '@/pages/TranzasaunKompra.vue'
import TranzasaunRetornuKompra from '@/pages/TranzasaunRetornuKompra.vue'
import HadiaStok from '@/pages/InventoriuHadiaStok.vue'
import RelatoriuFaan from '@/pages/RelatoriuFaan.vue'
import RelatoriuProdutu from '@/pages/RelatoriuProdutu.vue'
import RelatoriuTranzasaun from '@/pages/RelatoriuTranzasaun.vue'
import RelatoriuFinansas from '@/pages/RelatoriuFinansas.vue'
import WarehouseList from '@/pages/WarehouseList.vue'
import WarehouseStock from '@/pages/WarehouseStock.vue'
import StockTransfer from '@/pages/StockTransfer.vue'
import StockMovements from '@/pages/StockMovementHistory.vue'
import ImportData from '@/pages/ImportData.vue'


const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login },
  { path: '/pos', component: POS },
  { path: '/cashier', component: POS }, 
  { path: '/customer', name: 'Customer', component: CustomerScreen }, 
  { path: '/admin', component: POS },
  { path: '/inventory', component: POS },
  { path: '/transactions', component: POS },
  { path: '/reports', component: Reports },
  { path: '/help', component: POS },
  { path: '/config', component: Konfigura },
  { path: '/admin/users', component: Administrasaun },
  { path: '/admin/komputador', component: KomputadorKasir },
  { path: '/inventory/categories', component: Kategoria },
  { path: '/inventory/suppliers', component: Supplier },
  { path: '/inventory/products', component: Produk },
  { path: '/inventory/customers', component: ListaKliente },
  { path: '/inventory/points', component: KonfiguraPontos },
  { path: '/inventory/banks', component: Banku },
  { path: '/inventory/units', component: Unidade },

  { path: '/sales/returns', component: TranzasaunRetornuFaan },
  { path: '/purchases', component: Kompra },
  { path: '/purchases/returns', component: TranzasaunRetornuKompra },
  { path: '/inventory/adjustment', component: HadiaStok },

  { path: '/reports/sales', component: RelatoriuFaan },
  { path: '/reports/products', component: RelatoriuProdutu },
  { path: '/reports/transactions', component: RelatoriuTranzasaun },
  { path: '/reports/finance', component: RelatoriuFinansas },
  { path: '/warehouse/list', component: WarehouseList },
  { path: '/warehouse/stock', component: WarehouseStock },
  { path: '/warehouse/transfer', component: StockTransfer },
  { path: '/warehouse/movements', component: StockMovements },
  
  { path: '/import', component: ImportData },

  // { path: '/help/about', component: Konaba },
  // { path: '/help/vue', component: KonabaVue },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  // Use enhanced AuthManager for input-safe navigation
  const isWindowsElectron = window.electronAPI && navigator.platform.includes('Win')
  
  if (isWindowsElectron) {
    // Use AuthManager's enhanced route guard
    authManager.beforeRouteEnter(to, from, next)
  } else {
    // Standard auth check for non-Windows platforms
    const token = localStorage.getItem('token')
    
    if (to.path === '/login' && token) {
      next('/pos')
    }
    else if (to.path !== '/login' && !token) {
      next('/login')
    }
    else {
      next()
    }
  }
})

// Windows Electron Fix: Re-enable inputs after route navigation
router.afterEach((to, from) => {
  const isWindowsElectron = window.electronAPI && navigator.platform.includes('Win')
  
  if (isWindowsElectron) {
    // Multiple timing strategies to ensure inputs are enabled
    setTimeout(() => {
      const inputs = document.querySelectorAll('input, textarea, select, button')
      inputs.forEach(input => {
        if (!input.hasAttribute('data-keep-disabled')) {
          input.removeAttribute('disabled')
          input.style.pointerEvents = 'auto'
          input.style.userSelect = 'text'
          input.style.webkitUserSelect = 'text'
          input.tabIndex = input.tabIndex || 0
          
          if (input.type === 'button' || input.type === 'submit') {
            input.style.cursor = 'pointer'
          }
        }
      })
      console.log('🔓 Router afterEach: Re-enabled inputs after navigation', {
        from: from.path,
        to: to.path,
        inputCount: inputs.length
      })
    }, 100)
    
    // Additional fallback timing
    setTimeout(() => {
      const inputs = document.querySelectorAll('input:disabled, textarea:disabled, select:disabled')
      if (inputs.length > 0) {
        inputs.forEach(input => {
          if (!input.hasAttribute('data-keep-disabled')) {
            input.removeAttribute('disabled')
            input.style.pointerEvents = 'auto'
          }
        })
        console.log('🔓 Router afterEach: Fallback re-enabled', inputs.length, 'disabled inputs')
      }
    }, 300)
  }
})

export default router
