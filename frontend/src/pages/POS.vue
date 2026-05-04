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
              class="w-full pl-11 pr-10 py-3.5 bg-white border-none rounded-2xl shadow-sm ring-1 ring-gray-200 focus:ring-2 focus:ring-green-500 focus:shadow-md outline-none text-sm transition-all placeholder:text-gray-400"
            />
            <button 
              v-if="searchQuery" 
              @click="searchQuery = ''; onSearchInput()"
              class="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <FeatherIcon name="x" class="w-4 h-4" />
            </button>
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
              class="group bg-white p-2.5 rounded-2xl shadow-sm hover:shadow-md border border-gray-100 transition-all text-left flex flex-col aspect-square relative active:scale-[0.98]"
            >
              <!-- Stock Badge (Top Layer) -->
              <div 
                :class="[
                  'absolute top-2 right-2 px-1.5 py-0.5 rounded-lg text-[9px] font-bold shadow-sm z-10',
                  (item.stock_qty || 0) > 0 ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
                ]"
              >
                {{ item.stock_qty || 0 }}
              </div>

              <!-- Content Wrapper -->
              <div class="flex flex-col h-full overflow-hidden">
                <!-- Item Image (Half Square) -->
                <div class="h-1/2 w-full rounded-xl bg-gray-50 mb-2 overflow-hidden flex items-center justify-center border border-gray-50 group-hover:border-green-100 transition-colors shrink-0">
                  <img v-if="item.image" :src="item.image" class="w-full h-full object-cover" />
                  <FeatherIcon v-else name="package" class="w-6 h-6 text-gray-200" />
                </div>
                
                <!-- Item Info -->
                <div class="flex-1 flex flex-col justify-between min-h-0">
                  <div class="min-h-0">
                    <p class="text-[9px] font-bold text-green-600 uppercase tracking-wider mb-0.5 truncate">{{ item.brand || 'No Brand' }}</p>
                    <p class="text-[11px] font-bold text-gray-900 leading-tight line-clamp-2 group-hover:text-green-600 transition-colors">{{ item.item_name || item.name }}</p>
                  </div>
                  
                  <div class="flex items-center justify-between mt-auto pt-1.5 border-t border-gray-50">
                    <p class="text-xs font-black text-gray-900">
                      {{ formatCurrency(getPrice(item)).replace(' DA', '') }}
                      <span class="text-[9px] font-normal text-gray-400">DA</span>
                    </p>
                  </div>
                </div>
              </div>
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
            @click="activeOrderId = order.id; focusedField = 'qty'"
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
              @click="activeOrder.selectedItemIndex = index"
              :class="[
                'flex items-center gap-2 p-2 hover:bg-gray-50 rounded-lg group cursor-pointer transition-colors',
                selectedItemIndex === index ? 'bg-green-50 ring-1 ring-green-200 shadow-sm' : ''
              ]"
            >
              <button
                @click.stop="removeFromCart(index)"
                class="shrink-0 p-1 text-gray-300 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <FeatherIcon name="trash-2" class="w-3 h-3" />
              </button>
              <p class="flex-1 text-xs font-semibold text-gray-900 truncate min-w-0">{{ item.item_name || item.name }}</p>
              
              <!-- Qty View -->
              <button 
                @click.stop="activeOrder.selectedItemIndex = index; focusedField = 'qty'"
                :class="[
                  'shrink-0 w-16 text-center text-xs py-1 rounded transition-all',
                  (selectedItemIndex === index && focusedField === 'qty') ? 'text-green-600 font-bold ring-1 ring-green-200 bg-green-50/50' : 'text-gray-700 hover:bg-gray-100'
                ]"
              >
                {{ item.qty }}
              </button>

              <!-- Price View -->
              <button 
                @click.stop="activeOrder.selectedItemIndex = index; focusedField = 'rate'"
                :class="[
                  'shrink-0 w-20 text-right text-xs py-1 rounded transition-all',
                  (selectedItemIndex === index && focusedField === 'rate') ? 'text-green-600 font-bold ring-1 ring-green-200 bg-green-50/50' : 'text-green-600 font-bold hover:bg-gray-100'
                ]"
              >
                {{ formatCurrency(item.standard_rate).replace(' DA', '') }}
              </button>
            </div>
          </div>
        </div>

        <!-- On-Screen Keyboard -->
        <div class="bg-gray-100 p-2 border-t mt-auto">
          <!-- Subtotal Row -->
          <div class="flex items-center justify-between px-3 py-2 bg-white rounded-xl mb-2 border shadow-sm">
            <span class="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Subtotal</span>
            <span class="text-base font-black text-gray-900">{{ formatCurrency(cartTotal) }}</span>
          </div>

          <div class="grid grid-cols-4 gap-1.5">
            <!-- Left 3 Columns: Numbers -->
            <div class="col-span-3 grid grid-cols-3 gap-1.5">
              <button 
                v-for="n in [1,2,3,4,5,6,7,8,9]" 
                :key="n" 
                @click="handleKeyboardInput(n)" 
                :disabled="selectedItemIndex === null"
                :class="[
                  'h-12 bg-white rounded-xl shadow-sm text-base font-bold transition-colors',
                  selectedItemIndex === null ? 'opacity-50 cursor-not-allowed' : 'active:bg-gray-200'
                ]"
              >
                {{ n }}
              </button>
              <button 
                @click="handleKeyboardInput('.')" 
                :disabled="selectedItemIndex === null"
                :class="['h-12 bg-white rounded-xl shadow-sm text-base font-bold', selectedItemIndex === null ? 'opacity-50 cursor-not-allowed' : 'active:bg-gray-200']"
              >.</button>
              <button 
                @click="handleKeyboardInput(0)" 
                :disabled="selectedItemIndex === null"
                :class="['h-12 bg-white rounded-xl shadow-sm text-base font-bold', selectedItemIndex === null ? 'opacity-50 cursor-not-allowed' : 'active:bg-gray-200']"
              >0</button>
              <button 
                @click="handleKeyboardInput('backspace')" 
                :disabled="selectedItemIndex === null"
                :class="['h-12 bg-white rounded-xl shadow-sm flex items-center justify-center', selectedItemIndex === null ? 'opacity-50 cursor-not-allowed' : 'active:bg-gray-200']"
              >
                <FeatherIcon name="delete" class="w-5 h-5 text-gray-600" />
              </button>
            </div>

            <!-- Right 1 Column: Controls -->
            <div class="col-span-1 grid grid-rows-4 gap-1.5">
              <button 
                @click="focusedField = 'qty'" 
                :disabled="selectedItemIndex === null"
                :class="[
                  'rounded-xl shadow-sm text-[10px] font-black uppercase transition-all border',
                  selectedItemIndex === null ? 'opacity-50 cursor-not-allowed bg-white text-gray-400' : 
                  (focusedField === 'qty' ? 'bg-green-600 text-white border-green-700 shadow-inner' : 'bg-white text-gray-500 border-transparent hover:bg-gray-50')
                ]"
              >
                Qty
              </button>
              <button 
                @click="focusedField = 'rate'" 
                :disabled="selectedItemIndex === null"
                :class="[
                  'rounded-xl shadow-sm text-[10px] font-black uppercase transition-all border',
                  selectedItemIndex === null ? 'opacity-50 cursor-not-allowed bg-white text-gray-400' :
                  (focusedField === 'rate' ? 'bg-green-600 text-white border-green-700 shadow-inner' : 'bg-white text-gray-500 border-transparent hover:bg-gray-50')
                ]"
              >
                Price
              </button>
              <button 
                @click="toggleSign" 
                :disabled="selectedItemIndex === null"
                :class="[
                  'rounded-xl border text-base font-black uppercase transition-colors',
                  selectedItemIndex === null ? 'opacity-50 cursor-not-allowed bg-white text-gray-400' : 'bg-gray-50 text-gray-700 border-gray-200 active:bg-gray-100'
                ]"
              >
                +/-
              </button>
              <button 
                @click="removeFromCart(selectedItemIndex)" 
                :disabled="selectedItemIndex === null"
                :class="[
                  'rounded-xl text-[10px] font-black uppercase transition-colors',
                  selectedItemIndex === null ? 'opacity-50 cursor-not-allowed bg-white text-gray-400' : 'bg-red-50 text-red-600 border border-red-100 active:bg-red-100'
                ]"
              >
                Remove
              </button>
            </div>

            <!-- Action Buttons -->
            <button 
              @click="checkout"
              :disabled="!selectedCustomer"
              :class="[
                'col-span-2 h-14 mt-1 rounded-2xl font-black uppercase tracking-widest transition-all active:scale-[0.98]',
                !selectedCustomer ? 'bg-gray-300 text-gray-500 cursor-not-allowed' : 'bg-green-600 text-white hover:bg-green-700'
              ]"
            >
              Complete
            </button>
            <button 
              @click="printReceipt"
              :disabled="cart.length === 0"
              :class="[
                'col-span-2 h-14 mt-1 rounded-2xl font-black uppercase tracking-widest transition-all active:scale-[0.98]',
                cart.length === 0 ? 'bg-gray-300 text-gray-500 cursor-not-allowed' : 'text-white hover:opacity-90'
              ]"
              :style="cart.length > 0 ? { backgroundColor: '#F7471C' } : {}"
            >
              Print
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Badge, FeatherIcon, createResource } from 'frappe-ui'

export default {
  name: 'POS',
  components: {
    Badge,
    FeatherIcon,
  },
  data() {
    return {
      searchQuery: '',
      searchTimeout: null,
      activeOrderId: null,
      orders: [
        {
          id: Date.now(),
          name: 'Order 1',
          cart: [],
          selectedCustomer: null,
          customerSearch: '',
          selectedPriceList: null,
          priceListSearch: 'Standard Selling',
          selectedItemIndex: null,
        }
      ],
      customers: [], // Global customers list
      priceLists: [], // Global price lists
      items: [], // Global items list
      showCustomerDropdown: false,
      showPriceListDropdown: false,
      focusedField: 'qty', // 'qty' or 'rate'
      
      // Resources
      customersResource: createResource({
        url: 'frappe.client.get_list',
        params: {
          doctype: 'Customer',
          fields: ['name', 'customer_name', 'mobile_no'],
          limit_page_length: 100,
        },
        auto: true,
        onSuccess: (data) => {
          this.customers = data
        }
      }),
      priceListsResource: createResource({
        url: 'frappe.client.get_list',
        params: {
          doctype: 'Price List',
          fields: ['name'],
          filters: { enabled: 1, selling: 1 },
        },
        auto: true,
        onSuccess: (data) => {
          this.priceLists = data
          this.itemsResource.fetch()
        }
      }),
      itemsResource: createResource({
        url: 'optilens_app.api.pos.get_item',
        params: {
          warehouse: 'Stores - OA'
        },
        onSuccess: (data) => {
          this.items = data
        }
      })
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
    selectedItemIndex() {
      return this.activeOrder?.selectedItemIndex ?? null
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
      // Map items to include the rate based on the selected price list
      return this.filteredItems.slice(0, 50).map(item => ({
        ...item,
        standard_rate: this.getPrice(item)
      }))
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
    if (this.orders.length > 0) {
      this.activeOrderId = this.orders[0].id
    }
    // Close dropdowns when clicking outside
    document.addEventListener('click', this.handleClickOutside)
    // Add keyboard shortcuts
    document.addEventListener('keydown', this.handleKeyDown)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside)
    document.removeEventListener('keydown', this.handleKeyDown)
  },
  methods: {
    getCookie(name) {
      const value = `; ${document.cookie}`
      const parts = value.split(`; ${name}=`)
      if (parts.length === 2) return parts.pop().split(';').shift()
    },
    handleKeyDown(e) {
      // Ignore if user is typing in an input field
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return

      const key = e.key.toLowerCase()
      if (key === 'q') {
        this.focusedField = 'qty'
      } else if (key === 'p') {
        this.focusedField = 'rate'
      } else if (this.selectedItemIndex !== null) {
        if (/^[0-9]$/.test(key)) {
          this.handleKeyboardInput(parseInt(key))
        } else if (key === '.') {
          this.handleKeyboardInput('.')
        } else if (key === 'backspace') {
          this.handleKeyboardInput('backspace')
        } else if (key === 'delete') {
          this.removeFromCart(this.selectedItemIndex)
        } else if (key === '-') {
          this.toggleSign()
        }
      }
    },
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
        selectedItemIndex: null,
      }
      this.orders.push(newOrder)
      this.activeOrderId = newOrder.id
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
    getPrice(item) {
      const priceList = this.selectedPriceList?.name || 'Standard Selling'
      const priceObj = item.prices?.find(p => p.price_list === priceList)
      return priceObj ? priceObj.price_list_rate : (item.standard_rate || 0)
    },
    handleKeyboardInput(val) {
      if (this.selectedItemIndex === null) return
      const item = this.cart[this.selectedItemIndex]
      const field = this.focusedField === 'qty' ? 'qty' : 'standard_rate'
      let currentVal = item[field].toString()

      if (val === 'backspace') {
        currentVal = currentVal.slice(0, -1)
        if (currentVal === '' || currentVal === '-') currentVal = '0'
      } else if (val === 'clear') {
        currentVal = '0'
      } else if (val === '.') {
        if (!currentVal.includes('.')) {
          currentVal += '.'
        }
      } else {
        if (currentVal === '0') {
          currentVal = val.toString()
        } else if (currentVal === '-0') {
          currentVal = '-' + val.toString()
        } else {
          currentVal += val.toString()
        }
      }

      const numVal = parseFloat(currentVal)
      if (!isNaN(numVal)) {
        if (this.focusedField === 'qty') {
          item.qty = numVal
        } else {
          item.standard_rate = numVal
        }
      }
    },
    toggleSign() {
      if (this.selectedItemIndex === null) return
      const item = this.cart[this.selectedItemIndex]
      const field = this.focusedField === 'qty' ? 'qty' : 'standard_rate'
      
      // Don't allow negative price
      if (field === 'standard_rate' && item[field] > 0) return
      
      item[field] = item[field] * -1
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
    selectCustomer(customer) {
      if (this.activeOrder) {
        this.activeOrder.selectedCustomer = customer
        this.activeOrder.customerSearch = customer.customer_name
        this.showCustomerDropdown = false
      }
    },
    onSearchInput() {
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        // Local filtering via computed properties
      }, 300)
    },
    clearCustomer() {
      if (this.activeOrder) {
        this.activeOrder.selectedCustomer = null
        this.activeOrder.customerSearch = ''
        this.showCustomerDropdown = false
      }
    },
    selectItem(item) {
      // Add item to cart directly on click (qty 1)
      const existingIndex = this.cart.findIndex(i => i.name === item.name)
      if (existingIndex !== -1) {
        this.cart[existingIndex].qty += 1
        this.activeOrder.selectedItemIndex = existingIndex
      } else {
        // Use the rate from the displayed item (which already accounted for the price list)
        this.cart.push({ ...item, qty: 1 })
        this.activeOrder.selectedItemIndex = this.cart.length - 1
      }
    },
    removeFromCart(index) {
      this.cart.splice(index, 1)
      if (this.activeOrder.selectedItemIndex === index) {
        this.activeOrder.selectedItemIndex = null
      } else if (this.activeOrder.selectedItemIndex > index) {
        this.activeOrder.selectedItemIndex--
      }
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
      if (this.cart.length === 0) return
      console.log('Checkout:', this.cart)
      // TODO: Create POS Invoice via Frappe API
      if (this.activeOrder) {
        this.activeOrder.cart = []
        this.activeOrder.selectedCustomer = null
        this.activeOrder.customerSearch = ''
        this.activeOrder.selectedItemIndex = null
      }
    },
    printReceipt() {
      if (this.cart.length === 0) return
      console.log('Printing receipt for:', this.cart)
      // TODO: Implement actual printing logic
      alert('Receipt sent to printer')
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
