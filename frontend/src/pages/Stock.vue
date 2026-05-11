<template>
  <div class="min-h-screen bg-gray-50 relative">
    <!-- Sidebar Toggle Button -->
    <button
      @click="toggleSidebar"
      class="fixed left-4 top-4 z-30 p-3 bg-blue-600 text-white rounded-xl shadow-lg hover:bg-blue-700 transition-all duration-300"
    >
      <FeatherIcon name="menu" class="w-5 h-5" />
    </button>

    <!-- Sidebar Overlay -->
    <div
      v-if="sidebarOpen"
      @click="closeSidebar"
      class="fixed inset-0 bg-black/30 z-40 transition-opacity duration-300"
    ></div>

    <!-- Sidebar -->
    <aside
      :class="[
        'fixed left-0 top-0 h-full w-64 bg-white shadow-2xl z-50 transition-transform duration-300 ease-out',
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      ]"
    >
      <div class="p-4 border-b flex items-center justify-between">
        <h2 class="font-semibold text-gray-900">Filters</h2>
        <button
          @click="closeSidebar"
          class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <FeatherIcon name="x" class="w-5 h-5 text-gray-600" />
        </button>
      </div>
      <div class="p-4 space-y-4 overflow-y-auto max-h-[calc(100vh-80px)]">
        <!-- Company Filter -->
        <div>
          <button
            @click="collapsed.company = !collapsed.company"
            class="flex items-center justify-between w-full text-left mb-2 hover:bg-gray-50 p-1 rounded"
          >
            <span class="text-sm font-medium text-gray-700">Company</span>
            <FeatherIcon
              :name="collapsed.company ? 'chevron-right' : 'chevron-down'"
              class="w-4 h-4 text-gray-500 transition-transform"
            />
          </button>
          <div v-show="!collapsed.company" class="rounded-lg p-2 space-y-1 transition-all">
            <label class="flex items-center gap-2 p-1 hover:bg-gray-50 rounded cursor-pointer font-medium">
              <input
                type="checkbox"
                :checked="filters.companies.length === $resources.filterOptions.data.companies.length"
                @change="toggleAllCompanies"
                class="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
              />
              <span class="text-sm text-gray-700">All</span>
            </label>
            <label
              v-for="company in $resources.filterOptions.data.companies"
              :key="company"
              class="flex items-center gap-2 p-1 hover:bg-gray-50 rounded cursor-pointer"
            >
              <input
                type="checkbox"
                v-model="filters.companies"
                :value="company"
                class="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
              />
              <span class="text-sm text-gray-700">{{ company }}</span>
            </label>
          </div>
        </div>

        <!-- Warehouse Filter -->
        <div>
          <button
            @click="collapsed.warehouse = !collapsed.warehouse"
            class="flex items-center justify-between w-full text-left mb-2 hover:bg-gray-50 p-1 rounded"
          >
            <span class="text-sm font-medium text-gray-700">Warehouse</span>
            <FeatherIcon
              :name="collapsed.warehouse ? 'chevron-right' : 'chevron-down'"
              class="w-4 h-4 text-gray-500 transition-transform"
            />
          </button>
          <div v-show="!collapsed.warehouse" class="rounded-lg p-2 space-y-1 transition-all">
            <p v-if="filters.companies.length === 0" class="text-sm text-gray-500 italic p-1">
              Select a company first
            </p>
            <label v-else class="flex items-center gap-2 p-1 hover:bg-gray-50 rounded cursor-pointer font-medium">
              <input
                type="checkbox"
                :checked="filters.warehouses.length === $resources.filterOptions.data.warehouses.length"
                @change="toggleAllWarehouses"
                class="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
              />
              <span class="text-sm text-gray-700">All</span>
            </label>
            <label
              v-for="warehouse in $resources.filterOptions.data.warehouses"
              :key="warehouse"
              class="flex items-center gap-2 p-1 hover:bg-gray-50 rounded cursor-pointer"
            >
              <input
                type="checkbox"
                v-model="filters.warehouses"
                :value="warehouse"
                class="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
              />
              <span class="text-sm text-gray-700">{{ warehouse }}</span>
            </label>
          </div>
        </div>

        <!-- Group Filter -->
        <div>
          <button
            @click="collapsed.group = !collapsed.group"
            class="flex items-center justify-between w-full text-left mb-2 hover:bg-gray-50 p-1 rounded"
          >
            <span class="text-sm font-medium text-gray-700">Group</span>
            <FeatherIcon
              :name="collapsed.group ? 'chevron-right' : 'chevron-down'"
              class="w-4 h-4 text-gray-500 transition-transform"
            />
          </button>
          <div v-show="!collapsed.group" class="rounded-lg p-2 space-y-1 transition-all">
            <label class="flex items-center gap-2 p-1 hover:bg-gray-50 rounded cursor-pointer font-medium">
              <input
                type="checkbox"
                :checked="filters.groups.length === $resources.filterOptions.data.groups.length"
                @change="toggleAllGroups"
                class="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
              />
              <span class="text-sm text-gray-700">All</span>
            </label>
            <label
              v-for="group in $resources.filterOptions.data.groups"
              :key="group"
              class="flex items-center gap-2 p-1 hover:bg-gray-50 rounded cursor-pointer"
            >
              <input
                type="checkbox"
                v-model="filters.groups"
                :value="group"
                class="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
              />
              <span class="text-sm text-gray-700">{{ group }}</span>
            </label>
          </div>
        </div>

        <!-- Brand Filter -->
        <div>
          <button
            @click="collapsed.brand = !collapsed.brand"
            class="flex items-center justify-between w-full text-left mb-2 hover:bg-gray-50 p-1 rounded"
          >
            <span class="text-sm font-medium text-gray-700">Brand</span>
            <FeatherIcon
              :name="collapsed.brand ? 'chevron-right' : 'chevron-down'"
              class="w-4 h-4 text-gray-500 transition-transform"
            />
          </button>
          <div v-show="!collapsed.brand" class="rounded-lg p-2 space-y-1 transition-all">
            <label class="flex items-center gap-2 p-1 hover:bg-gray-50 rounded cursor-pointer font-medium">
              <input
                type="checkbox"
                :checked="filters.brands.length === $resources.filterOptions.data.brands.length"
                @change="toggleAllBrands"
                class="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
              />
              <span class="text-sm text-gray-700">All</span>
            </label>
            <label
              v-for="brand in $resources.filterOptions.data.brands"
              :key="brand"
              class="flex items-center gap-2 p-1 hover:bg-gray-50 rounded cursor-pointer"
            >
              <input
                type="checkbox"
                v-model="filters.brands"
                :value="brand"
                class="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
              />
              <span class="text-sm text-gray-700">{{ brand }}</span>
            </label>
          </div>
        </div>

        <!-- Apply Button -->
        <button
          @click="applyFilters"
          class="w-full mt-4 p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium text-sm"
        >
          Apply Filters ({{ totalSelected }})
        </button>
      </div>
    </aside>

    <div class="p-6 pl-16">
      <!-- Lens Prescription Matrix -->
      <div class="bg-white rounded-xl shadow-sm border">
        <div class="p-4">
          <div class="flex items-center gap-4 mb-4">
            <div class="flex items-center gap-2">
              <label class="text-sm text-gray-600">SPH Range:</label>
              <select v-model="sphRange" class="border rounded px-2 py-1 text-sm">
                <option value="full">0.00 to 20.00</option>
                <option value="half">0.00 to 10.00</option>
                <option value="quarter">0.00 to 5.00</option>
              </select>
            </div>
            <div class="flex items-center gap-2">
              <label class="text-sm text-gray-600">CLY Range:</label>
              <select v-model="clyRange" class="border rounded px-2 py-1 text-sm">
                <option value="full">0.00 to 20.00</option>
                <option value="half">0.00 to 10.00</option>
                <option value="quarter">0.00 to 5.00</option>
              </select>
            </div>
          </div>

          <div class="overflow-auto max-h-[600px] border rounded-lg">
            <table class="w-full text-sm">
              <thead class="bg-gray-50 sticky top-0 z-10">
                <tr>
                  <th class="p-2 border sticky left-0 bg-gray-50 z-20 text-xs font-medium text-gray-600 min-w-[60px]">
                    SPH \ CLY
                  </th>
                  <th 
                    v-for="cly in clyValues" 
                    :key="cly"
                    class="p-2 border text-xs font-medium text-gray-600 min-w-[50px] text-center"
                  >
                    {{ cly }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="sph in sphValues" :key="sph" class="hover:bg-gray-50">
                  <td class="p-2 border sticky left-0 bg-gray-50 font-medium text-gray-700 text-center">
                    {{ sph }}
                  </td>
                  <td 
                    v-for="cly in clyValues" 
                    :key="`${sph}-${cly}`"
                    :class="[
                      'p-1 border cursor-pointer transition-colors text-center text-xs font-medium',
                      (matrix[`${sph}-${cly}`]?.qty || 0) <= 0 ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
                    ]"
                    @click="showCellDetails(sph, cly)"
                  >
                    {{ matrix[`${sph}-${cly}`]?.qty || 0 }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Cell Details Modal -->
    <Dialog
      v-model="showDetailsModal"
      :options="{
        title: `Stock Details (SPH ${selectedCell?.sph} \\ CLY ${selectedCell?.cly})`,
        size: 'xl'
      }"
    >
      <template #body-content>
        <div v-if="selectedCell?.items?.length > 0" class="overflow-hidden rounded-lg border">
          <table class="w-full text-sm text-left">
            <thead class="bg-gray-50 text-gray-600 font-medium border-b">
              <tr>
                <th class="p-3">Item Name</th>
                <th class="p-3">Company</th>
                <th class="p-3">Warehouse</th>
                <th class="p-3 text-right">Qty</th>
              </tr>
            </thead>
            <tbody class="divide-y">
              <tr 
                v-for="(item, idx) in selectedCell.items" 
                :key="idx"
                class="hover:bg-gray-50 transition-colors"
              >
                <td class="p-3 font-medium text-gray-900">{{ item.item_name }}</td>
                <td class="p-3 text-gray-600">{{ item.company }}</td>
                <td class="p-3 text-gray-600 text-xs">{{ item.warehouse }}</td>
                <td :class="['p-3 text-right font-bold', item.qty < 0 ? 'text-red-600' : 'text-gray-900']">
                  {{ item.qty }}
                </td>
              </tr>
            </tbody>
            <tfoot class="bg-gray-50 border-t font-black">
              <tr>
                <td colspan="3" class="p-3 text-right text-gray-700">Total Selection</td>
                <td class="p-3 text-right text-blue-600">{{ selectedCell.qty }}</td>
              </tr>
            </tfoot>
          </table>
        </div>
        <div v-else class="py-12 text-center">
          <FeatherIcon name="package" class="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p class="text-gray-500 font-medium">No stock found for this prescription combination.</p>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script>
import { Button, FeatherIcon, Dialog } from 'frappe-ui'

export default {
  name: 'Stock',
  components: {
    Button,
    FeatherIcon,
    Dialog,
  },
  data() {
    return {
      sphRange: 'half',
      clyRange: 'half',
      matrix: {},
      matrixData: {},
      saving: false,
      dirtyCells: new Set(),
      sidebarOpen: false,
      showDetailsModal: false,
      selectedCell: null,
      filters: {
        companies: [],
        warehouses: [],
        groups: [],
        brands: [],
      },
      collapsed: {
        company: true,
        warehouse: true,
        group: true,
        brand: true,
      },
    }
  },
  resources: {
    stockMatrix() {
      return {
        url: 'optilens_app.api.dashboard.get_stock_matrix',
        auto: false,
        makeParams: () => {
          return {
            companies: this.filters.companies,
            warehouses: this.filters.warehouses,
            groups: this.filters.groups,
            brands: this.filters.brands,
          }
        },
        onSuccess: (data) => {
          this.matrixData = data || {}
          // Fill the editable matrix with these values
          this.matrix = { ...this.matrixData }
        },
        onError(error) {
          console.error('Stock Matrix error:', error)
        },
      }
    },
    filterOptions() {
      return {
        url: 'optilens_app.api.dashboard.get_stock_filter_options',
        auto: true,
        initialData: {
          companies: [],
          warehouses: [],
          groups: [],
          brands: [],
        },
        makeParams: () => {
          return {
            companies: this.filters.companies,
          }
        },
        onError(error) {
          console.error('Resource error:', error)
        },
      }
    },
  },
  watch: {
    'filters.companies': {
      handler() {
        // Clear warehouse selections when companies change
        this.filters.warehouses = []
        // Reload filter options to get filtered warehouses
        this.$resources.filterOptions.reload()
      },
      deep: true,
    },
  },
  computed: {
    sphValues() {
      return this.generatePrescriptionValues(this.sphRange)
    },
    clyValues() {
      return this.generatePrescriptionValues(this.clyRange)
    },
    totalSelected() {
      return this.filters.companies.length +
             this.filters.warehouses.length +
             this.filters.groups.length +
             this.filters.brands.length
    },
  },
  methods: {
    generatePrescriptionValues(range) {
      const max = {
        quarter: 5.00,
        half: 10.00,
        full: 20.00,
      }[range] || 20.00
      
      const values = []
      for (let i = 0; i <= max * 4; i++) {
        const val = (i * 0.25).toFixed(2)
        values.push(val)
      }
      return values
    },
    markDirty(sph, cly) {
      this.dirtyCells.add(`${sph}-${cly}`)
    },
    toggleSidebar() {
      this.sidebarOpen = !this.sidebarOpen
    },
    closeSidebar() {
      this.sidebarOpen = false
    },
    toggleAllCompanies() {
      if (this.filters.companies.length === this.$resources.filterOptions.data.companies.length) {
        this.filters.companies = []
      } else {
        this.filters.companies = [...this.$resources.filterOptions.data.companies]
      }
    },
    toggleAllWarehouses() {
      if (this.filters.warehouses.length === this.$resources.filterOptions.data.warehouses.length) {
        this.filters.warehouses = []
      } else {
        this.filters.warehouses = [...this.$resources.filterOptions.data.warehouses]
      }
    },
    toggleAllGroups() {
      if (this.filters.groups.length === this.$resources.filterOptions.data.groups.length) {
        this.filters.groups = []
      } else {
        this.filters.groups = [...this.$resources.filterOptions.data.groups]
      }
    },
    toggleAllBrands() {
      if (this.filters.brands.length === this.$resources.filterOptions.data.brands.length) {
        this.filters.brands = []
      } else {
        this.filters.brands = [...this.$resources.filterOptions.data.brands]
      }
    },
    applyFilters() {
      console.log('Applying filters:', this.filters)
      this.$resources.stockMatrix.fetch()
      this.closeSidebar()
    },
    showCellDetails(sph, cly) {
      const cell = this.matrix[`${sph}-${cly}`] || { qty: 0, items: [] }
      this.selectedCell = {
        sph,
        cly,
        ...cell
      }
      this.showDetailsModal = true
    },
    async saveMatrix() {
      this.saving = true
      try {
        // TODO: Save to backend API
        console.log('Saving matrix data:', this.matrix)
        console.log('Dirty cells:', [...this.dirtyCells])
        this.dirtyCells.clear()
        alert('Stock updated successfully!')
      } catch (error) {
        console.error('Failed to save:', error)
        alert('Failed to save stock')
      } finally {
        this.saving = false
      }
    },
  },
}
</script>
