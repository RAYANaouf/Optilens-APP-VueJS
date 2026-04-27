<template>
  <button 
    @click="$emit('click')"
    class="w-full flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:border-gray-300 hover:bg-gray-50 transition-all duration-200 group"
  >
    <div 
      class="w-10 h-10 rounded-lg flex items-center justify-center transition-colors"
      :class="iconBgClass"
    >
      <FeatherIcon 
        :name="icon" 
        class="w-5 h-5 transition-colors"
        :class="iconColorClass"
      />
    </div>
    <div class="text-left flex-1">
      <p class="font-medium text-gray-900 group-hover:text-gray-700">{{ title }}</p>
      <p class="text-xs text-gray-500">{{ description }}</p>
    </div>
    <FeatherIcon 
      name="chevron-right" 
      class="w-4 h-4 text-gray-300 group-hover:text-gray-400"
    />
  </button>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'

export default {
  name: 'QuickAction',
  components: {
    FeatherIcon,
  },
  props: {
    title: {
      type: String,
      required: true,
    },
    description: {
      type: String,
      required: true,
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
  },
  computed: {
    iconBgClass() {
      const classes = {
        blue: 'bg-blue-100 group-hover:bg-blue-200',
        green: 'bg-green-100 group-hover:bg-green-200',
        red: 'bg-red-100 group-hover:bg-red-200',
        purple: 'bg-purple-100 group-hover:bg-purple-200',
        orange: 'bg-orange-100 group-hover:bg-orange-200',
        gray: 'bg-gray-100 group-hover:bg-gray-200',
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
