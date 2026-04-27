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
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center">
              <FeatherIcon name="package" class="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 class="text-xl font-bold text-gray-900">Stock</h1>
              <p class="text-xs text-gray-500">Inventory Management</p>
            </div>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <Badge v-if="lowStockCount > 0" :label="`${lowStockCount} Low Stock`" color="red" />
          <Badge v-else :label="'All Good'" color="green" />
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <div class="p-6">
      <!-- Quick Actions -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <button 
          @click="openPage('stock-entry/new')"
          class="flex items-center gap-3 p-4 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors shadow-lg shadow-blue-200"
        >
          <FeatherIcon name="plus-circle" class="w-6 h-6" />
          <div class="text-left">
            <p class="font-semibold">Stock Entry</p>
            <p class="text-xs text-blue-100">Record movement</p>
          </div>
        </button>

        <button 
          @click="openPage('item')"
          class="flex items-center gap-3 p-4 bg-white border rounded-xl hover:border-blue-400 transition-colors"
        >
          <div class="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
            <FeatherIcon name="package" class="w-5 h-5 text-blue-600" />
          </div>
          <div class="text-left">
            <p class="font-medium text-gray-900">Items</p>
            <p class="text-xs text-gray-500">Products</p>
          </div>
        </button>

        <button 
          @click="openPage('warehouse')"
          class="flex items-center gap-3 p-4 bg-white border rounded-xl hover:border-blue-400 transition-colors"
        >
          <div class="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center">
            <FeatherIcon name="map-pin" class="w-5 h-5 text-gray-600" />
          </div>
          <div class="text-left">
            <p class="font-medium text-gray-900">Warehouses</p>
            <p class="text-xs text-gray-500">Locations</p>
          </div>
        </button>

        <button 
          @click="openPage('stock-balance')"
          class="flex items-center gap-3 p-4 bg-white border rounded-xl hover:border-blue-400 transition-colors"
        >
          <div class="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center">
            <FeatherIcon name="pie-chart" class="w-5 h-5 text-gray-600" />
          </div>
          <div class="text-left">
            <p class="font-medium text-gray-900">Balance</p>
            <p class="text-xs text-gray-500">Stock levels</p>
          </div>
        </button>
      </div>

      <!-- Low Stock Alert -->
      <div v-if="lowStockItems.length > 0" class="mb-6 bg-red-50 border border-red-200 rounded-xl p-4">
        <div class="flex items-center gap-2 text-red-700 font-medium mb-3">
          <FeatherIcon name="alert-triangle" class="w-5 h-5" />
          <h3>Low Stock Alerts</h3>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          <div 
            v-for="item in lowStockItems" 
            :key="item.name"
            class="bg-white rounded-lg p-3 flex items-center justify-between"
          >
            <div>
              <p class="font-medium text-gray-900">{{ item.name }}</p>
              <p class="text-xs text-gray-500">{{ item.warehouse }}</p>
            </div>
            <div class="text-right">
              <p class="text-lg font-bold text-red-600">{{ item.qty }}</p>
              <p class="text-xs text-gray-400">left</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Stock Summary -->
      <div class="bg-white rounded-xl shadow-sm border">
        <div class="p-4 border-b">
          <h2 class="font-semibold text-gray-900">Stock Summary</h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x">
          <div class="p-6 text-center">
            <p class="text-3xl font-bold text-gray-900">{{ totalItems }}</p>
            <p class="text-sm text-gray-500 mt-1">Total Items</p>
          </div>
          <div class="p-6 text-center">
            <p class="text-3xl font-bold text-blue-600">{{ totalWarehouses }}</p>
            <p class="text-sm text-gray-500 mt-1">Warehouses</p>
          </div>
          <div class="p-6 text-center">
            <p class="text-3xl font-bold text-green-600">{{ stockValue }}</p>
            <p class="text-sm text-gray-500 mt-1">Stock Value</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Badge, FeatherIcon } from 'frappe-ui'

export default {
  name: 'Stock',
  components: {
    Badge,
    FeatherIcon,
  },
  data() {
    return {
      totalItems: 156,
      totalWarehouses: 4,
      stockValue: '$45,230',
      lowStockCount: 3,
      lowStockItems: [
        { name: 'Lens A-45', warehouse: 'Main', qty: 2 },
        { name: 'Frame B-12', warehouse: 'Branch 1', qty: 5 },
        { name: 'Contact Lens C', warehouse: 'Main', qty: 3 },
      ],
    }
  },
  methods: {
    openPage(route) {
      window.open(`/app/${route}`, '_blank')
    },
  },
}
</script>
