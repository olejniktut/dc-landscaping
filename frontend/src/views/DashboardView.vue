<template>
  <AppLayout>
    <h2 class="text-2xl font-bold text-gray-800 mb-6">Dashboard</h2>
    
    <!-- Quick Actions -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
      <button
        @click="showTimerModal = true"
        class="bg-green-600 text-white p-6 rounded-xl hover:bg-green-700 transition flex items-center gap-4"
      >
        <div class="w-14 h-14 bg-white/20 rounded-full flex items-center justify-center">
          <span class="text-3xl">⏱️</span>
        </div>
        <div class="text-left">
          <p class="font-bold text-lg">
            {{ appStore.activeTimer ? 'View Timer' : 'Start Tracking' }}
          </p>
          <p class="text-green-100 text-sm">
            {{ appStore.activeTimer 
              ? appStore.formatTime(appStore.timerSeconds) 
              : 'Begin time tracking' 
            }}
          </p>
        </div>
      </button>
      
      <button
        @click="showManualEntry = true"
        class="bg-blue-600 text-white p-6 rounded-xl hover:bg-blue-700 transition flex items-center gap-4"
      >
        <div class="w-14 h-14 bg-white/20 rounded-full flex items-center justify-center">
          <span class="text-3xl">✏️</span>
        </div>
        <div class="text-left">
          <p class="font-bold text-lg">Manual Entry</p>
          <p class="text-blue-100 text-sm">Add time manually</p>
        </div>
      </button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
      <div class="card p-6">
        <p class="text-gray-500 text-sm">Today's Hours</p>
        <p class="text-3xl font-bold text-gray-800">{{ todayHours }}h</p>
      </div>
      <div class="card p-6">
        <p class="text-gray-500 text-sm">Today's Cost</p>
        <p class="text-3xl font-bold text-gray-800">{{ todayCost }}</p>
      </div>
      <div class="card p-6">
        <p class="text-gray-500 text-sm">Active Workers</p>
        <p class="text-3xl font-bold text-gray-800">{{ activeWorkersCount }}</p>
      </div>
      <div class="card p-6">
        <p class="text-gray-500 text-sm">Records Today</p>
        <p class="text-3xl font-bold text-gray-800">{{ appStore.todayRecords.length }}</p>
      </div>
    </div>

    <!-- Today's Records -->
    <div class="card">
      <div class="p-6 border-b">
        <h3 class="font-bold text-gray-800">Today's Records</h3>
      </div>
      
      <div v-if="appStore.todayRecords.length === 0" class="p-8 text-center text-gray-500">
        No records for today yet. Start tracking or add a manual entry.
      </div>
      
      <div v-else class="divide-y">
        <div 
          v-for="record in appStore.todayRecords" 
          :key="record.id"
          class="p-4 flex items-center justify-between hover:bg-gray-50"
        >
          <div>
            <p class="font-medium text-gray-800">{{ record.property?.name }}</p>
            <p class="text-sm text-gray-500">
              {{ record.start_time?.slice(0, 5) }} - {{ record.end_time?.slice(0, 5) || 'In progress' }}
              • {{ record.workers?.map(w => w.name).join(', ') }}
            </p>
          </div>
          <div class="text-right">
            <p class="font-bold text-gray-800">
              {{ record.total_minutes ? (record.total_minutes / 60).toFixed(2) : '-' }}h
            </p>
            <p class="text-sm text-gray-500">
              {{ record.total_cost ? parseFloat(record.total_cost).toFixed(2) : '-' }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <TimerModal 
      :show="showTimerModal" 
      @close="showTimerModal = false" 
    />
    
    <ManualEntryModal 
      :show="showManualEntry" 
      @close="showManualEntry = false"
      @saved="handleRecordSaved"
    />
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import TimerModal from '@/components/TimerModal.vue'
import ManualEntryModal from '@/components/ManualEntryModal.vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

const showTimerModal = ref(false)
const showManualEntry = ref(false)

const todayHours = computed(() => {
  const totalMinutes = appStore.todayRecords.reduce((sum, r) => sum + (r.total_minutes || 0), 0)
  return (totalMinutes / 60).toFixed(1)
})

const todayCost = computed(() => {
  const total = appStore.todayRecords.reduce((sum, r) => sum + parseFloat(r.total_cost || 0), 0)
  return total.toFixed(2)
})

const activeWorkersCount = computed(() => 
  appStore.workers.filter(w => w.is_active).length
)

function handleRecordSaved() {
  // Records are already refreshed in the modal
}

onMounted(() => {
  appStore.fetchAll()
})
</script>
