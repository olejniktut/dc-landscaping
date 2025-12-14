<template>
  <div class="min-h-screen bg-gradient-to-br from-green-800 to-green-600 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md">
      <div class="text-center mb-8">
        <div class="w-20 h-20 bg-green-600 rounded-full mx-auto mb-4 flex items-center justify-center">
          <span class="text-4xl">🌿</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-800">DC Landscaping</h1>
        <p class="text-gray-500 mt-1">Time Tracking System</p>
      </div>
      
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Username</label>
          <input
            v-model="username"
            type="text"
            class="w-full"
            placeholder="Enter username"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
          <input
            v-model="password"
            type="password"
            class="w-full"
            placeholder="Enter password"
            @keyup.enter="handleLogin"
          />
        </div>
        
        <p v-if="error" class="text-red-500 text-sm bg-red-50 p-3 rounded-lg">
          ❌ {{ error }}
        </p>
        
        <button
          @click="handleLogin"
          :disabled="loading"
          class="btn btn-primary w-full py-3"
        >
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  if (!username.value || !password.value) {
    error.value = 'Please enter username and password'
    return
  }
  
  loading.value = true
  error.value = ''
  
  const result = await authStore.login(username.value, password.value)
  
  loading.value = false
  
  if (result.success) {
    router.push('/')
  } else {
    error.value = result.error || 'Invalid username or password'
  }
}
</script>