<template>
  <div class="h-screen bg-[#44b8b3] flex overflow-hidden relative">
    <!-- Left Section: Top Bar + Item Selector -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- Top Action Bar (Left Side Only) -->
      <div class="h-14 shrink-0 flex items-center justify-between px-6 z-[60]">
        <div class="flex items-center gap-4">
          <button 
            @click="showSidebar = true"
            class="p-2.5 bg-white shadow-sm hover:bg-gray-50 rounded-xl transition-all active:scale-[0.98] group flex items-center justify-center border border-white/20"
          >
            <FeatherIcon name="chevron-right" class="w-5 h-5 text-black group-hover:translate-x-0.5 transition-transform" stroke-width="3" />
          </button>
          <h1 class="text-5xl font-black text-black tracking-tight flex items-center gap-2">
            <span>Optilens <span class="text-[#F7471C]">POS</span></span>
            <div v-if="loginData.profile" class="flex items-center gap-1.5 ml-3 pl-4 border-l border-black/20">
              <FeatherIcon name="user" class="w-4 h-4 text-black" stroke-width="3" />
              <span class="text-xs font-black text-black tracking-tight uppercase">{{ loginData.profile }}</span>
              <div v-if="openingTime" class="flex items-center gap-1.5 ml-2 pl-3 border-l border-black/10">
                <FeatherIcon name="clock" class="w-3.5 h-3.5 text-black" stroke-width="2.5" />
                <span class="text-xs font-black text-black">{{ openingTime }}</span>
              </div>
            </div>
          </h1>
        </div>
        
        <div class="flex items-center gap-3">
          <!-- Sync & Status Button -->
          <button 
            @click="syncData"
            :disabled="!isOnline"
            class="flex items-center gap-2 px-4 py-2 bg-white rounded-xl shadow-sm hover:shadow-md border border-gray-100 transition-all active:scale-[0.98] text-sm font-bold text-gray-700 disabled:opacity-50"
          >
            <div :class="['w-2 h-2 rounded-full', isOnline ? 'bg-green-500 animate-pulse' : 'bg-red-500']"></div>
            <span>{{ isOnline ? 'Sync' : 'Offline' }}</span>
          </button>

          <button 
            @click="showMoneyModal = true"
            class="flex items-center gap-2 px-4 py-2 bg-white rounded-xl shadow-sm hover:shadow-md border border-gray-100 transition-all active:scale-[0.98] text-sm font-bold text-gray-700"
          >
            <FeatherIcon name="dollar-sign" class="w-4 h-4 text-[#39ADA8]" />
            Money
          </button>

          <button 
            @click="checkout"
            class="flex items-center gap-2 px-4 py-2 bg-white rounded-xl shadow-sm hover:shadow-md border border-gray-100 transition-all active:scale-[0.98] text-sm font-bold text-[#39ADA8] shadow-[#39ADA8]/10"
          >
            <FeatherIcon name="credit-card" class="w-4 h-4" />
            Payment
          </button>
          
          <button 
            @click="showHistoryModal = true"
            class="flex items-center gap-2 px-4 py-2 bg-white rounded-xl shadow-sm hover:shadow-md border border-gray-100 transition-all active:scale-[0.98] text-sm font-bold text-gray-700"
          >
            <FeatherIcon name="clock" class="w-4 h-4 text-blue-600" />
            History
          </button>
        </div>
      </div>

      <!-- Item Selector Content (Card Style) -->
      <div class="flex-1 flex flex-col px-6 pb-2 overflow-hidden border border-gray-200 m-4 rounded-2xl bg-white shadow-sm">
        <!-- Search Bar -->
        <div class="h-12 shrink-0 flex items-center my-2">
          <div class="relative group w-full">
            <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <FeatherIcon name="search" class="w-4 h-4 text-gray-400 group-focus-within:text-[#39ADA8] transition-colors" />
            </div>
            <input v-model="searchQuery" @input="onSearchInput" type="text" placeholder="Search items..." class="w-full pl-11 pr-10 py-2 bg-gray-50/50 border-none rounded-2xl focus:ring-2 focus:ring-[#39ADA8] outline-none text-sm placeholder:text-gray-400 transition-all" />
            <button v-if="searchQuery" @click="searchQuery = ''; onSearchInput()" class="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 text-gray-400 hover:text-gray-600 transition-colors"><FeatherIcon name="x" class="w-4 h-4" /></button>
          </div>
        </div>

        <!-- Items Grid -->
        <div class="flex-1 overflow-y-auto">
          <div v-if="displayedItems.length === 0" class="text-center py-12 text-gray-500">
            <FeatherIcon name="package" class="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p>No items found</p>
          </div>
          <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3 pb-4">
            <button v-for="item in displayedItems" :key="item.name" @click="selectItem(item)" class="group bg-white p-2.5 rounded-2xl shadow-sm hover:shadow-md border border-gray-100 transition-all text-left flex flex-col aspect-square relative active:scale-[0.98]">
              <div :class="['absolute top-2 right-2 px-1.5 py-0.5 rounded-lg text-[9px] font-bold shadow-sm z-10', (item.stock_qty || 0) > 0 ? 'bg-[#39ADA8] text-white' : 'bg-red-500 text-white']">{{ item.stock_qty || 0 }}</div>
              <div class="flex flex-col h-full overflow-hidden">
                <div class="h-1/2 w-full rounded-xl bg-gray-50 mb-2 overflow-hidden flex items-center justify-center border border-gray-50 group-hover:border-[#39ADA8]/20 shrink-0">
                  <img v-if="item.image" :src="item.image" class="w-full h-full object-cover" />
                  <FeatherIcon v-else name="package" class="w-6 h-6 text-gray-200" />
                </div>
                <div class="flex-1 flex flex-col justify-between min-h-0">
                  <div class="min-h-0">
                    <p class="text-[9px] font-bold text-[#39ADA8] uppercase mb-0.5 truncate tracking-wider">{{ item.brand || 'No Brand' }}</p>
                    <p class="text-[11px] font-bold text-gray-900 leading-tight line-clamp-2 group-hover:text-[#39ADA8] transition-colors">{{ item.item_name || item.name }}</p>
                  </div>
                  <div class="mt-auto pt-1.5 border-t border-gray-50">
                    <p class="text-xs font-black text-gray-900">{{ formatCurrency(getPrice(item)).replace(' DA', '') }} <span class="text-[9px] font-normal text-gray-400">DA</span></p>
                  </div>
                </div>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Section: Orders Panel (Takes whole height as a card) -->
    <div class="w-[400px] flex flex-col bg-white overflow-hidden shrink-0 border border-gray-200 h-[calc(100vh-2rem)] m-4 rounded-2xl shadow-2xl shadow-gray-200/50">
      <!-- Multi-Order Tabs (Top of Right Section) -->
      <div class="flex items-center gap-1 p-2 bg-gray-50 border-b overflow-x-auto no-scrollbar shrink-0">
        <button v-for="order in orders" :key="order.id" @click="activeOrderId = order.id; focusedField = 'qty'" :class="['px-3 py-1.5 text-xs font-semibold rounded-lg transition-all flex items-center gap-2 shrink-0 border', (activeOrderId === order.id || (!activeOrderId && orders[0].id === order.id)) ? 'bg-white text-[#39ADA8] border-[#39ADA8]/20 shadow-sm' : 'text-gray-500 border-transparent hover:bg-white/50']">
          <span class="truncate max-w-[80px]">{{ order.selectedCustomer?.customer_name || order.name }}</span>
          <FeatherIcon v-if="orders.length > 1" @click.stop="closeOrder(order.id)" name="x" class="w-3 h-3 hover:text-red-500" />
        </button>
        <button @click="addNewOrder" class="p-1.5 text-gray-400 hover:text-[#39ADA8] transition-colors"><FeatherIcon name="plus" class="w-4 h-4" /></button>
      </div>

      <!-- Customer & Price List -->
      <div class="p-4 space-y-3 border-b shrink-0 bg-white">
        <div class="grid grid-cols-2 gap-3">
          <div id="customer-selection-container" class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
              <FeatherIcon name="user" class="w-3.5 h-3.5" />
            </div>
            <input v-model="customerSearch" @focus="showCustomerDropdown = true" @input="onCustomerInput" type="text" placeholder="Customer..." class="w-full pl-9 pr-8 py-2 bg-gray-50 border-none rounded-xl text-xs outline-none focus:ring-2 focus:ring-[#39ADA8] transition-all placeholder:text-gray-400" />
            <div v-if="showCustomerDropdown && filteredCustomers.length > 0" class="absolute top-full left-0 right-0 mt-2 bg-white border rounded-xl shadow-xl z-50 max-h-60 overflow-y-auto">
              <button v-for="c in filteredCustomers" :key="c.name" @click="selectCustomer(c)" class="w-full text-left px-4 py-2.5 hover:bg-[#39ADA8]/5 border-b last:border-0">
                <p class="font-bold text-gray-900 text-xs">{{ c.customer_name }}</p>
                <p class="text-[10px] text-gray-400">{{ c.mobile_no || 'No mobile' }}</p>
              </button>
            </div>
          </div>
          <div id="pricelist-selection-container" class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
              <FeatherIcon name="tag" class="w-3.5 h-3.5" />
            </div>
            <input v-model="priceListSearch" @focus="showPriceListDropdown = true" @input="onPriceListInput" type="text" placeholder="Price List..." class="w-full pl-9 pr-8 py-2 bg-gray-50 border-none rounded-xl text-xs outline-none focus:ring-2 focus:ring-[#39ADA8] transition-all placeholder:text-gray-400" />
            <div v-if="showPriceListDropdown && filteredPriceLists.length > 0" class="absolute top-full left-0 right-0 mt-2 bg-white border rounded-xl shadow-xl z-50 max-h-60 overflow-y-auto">
              <button v-for="pl in filteredPriceLists" :key="pl.name" @click="selectPriceList(pl)" class="w-full text-left px-4 py-2.5 hover:bg-[#39ADA8]/5 border-b last:border-0">
                <p class="font-semibold text-gray-900 text-xs">{{ pl.name }}</p>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Cart List (Scrollable) -->
      <div class="flex-1 flex flex-col overflow-hidden bg-white">
        <div v-if="cart.length === 0" class="flex-1 flex items-center justify-center text-gray-400 p-6 text-center opacity-50">
          <div><FeatherIcon name="shopping-cart" class="w-12 h-12 mx-auto mb-3 opacity-20" /><p class="text-sm italic font-bold">Cart is empty</p></div>
        </div>
        <div v-else class="flex-1 flex flex-col overflow-hidden">
          <div class="flex items-center gap-2 px-6 py-2 text-[10px] font-bold uppercase tracking-wider text-gray-400 border-b shrink-0 bg-white">
            <span class="w-7"></span><span class="flex-1">Name</span><span class="shrink-0 w-14 text-center">Qty</span><span class="shrink-0 w-20 text-right pr-2">Price</span>
          </div>
          <div class="flex-1 overflow-y-auto px-4 py-2 space-y-1">
            <div v-for="(item, index) in cart" :key="index" @click="activeOrder.selectedItemIndex = index" :class="['h-12 px-2 rounded-xl cursor-pointer border flex items-center gap-2 shrink-0 transition-all duration-200', selectedItemIndex === index ? 'bg-[#39ADA8]/5 border-[#39ADA8]' : 'bg-white border-transparent hover:bg-gray-50']">
              <button @click.stop="removeFromCart(index)" class="shrink-0 w-7 h-7 flex items-center justify-center rounded-lg bg-red-50 text-red-400 hover:text-red-600 transition-colors"><FeatherIcon name="trash-2" class="w-3.5 h-3.5" /></button>
              <p class="flex-1 text-xs font-semibold text-gray-900 truncate">{{ item.item_name || item.name }}</p>
              <button @click.stop="activeOrder.selectedItemIndex = index; focusedField = 'qty'" :class="['shrink-0 w-14 h-8 flex items-center justify-center text-xs rounded-lg transition-all', (selectedItemIndex === index && focusedField === 'qty') ? 'text-[#39ADA8] font-bold bg-[#39ADA8]/10' : 'text-gray-700 hover:bg-gray-100']">{{ item.qty }}</button>
              <button @click.stop="activeOrder.selectedItemIndex = index; focusedField = 'rate'" :class="['shrink-0 w-20 h-8 flex items-center justify-end px-2 text-xs rounded-lg transition-all', (selectedItemIndex === index && focusedField === 'rate') ? 'text-[#39ADA8] font-bold bg-[#39ADA8]/10' : 'text-[#39ADA8] font-bold hover:bg-gray-100']">{{ formatCurrency(item.standard_rate).replace(' DA', '') }}</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Keyboard Area (Fixed at bottom) -->
      <div class="bg-gray-100 p-1.5 border-t shrink-0">
        <div class="flex items-center justify-between px-3 py-1.5 bg-white rounded-xl mb-1.5 border shadow-sm">
          <span class="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Subtotal</span>
          <span class="text-base font-black text-gray-900">{{ formatCurrency(cartTotal) }}</span>
        </div>
        <div class="grid grid-cols-4 gap-1.5">
          <div class="col-span-3 grid grid-cols-3 gap-1.5">
            <button v-for="n in [1,2,3,4,5,6,7,8,9]" :key="n" @click="handleKeyboardInput(n)" class="h-11 bg-white rounded-xl shadow-sm text-base font-bold transition-colors border border-gray-100 active:bg-gray-100">{{ n }}</button>
            <button @click="handleKeyboardInput('.')" class="h-11 bg-white rounded-xl shadow-sm text-base font-bold border border-gray-100 active:bg-gray-100">.</button>
            <button @click="handleKeyboardInput(0)" class="h-11 bg-white rounded-xl shadow-sm text-base font-bold border border-gray-100 active:bg-gray-100">0</button>
            <button @click="handleKeyboardInput('backspace')" class="h-11 bg-white rounded-xl shadow-sm flex items-center justify-center border border-gray-100 active:bg-gray-100"><FeatherIcon name="delete" class="w-5 h-5 text-gray-600" /></button>
          </div>
          <div class="col-span-1 grid grid-rows-4 gap-1.5">
            <button @click="focusedField = 'qty'" :class="['rounded-xl shadow-sm text-[10px] font-black uppercase transition-all border', (focusedField === 'qty') ? 'bg-[#39ADA8] text-white border-[#39ADA8] shadow-inner' : 'bg-white text-gray-500 border-gray-100']">Qty</button>
            <button @click="focusedField = 'rate'" :class="['rounded-xl shadow-sm text-[10px] font-black uppercase transition-all border', (focusedField === 'rate') ? 'bg-[#39ADA8] text-white border-[#39ADA8] shadow-inner' : 'bg-white text-gray-500 border-gray-100']">Price</button>
            <button @click="toggleSign" class="rounded-xl border border-gray-100 text-base font-black uppercase bg-gray-50 text-gray-700 active:bg-gray-100 transition-colors">+/-</button>
            <button @click="removeFromCart(selectedItemIndex)" class="rounded-xl text-[10px] font-black uppercase bg-red-50 text-red-600 border border-red-100 active:bg-red-100 transition-colors">Del</button>
          </div>
        </div>

        <!-- Action Buttons (Done & Print) -->
        <div class="grid grid-cols-2 gap-2 mt-2">
          <button 
            @click="checkout" 
            :disabled="cart.length === 0"
            class="flex items-center justify-center gap-2 py-3.5 bg-[#39ADA8] text-white rounded-2xl font-black text-sm shadow-lg shadow-[#39ADA8]/20 hover:opacity-90 transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <FeatherIcon name="check-circle" class="w-4 h-4" />
            Done
          </button>
          <button 
            @click="printReceipt" 
            :disabled="cart.length === 0"
            class="flex items-center justify-center gap-2 py-3.5 bg-[#F7471C] text-white rounded-2xl font-black text-sm shadow-lg shadow-red-100 hover:opacity-90 transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <FeatherIcon name="printer" class="w-4 h-4" />
            Print
          </button>
        </div>
      </div>
    </div>

    <!-- Initialization Progress Overlay -->
    <div v-if="isInitializing" class="fixed inset-0 z-[100] flex items-center justify-center bg-gray-900/50 backdrop-blur-sm">
      <div class="bg-white p-8 rounded-3xl shadow-2xl max-w-sm w-full mx-4 border border-gray-100">
        <div class="text-center mb-6">
          <div class="w-16 h-16 bg-[#39ADA8]/10 rounded-2xl flex items-center justify-center mx-auto mb-4 animate-bounce"><FeatherIcon name="loader" class="w-8 h-8 text-[#39ADA8] animate-spin" /></div>
          <h2 class="text-xl font-black text-gray-900">Setting up POS</h2>
          <p class="text-sm text-gray-500 mt-1">Please wait while we sync your data...</p>
        </div>
        <div class="space-y-3">
          <div v-for="step in loadingSteps" :key="step.label" class="flex items-center justify-between p-3 rounded-xl border border-gray-50 transition-colors" :class="step.completed ? 'bg-[#39ADA8]/5 border-[#39ADA8]/20' : 'bg-gray-50'">
            <div class="flex items-center gap-3">
              <div :class="['w-5 h-5 rounded-full flex items-center justify-center', step.completed ? 'bg-[#39ADA8]' : 'bg-gray-200 animate-pulse']"><FeatherIcon v-if="step.completed" name="check" class="w-3 h-3 text-white" /></div>
              <span :class="['text-xs font-bold', step.completed ? 'text-[#39ADA8]' : 'text-gray-400']">{{ step.label }}</span>
            </div>
            <span v-if="step.completed" class="text-[10px] font-black text-[#39ADA8] uppercase">Ready</span>
            <span v-else class="text-[10px] font-bold text-gray-300 uppercase animate-pulse">Syncing...</span>
          </div>
        </div>
        <div class="mt-8">
          <div class="w-full bg-gray-100 h-2 rounded-full overflow-hidden"><div class="bg-[#39ADA8] h-full transition-all duration-500 ease-out" :style="{ width: `${progressPercentage}%` }"></div></div>
          <p class="text-[10px] font-black text-gray-400 uppercase tracking-widest text-center mt-3">{{ progressPercentage }}% Complete</p>
        </div>
      </div>
    </div>

    <!-- Sidebar Overlay & Menu Logic -->
    <Transition enter-active-class="transition-opacity duration-300 ease-out" enter-from-class="opacity-0" enter-to-class="opacity-100" leave-active-class="transition-opacity duration-200 ease-in" leave-from-class="opacity-100" leave-to-class="opacity-0">
      <div v-if="showSidebar" @click="showSidebar = false" class="fixed inset-0 bg-gray-900/20 backdrop-blur-[2px] z-[70]"></div>
    </Transition>
    <Transition enter-active-class="transition-transform duration-300 ease-out" enter-from-class="-translate-x-full" enter-to-class="translate-x-0" leave-active-class="transition-transform duration-200 ease-in" leave-from-class="translate-x-0" leave-to-class="-translate-x-full">
      <div v-if="showSidebar" class="fixed inset-y-0 left-0 w-72 bg-white shadow-2xl z-[80] border-r border-gray-100 flex flex-col">
        <div class="p-6 border-b border-gray-50 flex items-center justify-between"><h2 class="text-xl font-black text-gray-900">Menu</h2><button @click="showSidebar = false" class="p-2 hover:bg-gray-50 rounded-xl transition-colors"><FeatherIcon name="x" class="w-5 h-5 text-gray-400" /></button></div>
        <div class="flex-1 p-4 space-y-2">
          <button class="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-[#39ADA8]/10 text-gray-600 hover:text-[#39ADA8] transition-all group"><div class="w-10 h-10 rounded-lg bg-gray-50 group-hover:bg-[#39ADA8]/10 flex items-center justify-center transition-colors"><FeatherIcon name="home" class="w-5 h-5" /></div><span class="font-bold">Dashboard</span></button>
          <button class="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-blue-50 text-gray-600 hover:text-blue-700 transition-all group"><div class="w-10 h-10 rounded-lg bg-gray-50 group-hover:bg-blue-100 flex items-center justify-center transition-colors"><FeatherIcon name="settings" class="w-5 h-5" /></div><span class="font-bold">Settings</span></button>
          <button class="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-orange-50 text-gray-600 hover:text-orange-700 transition-all group"><div class="w-10 h-10 rounded-lg bg-gray-50 group-hover:bg-orange-100 flex items-center justify-center transition-colors"><FeatherIcon name="users" class="w-5 h-5" /></div><span class="font-bold">Customers</span></button>
        </div>
        <div class="p-4 border-t border-gray-50"><button @click="closePOS" class="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-red-50 text-red-500 transition-all group"><div class="w-10 h-10 rounded-lg bg-red-50 group-hover:bg-red-100 flex items-center justify-center transition-colors"><FeatherIcon name="log-out" class="w-5 h-5" /></div><span class="font-bold">Exit POS</span></button></div>
      </div>
    </Transition>

    <!-- Initial Profile Selection Popup -->
    <div v-if="showLoginModal" class="fixed inset-0 z-[200] flex items-center justify-center bg-gray-900/60 backdrop-blur-md">
      <div class="bg-white p-6 rounded-[2rem] shadow-2xl max-w-sm w-full mx-4 border border-gray-100 relative overflow-hidden">
        <div class="absolute top-0 left-0 right-0 h-1.5 bg-[#39ADA8]"></div>
        
        <div v-if="!showDenominations">
          <div class="text-center mb-6">
            <div class="w-16 h-16 bg-[#39ADA8]/10 rounded-2xl flex items-center justify-center mx-auto mb-3 text-[#39ADA8]">
              <FeatherIcon name="unlock" class="w-8 h-8" />
            </div>
            <h2 class="text-xl font-black text-gray-900">Welcome to Optilens</h2>
            <p class="text-xs text-gray-500 mt-1 font-medium">Please select your profile to continue</p>
          </div>

          <div class="space-y-4">
            <div class="space-y-1">
              <label class="text-[10px] font-bold text-gray-400 uppercase tracking-widest ml-1">Company</label>
              <select v-model="loginData.company" class="w-full px-4 py-3 bg-gray-50 border-2 border-transparent rounded-xl outline-none focus:border-[#39ADA8] transition-all font-bold text-sm text-gray-700 appearance-none cursor-pointer">
                <option value="" disabled>Select Company</option>
                <option v-for="c in companiesList" :key="c.name" :value="c.name">{{ c.name }}</option>
              </select>
            </div>

            <div class="space-y-1">
              <label class="text-[10px] font-bold text-gray-400 uppercase tracking-widest ml-1">POS Profile</label>
              <select v-model="loginData.profile" :disabled="!loginData.company" class="w-full px-4 py-3 bg-gray-50 border-2 border-transparent rounded-xl outline-none focus:border-[#39ADA8] transition-all font-bold text-sm text-gray-700 appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed">
                <option value="" disabled>Select Profile</option>
                <option v-for="p in filteredProfiles" :key="p.name" :value="p.name">{{ p.name }}</option>
              </select>
            </div>

            <div class="space-y-1">
              <label class="text-[10px] font-bold text-gray-400 uppercase tracking-widest ml-1">Password / PIN</label>
              <div class="relative">
                <input v-model="loginData.password" @input="loginError = ''" type="password" placeholder="••••" class="w-full px-4 py-3 bg-gray-50 border-2 border-transparent rounded-xl outline-none focus:border-[#39ADA8] transition-all font-bold text-gray-700 placeholder:text-gray-300 text-center text-xl tracking-[0.8em]" />
              </div>
            </div>

            <div v-if="loginError" class="p-3 bg-red-50 border border-red-100 rounded-xl">
              <p class="text-[10px] text-red-600 font-bold text-center leading-tight uppercase tracking-tighter">
                {{ loginError }}
              </p>
            </div>

            <button 
              @click="handleLogin" 
              :disabled="!isLoginValid || posDataResource.loading"
              class="w-full py-4 bg-[#39ADA8] text-white rounded-2xl font-black text-base shadow-lg shadow-[#39ADA8]/10 hover:opacity-90 transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none mt-2 flex items-center justify-center gap-2"
            >
              <FeatherIcon v-if="posDataResource.loading" name="loader" class="w-4 h-4 animate-spin" />
              {{ posDataResource.loading ? 'Validating...' : 'Open POS Session' }}
            </button>
          </div>
        </div>

        <!-- Cash Opening Step -->
        <div v-else>
          <div class="text-center mb-6">
            <h2 class="text-xl font-black text-gray-900">Opening Balance</h2>
          </div>

          <div class="max-h-[350px] overflow-y-auto custom-scrollbar border border-gray-100 rounded-2xl">
            <table class="w-full text-left border-collapse">
              <thead class="sticky top-0 bg-white z-10">
                <tr class="border-b border-gray-100 bg-gray-50/50">
                  <th class="px-4 py-3 text-[10px] font-black text-gray-400 uppercase tracking-wider">Note</th>
                  <th class="px-4 py-3 text-[10px] font-black text-gray-400 uppercase tracking-wider text-center">Qty</th>
                  <th class="px-4 py-3 text-[10px] font-black text-gray-400 uppercase tracking-wider text-right">Subtotal</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-50">
                <tr v-for="(d, index) in denominations" :key="d.value" class="hover:bg-gray-50/50 transition-colors">
                  <td class="px-4 py-0.5">
                    <span class="text-xs font-black text-gray-700">{{ d.value }} <span class="text-[8px] font-normal text-gray-400 uppercase ml-0.5">DA</span></span>
                  </td>
                  <td class="px-4 py-0.5 text-center">
                    <input 
                      ref="denomInput"
                      v-model.number="d.qty" 
                      type="number" 
                      min="0" 
                      placeholder="0" 
                      @keydown="handleDenomKey($event, index)"
                      class="w-14 h-6 bg-gray-50 border border-gray-100 rounded-md text-center font-bold text-gray-900 outline-none focus:border-[#39ADA8] text-xs [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none" 
                    />
                  </td>
                  <td class="px-4 py-0.5 text-right">
                    <span class="text-[11px] font-bold text-gray-900">{{ (d.value * (d.qty || 0)).toLocaleString() }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="mt-4 p-4 bg-[#39ADA8]/5 rounded-2xl border border-[#39ADA8]/20 flex items-center justify-between shadow-sm">
            <div class="flex flex-col">
              <span class="text-[9px] font-black text-gray-400 uppercase tracking-widest leading-none mb-1">Total Opening Balance</span>
            </div>
            <span class="text-xl font-black text-[#39ADA8]">{{ formatCurrency(openingAmount) }}</span>
          </div>

          <div class="grid grid-cols-2 gap-3 mt-6">
            <button @click="showDenominations = false" class="py-4 bg-gray-100 text-gray-600 rounded-2xl font-black text-sm hover:bg-gray-200 transition-all">Back</button>
            <button @click="handleOpenSession" :disabled="createSessionResource.loading" class="py-4 bg-[#39ADA8] text-white rounded-2xl font-black text-sm shadow-lg shadow-[#39ADA8]/20 hover:opacity-90 transition-all flex items-center justify-center gap-2">
              <FeatherIcon v-if="createSessionResource.loading" name="loader" class="w-4 h-4 animate-spin" />
              {{ createSessionResource.loading ? 'Opening...' : 'Done' }}
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
      suppliers: [], // Global suppliers list
      priceLists: [], // Global price lists
      items: [], // Global items list
      showCustomerDropdown: false,
      showPriceListDropdown: false,
      focusedField: 'qty', // 'qty' or 'rate'
      showMoneyModal: false,
      showHistoryModal: false,
      showSidebar: false,
      showLoginModal: false, // Wait for master data sync first
      loginData: {
        company: '',
        profile: '',
        password: ''
      },
      loginError: '',
      openingTime: null,
      isOnline: navigator.onLine,
      showDenominations: false,
      denominations: [
        { value: 5, qty: 0 },
        { value: 10, qty: 0 },
        { value: 20, qty: 0 },
        { value: 50, qty: 0 },
        { value: 100, qty: 0 },
        { value: 200, qty: 0 },
        { value: 500, qty: 0 },
        { value: 1000, qty: 0 },
        { value: 2000, qty: 0 }
      ],
      companiesList: [],
      availableProfiles: [],
      
      // Resources
      posDataResource: createResource({
        url: 'optilens_app.api.pos.get_pos_data',
        auto: true,
        onSuccess: (data) => {
          this.companiesList = data.companies || []
          this.availableProfiles = data.profiles || []
          
          if (data.opening_entry) {
            // Pre-select based on active opening entry
            this.loginData.company = data.opening_entry.company
            this.loginData.profile = data.opening_entry.pos_profile
          }
        }
      }),
      createSessionResource: createResource({
        url: 'optilens_app.api.pos.create_pos_session'
      }),
      customersResource: createResource({
        url: 'frappe.client.get_list',
        params: {
          doctype: 'Customer',
          fields: ['name', 'customer_name', 'mobile_no'],
          limit_page_length: 2000,
        },
        auto: true,
        onSuccess: (data) => {
          this.customers = data
        }
      }),
      suppliersResource: createResource({
        url: 'frappe.client.get_list',
        params: {
          doctype: 'Supplier',
          fields: ['name', 'supplier_name'],
          limit_page_length: 100,
        },
        auto: true,
        onSuccess: (data) => {
          this.suppliers = data
        }
      }),
      priceListsResource: createResource({
        url: 'frappe.client.get_list',
        params: {
          doctype: 'Price List',
          fields: ['name'],
          filters: { enabled: 1, selling: 1 },
          limit_page_length: 100,
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
          // All steps are auto-managed via computed, popup closes when all ready
        }
      })
    }
  },
  computed: {
    loadingSteps() {
      return [
        { label: 'POS Context', completed: this.companiesList.length > 0 },
        { label: 'Price Lists', completed: this.priceLists.length > 0 },
        { label: 'Customers', completed: this.customers.length > 0 },
        { label: 'Suppliers', completed: this.suppliers.length > 0 },
        { label: 'Product Catalog', completed: this.items.length > 0 }
      ]
    },
    filteredProfiles() {
      if (!this.loginData.company) return []
      return this.availableProfiles.filter(p => p.company === this.loginData.company)
    },
    isLoginValid() {
      return this.loginData.company && this.loginData.profile && this.loginData.password.length >= 4
    },
    openingAmount() {
      return this.denominations.reduce((sum, d) => sum + (d.value * (d.qty || 0)), 0)
    },
    progressPercentage() {
      const completed = this.loadingSteps.filter(s => s.completed).length
      return Math.round((completed / this.loadingSteps.length) * 100)
    },
    isInitializing() {
      return this.loadingSteps.some(s => !s.completed)
    },
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
  watch: {
    isInitializing(newVal) {
      if (!newVal) {
        // Data loading finished, show login modal
        this.showLoginModal = true
      }
    }
  },
  mounted() {
    if (this.orders.length > 0) {
      this.activeOrderId = this.orders[0].id
    }
    // Connectivity listeners
    window.addEventListener('online', this.updateOnlineStatus)
    window.addEventListener('offline', this.updateOnlineStatus)
    // Close dropdowns when clicking outside
    document.addEventListener('click', this.handleClickOutside)
    // Add keyboard shortcuts
    document.addEventListener('keydown', this.handleKeyDown)
  },
  beforeUnmount() {
    window.removeEventListener('online', this.updateOnlineStatus)
    window.removeEventListener('offline', this.updateOnlineStatus)
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
    handleLogin() {
      this.loginError = ''
      
      // Call get_pos_data with params to check for specific opening entry
      this.posDataResource.fetch({
        company: this.loginData.company,
        pos_profile: this.loginData.profile
      }).then((data) => {
        console.log("founded ====> " , data.opening_entry)
        if (!data || !data.opening_entry) {
          console.log("No session found, show denominations screen")
          // No session found, show denominations screen
          this.showDenominations = true
          return
        }

        console.log("Session exists, proceed with login")
        // Session exists, proceed with login
        const profile = this.availableProfiles.find(p => p.name === this.loginData.profile)
        if (profile) {
          // Update active order with profile defaults
          if (this.activeOrder) {
            this.activeOrder.selectedPriceList = { name: profile.selling_price_list || profile.price_list }
            this.activeOrder.priceListSearch = profile.selling_price_list || profile.price_list
          }
          this.showLoginModal = false
          this.setOpeningTime()
          // Start loading items for the profile's warehouse
          this.itemsResource.fetch({ warehouse: profile.warehouse })
        }
      }).catch((err) => {
        this.loginError = 'An error occurred during session validation.'
        console.error(err)
      })
    },
    handleOpenSession() {
      this.loginError = ''
      
      this.createSessionResource.submit({
        company: this.loginData.company,
        pos_profile: this.loginData.profile,
        denominations: this.denominations
      }).then((data) => {
        const profile = this.availableProfiles.find(p => p.name === this.loginData.profile)
        if (profile) {
          if (this.activeOrder) {
            this.activeOrder.selectedPriceList = { name: profile.selling_price_list || profile.price_list }
            this.activeOrder.priceListSearch = profile.selling_price_list || profile.price_list
          }
          this.showLoginModal = false
          this.showDenominations = false
          this.setOpeningTime()
          this.itemsResource.fetch({ warehouse: profile.warehouse })
        }
      }).catch((err) => {
        this.loginError = 'Failed to create new POS session.'
        console.error(err)
      })
    },
    setOpeningTime() {
      const now = new Date()
      this.openingTime = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    },
    syncData() {
      if (!this.isOnline) return
      
      // Reload master data
      this.posDataResource.reload()
      this.customersResource.reload()
      this.priceListsResource.reload()
      
      // Reload items for current warehouse
      const profile = this.availableProfiles.find(p => p.name === this.loginData.profile)
      if (profile) {
        this.itemsResource.fetch({ warehouse: profile.warehouse })
      }
    },
    updateOnlineStatus() {
      this.isOnline = navigator.onLine
    },
    handleDenomKey(e, index) {
      if (e.key === 'ArrowDown') {
        e.preventDefault()
        const nextInput = this.$refs.denomInput[index + 1]
        if (nextInput) nextInput.focus()
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        const prevInput = this.$refs.denomInput[index - 1]
        if (prevInput) prevInput.focus()
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
    closePOS() {
      // Redirect to Frappe Desk or Home
      window.location.href = '/app'
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
