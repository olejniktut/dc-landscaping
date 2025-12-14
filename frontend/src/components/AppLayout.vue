<template>
  <div class="min-h-screen bg-gray-50 flex">
    <!-- Sidebar -->
    <aside 
      class="fixed lg:static inset-y-0 left-0 z-40 w-64 bg-white shadow-lg flex flex-col transform transition-transform lg:transform-none"
      :class="{ '-translate-x-full': !sidebarOpen }"
    >
      <div class="p-6 border-b">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-green-600 rounded-full flex items-center justify-center">
            <span class="text-xl">🌿</span>
          </div>
          <div>
            <h1 class="font-bold text-gray-800">DC Landscaping</h1>
            <p class="text-xs text-gray-500 capitalize">{{ authStore.user?.role }}</p>
          </div>
        </div>
      </div>
      
      <nav class="flex-1 p-4 space-y-2">
        <router-link 
          v-for="item in navItems" 
          :key="item.path"
          :to="item.path"
          class="flex items-center gap-3 w-full px-4 py-3 rounded-lg transition"
          :class="[
            $route.path === item.path 
              ? 'bg-green-600 text-white' 
              : 'text-gray-600 hover:bg-gray-100'
          ]"
          @click="sidebarOpen = false"
        >
          <span class="text-xl">{{ item.icon }}</span>
          <span class="font-medium">{{ item.label }}</span>
        </router-link>
      </nav>
      
      <div class="p-4 border-t">
        <button
          @click="handleLogout"
          class="flex items-center gap-3 w-full px-4 py-3 text-red-600 hover:bg-red-50 rounded-lg transition"
        >
          <span>🚪</span>
          <span class="font-medium">Logout</span>
        </button>
      </div>
    </aside>

    <!-- Mobile sidebar overlay -->
    <div 
      v-if="sidebarOpen"
      class="fixed inset-0 bg-black/50 z-30 lg:hidden"
      @click="sidebarOpen = false"
    />

    <!-- Main Content -->
    <div class="flex-1 flex flex-col min-h-screen">
      <!-- Mobile header -->
      <header class="lg:hidden bg-white shadow-sm p-4 flex items-center gap-4">
        <button @click="sidebarOpen = true" class="text-gray-600">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <h1 class="font-bold text-gray-800">DC Landscaping</h1>
      </header>

      <!-- Page content -->
      <main class="flex-1 p-4 lg:p-8 overflow-auto">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const sidebarOpen = ref(false)

const navItems = computed(() => {
  const items = [
    { path: '/', icon: '🏠', label: 'Dashboard' },
    { path: '/properties', icon: '📍', label: 'Properties' },
    { path: '/workers', icon: '👷', label: 'Workers' },
    { path: '/records', icon: '📋', label: 'Time Records' },
  ]
  
  if (authStore.isAdmin) {
    items.push({ path: '/reports', icon: '📊', label: 'Reports' })
  }
  
  return items
})

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>
