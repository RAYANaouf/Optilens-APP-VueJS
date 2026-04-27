<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center p-6">
    <div class="w-full max-w-5xl">
      <!-- Header -->
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold text-gray-900 mb-2">Optilens</h1>
        <p class="text-gray-500">Select a module to continue</p>
      </div>

      <!-- 3 Box Grid -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- POS Box -->
        <router-link 
          to="/pos" 
          class="group bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 p-8 text-center border border-gray-100 hover:border-green-200 hover:-translate-y-1"
        >
          <div class="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
            <FeatherIcon name="shopping-cart" class="w-10 h-10 text-white" />
          </div>
          <h2 class="text-2xl font-bold text-gray-900 mb-2 group-hover:text-green-600 transition-colors">POS</h2>
          <p class="text-gray-500 text-sm">Point of Sale operations and invoicing</p>
          <div class="mt-6 flex items-center justify-center gap-2 text-green-600 font-medium opacity-0 group-hover:opacity-100 transition-opacity">
            <span>Open</span>
            <FeatherIcon name="arrow-right" class="w-4 h-4" />
          </div>
        </router-link>

        <!-- Stock Box -->
        <router-link 
          to="/stock" 
          class="group bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 p-8 text-center border border-gray-100 hover:border-blue-200 hover:-translate-y-1"
        >
          <div class="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
            <FeatherIcon name="package" class="w-10 h-10 text-white" />
          </div>
          <h2 class="text-2xl font-bold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">Stock</h2>
          <p class="text-gray-500 text-sm">Inventory management and warehouses</p>
          <div class="mt-6 flex items-center justify-center gap-2 text-blue-600 font-medium opacity-0 group-hover:opacity-100 transition-opacity">
            <span>Open</span>
            <FeatherIcon name="arrow-right" class="w-4 h-4" />
          </div>
        </router-link>

        <!-- Pricing Box -->
        <router-link 
          to="/pricing" 
          class="group bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 p-8 text-center border border-gray-100 hover:border-purple-200 hover:-translate-y-1"
        >
          <div class="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-purple-400 to-purple-600 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
            <FeatherIcon name="tag" class="w-10 h-10 text-white" />
          </div>
          <h2 class="text-2xl font-bold text-gray-900 mb-2 group-hover:text-purple-600 transition-colors">Pricing</h2>
          <p class="text-gray-500 text-sm">Price lists and customer management</p>
          <div class="mt-6 flex items-center justify-center gap-2 text-purple-600 font-medium opacity-0 group-hover:opacity-100 transition-opacity">
            <span>Open</span>
            <FeatherIcon name="arrow-right" class="w-4 h-4" />
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'

export default {
  name: 'Dashboard',
  components: {
    FeatherIcon,
  },
}
</script>
