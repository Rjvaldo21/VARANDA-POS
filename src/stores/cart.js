import { defineStore } from 'pinia'

export const useCartStore = defineStore('cart', {
  state: () => ({
    items: JSON.parse(localStorage.getItem('cartItems') || '[]'),
    lastScannedProduct: null
  }),

  actions: {
    addItem(item) {
      const existing = this.items.find(p => p.id === item.id)
      if (existing) {
        existing.quantity += item.quantity
      } else {
        this.items.push(item)
      }
      this.lastScannedProduct = item
      this.saveToStorage()
    },

    removeItem(id) {
      this.items = this.items.filter(p => p.id !== id)
      this.saveToStorage()
    },

    clearCart() {
      this.items = []
      this.saveToStorage()
    },

    saveToStorage() {
      localStorage.setItem('cartItems', JSON.stringify(this.items))
    }
  },

  getters: {
    totalPrice(state) {
      return state.items.reduce((acc, p) => {
        const price = p.price ?? 0
        const quantity = p.quantity ?? 0
        const discountPercent = p.discount ?? 0
        const discountValue = price * (discountPercent / 100)
        const finalPrice = price - discountValue
        return acc + (finalPrice * quantity)
      }, 0)
    },

    itemsWithTotal: (state) => {
      return state.items.map(item => {
        const price = item.price ?? 0
        const discountPercent = item.discount ?? 0
        const quantity = item.quantity ?? 0
        const discountValue = price * (discountPercent / 100)
        const priceAfterDiscount = price - discountValue

        return {
          ...item,
          total: priceAfterDiscount * quantity,
          price_after_discount: priceAfterDiscount,
          discount_value: discountValue
        }
      })
    }
  }
})
