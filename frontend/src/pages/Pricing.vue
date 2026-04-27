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
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-400 to-purple-600 flex items-center justify-center">
              <FeatherIcon name="tag" class="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 class="text-xl font-bold text-gray-900">Pricing</h1>
              <p class="text-xs text-gray-500">Price Lists & Rules</p>
            </div>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <Badge :label="`${activePriceLists} Active`" color="purple" />
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <div class="p-6">
      <!-- Quick Actions -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <button 
          @click="openPage('price-list')"
          class="flex items-center gap-3 p-4 bg-purple-600 text-white rounded-xl hover:bg-purple-700 transition-colors shadow-lg shadow-purple-200"
        >
          <FeatherIcon name="list" class="w-6 h-6" />
          <div class="text-left">
            <p class="font-semibold">Price Lists</p>
            <p class="text-xs text-purple-100">Manage prices</p>
          </div>
        </button>

        <button 
          @click="openPage('item-price')"
          class="flex items-center gap-3 p-4 bg-white border rounded-xl hover:border-purple-400 transition-colors"
        >
          <div class="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
            <FeatherIcon name="edit-3" class="w-5 h-5 text-purple-600" />
          </div>
          <div class="text-left">
            <p class="font-medium text-gray-900">Item Prices</p>
            <p class="text-xs text-gray-500">Update prices</p>
          </div>
        </button>

        <button 
          @click="openPage('pricing-rule')"
          class="flex items-center gap-3 p-4 bg-white border rounded-xl hover:border-purple-400 transition-colors"
        >
          <div class="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center">
            <FeatherIcon name="percent" class="w-5 h-5 text-gray-600" />
          </div>
          <div class="text-left">
            <p class="font-medium text-gray-900">Pricing Rules</p>
            <p class="text-xs text-gray-500">Discounts</p>
          </div>
        </button>

        <button 
          @click="openPage('customer')"
          class="flex items-center gap-3 p-4 bg-white border rounded-xl hover:border-purple-400 transition-colors"
        >
          <div class="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center">
            <FeatherIcon name="users" class="w-5 h-5 text-gray-600" />
          </div>
          <div class="text-left">
            <p class="font-medium text-gray-900">Customers</p>
            <p class="text-xs text-gray-500">Management</p>
          </div>
        </button>
      </div>

      <!-- Price Lists Overview -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Active Price Lists -->
        <div class="bg-white rounded-xl shadow-sm border">
          <div class="p-4 border-b flex items-center justify-between">
            <h2 class="font-semibold text-gray-900">Active Price Lists</h2>
            <Button variant="ghost" size="sm" @click="openPage('price-list')">
              Manage
            </Button>
          </div>
          <div class="divide-y">
            <div 
              v-for="list in priceLists" 
              :key="list.name"
              class="p-4 flex items-center justify-between hover:bg-gray-50"
            >
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
                  <FeatherIcon name="tag" class="w-5 h-5 text-purple-600" />
                </div>
                <div>
                  <p class="font-medium text-gray-900">{{ list.name }}</p>
                  <p class="text-xs text-gray-500">{{ list.currency }}</p>
                </div>
              </div>
              <Badge :label="list.enabled ? 'Active' : 'Inactive'" :color="list.enabled ? 'green' : 'gray'" />
            </div>
          </div>
        </div>

        <!-- Pricing Summary -->
        <div class="bg-white rounded-xl shadow-sm border">
          <div class="p-4 border-b">
            <h2 class="font-semibold text-gray-900">Pricing Summary</h2>
          </div>
          <div class="p-6 grid grid-cols-2 gap-6">
            <div class="text-center p-4 bg-purple-50 rounded-xl">
              <p class="text-3xl font-bold text-purple-600">{{ activePriceLists }}</p>
              <p class="text-sm text-gray-600 mt-1">Active Price Lists</p>
            </div>
            <div class="text-center p-4 bg-gray-50 rounded-xl">
              <p class="text-3xl font-bold text-gray-700">{{ totalCustomers }}</p>
              <p class="text-sm text-gray-600 mt-1">Total Customers</p>
            </div>
            <div class="text-center p-4 bg-gray-50 rounded-xl">
              <p class="text-3xl font-bold text-gray-700">{{ pricingRules }}</p>
              <p class="text-sm text-gray-600 mt-1">Pricing Rules</p>
            </div>
            <div class="text-center p-4 bg-gray-50 rounded-xl">
              <p class="text-3xl font-bold text-gray-700">{{ itemPrices }}</p>
              <p class="text-sm text-gray-600 mt-1">Item Prices</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Badge, Button, FeatherIcon } from 'frappe-ui'

export default {
  name: 'Pricing',
  components: {
    Badge,
    Button,
    FeatherIcon,
  },
  data() {
    return {
      activePriceLists: 3,
      totalCustomers: 45,
      pricingRules: 8,
      itemPrices: 156,
      priceLists: [
        { name: 'Standard Selling', currency: 'USD', enabled: true },
        { name: 'Wholesale', currency: 'USD', enabled: true },
        { name: 'Retail', currency: 'USD', enabled: true },
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
