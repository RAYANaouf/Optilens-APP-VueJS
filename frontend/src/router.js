import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/pages/Dashboard.vue'),
  },
  {
    path: '/pos',
    name: 'POS',
    component: () => import('@/pages/POS.vue'),
  },
  {
    path: '/stock',
    name: 'Stock',
    component: () => import('@/pages/Stock.vue'),
  },
  {
    path: '/pricing',
    name: 'Pricing',
    component: () => import('@/pages/Pricing.vue'),
  },
]

let router = createRouter({
  history: createWebHistory(import.meta.env.PROD ? '/frontend/' : '/'),
  routes,
})

export default router
