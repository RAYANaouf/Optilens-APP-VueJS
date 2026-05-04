<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Main Content -->
    <div class="flex h-screen">
      <!-- Left: Item Selector -->
      <div class="flex-1 flex flex-col p-6 overflow-hidden">
        <!-- Search Bar -->
        <div class="mb-6">
          <div class="relative group">
            <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <FeatherIcon 
                name="search" 
                class="w-5 h-5 text-gray-400 group-focus-within:text-green-500 transition-colors" 
              />
            </div>
            <input
              id="item-search"
              v-model="searchQuery"
              @input="onSearchInput"
              type="text"
              placeholder="Search items by name, code, or brand..."
              class="w-full pl-11 pr-4 py-3.5 bg-white border-none rounded-2xl shadow-sm ring-1 ring-gray-200 focus:ring-2 focus:ring-green-500 focus:shadow-md outline-none text-sm transition-all placeholder:text-gray-400"
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

      <!-- Right: Orders Panel -->
      <div class="w-96 bg-white m-4 rounded-2xl shadow-lg border flex flex-col overflow-hidden">
        <!-- Multi-Order Tabs -->
        <div class="flex items-center gap-1 p-2 bg-gray-50 border-b overflow-x-auto no-scrollbar">
          <button 
            v-for="order in orders"
            :key="order.id"
            @click="activeOrderId = order.id"
            :class="[
              'px-3 py-1.5 text-xs font-semibold rounded-lg transition-all flex items-center gap-2 shrink-0 border',
              (activeOrderId === order.id || (!activeOrderId && orders[0].id === order.id))
                ? 'bg-white text-green-600 border-green-200 shadow-sm' 
                : 'text-gray-500 border-transparent hover:bg-white/50'
            ]"
          >
            <span class="truncate max-w-[80px]">{{ order.selectedCustomer?.customer_name || order.name }}</span>
            <button 
              v-if="orders.length > 1"
              @click.stop="closeOrder(order.id)"
              class="hover:text-red-500 rounded p-0.5"
            >
              <FeatherIcon name="x" class="w-2.5 h-2.5" />
            </button>
          </button>
          <button 
            @click="addNewOrder"
            class="p-1.5 text-gray-400 hover:text-green-600 hover:bg-white rounded-lg transition-colors border border-dashed border-gray-300 shrink-0"
            title="New Order"
          >
            <FeatherIcon name="plus" class="w-4 h-4" />
          </button>
        </div>

        <!-- Order Header (Customer & Price List Selection) -->
        <div class="p-4 border-b bg-white">
          <div class="grid grid-cols-2 gap-3">
            <!-- Customer Column -->
            <div id="customer-selection-container" class="relative">
              <div class="relative">
                <FeatherIcon 
                  :name="selectedCustomer ? 'check-circle' : 'user'" 
                  :class="['w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 transition-colors', selectedCustomer ? 'text-green-500' : 'text-gray-400']" 
                />
                <input
                  v-model="customerSearch"
                  @focus="showCustomerDropdown = true"
                  @input="onCustomerInput"
                  type="text"
                  placeholder="Select Customer..."
                  class="w-full pl-9 pr-8 py-2 bg-gray-50 border-none rounded-xl text-xs outline-none focus:ring-2 focus:ring-green-500"
                />
                <button 
                  v-if="customerSearch" 
                  @click="clearCustomer"
                  class="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-gray-600"
                >
                  <FeatherIcon name="x" class="w-3 h-3" />
                </button>
                
                <!-- Customer Dropdown -->
                <div v-if="showCustomerDropdown && filteredCustomers.length > 0" class="absolute top-full left-0 right-0 mt-2 bg-white border rounded-xl shadow-xl z-20 max-h-60 overflow-y-auto">
                  <button
                    v-for="customer in filteredCustomers"
                    :key="customer.name"
                    @click="selectCustomer(customer)"
                    class="w-full text-left px-4 py-2.5 hover:bg-green-50 text-sm border-b last:border-0"
                  >
                    <p class="font-semibold text-gray-900 text-xs">{{ customer.customer_name }}</p>
                    <p class="text-[10px] text-gray-500">{{ customer.mobile_no || 'No phone' }}</p>
                  </button>
                </div>
              </div>
            </div>

            <!-- Price List Column -->
            <div id="pricelist-selection-container" class="relative">
              <div class="relative">
                <FeatherIcon 
                  name="tag" 
                  class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" 
                />
                <input
                  v-model="priceListSearch"
                  @focus="showPriceListDropdown = true"
                  @input="onPriceListInput"
                  type="text"
                  placeholder="Price List..."
                  class="w-full pl-9 pr-8 py-2 bg-gray-50 border-none rounded-xl text-xs outline-none focus:ring-2 focus:ring-green-500"
                />
                <button 
                  v-if="priceListSearch" 
                  @click="clearPriceList"
                  class="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-gray-600"
                >
                  <FeatherIcon name="x" class="w-3 h-3" />
                </button>
                
                <!-- Price List Dropdown -->
                <div v-if="showPriceListDropdown && filteredPriceLists.length > 0" class="absolute top-full left-0 right-0 mt-2 bg-white border rounded-xl shadow-xl z-20 max-h-60 overflow-y-auto">
                  <button
                    v-for="pl in filteredPriceLists"
                    :key="pl.name"
                    @click="selectPriceList(pl)"
                    class="w-full text-left px-4 py-2.5 hover:bg-green-50 text-sm border-b last:border-0"
                  >
                    <p class="font-semibold text-gray-900 text-xs">{{ pl.name }}</p>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Cart Content -->
        <div class="flex-1 flex flex-col overflow-hidden">
          <!-- Empty Cart -->
          <div v-if="cart.length === 0" class="flex-1 flex items-center justify-center text-gray-400 p-6">
            <div class="text-center">
              <FeatherIcon name="shopping-cart" class="w-12 h-12 mx-auto mb-3" />
              <p class="text-sm">Click an item to add to cart</p>
            </div>
          </div>

          <!-- Cart Items -->
          <div v-else class="flex-1 overflow-y-auto px-4 pt-2 pb-4 space-y-1">
            <div class="flex items-center gap-2 px-2 pb-1 text-[10px] font-bold uppercase tracking-wider text-gray-400 border-b">
              <span class="w-4"></span>
              <span class="flex-1">Name</span>
              <span class="shrink-0 w-16 text-center">Qty</span>
              <span class="shrink-0 w-20 text-right">Price</span>
            </div>
            <div
              v-for="(item, index) in cart"
              :key="item.name"
              class="flex items-center gap-2 p-2 hover:bg-gray-50 rounded-lg group"
            >
              <button
                @click="removeFromCart(index)"
                class="shrink-0 p-1 text-gray-300 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <FeatherIcon name="trash-2" class="w-3 h-3" />
              </button>
              <p class="flex-1 text-xs font-semibold text-gray-900 truncate min-w-0">{{ item.item_name || item.name }}</p>
              <input
                :value="item.qty"
                @input="e => updateQty(index, parseInt(e.target.value) || 1)"
                type="number"
                min="1"
                class="selected-intem-style shrink-0 w-16 text-center text-xs text-gray-700 bg-transparent focus:outline-none"
              />
              <input
                :value="item.standard_rate"
                @input="e => updateRate(index, parseFloat(e.target.value) || 0)"
                type="number"
                step="0.01"
                min="0"
                class="selected-intem-style shrink-0 w-20 text-right text-xs text-green-600 font-bold bg-transparent focus:outline-none"
              />
            </div>
          </div>
        </div>

        <!-- Checkout Section -->
        <div class="border-t p-4 bg-gray-50 space-y-3">
          <div class="flex items-center justify-between px-1">
            <span class="text-sm text-gray-500 font-medium">Subtotal</span>
            <span class="text-xl font-black text-gray-900">{{ formatCurrency(cartTotal) }}</span>
          </div>
          <button
            @click="checkout"
            :disabled="cart.length === 0"
            :class="[
              'w-full py-4 text-white rounded-2xl font-bold text-lg shadow-lg transition-all active:scale-[0.98]',
              cart.length === 0 
                ? 'bg-gray-300 cursor-not-allowed shadow-none' 
                : 'bg-green-600 hover:bg-green-700 shadow-green-200'
            ]"
          >
            {{ selectedCustomer ? 'Complete Order' : 'Checkout as Guest' }}
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
      items: [],
      searchTimeout: null,
      orders: [
        {
          id: Date.now(),
          name: 'Order 1',
          cart: [],
          selectedCustomer: null,
          customerSearch: '',
          selectedPriceList: null,
          priceListSearch: 'Standard Selling',
        }
      ],
      activeOrderId: null,
      customers: [], // Global customers list
      priceLists: [], // Global price lists
      showCustomerDropdown: false,
      showPriceListDropdown: false,
    }
  },
  computed: {
    activeOrder() {
      const order = this.orders.find(o => o.id === this.activeOrderId)
      return order || this.orders[0]
    },
    cart() {
      return this.activeOrder?.cart || []
    },
    selectedCustomer() {
      return this.activeOrder?.selectedCustomer || null
    },
    selectedPriceList() {
      return this.activeOrder?.selectedPriceList || null
    },
    customerSearch: {
      get() { return this.activeOrder?.customerSearch || '' },
      set(val) { if (this.activeOrder) this.activeOrder.customerSearch = val }
    },
    priceListSearch: {
      get() { return this.activeOrder?.priceListSearch || '' },
      set(val) { if (this.activeOrder) this.activeOrder.priceListSearch = val }
    },
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
    filteredCustomers() {
      if (!this.customerSearch) return this.customers
      const q = this.customerSearch.toLowerCase()
      return this.customers.filter(c => 
        (c.customer_name || '').toLowerCase().includes(q) ||
        (c.mobile_no || '').toLowerCase().includes(q)
      )
    },
    filteredPriceLists() {
      if (!this.priceListSearch) return this.priceLists
      const q = this.priceListSearch.toLowerCase()
      return this.priceLists.filter(pl => 
        (pl.name || '').toLowerCase().includes(q)
      )
    },
    cartTotal() {
      return this.cart.reduce((sum, item) => sum + ((item.standard_rate || 0) * item.qty), 0)
    },
  },
  mounted() {
    this.fetchItems()
    this.fetchCustomers()
    this.fetchPriceLists()
    if (this.orders.length > 0) {
      this.activeOrderId = this.orders[0].id
    }
    // Close dropdowns when clicking outside
    document.addEventListener('click', this.handleClickOutside)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside)
  },
  methods: {
    handleClickOutside(e) {
      if (!e.target.closest('#customer-selection-container')) {
        this.showCustomerDropdown = false
      }
      if (!e.target.closest('#pricelist-selection-container')) {
        this.showPriceListDropdown = false
      }
    },
    addNewOrder() {
      const newOrder = {
        id: Date.now(),
        name: `Order ${this.orders.length + 1}`,
        cart: [],
        selectedCustomer: null,
        customerSearch: '',
        selectedPriceList: null,
        priceListSearch: 'Standard Selling',
      }
      this.orders.push(newOrder)
      this.activeOrderId = newOrder.id
    },
    async fetchPriceLists() {
      try {
        const response = await fetch('/api/method/frappe.client.get_list', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({
            doctype: 'Price List',
            fields: ['name'],
            filters: { enabled: 1, selling: 1 },
          }),
        })
        const data = await response.json()
        if (data.message) {
          this.priceLists = data.message
        }
      } catch (error) {
        console.error('Failed to fetch price lists:', error)
      }
    },
    selectPriceList(pl) {
      if (this.activeOrder) {
        this.activeOrder.selectedPriceList = pl
        this.activeOrder.priceListSearch = pl.name
        this.showPriceListDropdown = false
      }
    },
    onPriceListInput() {
      if (this.activeOrder) {
        this.activeOrder.selectedPriceList = null
        this.showPriceListDropdown = true
      }
    },
    clearPriceList() {
      if (this.activeOrder) {
        this.activeOrder.selectedPriceList = null
        this.activeOrder.priceListSearch = ''
        this.showPriceListDropdown = false
      }
    },
    closeOrder(id) {
      const index = this.orders.findIndex(o => o.id === id)
      if (index !== -1 && this.orders.length > 1) {
        this.orders.splice(index, 1)
        if (this.activeOrderId === id) {
          this.activeOrderId = this.orders[Math.max(0, index - 1)].id
        }
      }
    },
    async fetchCustomers() {
      try {
        const response = await fetch('/api/method/frappe.client.get_list', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({
            doctype: 'Customer',
            fields: ['name', 'customer_name', 'mobile_no'],
            limit_page_length: 100,
          }),
        })
        const data = await response.json()
        if (data.message) {
          this.customers = data.message
        }
      } catch (error) {
        console.error('Failed to fetch customers:', error)
      }
    },
    selectCustomer(customer) {
      if (this.activeOrder) {
        this.activeOrder.selectedCustomer = customer
        this.activeOrder.customerSearch = customer.customer_name
        this.showCustomerDropdown = false
      }
    },
    onCustomerInput() {
      if (this.activeOrder) {
        this.activeOrder.selectedCustomer = null
        this.showCustomerDropdown = true
      }
    },
    clearCustomer() {
      if (this.activeOrder) {
        this.activeOrder.selectedCustomer = null
        this.activeOrder.customerSearch = ''
        this.showCustomerDropdown = false
      }
    },
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

<style scoped>
input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
input[type="number"] {
  -moz-appearance: textfield;
  appearance: textfield;
}
</style>
