<template>
  <AppLayout>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-800">Workers</h2>
      <button @click="openModal()" class="btn btn-primary flex items-center gap-2">
        <span>+</span> Add Worker
      </button>
    </div>

    <!-- Search -->
    <div class="mb-4">
      <input 
        v-model="searchQuery" 
        type="text" 
        placeholder="🔍 Search workers..." 
        class="w-full md:w-80"
      />
    </div>

    <div v-if="filteredWorkers.length === 0" class="card p-8 text-center text-gray-500">
      No workers found.
    </div>

    <div v-else class="card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="text-left px-6 py-4 text-sm font-medium text-gray-500">Name</th>
              <th class="text-left px-6 py-4 text-sm font-medium text-gray-500">Phone</th>
              <th class="text-left px-6 py-4 text-sm font-medium text-gray-500">Rate/hr</th>
              <th class="text-left px-6 py-4 text-sm font-medium text-gray-500">Status</th>
              <th class="text-right px-6 py-4 text-sm font-medium text-gray-500">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y">
            <tr v-for="worker in filteredWorkers" :key="worker.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 font-medium text-gray-800">{{ worker.name }}</td>
              <td class="px-6 py-4 text-gray-600">{{ worker.phone || '-' }}</td>
              <td class="px-6 py-4 text-gray-600">{{ parseFloat(worker.hourly_rate).toFixed(2) }}</td>
              <td class="px-6 py-4">
                <span 
                  class="px-2 py-1 rounded text-xs"
                  :class="worker.is_active 
                    ? 'bg-green-100 text-green-700' 
                    : 'bg-gray-100 text-gray-600'"
                >
                  {{ worker.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="px-6 py-4 text-right">
                <button @click="openModal(worker)" class="text-blue-600 hover:text-blue-800 mr-3">
                  Edit
                </button>
                <button @click="deleteWorker(worker)" class="text-red-600 hover:text-red-800">
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Worker Modal -->
    <div v-if="showModal" class="modal-backdrop" @click.self="showModal = false">
      <div class="modal-content">
        <h3 class="text-xl font-bold text-gray-800 mb-4">
          {{ editingWorker ? 'Edit Worker' : 'Add Worker' }}
        </h3>
        
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input v-model="form.name" type="text" required placeholder="Short name" />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Phone (optional)</label>
            <input v-model="form.phone" type="tel" placeholder="204-555-0100" />
          </div>
          
          <div v-if="authStore.isAdmin">
            <label class="block text-sm font-medium text-gray-700 mb-1">Hourly Rate</label>
            <input v-model.number="form.hourly_rate" type="number" step="0.01" min="0" />
          </div>
          
          <div class="flex items-center gap-2">
            <input v-model="form.is_active" type="checkbox" id="active" class="w-4 h-4" />
            <label for="active" class="text-sm text-gray-700">Active</label>
          </div>

          <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>
<div class="flex gap-3">
            <button type="button" @click="showModal = false" class="btn btn-secondary flex-1">
              Cancel
            </button>
            <button type="submit" :disabled="loading" class="btn btn-primary flex-1">
              {{ loading ? 'Saving...' : (editingWorker ? 'Save Changes' : 'Add Worker') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'
import { workersApi } from '@/api'

const appStore = useAppStore()
const authStore = useAuthStore()

const showModal = ref(false)
const editingWorker = ref(null)
const loading = ref(false)
const error = ref('')
const searchQuery = ref('')

const form = ref({
  name: '',
  phone: '',
  hourly_rate: 20,
  is_active: true
})

const filteredWorkers = computed(() => {
  const search = searchQuery.value.toLowerCase().trim()
  if (!search) return appStore.workers
  
  return appStore.workers.filter(w => 
    w.name.toLowerCase().includes(search) ||
    (w.phone && w.phone.toLowerCase().includes(search))
  )
})

function openModal(worker = null) {
  editingWorker.value = worker
  if (worker) {
    form.value = {
      name: worker.name,
      phone: worker.phone || '',
      hourly_rate: parseFloat(worker.hourly_rate),
      is_active: worker.is_active
    }
  } else {
    form.value = {
      name: '',
      phone: '',
      hourly_rate: 20,
      is_active: true
    }
  }
  error.value = ''
  showModal.value = true
}

async function handleSubmit() {
  loading.value = true
  error.value = ''
  
  try {
    const data = { ...form.value }
    
    // Only admins can set hourly_rate
    if (!authStore.isAdmin) {
      delete data.hourly_rate
    }
    
    if (editingWorker.value) {
      await workersApi.update(editingWorker.value.id, data)
    } else {
      await workersApi.create(data)
    }
    
    await appStore.fetchWorkers()
    showModal.value = false
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to save worker'
  }
  
  loading.value = false
}

async function deleteWorker(worker) {
  if (!confirm(`Delete "${worker.name}"?`)) return
  
  try {
    await workersApi.delete(worker.id)
    await appStore.fetchWorkers()
  } catch (err) {
    alert(err.response?.data?.detail || 'Failed to delete worker')
  }
}

onMounted(() => {
  appStore.fetchWorkers()
})
</script>