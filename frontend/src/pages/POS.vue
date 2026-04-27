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
    <div class="p-6">
      <!-- Quick Actions -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <button 
          @click="openNewInvoice"
          class="flex items-center gap-3 p-4 bg-green-600 text-white rounded-xl hover:bg-green-700 transition-colors shadow-lg shadow-green-200"
        >
          <FeatherIcon name="plus-circle" class="w-6 h-6" />
          <div class="text-left">
            <p class="font-semibold">New Invoice</p>
            <p class="text-xs text-green-100">Create a sale</p>
          </div>
        </button>

        <button 
          @click="openPage('pos-invoice')"
          class="flex items-center gap-3 p-4 bg-white border rounded-xl hover:border-green-400 transition-colors"
        >
          <div class="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
            <FeatherIcon name="file-text" class="w-5 h-5 text-green-600" />
          </div>
          <div class="text-left">
            <p class="font-medium text-gray-900">Invoices</p>
            <p class="text-xs text-gray-500">View all</p>
          </div>
        </button>

        <button 
          @click="openPage('pos-profile')"
          class="flex items-center gap-3 p-4 bg-white border rounded-xl hover:border-green-400 transition-colors"
        >
          <div class="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center">
            <FeatherIcon name="settings" class="w-5 h-5 text-gray-600" />
          </div>
          <div class="text-left">
            <p class="font-medium text-gray-900">POS Profile</p>
            <p class="text-xs text-gray-500">Settings</p>
          </div>
        </button>

        <button 
          @click="openPage('sales-register')"
          class="flex items-center gap-3 p-4 bg-white border rounded-xl hover:border-green-400 transition-colors"
        >
          <div class="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center">
            <FeatherIcon name="bar-chart-2" class="w-5 h-5 text-gray-600" />
          </div>
          <div class="text-left">
            <p class="font-medium text-gray-900">Reports</p>
            <p class="text-xs text-gray-500">Sales register</p>
          </div>
        </button>
      </div>

      <!-- Recent Invoices -->
      <div class="bg-white rounded-xl shadow-sm border">
        <div class="p-4 border-b flex items-center justify-between">
          <h2 class="font-semibold text-gray-900">Recent Invoices</h2>
          <Button variant="ghost" size="sm" @click="openPage('pos-invoice')">
            View All
          </Button>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500">Invoice</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500">Customer</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500">Date</th>
                <th class="px-4 py-3 text-right text-xs font-medium text-gray-500">Amount</th>
                <th class="px-4 py-3 text-center text-xs font-medium text-gray-500">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y">
              <tr v-for="inv in invoices" :key="inv.name" class="hover:bg-gray-50">
                <td class="px-4 py-3 text-sm font-medium">{{ inv.name }}</td>
                <td class="px-4 py-3 text-sm text-gray-600">{{ inv.customer }}</td>
                <td class="px-4 py-3 text-sm text-gray-500">{{ inv.date }}</td>
                <td class="px-4 py-3 text-sm text-right font-medium">${{ inv.amount }}</td>
                <td class="px-4 py-3 text-center">
                  <Badge :label="inv.status" :color="inv.status === 'Paid' ? 'green' : 'orange'" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Badge, Button, FeatherIcon } from 'frappe-ui'

export default {
  name: 'POS',
  components: {
    Badge,
    Button,
    FeatherIcon,
  },
  data() {
    return {
      invoices: [
        { name: 'POS-001', customer: 'Walk-in', date: '2026-04-27', amount: '125.00', status: 'Paid' },
        { name: 'POS-002', customer: 'John Doe', date: '2026-04-27', amount: '340.50', status: 'Paid' },
        { name: 'POS-003', customer: 'Walk-in', date: '2026-04-26', amount: '89.99', status: 'Paid' },
        { name: 'POS-004', customer: 'Jane Smith', date: '2026-04-26', amount: '550.00', status: 'Paid' },
      ],
    }
  },
  methods: {
    openNewInvoice() {
      window.open('/app/pos', '_blank')
    },
    openPage(route) {
      window.open(`/app/${route}`, '_blank')
    },
  },
}
</script>
