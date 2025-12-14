import { defineStore } from 'pinia'
import { ref } from 'vue'
import { workersApi, propertiesApi, timeRecordsApi } from '@/api'

export const useAppStore = defineStore('app', () => {
  const workers = ref([])
  const properties = ref([])
  const todayRecords = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  // Active timer state
  const activeTimer = ref(null)
  const timerSeconds = ref(0)
  const breakSeconds = ref(0)
  const isPaused = ref(false)
  let timerInterval = null
  
  // Last selected workers (for persistence)
  const lastSelectedWorkers = ref(
    JSON.parse(localStorage.getItem('lastSelectedWorkers') || '[]')
  )
  
  async function fetchWorkers() {
    try {
      const response = await workersApi.getAll()
      workers.value = response.data
    } catch (err) {
      error.value = err.message
    }
  }
  
  async function fetchProperties() {
    try {
      const response = await propertiesApi.getAll()
      properties.value = response.data
    } catch (err) {
      error.value = err.message
    }
  }
  
  async function fetchTodayRecords() {
    try {
      const response = await timeRecordsApi.getToday()
      todayRecords.value = response.data
    } catch (err) {
      error.value = err.message
    }
  }
  
  async function fetchAll() {
    loading.value = true
    await Promise.all([
      fetchWorkers(),
      fetchProperties(),
      fetchTodayRecords()
    ])
    loading.value = false
  }
  
  // Timer functions
  function startTimerInterval() {
    timerInterval = setInterval(() => {
      if (!isPaused.value) {
        timerSeconds.value++
      } else {
        breakSeconds.value++
      }
    }, 1000)
  }
  
  function stopTimerInterval() {
    if (timerInterval) {
      clearInterval(timerInterval)
      timerInterval = null
    }
  }
  
  async function startTimer(propertyId, workerIds) {
    try {
      const response = await timeRecordsApi.start({
        property_id: propertyId,
        worker_ids: workerIds
      })
      
      activeTimer.value = response.data
      timerSeconds.value = 0
      breakSeconds.value = 0
      isPaused.value = false
      
      // Save last selected workers
      lastSelectedWorkers.value = workerIds
      localStorage.setItem('lastSelectedWorkers', JSON.stringify(workerIds))
      
      startTimerInterval()
      return { success: true, data: response.data }
    } catch (err) {
      return { success: false, error: err.response?.data?.detail || err.message }
    }
  }
  
  async function stopTimer(workerIds = null) {
    if (!activeTimer.value) return { success: false, error: 'No active timer' }
    
    try {
      const response = await timeRecordsApi.stop({
        time_record_id: activeTimer.value.id,
        break_minutes: Math.floor(breakSeconds.value / 60),
        worker_ids: workerIds || activeTimer.value.workers.map(w => w.id)
      })
      
      stopTimerInterval()
      activeTimer.value = null
      timerSeconds.value = 0
      breakSeconds.value = 0
      isPaused.value = false
      
      await fetchTodayRecords()
      return { success: true, data: response.data }
    } catch (err) {
      return { success: false, error: err.response?.data?.detail || err.message }
    }
  }
  
  function togglePause() {
    isPaused.value = !isPaused.value
  }
  
  function formatTime(seconds) {
    const h = Math.floor(seconds / 3600)
    const m = Math.floor((seconds % 3600) / 60)
    const s = seconds % 60
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
  }
  
  return {
    workers,
    properties,
    todayRecords,
    loading,
    error,
    activeTimer,
    timerSeconds,
    breakSeconds,
    isPaused,
    lastSelectedWorkers,
    fetchWorkers,
    fetchProperties,
    fetchTodayRecords,
    fetchAll,
    startTimer,
    stopTimer,
    togglePause,
    formatTime
  }
})
