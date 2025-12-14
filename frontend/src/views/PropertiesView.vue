<template>
  <AppLayout>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-800">Properties</h2>
      <button @click="openModal()" class="btn btn-primary flex items-center gap-2">
        <span>+</span> Add Property
      </button>
    </div>

    <!-- Search -->
    <div class="mb-4">
      <input 
        v-model="searchQuery" 
        type="text" 
        placeholder="🔍 Search properties..." 
        class="w-full md:w-80"
      />
    </div>

    <div v-if="filteredProperties.length === 0" class="card p-8 text-center text-gray-500">
      No properties found.
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="property in filteredProperties" :key="property.id" class="card p-6">
        <div class="flex justify-between items-start mb-4">
          <div>
            <h3 class="font-bold text-gray-800">{{ property.name }}</h3>
            <p class="text-sm text-gray-500">{{ property.address || 'No address' }}</p>
          </div>
          <div class="flex gap-2">
            <button @click="openModal(property)" class="text-gray-400 hover:text-blue-600">
              ✏️
            </button>
            <button @click="deleteProperty(property)" class="text-gray-400 hover:text-red-600">
              🗑️
            </button>
          </div>
        </div>
        
        <div class="flex gap-2 mb-4">
          <span 
            v-if="property.is_spring_cleanup"
            class="px-2 py-1 bg-green-100 text-green-700 rounded text-xs"
          >
            Spring
          </span>
          <span 
            v-if="property.is_fall_cleanup"
            class="px-2 py-1 bg-orange-100 text-orange-700 rounded text-xs"
          >
            Fall
          </span>
        </div>
        
        <button
          @click="startTracking(property.id)"
          class="w-full bg-green-50 text-green-600 py-2 rounded-lg hover:bg-green-100 transition font-medium"
        >
          Start Tracking
        </button>
      </div>
    </div>

    <!-- Property Modal -->
    <div v-if="showModal" class="modal-backdrop" @click.self="showModal = false">
      <div class="modal-content">
        <h3 class="text-xl font-bold text-gray-800 mb-4">
          {{ editingProperty ? 'Edit Property' : 'Add Property' }}
        </h3>
        
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input v-model="form.name" type="text" required placeholder="Property name" />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Address</label>
            <input v-model="form.address" type="text" placeholder="123 Main St" />
          </div>
          
          <div class="flex gap-4">
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="form.is_spring_cleanup" type="checkbox" class="w-4 h-4" />
              <span class="text-sm text-gray-700">Spring Cleanup</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="form.is_fall_cleanup" type="checkbox" class="w-4 h-4" />
              <span class="text-sm text-gray-700">Fall Cleanup</span>
            </label>
          </div>

          <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>

          <div class="flex gap-3">
            <button type="button" @click="showModal = false" class="btn btn-secondary flex-1">
              Cancel
            </button>
            <button type="submit" :disabled="loading" class="btn btn-primary flex-1">
              {{ loading ? 'Saving...' : (editingProperty ? 'Save Changes' : 'Add Property') }}
            </button>
          </div>
        </form>
      </div>
    </div>

<!-- Timer Modal -->
    <TimerModal 
      :show="showTimerModal" 
      :property-id="selectedPropertyId"
      @close="showTimerModal = false" 
    />
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import TimerModal from '@/components/TimerModal.vue'
import { useAppStore } from '@/stores/app'
import { propertiesApi } from '@/api'

const appStore = useAppStore()

const showModal = ref(false)
const showTimerModal = ref(false)
const selectedPropertyId = ref(null)
const editingProperty = ref(null)
const loading = ref(false)
const error = ref('')
const searchQuery = ref('')

const form = ref({
  name: '',
  address: '',
  is_spring_cleanup: false,
  is_fall_cleanup: false
})

const filteredProperties = computed(() => {
  const search = searchQuery.value.toLowerCase().trim()
  if (!search) return appStore.properties
  
  return appStore.properties.filter(p => 
    p.name.toLowerCase().includes(search) ||
    (p.address && p.address.toLowerCase().includes(search))
  )
})

function openModal(property = null) {
  editingProperty.value = property
  if (property) {
    form.value = {
      name: property.name,
      address: property.address || '',
      is_spring_cleanup: property.is_spring_cleanup,
      is_fall_cleanup: property.is_fall_cleanup
    }
  } else {
    form.value = {
      name: '',
      address: '',
      is_spring_cleanup: false,
      is_fall_cleanup: false
    }
  }
  error.value = ''
  showModal.value = true
}

function startTracking(propertyId) {
  selectedPropertyId.value = propertyId
  showTimerModal.value = true
}

async function handleSubmit() {
  loading.value = true
  error.value = ''
  
  try {
    if (editingProperty.value) {
      await propertiesApi.update(editingProperty.value.id, form.value)
    } else {
      await propertiesApi.create(form.value)
    }
    
    await appStore.fetchProperties()
    showModal.value = false
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to save property'
  }
  
  loading.value = false
}

async function deleteProperty(property) {
  if (!confirm(`Delete "${property.name}"?`)) return
  
  try {
    await propertiesApi.delete(property.id)
    await appStore.fetchProperties()
  } catch (err) {
    alert(err.response?.data?.detail || 'Failed to delete property')
  }
}

onMounted(() => {
  appStore.fetchProperties()
})
</script>