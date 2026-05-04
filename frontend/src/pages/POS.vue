<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white border-b sticky top-0 z-10">
      <div class="flex items-center justify-between px-6 py-4">
        <div class="flex items-center gap-4">
          <router-link to="/" class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <FeatherIcon name="arrow-left" class="w-5 h-5 text-gray-600" />
          </router-link>
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center">
              <FeatherIcon name="shopping-cart" class="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 class="text-xl font-bold text-gray-900">POS</h1>
              <p class="text-xs text-gray-500">Point of Sale</p>
            </div>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <Badge :label="'Online'" color="green" />
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <div class="flex h-[calc(100vh-73px)]">
      <!-- Left: Item Selector -->
      <div class="flex-1 flex flex-col p-6 overflow-hidden">
        <!-- Search Bar -->
        <div class="mb-4">
          <div class="relative">
            <FeatherIcon name="search" class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              v-model="searchQuery"
              @input="onSearchInput"
              type="text"
              placeholder="Search items by name, code, or brand..."
              class="w-full pl-10 pr-4 py-3 border rounded-xl focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none text-sm"
            />
          </div>
        </div>

        <!-- Items Grid -->
        <div class="flex-1 overflow-y-auto">
          <div v-if="displayedItems.length === 0" class="text-center py-12 text-gray-500">
            <FeatherIcon name="package" class="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p>No items found</p>
          </div>
          <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
            <button
              v-for="item in displayedItems"
              :key="item.name"
              @click="selectItem(item)"
              :class="[
                'p-3 rounded-xl border text-left transition-all hover:shadow-md relative',
                cart.find(i => i.name === item.name)
                  ? 'border-green-500 bg-green-50 ring-2 ring-green-200'
                  : 'border-gray-200 bg-white hover:border-green-300'
              ]"
            >
              <div v-if="cart.find(i => i.name === item.name)" class="absolute top-2 right-2 w-5 h-5 bg-green-500 text-white rounded-full text-xs flex items-center justify-center font-bold">
                {{ cart.find(i => i.name === item.name).qty }}
              </div>
              <div class="w-full h-24 bg-gray-100 rounded-lg mb-2 flex items-center justify-center overflow-hidden">
                <FeatherIcon name="package" class="w-8 h-8 text-gray-400" />
              </div>
              <p class="text-xs font-medium text-gray-900 truncate">{{ item.item_name || item.name }}</p>
              <p class="text-xs text-gray-500 truncate">{{ item.item_code }}</p>
              <p class="text-sm font-bold text-green-600 mt-1">{{ formatCurrency(item.standard_rate) }}</p>
            </button>
          </div>
        </div>
      </div>

      <!-- Right: Cart -->
      <div class="w-96 bg-white border-l flex flex-col">
        <div class="p-4 border-b flex items-center justify-between">
          <h2 class="font-semibold text-gray-900">Cart</h2>
          <span v-if="cart.length > 0" class="text-xs bg-gray-100 px-2 py-1 rounded-lg text-gray-600">{{ cart.length }} items</span>
        </div>

        <!-- Empty Cart -->
        <div v-if="cart.length === 0" class="flex-1 flex items-center justify-center text-gray-400 p-6">
          <div class="text-center">
            <FeatherIcon name="shopping-cart" class="w-12 h-12 mx-auto mb-3" />
            <p class="text-sm">Click an item to add to cart</p>
          </div>
        </div>

        <!-- Cart Items -->
        <div v-else class="flex-1 overflow-y-auto px-4 pt-2 pb-4 space-y-2">
          <div class="flex items-center gap-2 px-2 pb-1 text-xs font-semibold text-gray-500 border-b">
            <span class="w-4"></span>
            <span class="flex-1">Name</span>
            <span class="shrink-0 w-10 text-center">Qty</span>
            <span class="shrink-0 w-16 text-right">Price</span>
          </div>
          <div
            v-for="(item, index) in cart"
            :key="item.name"
            class="flex items-center gap-2 p-2 border rounded-lg"
          >
            <button
              @click="removeFromCart(index)"
              class="shrink-0 p-0.5 text-gray-400 hover:text-red-500"
            >
              <FeatherIcon name="x" class="w-3 h-3" />
            </button>
            <p class="flex-1 text-xs font-semibold text-gray-900 truncate min-w-0">{{ item.item_name || item.name }}</p>
            <input
              :value="item.qty"
              @input="e => updateQty(index, parseInt(e.target.value) || 1)"
              type="number"
              min="1"
              class="shrink-0 w-10 text-center text-xs text-gray-700 bg-transparent focus:outline-none"
            />
            <input
              :value="item.standard_rate"
              @input="e => updateRate(index, parseFloat(e.target.value) || 0)"
              type="number"
              step="0.01"
              min="0"
              class="shrink-0 w-16 text-right text-xs text-green-600 font-bold bg-transparent focus:outline-none"
            />
          </div>
        </div>

        <!-- Cart Summary & Checkout -->
        <div class="border-t p-4 bg-gray-50 space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-600">Subtotal</span>
            <span class="text-lg font-bold text-gray-900">{{ formatCurrency(cartTotal) }}</span>
          </div>
          <button
            @click="checkout"
            class="w-full py-3 bg-gray-900 text-white rounded-xl font-medium hover:bg-gray-800 transition-colors"
          >
            Checkout
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Badge, FeatherIcon } from 'frappe-ui'

export default {
  name: 'POS',
  components: {
    Badge,
    FeatherIcon,
  },
  data() {
    return {
      searchQuery: '',
      cart: [],
      items: [],
      searchTimeout: null,
    }
  },
  computed: {
    filteredItems() {
      if (!this.searchQuery) return this.items
      const q = this.searchQuery.toLowerCase()
      return this.items.filter(item =>
        (item.item_name || item.name).toLowerCase().includes(q) ||
        (item.item_code || '').toLowerCase().includes(q) ||
        (item.brand || '').toLowerCase().includes(q)
      )
    },
    displayedItems() {
      // Cap at 50 to prevent browser freeze; search shows all matches
      return this.filteredItems.slice(0, 50)
    },
    cartTotal() {
      return this.cart.reduce((sum, item) => sum + ((item.standard_rate || 0) * item.qty), 0)
    },
  },
  mounted() {
    this.fetchItems()
  },
  methods: {
    async fetchItems(search = '') {
      try {
        const filters = { disabled: 0, is_sales_item: 1 }
        if (search) {
          filters.item_name = ['like', '%' + search + '%']
        }

        const response = await fetch('/api/method/frappe.client.get_list', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({
            doctype: 'Item',
            fields: ['name', 'item_name', 'item_code', 'brand', 'item_group', 'standard_rate', 'stock_uom'],
            filters: filters,
            limit_page_length: 0,
          }),
        })
        const data = await response.json()
        if (data.message) {
          this.items = data.message.map(item => ({ ...item, stock: 0 }))
          this.fetchStock()
        }
      } catch (error) {
        console.error('Failed to fetch items:', error)
      }
    },
    onSearchInput() {
      // Client-side filtering via computed property; no server call needed
      clearTimeout(this.searchTimeout)
    },
    async fetchStock() {
      // Fetch stock quantities for items
      try {
        const itemNames = this.items.map(i => i.name)
        if (itemNames.length === 0) return

        const response = await fetch('/api/method/frappe.client.get_list', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({
            doctype: 'Bin',
            fields: ['item_code', 'actual_qty'],
            filters: { item_code: ['in', itemNames] },
            limit_page_length: 500,
          }),
        })
        const data = await response.json()
        if (data.message) {
          const stockMap = {}
          data.message.forEach(bin => {
            stockMap[bin.item_code] = (stockMap[bin.item_code] || 0) + (bin.actual_qty || 0)
          })
          this.items = this.items.map(item => ({
            ...item,
            stock: stockMap[item.name] || 0,
          }))
        }
      } catch (error) {
        console.error('Failed to fetch stock:', error)
      }
    },
    selectItem(item) {
      // Add item to cart directly on click (qty 1)
      const existing = this.cart.find(i => i.name === item.name)
      if (existing) {
        existing.qty += 1
      } else {
        this.cart.push({ ...item, qty: 1 })
      }
    },
    removeFromCart(index) {
      this.cart.splice(index, 1)
    },
    updateQty(index, newQty) {
      if (newQty < 1) return
      this.cart[index].qty = newQty
    },
    updateRate(index, newRate) {
      if (newRate < 0) return
      this.cart[index].standard_rate = newRate
    },
    checkout() {
      console.log('Checkout:', this.cart)
      // TODO: Create POS Invoice via Frappe API
      this.cart = []
    },
    formatCurrency(value) {
      if (!value) return '0.00 DA'
      return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }).format(value) + ' DA'
    },
  },
}
</script>
