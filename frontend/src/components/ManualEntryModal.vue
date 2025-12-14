<template>
  <div v-if="show" class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal-content max-w-md">
      <h3 class="text-xl font-bold text-gray-800 mb-4">
        {{ editRecord ? 'Edit Time Record' : 'Manual Time Entry' }}
      </h3>
      
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Property</label>
          <select v-model="form.property_id" required class="w-full">
            <option value="">Choose property...</option>
            <option v-for="p in appStore.properties" :key="p.id" :value="p.id">
              {{ p.name }}
            </option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Date</label>
          <input 
            v-model="form.work_date" 
            type="date" 
            class="w-full"
            :max="maxDate"
            :disabled="!canEditDate"
            required
          />
          <p v-if="!canEditDate" class="text-xs text-gray-500 mt-1">
            Workers can only edit today's records
          </p>
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Start Time</label>
            <input v-model="form.start_time" type="time" class="w-full" required />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">End Time</label>
            <input v-model="form.end_time" type="time" class="w-full" required />
          </div>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Break (minutes)</label>
          <input v-model.number="form.break_minutes" type="number" min="0" class="w-full" placeholder="0" />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Workers</label>
          <div class="space-y-2 max-h-32 overflow-auto border rounded-lg p-2">
            <label 
              v-for="worker in activeWorkers" 
              :key="worker.id" 
              class="flex items-center gap-3 p-1 cursor-pointer"
            >
              <input
                type="checkbox"
                :value="worker.id"
                v-model="form.worker_ids"
                class="w-4 h-4 text-green-600"
              />
              <span>{{ worker.name }}</span>
            </label>
          </div>
        </div>

        <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>

        <div class="flex gap-3">
          <button type="button" @click="$emit('close')" class="btn btn-secondary flex-1">
            Cancel
          </button>
          <button 
            type="submit" 
            :disabled="loading || form.worker_ids.length === 0"
            class="btn btn-primary flex-1"
          >
            {{ loading ? 'Saving...' : (editRecord ? 'Save Changes' : 'Save Entry') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'
import { timeRecordsApi } from '@/api'

const props = defineProps({
  show: Boolean,
  editRecord: Object
})

const emit = defineEmits(['close', 'saved'])

const appStore = useAppStore()
const authStore = useAuthStore()

const loading = ref(false)
const error = ref('')

const today = new Date().toISOString().split('T')[0]

const form = ref({
  property_id: '',
  work_date: today,
  start_time: '',
  end_time: '',
  break_minutes: 0,
  worker_ids: []
})

const activeWorkers = computed(() => 
  appStore.workers.filter(w => w.is_active)
)

const canEditDate = computed(() => authStore.isAdmin)

const maxDate = computed(() => {
  if (authStore.isAdmin) return undefined
  return today
})

// Initialize form when editing
watch(() => props.show, (newVal) => {
  if (newVal) {
    if (props.editRecord) {
      form.value = {
        property_id: props.editRecord.property_id,
        work_date: props.editRecord.work_date,
        start_time: props.editRecord.start_time,
        end_time: props.editRecord.end_time || '',
        break_minutes: props.editRecord.break_minutes || 0,
        worker_ids: props.editRecord.workers?.map(w => w.id) || []
      }
    } else {
      // Reset form for new entry
      form.value = {
        property_id: '',
        work_date: today,
        start_time: '',
        end_time: '',
        break_minutes: 0,
        worker_ids: appStore.lastSelectedWorkers.length > 0 
          ? [...appStore.lastSelectedWorkers]
          : activeWorkers.value.slice(0, 3).map(w => w.id)
      }
    }
    error.value = ''
  }
})

async function handleSubmit() {
  loading.value = true
  error.value = ''
  
  try {
    if (props.editRecord) {
      await timeRecordsApi.update(props.editRecord.id, form.value)
    } else {
      await timeRecordsApi.create({
        ...form.value,
        is_manual_entry: true
      })
    }
    
    await appStore.fetchTodayRecords()
    emit('saved')
    emit('close')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to save record'
  }
  
  loading.value = false
}
</script>
