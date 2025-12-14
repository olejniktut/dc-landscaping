<template>
  <AppLayout>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-800">Time Records</h2>
      <button @click="showManualEntry = true" class="btn btn-primary flex items-center gap-2">
        <span>+</span> Add Record
      </button>
    </div>

    <!-- Filters -->
    <div class="card p-4 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">From Date</label>
          <input v-model="filters.start_date" type="date" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">To Date</label>
          <input v-model="filters.end_date" type="date" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Property</label>
          <select v-model="filters.property_id">
            <option value="">All Properties</option>
            <option v-for="p in appStore.properties" :key="p.id" :value="p.id">
              {{ p.name }}
            </option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="fetchRecords" class="btn btn-primary w-full">
            Apply Filters
          </button>
        </div>
      </div>
    </div>

    <!-- Records Table -->
    <div class="card overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-gray-500">
        Loading records...
      </div>
      
      <div v-else-if="records.length === 0" class="p-8 text-center text-gray-500">
        No records found. Try adjusting your filters.
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="text-left px-6 py-4 text-sm font-medium text-gray-500">Date</th>
              <th class="text-left px-6 py-4 text-sm font-medium text-gray-500">Property</th>
              <th class="text-left px-6 py-4 text-sm font-medium text-gray-500">Time</th>
              <th class="text-left px-6 py-4 text-sm font-medium text-gray-500">Break</th>
              <th class="text-left px-6 py-4 text-sm font-medium text-gray-500">Workers</th>
              <th class="text-left px-6 py-4 text-sm font-medium text-gray-500">Hours</th>
              <th class="text-left px-6 py-4 text-sm font-medium text-gray-500">Cost</th>
              <th class="text-right px-6 py-4 text-sm font-medium text-gray-500">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y">
            <tr v-for="record in records" :key="record.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 text-gray-800">{{ record.work_date }}</td>
              <td class="px-6 py-4 text-gray-800">{{ record.property?.name }}</td>
              <td class="px-6 py-4 text-gray-600">
                {{ record.start_time?.slice(0, 5) }} - {{ record.end_time?.slice(0, 5) || '-' }}
              </td>
              <td class="px-6 py-4 text-gray-600">{{ record.break_minutes }}min</td>
              <td class="px-6 py-4 text-gray-600">
                {{ record.workers?.map(w => w.name).join(', ') }}
              </td>
              <td class="px-6 py-4 font-medium text-gray-800">
                {{ record.total_minutes ? (record.total_minutes / 60).toFixed(2) : '-' }}
              </td>
              <td class="px-6 py-4 font-medium text-gray-800">
                {{ record.total_cost ? parseFloat(record.total_cost).toFixed(2) : '-' }}
              </td>
              <td class="px-6 py-4 text-right">
                <button 
                  v-if="canEdit(record)"
                  @click="editRecord(record)" 
                  class="text-blue-600 hover:text-blue-800 mr-2"
                >
                  Edit
                </button>
                <button 
                  v-if="canEdit(record)"
                  @click="deleteRecord(record)" 
                  class="text-red-600 hover:text-red-800"
                >
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Manual Entry Modal -->
    <ManualEntryModal 
      :show="showManualEntry" 
      :edit-record="editingRecord"
      @close="closeManualEntry"
      @saved="handleSaved"
    />
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import ManualEntryModal from '@/components/ManualEntryModal.vue'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'
import { timeRecordsApi } from '@/api'

const appStore = useAppStore()
const authStore = useAuthStore()

const records = ref([])
const loading = ref(false)
const showManualEntry = ref(false)
const editingRecord = ref(null)

const today = new Date().toISOString().split('T')[0]

const filters = ref({
  start_date: today,
  end_date: today,
  property_id: ''
})

async function fetchRecords() {
  loading.value = true
  
  try {
    const params = {}
    if (filters.value.start_date) params.start_date = filters.value.start_date
    if (filters.value.end_date) params.end_date = filters.value.end_date
    if (filters.value.property_id) params.property_id = filters.value.property_id
    
    const response = await timeRecordsApi.getAll(params)
    records.value = response.data
  } catch (err) {
    console.error('Failed to fetch records:', err)
  }
  
  loading.value = false
}

function canEdit(record) {
  if (authStore.isAdmin) return true
  return record.work_date === today
}

function editRecord(record) {
  editingRecord.value = record
  showManualEntry.value = true
}

function closeManualEntry() {
  showManualEntry.value = false
  editingRecord.value = null
}

async function deleteRecord(record) {
  if (!confirm('Are you sure you want to delete this record?')) return
  
  try {
    await timeRecordsApi.delete(record.id)
    await fetchRecords()
  } catch (err) {
    alert(err.response?.data?.detail || 'Failed to delete record')
  }
}

function handleSaved() {
  fetchRecords()
}

onMounted(() => {
  appStore.fetchAll()
  fetchRecords()
})
</script>
