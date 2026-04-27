<template>
  <div class="bg-white rounded-lg shadow-sm border p-4">
    <div class="flex items-start justify-between">
      <div>
        <p class="text-sm text-gray-500 mb-1">{{ title }}</p>
        <p class="text-2xl font-bold text-gray-900">
          {{ prefix }}{{ formattedValue }}
        </p>
        <div v-if="trend !== undefined && trend !== 0" class="flex items-center gap-1 mt-1">
          <FeatherIcon 
            :name="trend > 0 ? 'trending-up' : 'trending-down'" 
            class="w-3 h-3"
            :class="trend > 0 ? 'text-green-500' : 'text-red-500'"
          />
          <span 
            class="text-xs"
            :class="trend > 0 ? 'text-green-600' : 'text-red-600'"
          >
            {{ Math.abs(trend) }}%
          </span>
          <span class="text-xs text-gray-400">vs yesterday</span>
        </div>
      </div>
      <div 
        class="w-12 h-12 rounded-lg flex items-center justify-center"
        :class="iconBgClass"
      >
        <FeatherIcon :name="icon" class="w-6 h-6" :class="iconColorClass" />
      </div>
    </div>
    <div v-if="alert" class="mt-3 flex items-center gap-2 text-sm text-red-600">
      <FeatherIcon name="alert-circle" class="w-4 h-4" />
      <span>Requires attention</span>
    </div>
  </div>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'

export default {
  name: 'StatCard',
  components: {
    FeatherIcon,
  },
  props: {
    title: {
      type: String,
      required: true,
    },
    value: {
      type: Number,
      default: 0,
    },
    prefix: {
      type: String,
      default: '',
    },
    icon: {
      type: String,
      required: true,
    },
    color: {
      type: String,
      default: 'blue',
      validator: (value) => ['blue', 'green', 'red', 'purple', 'orange', 'gray'].includes(value),
    },
    trend: {
      type: Number,
      default: 0,
    },
    alert: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    formattedValue() {
      if (this.value >= 1000000) {
        return (this.value / 1000000).toFixed(1) + 'M'
      }
      if (this.value >= 1000) {
        return (this.value / 1000).toFixed(1) + 'K'
      }
      return this.value.toLocaleString()
    },
    iconBgClass() {
      const classes = {
        blue: 'bg-blue-100',
        green: 'bg-green-100',
        red: 'bg-red-100',
        purple: 'bg-purple-100',
        orange: 'bg-orange-100',
        gray: 'bg-gray-100',
      }
      return classes[this.color]
    },
    iconColorClass() {
      const classes = {
        blue: 'text-blue-600',
        green: 'text-green-600',
        red: 'text-red-600',
        purple: 'text-purple-600',
        orange: 'text-orange-600',
        gray: 'text-gray-600',
      }
      return classes[this.color]
    },
  },
}
</script>
