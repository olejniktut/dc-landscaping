import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { guest: true }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/properties',
    name: 'Properties',
    component: () => import('@/views/PropertiesView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/workers',
    name: 'Workers',
    component: () => import('@/views/WorkersView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/records',
    name: 'Records',
    component: () => import('@/views/RecordsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('@/views/ReportsView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      return next('/login')
    }
    
    // Check if route requires admin
    if (to.meta.requiresAdmin && !authStore.isAdmin) {
      return next('/')
    }
  }
  
  // Redirect authenticated users away from login
  if (to.meta.guest && authStore.isAuthenticated) {
    return next('/')
  }
  
  next()
})

export default router
