<template>
  <div class="min-h-screen bg-gray-50 relative">
    <!-- Loading Overlay -->
    <div v-if="$resources.stockMatrix.loading" class="fixed inset-0 bg-white/60 backdrop-blur-[2px] z-[100] flex items-center justify-center transition-all">
      <div class="bg-white p-6 rounded-2xl shadow-2xl flex flex-col items-center gap-4 border border-blue-50">
        <div class="w-12 h-12 border-4 border-blue-100 border-t-blue-600 rounded-full animate-spin"></div>
        <div class="flex flex-col items-center">
          <span class="text-sm font-semibold text-gray-900">Loading Stock Matrix</span>
          <span class="text-xs text-gray-500 animate-pulse">Fetching latest levels...</span>
        </div>
      </div>
    </div>

    <!-- Sidebar Toggle Button -->
    <button
      @click="toggleSidebar"
      class="fixed left-4 top-4 z-30 p-3 bg-blue-600 text-white rounded-xl shadow-lg hover:bg-blue-700 transition-all duration-300"
    >
      <FeatherIcon name="menu" class="w-5 h-5" />
    </button>

    <!-- Sidebar Overlay -->
    <div
      v-if="sidebarOpen || showPeriodDropdown"
      @click="closeSidebar(); closeDropdowns()"
      class="fixed inset-0 bg-black/5 z-40 transition-opacity duration-300"
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
        <!-- Sales Filter -->
        <div>
          <button
            @click="collapsed.sales = !collapsed.sales"
            class="flex items-center justify-between w-full text-left mb-2 hover:bg-gray-50 p-1 rounded"
          >
            <span class="text-sm font-medium text-gray-700">Sales</span>
            <FeatherIcon
              :name="collapsed.sales ? 'chevron-right' : 'chevron-down'"
              class="w-4 h-4 text-gray-500 transition-transform"
            />
          </button>
          <div v-show="!collapsed.sales" class="p-2 space-y-4 transition-all">
            <div class="flex flex-col gap-2">
              <label class="text-[10px] font-bold text-gray-400 uppercase tracking-widest ml-1">Sales Period</label>
              <div class="space-y-3 bg-gray-50/50 p-3 rounded-xl border border-gray-100">
                <!-- Start Date -->
                <div class="space-y-1 relative">
                  <span class="text-[9px] font-bold text-blue-500/70 uppercase ml-1">From</span>
                  <div 
                    @click="openCustomPicker('start')"
                    class="w-full px-3 py-2 text-xs bg-white border border-gray-200 rounded-lg cursor-pointer hover:border-blue-300 transition-all flex justify-between items-center"
                  >
                    <span :class="filters.sales.start ? 'text-gray-900' : 'text-gray-400'">
                      {{ filters.sales.start ? formatDateDisplay(filters.sales.start) : 'Select date & time' }}
                    </span>
                    <FeatherIcon name="calendar" class="w-3.5 h-3.5 text-gray-400" />
                  </div>
                  
                  <!-- Custom Popup for Start Date -->
                  <div v-if="showDatePicker === 'start'" class="fixed left-64 top-1/2 -translate-y-1/2 ml-4 z-[100] bg-white rounded-2xl shadow-2xl border border-gray-100 p-5 w-[320px]">
                    <div class="flex justify-between items-center mb-5 pb-2 border-b">
                      <span class="text-xs font-bold text-gray-900 uppercase tracking-widest">Pick Start Date</span>
                      <button @click.stop="showDatePicker = null" class="p-1 hover:bg-gray-100 rounded-lg">
                        <FeatherIcon name="x" class="w-4 h-4 text-gray-400" />
                      </button>
                    </div>
                    
                    <div class="space-y-6">
                      <!-- Custom Calendar Selection -->
                      <div class="space-y-3">
                        <div class="flex items-center justify-between px-1">
                          <button @click="prevMonth" class="p-1 hover:bg-gray-100 rounded-lg">
                            <FeatherIcon name="chevron-left" class="w-4 h-4 text-gray-600" />
                          </button>
                          <span class="text-xs font-bold text-gray-700">{{ monthName }} {{ currentCalendarYear }}</span>
                          <button @click="nextMonth" class="p-1 hover:bg-gray-100 rounded-lg">
                            <FeatherIcon name="chevron-right" class="w-4 h-4 text-gray-600" />
                          </button>
                        </div>
                        
                        <div class="grid grid-cols-7 gap-1 text-center">
                          <span v-for="d in ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']" :key="d" class="text-[9px] font-bold text-gray-400 uppercase">{{ d }}</span>
                          <template v-for="(day, idx) in calendarDays" :key="idx">
                            <button 
                              v-if="day"
                              @click="selectCalendarDate(day)"
                              :class="[
                                'h-8 w-8 text-[11px] rounded-lg transition-all flex items-center justify-center',
                                tempDateTime.date === `${currentCalendarYear}-${(currentCalendarMonth+1).toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`
                                  ? 'bg-blue-600 text-white font-bold shadow-md shadow-blue-500/30'
                                  : 'text-gray-600 hover:bg-blue-50 hover:text-blue-600'
                              ]"
                            >
                              {{ day }}
                            </button>
                            <div v-else class="h-8 w-8"></div>
                          </template>
                        </div>
                      </div>

                      <!-- Custom Time Selection -->
                      <div class="space-y-3 pt-2 border-t border-gray-100">
                        <label class="text-[10px] font-bold text-gray-400 uppercase tracking-widest ml-1">Time Selection</label>
                        <div class="flex gap-2 items-center">
                          <div class="flex-1 bg-gray-50 rounded-xl p-1 flex items-center">
                            <select v-model="tempDateTime.hours" class="w-full bg-transparent border-none text-xs font-bold text-gray-700 focus:ring-0 cursor-pointer text-center">
                              <option v-for="h in 24" :key="h-1" :value="(h-1).toString().padStart(2, '0')">{{ (h-1).toString().padStart(2, '0') }}</option>
                            </select>
                            <span class="text-gray-400 text-[10px]">:</span>
                            <select v-model="tempDateTime.minutes" class="w-full bg-transparent border-none text-xs font-bold text-gray-700 focus:ring-0 cursor-pointer text-center">
                              <option v-for="m in ['00', '15', '30', '45']" :key="m" :value="m">{{ m }}</option>
                            </select>
                          </div>
                          <div class="px-2 py-2 bg-blue-50 rounded-lg">
                            <FeatherIcon name="clock" class="w-4 h-4 text-blue-600" />
                          </div>
                        </div>
                      </div>
                    </div>

                    <button 
                      @click="commitDateTime('start')"
                      class="w-full mt-8 py-3 bg-blue-600 text-white rounded-xl text-xs font-bold hover:bg-blue-700 transition-all shadow-lg shadow-blue-500/20 active:scale-95"
                    >
                      Apply Selection
                    </button>
                  </div>
                </div>

                <!-- End Date -->
                <div class="space-y-1 relative">
                  <span class="text-[9px] font-bold text-blue-500/70 uppercase ml-1">To</span>
                  <div 
                    @click="openCustomPicker('end')"
                    class="w-full px-3 py-2 text-xs bg-white border border-gray-200 rounded-lg cursor-pointer hover:border-blue-300 transition-all flex justify-between items-center"
                  >
                    <span :class="filters.sales.end ? 'text-gray-900' : 'text-gray-400'">
                      {{ filters.sales.end ? formatDateDisplay(filters.sales.end) : 'Select date & time' }}
                    </span>
                    <FeatherIcon name="calendar" class="w-3.5 h-3.5 text-gray-400" />
                  </div>

                  <!-- Custom Popup for End Date -->
                  <div v-if="showDatePicker === 'end'" class="fixed left-64 top-1/2 -translate-y-1/2 ml-4 z-[100] bg-white rounded-2xl shadow-2xl border border-gray-100 p-5 w-[320px]">
                    <div class="flex justify-between items-center mb-5 pb-2 border-b">
                      <span class="text-xs font-bold text-gray-900 uppercase tracking-widest">Pick End Date</span>
                      <button @click.stop="showDatePicker = null" class="p-1 hover:bg-gray-100 rounded-lg">
                        <FeatherIcon name="x" class="w-4 h-4 text-gray-400" />
                      </button>
                    </div>
                    
                    <div class="space-y-6">
                      <!-- Custom Calendar Selection -->
                      <div class="space-y-3">
                        <div class="flex items-center justify-between px-1">
                          <button @click="prevMonth" class="p-1 hover:bg-gray-100 rounded-lg">
                            <FeatherIcon name="chevron-left" class="w-4 h-4 text-gray-600" />
                          </button>
                          <span class="text-xs font-bold text-gray-700">{{ monthName }} {{ currentCalendarYear }}</span>
                          <button @click="nextMonth" class="p-1 hover:bg-gray-100 rounded-lg">
                            <FeatherIcon name="chevron-right" class="w-4 h-4 text-gray-600" />
                          </button>
                        </div>
                        
                        <div class="grid grid-cols-7 gap-1 text-center">
                          <span v-for="d in ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']" :key="d" class="text-[9px] font-bold text-gray-400 uppercase">{{ d }}</span>
                          <template v-for="(day, idx) in calendarDays" :key="idx">
                            <button 
                              v-if="day"
                              @click="selectCalendarDate(day)"
                              :class="[
                                'h-8 w-8 text-[11px] rounded-lg transition-all flex items-center justify-center',
                                tempDateTime.date === `${currentCalendarYear}-${(currentCalendarMonth+1).toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`
                                  ? 'bg-blue-600 text-white font-bold shadow-md shadow-blue-500/30'
                                  : 'text-gray-600 hover:bg-blue-50 hover:text-blue-600'
                              ]"
                            >
                              {{ day }}
                            </button>
                            <div v-else class="h-8 w-8"></div>
                          </template>
                        </div>
                      </div>

                      <!-- Custom Time Selection -->
                      <div class="space-y-3 pt-2 border-t border-gray-100">
                        <label class="text-[10px] font-bold text-gray-400 uppercase tracking-widest ml-1">Time Selection</label>
                        <div class="flex gap-2 items-center">
                          <div class="flex-1 bg-gray-50 rounded-xl p-1 flex items-center">
                            <select v-model="tempDateTime.hours" class="w-full bg-transparent border-none text-xs font-bold text-gray-700 focus:ring-0 cursor-pointer text-center">
                              <option v-for="h in 24" :key="h-1" :value="(h-1).toString().padStart(2, '0')">{{ (h-1).toString().padStart(2, '0') }}</option>
                            </select>
                            <span class="text-gray-400 text-[10px]">:</span>
                            <select v-model="tempDateTime.minutes" class="w-full bg-transparent border-none text-xs font-bold text-gray-700 focus:ring-0 cursor-pointer text-center">
                              <option v-for="m in ['00', '15', '30', '45']" :key="m" :value="m">{{ m }}</option>
                            </select>
                          </div>
                          <div class="px-2 py-2 bg-blue-50 rounded-lg">
                            <FeatherIcon name="clock" class="w-4 h-4 text-blue-600" />
                          </div>
                        </div>
                      </div>
                    </div>

                    <button 
                      @click="commitDateTime('end')"
                      class="w-full mt-8 py-3 bg-blue-600 text-white rounded-xl text-xs font-bold hover:bg-blue-700 transition-all shadow-lg shadow-blue-500/20 active:scale-95"
                    >
                      Apply Selection
                    </button>
                  </div>
                </div>

                <div class="pt-1 flex gap-2">
                  <button 
                    @click="setQuickDate('today')"
                    class="flex-1 py-1 text-[10px] font-bold bg-white border border-gray-200 text-gray-600 rounded-md hover:border-blue-300 hover:text-blue-600 transition-all"
                  >
                    Today
                  </button>
                  <button 
                    @click="setQuickDate('week')"
                    class="flex-1 py-1 text-[10px] font-bold bg-white border border-gray-200 text-gray-600 rounded-md hover:border-blue-300 hover:text-blue-600 transition-all"
                  >
                    This Week
                  </button>
                </div>

                <!-- Best Sellers Toggle -->
                <div class="pt-2 border-t border-gray-100 mt-2">
                  <label class="flex items-center gap-2 cursor-pointer group">
                    <div class="relative">
                      <input
                        type="checkbox"
                        v-model="filters.sales.getBestSellers"
                        class="sr-only"
                      />
                      <div :class="['w-8 h-4 rounded-full transition-colors duration-200 ease-in-out', filters.sales.getBestSellers ? 'bg-blue-600' : 'bg-gray-200']"></div>
                      <div :class="['absolute left-0.5 top-0.5 w-3 h-3 bg-white rounded-full transition-transform duration-200 ease-in-out shadow-sm', filters.sales.getBestSellers ? 'translate-x-4' : 'translate-x-0']"></div>
                    </div>
                    <span class="text-[10px] font-bold text-gray-600 uppercase tracking-wider group-hover:text-blue-600 transition-colors">Best Sellers Only</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>

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
            <input
              v-model="searchQueries.company"
              type="text"
              placeholder="Search Company..."
              class="w-full mb-2 p-1.5 text-xs border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <label class="flex items-center gap-2 p-1 hover:bg-gray-50 rounded cursor-pointer font-medium">
              <input
                type="checkbox"
                :checked="filters.companies.length === $resources.filterOptions.data.companies.length && $resources.filterOptions.data.companies.length > 0"
                @change="toggleAllCompanies"
                class="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
              />
              <span class="text-sm text-gray-700">All</span>
            </label>
            <label
              v-for="company in filteredOptions.companies"
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
            <template v-else>
              <input
                v-model="searchQueries.warehouse"
                type="text"
                placeholder="Search Warehouse..."
                class="w-full mb-2 p-1.5 text-xs border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <label class="flex items-center gap-2 p-1 hover:bg-gray-50 rounded cursor-pointer font-medium">
                <input
                  type="checkbox"
                  :checked="filters.warehouses.length === $resources.filterOptions.data.warehouses.length && $resources.filterOptions.data.warehouses.length > 0"
                  @change="toggleAllWarehouses"
                  class="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                />
                <span class="text-sm text-gray-700">All</span>
              </label>
              <label
                v-for="warehouse in filteredOptions.warehouses"
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
            </template>
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
            <input
              v-model="searchQueries.group"
              type="text"
              placeholder="Search Group..."
              class="w-full mb-2 p-1.5 text-xs border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <label class="flex items-center gap-2 p-1 hover:bg-gray-50 rounded cursor-pointer font-medium">
              <input
                type="checkbox"
                :checked="filters.groups.length === $resources.filterOptions.data.groups.length && $resources.filterOptions.data.groups.length > 0"
                @change="toggleAllGroups"
                class="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
              />
              <span class="text-sm text-gray-700">All</span>
            </label>
            <label
              v-for="group in filteredOptions.groups"
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
            <input
              v-model="searchQueries.brand"
              type="text"
              placeholder="Search Brand..."
              class="w-full mb-2 p-1.5 text-xs border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <label class="flex items-center gap-2 p-1 hover:bg-gray-50 rounded cursor-pointer font-medium">
              <input
                type="checkbox"
                :checked="filters.brands.length === $resources.filterOptions.data.brands.length && $resources.filterOptions.data.brands.length > 0"
                @change="toggleAllBrands"
                class="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
              />
              <span class="text-sm text-gray-700">All</span>
            </label>
            <label
              v-for="brand in filteredOptions.brands"
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
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-6 flex-wrap">
              <div class="flex items-center gap-2">
                <label class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Signs:</label>
                <div class="flex items-center bg-gray-100 p-0.5 rounded-lg border">
                  <button 
                    v-for="type in ['+/+', '-/-', '+/-', '-/+']" 
                    :key="type"
                    @click="matrixType = type; applyFilters()"
                    :class="[
                      'px-3 py-1 text-xs font-bold rounded-md transition-all whitespace-nowrap',
                      matrixType === type ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'
                    ]"
                  >
                    {{ type }}
                  </button>
                </div>
              </div>

              <div class="flex items-center gap-2">
                <label class="text-xs font-semibold text-gray-500 uppercase tracking-wider">SPH:</label>
                <select v-model="sphRange" class="border rounded-lg px-2 py-1 text-sm bg-gray-50 focus:ring-2 focus:ring-blue-500 outline-none transition-all">
                  <option value="full">20.00</option>
                  <option value="half">10.00</option>
                  <option value="quarter">5.00</option>
                </select>
              </div>

              <div class="flex items-center gap-2">
                <label class="text-xs font-semibold text-gray-500 uppercase tracking-wider">CLY:</label>
                <select v-model="clyRange" class="border rounded-lg px-2 py-1 text-sm bg-gray-50 focus:ring-2 focus:ring-blue-500 outline-none transition-all">
                  <option value="full">20.00</option>
                  <option value="half">10.00</option>
                  <option value="quarter">5.00</option>
                </select>
              </div>

              <div class="h-6 w-px bg-gray-200 mx-1"></div>

              <div class="flex items-center gap-4">
                <label class="flex items-center gap-2 cursor-pointer group">
                  <div class="relative">
                    <input
                      type="checkbox"
                      v-model="matrixFilters.isEnough"
                      class="sr-only"
                    />
                    <div :class="['w-8 h-4 rounded-full transition-colors duration-200 ease-in-out', matrixFilters.isEnough ? 'bg-green-600' : 'bg-gray-200']"></div>
                    <div :class="['absolute left-0.5 top-0.5 w-3 h-3 bg-white rounded-full transition-transform duration-200 ease-in-out shadow-sm', matrixFilters.isEnough ? 'translate-x-4' : 'translate-x-0']"></div>
                  </div>
                  <span class="text-xs font-bold text-gray-600 uppercase tracking-wider group-hover:text-green-600 transition-colors">Is Enough</span>
                </label>

                <div class="flex items-center gap-2">
                  <label class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Period:</label>
                  <div class="flex items-center bg-gray-50 border rounded-lg px-2 py-1 gap-1 focus-within:ring-2 focus-within:ring-blue-500 transition-all relative">
                    <input 
                      v-model.number="matrixFilters.periodValue"
                      type="number" 
                      min="1"
                      class="w-12 bg-transparent border-none text-sm font-bold text-gray-700 focus:ring-0 p-0 text-center"
                    />
                    
                    <!-- Custom Dropdown -->
                    <div class="relative">
                      <button 
                        @click.stop="showPeriodDropdown = !showPeriodDropdown"
                        class="flex items-center gap-1 px-1.5 py-0.5 hover:bg-blue-50 rounded transition-colors group/unit"
                      >
                        <span class="text-[10px] font-bold text-blue-600 uppercase">{{ matrixFilters.periodUnit }}</span>
                        <FeatherIcon 
                          name="chevron-down" 
                          :class="['w-2.5 h-2.5 text-blue-400 transition-transform duration-200', showPeriodDropdown ? 'rotate-180' : '']"
                        />
                      </button>

                      <!-- Dropdown Menu -->
                      <div 
                        v-if="showPeriodDropdown"
                        class="absolute right-0 top-full mt-1.5 z-[110] bg-white rounded-xl shadow-2xl border border-gray-100 py-1.5 min-w-[100px] overflow-hidden animate-in fade-in zoom-in-95 duration-100"
                      >
                        <button 
                          v-for="unit in ['days', 'months', 'years']" 
                          :key="unit"
                          @click="matrixFilters.periodUnit = unit; showPeriodDropdown = false"
                          :class="[
                            'w-full px-3 py-1.5 text-left text-[10px] font-bold uppercase transition-colors flex items-center justify-between',
                            matrixFilters.periodUnit === unit ? 'bg-blue-50 text-blue-600' : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700'
                          ]"
                        >
                          {{ unit }}
                          <FeatherIcon v-if="matrixFilters.periodUnit === unit" name="check" class="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <button 
              @click="exportToExcel"
              class="flex items-center gap-2 px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-xs font-bold shadow-sm"
            >
              <FeatherIcon name="download" class="w-4 h-4" />
              Export to XL
            </button>
          </div>

          <div class="overflow-auto max-h-[600px] border rounded-lg shadow-inner">
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
                    :class="getCellClass(sph, cly)"
                    @click="showCellDetails(sph, cly)"
                  >
                    {{ matrix[`${sph}-${cly}`]?.qty || 0 }}
                    <!-- Best Sell Qty Badge -->
                    <span 
                      v-if="filters.sales.getBestSellers && (matrix[`${sph}-${cly}`]?.best_sell_qty || 0) > 0"
                      class="absolute top-0 right-0 bg-purple-600 text-white text-[9px] px-1 rounded-bl leading-tight font-bold shadow-sm"
                      title="Best Monthly Sale (Last 1 Year)"
                    >
                      {{ matrix[`${sph}-${cly}`]?.best_sell_qty }}
                    </span>
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
          <table class="w-full text-sm text-left table-fixed">
            <thead class="bg-gray-50 text-gray-600 font-medium border-b">
              <tr>
                <th class="p-3 w-[30%]">Item Name</th>
                <th class="p-3 w-[20%]">Company</th>
                <th class="p-3 w-[20%]">Warehouse</th>
                <th class="p-3 text-right w-[7%]">Qty</th>
                <th v-if="filters.sales.getBestSellers" class="p-3 text-right text-blue-600 w-[7%]">Sold</th>
                <th v-if="filters.sales.getBestSellers" class="p-3 text-right text-purple-600 w-[16%]">Best Month</th>
              </tr>
            </thead>
            <tbody class="divide-y">
              <tr 
                v-for="(item, idx) in selectedCell.items" 
                :key="idx"
                class="hover:bg-gray-50 transition-colors"
              >
                <td class="p-3 font-medium text-gray-900 truncate" :title="item.item_name">{{ item.item_name }}</td>
                <td class="p-3 text-gray-600 truncate" :title="item.company">{{ item.company }}</td>
                <td class="p-3 text-gray-600 text-xs truncate" :title="item.warehouse">{{ item.warehouse }}</td>
                <td :class="['p-3 text-right font-bold', item.qty < 0 ? 'text-red-600' : 'text-gray-900']">
                  {{ item.qty }}
                </td>
                <td v-if="filters.sales.getBestSellers" class="p-3 text-right font-bold text-blue-600">
                  {{ item.sold_qty || 0 }}
                </td>
                <td v-if="filters.sales.getBestSellers" class="p-3 text-right font-bold text-purple-600">
                  <div v-if="item.best_sell_qty > 0" class="flex flex-col items-end leading-tight">
                    <span>{{ item.best_sell_qty }}</span>
                    <span class="text-[9px] text-purple-400 font-medium uppercase">{{ formatMonthOnly(item.best_sell_month) }}</span>
                  </div>
                  <span v-else>-</span>
                </td>
              </tr>
            </tbody>
            <tfoot class="bg-gray-50 border-t font-black">
              <tr>
                <td colspan="3" class="p-3 text-right text-gray-700">Total Selection</td>
                <td class="p-3 text-right text-blue-600">{{ selectedCell.qty }}</td>
                <td v-if="filters.sales.getBestSellers" class="p-3 text-right text-blue-600 border-l border-gray-200">
                  {{ selectedCell.sold_qty }}
                </td>
                <td v-if="filters.sales.getBestSellers" class="p-3 text-right text-purple-600 border-l border-gray-200">
                  {{ selectedCell.best_sell_qty }}
                </td>
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
      matrixType: '+/+', // New matrix sign filter
      matrix: {},
      matrixData: {},
      saving: false,
      dirtyCells: new Set(),
      sidebarOpen: false,
      showDetailsModal: false,
      selectedCell: null,
      showDatePicker: null, // 'start' or 'end' or null
      currentCalendarMonth: new Date().getMonth(),
      currentCalendarYear: new Date().getFullYear(),
      tempDateTime: {
        date: '',
        hours: '00',
        minutes: '00'
      },
      searchQueries: {
        company: '',
        warehouse: '',
        group: '',
        brand: '',
      },
      filters: {
        companies: [],
        warehouses: [],
        groups: [],
        brands: [],
        sales: {
          start: '',
          end: '',
          getBestSellers: false,
        },
      },
      collapsed: {
        sales: false,
        company: true,
        warehouse: true,
        group: true,
        brand: true,
      },
      matrixFilters: {
        isEnough: false,
        periodValue: 30,
        periodUnit: 'days'
      },
      showPeriodDropdown: false,
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
            matrix_type: this.matrixType, // Pass the sign type to backend
            sales_start: this.filters.sales.start,
            sales_end: this.filters.sales.end,
            include_sales_data: this.filters.sales.getBestSellers ? 1 : 0,
            is_enough: this.matrixFilters.isEnough ? 1 : 0,
            period_value: this.matrixFilters.periodValue,
            period_unit: this.matrixFilters.periodUnit,
          }
        },
        onSuccess: (data) => {
          console.log('Stock Matrix data:', data)
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
    calendarDays() {
      const daysInMonth = new Date(this.currentCalendarYear, this.currentCalendarMonth + 1, 0).getDate()
      const firstDayOfMonth = new Date(this.currentCalendarYear, this.currentCalendarMonth, 1).getDay()
      
      const days = []
      // Padding for first week
      for (let i = 0; i < firstDayOfMonth; i++) {
        days.push(null)
      }
      // Actual days
      for (let i = 1; i <= daysInMonth; i++) {
        days.push(i)
      }
      return days
    },
    monthName() {
      return new Intl.DateTimeFormat('en-US', { month: 'long' }).format(new Date(this.currentCalendarYear, this.currentCalendarMonth))
    },
    totalSelected() {
      return this.filters.companies.length +
             this.filters.warehouses.length +
             this.filters.groups.length +
             this.filters.brands.length
    },
    filteredOptions() {
      const options = this.$resources.filterOptions.data || { companies: [], warehouses: [], groups: [], brands: [] }
      return {
        companies: options.companies.filter(i => i.toLowerCase().includes(this.searchQueries.company.toLowerCase())),
        warehouses: options.warehouses.filter(i => i.toLowerCase().includes(this.searchQueries.warehouse.toLowerCase())),
        groups: options.groups.filter(i => i.toLowerCase().includes(this.searchQueries.group.toLowerCase())),
        brands: options.brands.filter(i => i.toLowerCase().includes(this.searchQueries.brand.toLowerCase())),
      }
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
    isEnough(cell) {
      if (!cell || !this.matrixFilters.isEnough) return null
      
      const qty = cell.qty || 0
      const bestSell = cell.best_sell_qty || 0
      
      // Calculate multiplier to convert period to months (since bestSell is monthly)
      let multiplier = 0
      if (this.matrixFilters.periodUnit === 'days') {
        multiplier = this.matrixFilters.periodValue / 30
      } else if (this.matrixFilters.periodUnit === 'months') {
        multiplier = this.matrixFilters.periodValue
      } else if (this.matrixFilters.periodUnit === 'years') {
        multiplier = this.matrixFilters.periodValue * 12
      }
      
      const neededQty = bestSell * multiplier
      
      // Stock is enough if it is greater than or equal to the needed quantity
      return qty >= neededQty
    },
    getCellClass(sph, cly) {
      const cell = this.matrix[`${sph}-${cly}`]
      const qty = cell?.qty || 0
      
      const baseClass = 'p-1 border cursor-pointer transition-colors text-center text-xs font-medium relative'
      
      // If "Is Enough" filter is ON
      if (this.matrixFilters.isEnough) {
        const enough = this.isEnough(cell)
        if (enough === true) return `${baseClass} bg-green-100 text-green-700`
        if (enough === false) return `${baseClass} bg-red-100 text-red-700`
      }
      
      // Default color logic (Stock > 0)
      return qty <= 0 
        ? `${baseClass} bg-red-100 text-red-700` 
        : `${baseClass} bg-green-100 text-green-700`
    },
    toggleSidebar() {
      this.sidebarOpen = !this.sidebarOpen
    },
    closeSidebar() {
      this.sidebarOpen = false
    },
    closeDropdowns() {
      this.showPeriodDropdown = false
      this.showDatePicker = null
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
    exportToExcel() {
      if (!this.matrixData || Object.keys(this.matrixData).length === 0) {
        alert('No data to export')
        return
      }

      const fileName = `Stock_Matrix_${this.matrixType.replace('/', '_')}_${new Date().toISOString().slice(0, 10)}.xls`

      // XML Spreadsheet 2003 template
      let xml = `<?xml version="1.0"?>
<?mso-application progid="Excel.Sheet"?>
<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"
 xmlns:o="urn:schemas-microsoft-com:office:office"
 xmlns:x="urn:schemas-microsoft-com:office:excel"
 xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet"
 xmlns:html="http://www.w3.org/TR/REC-html40">
 <Styles>
  <Style ss:ID="Default" ss:Name="Normal">
   <Alignment ss:Vertical="Bottom"/>
   <Borders/>
   <Font ss:FontName="Calibri" x:Family="Swiss" ss:Size="11" ss:Color="#000000"/>
   <Interior/>
   <NumberFormat/>
   <Protection/>
  </Style>
  <Style ss:ID="Header">
   <Alignment ss:Horizontal="Center" ss:Vertical="Center"/>
   <Borders>
    <Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="1"/>
    <Border ss:Position="Left" ss:LineStyle="Continuous" ss:Weight="1"/>
    <Border ss:Position="Right" ss:LineStyle="Continuous" ss:Weight="1"/>
    <Border ss:Position="Top" ss:LineStyle="Continuous" ss:Weight="1"/>
   </Borders>
   <Font ss:FontName="Calibri" x:Family="Swiss" ss:Size="11" ss:Color="#495057" ss:Bold="1"/>
   <Interior ss:Color="#F8F9FA" ss:Pattern="Solid"/>
  </Style>
  <Style ss:ID="StockPos">
   <Alignment ss:Horizontal="Center" ss:Vertical="Center"/>
   <Borders>
    <Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="1"/>
    <Border ss:Position="Left" ss:LineStyle="Continuous" ss:Weight="1"/>
    <Border ss:Position="Right" ss:LineStyle="Continuous" ss:Weight="1"/>
    <Border ss:Position="Top" ss:LineStyle="Continuous" ss:Weight="1"/>
   </Borders>
   <Font ss:FontName="Calibri" x:Family="Swiss" ss:Size="11" ss:Color="#065F46"/>
   <Interior ss:Color="#D1FAE5" ss:Pattern="Solid"/>
   <NumberFormat ss:Format="0.00"/>
  </Style>
  <Style ss:ID="StockNeg">
   <Alignment ss:Horizontal="Center" ss:Vertical="Center"/>
   <Borders>
    <Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="1"/>
    <Border ss:Position="Left" ss:LineStyle="Continuous" ss:Weight="1"/>
    <Border ss:Position="Right" ss:LineStyle="Continuous" ss:Weight="1"/>
    <Border ss:Position="Top" ss:LineStyle="Continuous" ss:Weight="1"/>
   </Borders>
   <Font ss:FontName="Calibri" x:Family="Swiss" ss:Size="11" ss:Color="#991B1B"/>
   <Interior ss:Color="#FEE2E2" ss:Pattern="Solid"/>
   <NumberFormat ss:Format="0.00"/>
  </Style>
 </Styles>
 <Worksheet ss:Name="${this.matrixType}">
  <Table>
   <Column ss:Width="80"/>
   ${this.clyValues.map(() => '<Column ss:Width="50"/>').join('')}
   <Row ss:Height="20">
    <Cell ss:StyleID="Header"><Data ss:Type="String">SPH \\ CLY</Data></Cell>
    ${this.clyValues.map(cly => `<Cell ss:StyleID="Header"><Data ss:Type="String">${cly}</Data></Cell>`).join('')}
   </Row>
   ${this.sphValues.map(sph => `
   <Row ss:Height="18">
    <Cell ss:StyleID="Header"><Data ss:Type="String">${sph}</Data></Cell>
    ${this.clyValues.map(cly => {
      const qty = this.matrixData[`${sph}-${cly}`]?.qty || 0
      const style = qty > 0 ? 'StockPos' : 'StockNeg'
      return `<Cell ss:StyleID="${style}"><Data ss:Type="Number">${qty}</Data></Cell>`
    }).join('')}
   </Row>`).join('')}
  </Table>
 </Worksheet>
</Workbook>`

      const blob = new Blob([xml], { type: 'application/vnd.ms-excel' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.setAttribute('href', url)
      link.setAttribute('download', fileName)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
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
        best_sell_qty: cell.best_sell_qty,
        sold_qty: cell.sold_qty,
        qty: cell.qty,
        items: cell.items
      }
      this.showDetailsModal = true
    },
    setQuickDate(range) {
      const now = new Date()
      const format = (d) => d.toISOString().slice(0, 16)
      
      if (range === 'today') {
        const start = new Date(now)
        start.setHours(0, 0, 0, 0)
        const end = new Date(now)
        end.setHours(23, 59, 59, 999)
        this.filters.sales.start = format(start)
        this.filters.sales.end = format(end)
      } else if (range === 'week') {
        const start = new Date(now)
        start.setDate(now.getDate() - now.getDay())
        start.setHours(0, 0, 0, 0)
        const end = new Date(now)
        end.setHours(23, 59, 59, 999)
        this.filters.sales.start = format(start)
        this.filters.sales.end = format(end)
      }
    },
    formatDateDisplay(isoString) {
      if (!isoString) return ''
      const date = new Date(isoString)
      return date.toLocaleDateString(undefined, { 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    formatMonthOnly(isoString) {
      if (!isoString) return ''
      const date = new Date(isoString)
      return date.toLocaleDateString(undefined, { 
        month: 'long', 
        year: 'numeric'
      })
    },
    openCustomPicker(type) {
      this.showDatePicker = type
      const current = this.filters.sales[type]
      if (current) {
        const [date, time] = current.split('T')
        const [hours, minutes] = (time || '00:00').split(':')
        this.tempDateTime = { 
          date: date || new Date().toISOString().split('T')[0], 
          hours: hours || '00', 
          minutes: minutes || '00' 
        }
      } else {
        const now = new Date()
        this.tempDateTime = {
          date: now.toISOString().split('T')[0],
          hours: now.getHours().toString().padStart(2, '0'),
          minutes: '00'
        }
      }
      
      // Initialize calendar if not set
      if (!this.currentCalendarMonth) {
        const d = new Date(this.tempDateTime.date)
        this.currentCalendarMonth = d.getMonth()
        this.currentCalendarYear = d.getFullYear()
      }
    },
    prevMonth() {
      if (this.currentCalendarMonth === 0) {
        this.currentCalendarMonth = 11
        this.currentCalendarYear--
      } else {
        this.currentCalendarMonth--
      }
    },
    nextMonth() {
      if (this.currentCalendarMonth === 11) {
        this.currentCalendarMonth = 0
        this.currentCalendarYear++
      } else {
        this.currentCalendarMonth++
      }
    },
    selectCalendarDate(day) {
      const date = new Date(this.currentCalendarYear, this.currentCalendarMonth, day)
      // Adjust for timezone to get correct YYYY-MM-DD
      const offset = date.getTimezoneOffset()
      const adjustedDate = new Date(date.getTime() - (offset * 60 * 1000))
      this.tempDateTime.date = adjustedDate.toISOString().split('T')[0]
    },
    commitDateTime(type) {
      if (!this.tempDateTime.date) {
        alert('Please select a date')
        return
      }
      this.filters.sales[type] = `${this.tempDateTime.date}T${this.tempDateTime.hours}:${this.tempDateTime.minutes}`
      this.showDatePicker = null
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

<style scoped>
.custom-datetime-input::-webkit-calendar-picker-indicator {
  cursor: pointer;
  border-radius: 4px;
  margin-right: -4px;
  padding: 2px;
  filter: invert(48%) sepia(79%) saturate(2718%) hue-rotate(192deg) brightness(101%) contrast(101%);
}

.custom-datetime-input::-webkit-calendar-picker-indicator:hover {
  background-color: rgba(59, 130, 246, 0.1);
}
</style>
