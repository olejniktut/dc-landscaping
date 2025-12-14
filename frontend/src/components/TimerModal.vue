<template>
  <div v-if="show" class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal-content max-w-md">
      <!-- Start Timer Form -->
      <template v-if="!appStore.activeTimer">
        <h3 class="text-xl font-bold text-gray-800 mb-4">Start Tracking</h3>
        
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">Select Property</label>
          
          <!-- Search Input -->
          <input
            v-model="propertySearch"
            type="text"
            class="w-full mb-2"
            placeholder="🔍 Search property..."
          />
          
          <!-- Property List -->
          <div class="max-h-48 overflow-auto border rounded-lg">
            <div
              v-for="p in filteredProperties"
              :key="p.id"
              @click="selectedProperty = p.id"
              class="px-3 py-2 cursor-pointer hover:bg-gray-100 flex justify-between items-center"
              :class="{ 'bg-green-100': selectedProperty === p.id }"
            >
              <div>
                <p class="font-medium">{{ p.name }}</p>
                <p class="text-xs text-gray-500">{{ p.address }}</p>
              </div>
              <span v-if="selectedProperty === p.id" class="text-green-600">✓</span>
            </div>
            <div v-if="filteredProperties.length === 0" class="px-3 py-4 text-center text-gray-500">
              No properties found
            </div>
          </div>
        </div>
        
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">Select Workers</label>
          <div class="space-y-2 max-h-40 overflow-auto border rounded-lg p-2">
            <label 
              v-for="worker in activeWorkers" 
              :key="worker.id" 
              class="flex items-center gap-3 p-2 hover:bg-gray-50 rounded cursor-pointer"
            >
              <input
                type="checkbox"
                :value="worker.id"
                v-model="selectedWorkers"
                class="w-4 h-4 text-green-600"
              />
              <span>{{ worker.name }}</span>
            </label>
          </div>
        </div>
        
        <div class="flex gap-3">
          <button @click="$emit('close')" class="btn btn-secondary flex-1">
            Cancel
          </button>
          <button 
            @click="handleStart"
            :disabled="!selectedProperty || selectedWorkers.length === 0"
            class="btn btn-primary flex-1"
          >
            Start
          </button>
        </div>
      </template>

      <!-- Active Timer -->
      <template v-else>
        <div class="text-center mb-6">
          <p class="text-gray-500 mb-2">{{ currentPropertyName }}</p>
          <p 
            class="text-5xl font-mono font-bold"
            :class="appStore.isPaused ? 'text-orange-500' : 'text-green-600'"
          >
            {{ appStore.formatTime(appStore.timerSeconds) }}
          </p>
          <p v-if="appStore.breakSeconds > 0" class="text-sm text-gray-500 mt-2">
            Break: {{ appStore.formatTime(appStore.breakSeconds) }}
          </p>
          <p v-if="appStore.isPaused" class="text-orange-500 font-medium mt-2">
            ⏸️ On Break
          </p>
        </div>
<div class="mb-6">
          <p class="text-sm font-medium text-gray-700 mb-2">
            Workers ({{ selectedWorkers.length }})
          </p>
          <div class="flex flex-wrap gap-2">
            <span 
              v-for="worker in selectedWorkersData" 
              :key="worker.id"
              class="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm"
            >
              {{ worker.name }}
            </span>
          </div>
          <button 
            @click="showEditWorkers = !showEditWorkers"
            class="text-blue-600 text-sm mt-2 hover:underline"
          >
            {{ showEditWorkers ? 'Hide' : 'Edit workers' }}
          </button>
          
          <div v-if="showEditWorkers" class="mt-2 border rounded-lg p-2 max-h-32 overflow-auto">
            <label 
              v-for="worker in activeWorkers" 
              :key="worker.id" 
              class="flex items-center gap-3 p-1 cursor-pointer"
            >
              <input
                type="checkbox"
                :value="worker.id"
                v-model="selectedWorkers"
                class="w-4 h-4 text-green-600"
              />
              <span class="text-sm">{{ worker.name }}</span>
            </label>
          </div>
        </div>

        <div class="flex gap-3">
          <button
            @click="appStore.togglePause()"
            class="flex-1 px-4 py-3 rounded-lg font-medium"
            :class="appStore.isPaused 
              ? 'bg-green-100 text-green-700 hover:bg-green-200' 
              : 'bg-orange-100 text-orange-700 hover:bg-orange-200'"
          >
            {{ appStore.isPaused ? '▶️ Resume' : '⏸️ Break' }}
          </button>
          <button
            @click="handleStop"
            class="flex-1 bg-red-600 text-white px-4 py-3 rounded-lg font-medium hover:bg-red-700"
          >
            ⏹️ Stop
          </button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useAppStore } from '@/stores/app'

const props = defineProps({
  show: Boolean,
  propertyId: Number
})

const emit = defineEmits(['close'])

const appStore = useAppStore()

const selectedProperty = ref(props.propertyId || '')
const selectedWorkers = ref([])
const showEditWorkers = ref(false)
const propertySearch = ref('')

const activeWorkers = computed(() => 
  appStore.workers.filter(w => w.is_active)
)

const filteredProperties = computed(() => {
  const search = propertySearch.value.toLowerCase().trim()
  if (!search) return appStore.properties
  
  return appStore.properties.filter(p => 
    p.name.toLowerCase().includes(search) ||
    (p.address && p.address.toLowerCase().includes(search))
  )
})

const selectedWorkersData = computed(() =>
  appStore.workers.filter(w => selectedWorkers.value.includes(w.id))
)

const currentPropertyName = computed(() => {
  if (!appStore.activeTimer) return ''
  const prop = appStore.properties.find(p => p.id === appStore.activeTimer.property_id)
  return prop?.name || ''
})

// Initialize selected workers from last selection or active timer
watch(() => props.show, (newVal) => {
  if (newVal) {
    propertySearch.value = ''
    
    if (appStore.activeTimer) {
      selectedWorkers.value = appStore.activeTimer.workers.map(w => w.id)
    } else if (appStore.lastSelectedWorkers.length > 0) {
      selectedWorkers.value = [...appStore.lastSelectedWorkers]
    } else {
      // Default to first 3 workers
      selectedWorkers.value = activeWorkers.value.slice(0, 3).map(w => w.id)
    }
    
    if (props.propertyId) {
      selectedProperty.value = props.propertyId
    }
  }
})

async function handleStart() {
  const result = await appStore.startTimer(selectedProperty.value, selectedWorkers.value)
  if (!result.success) {
    alert(result.error)
  }
}

async function handleStop() {
  const result = await appStore.stopTimer(selectedWorkers.value)
  if (result.success) {
    emit('close')
  } else {
    alert(result.error)
  }
}
</script>
