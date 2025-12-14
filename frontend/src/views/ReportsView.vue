<template>
  <AppLayout>
    <h2 class="text-2xl font-bold text-gray-800 mb-6">Reports</h2>
    
    <!-- Report Filters -->
    <div class="card p-6 mb-6">
      <h3 class="font-bold text-gray-800 mb-4">Generate Report</h3>
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
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Type</label>
          <select v-model="filters.cleanup_type">
            <option value="">All</option>
            <option value="spring">Spring Cleanup</option>
            <option value="fall">Fall Cleanup</option>
          </select>
        </div>
      </div>
      <div class="flex gap-4 mt-6">
        <button
          @click="previewReport"
          :disabled="loading"
          class="btn btn-primary"
        >
          {{ loading ? 'Loading...' : 'Preview Report' }}
        </button>
        <button 
          @click="exportExcel"
          :disabled="loading || !previewData"
          class="btn flex items-center gap-2 bg-blue-600 text-white hover:bg-blue-700"
        >
          <span>📥</span> Export Excel
        </button>
      </div>
    </div>

    <!-- Quick Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div class="card p-6">
        <p class="text-gray-500 text-sm">This Month</p>
        <p class="text-3xl font-bold text-gray-800">{{ dashboardStats.month_hours }}h</p>
        <p class="text-green-600 text-sm">{{ dashboardStats.month_cost }} total cost</p>
      </div>
      <div class="card p-6">
        <p class="text-gray-500 text-sm">This Year</p>
        <p class="text-3xl font-bold text-gray-800">{{ dashboardStats.year_hours }}h</p>
        <p class="text-green-600 text-sm">{{ dashboardStats.year_cost }} total cost</p>
      </div>
      <div class="card p-6">
        <p class="text-gray-500 text-sm">Today</p>
        <p class="text-3xl font-bold text-gray-800">{{ dashboardStats.today_hours }}h</p>
        <p class="text-green-600 text-sm">{{ dashboardStats.today_cost }} total cost</p>
      </div>
    </div>

    <!-- Report Preview -->
    <div v-if="previewData" class="card overflow-hidden">
      <div class="p-6 border-b flex justify-between items-center">
        <h3 class="font-bold text-gray-800">Report Preview</h3>
        <div class="text-sm text-gray-500">
          {{ previewData.records.length }} records
        </div>
      </div>
      
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-100">
            <tr>
              <th class="text-left px-4 py-3 text-sm font-medium text-gray-700">Date</th>
              <th class="text-left px-4 py-3 text-sm font-medium text-gray-700">Property</th>
              <th class="text-left px-4 py-3 text-sm font-medium text-gray-700">Type</th>
              <th class="text-left px-4 py-3 text-sm font-medium text-gray-700">Workers</th>
              <th class="text-right px-4 py-3 text-sm font-medium text-gray-700">Hours</th>
              <th class="text-right px-4 py-3 text-sm font-medium text-gray-700">Cost</th>
            </tr>
          </thead>
          <tbody class="divide-y">
            <tr v-for="record in previewData.records" :key="record.id">
              <td class="px-4 py-3">{{ record.date }}</td>
              <td class="px-4 py-3">{{ record.property }}</td>
              <td class="px-4 py-3">
                <span 
                  v-if="record.type"
                  class="px-2 py-1 rounded text-xs"
                  :class="record.type === 'Spring' 
                    ? 'bg-green-100 text-green-700' 
                    : 'bg-orange-100 text-orange-700'"
                >
                  {{ record.type }}
                </span>
              </td>
              <td class="px-4 py-3">{{ record.workers.join(', ') }}</td>
              <td class="px-4 py-3 text-right">{{ record.hours }}</td>
              <td class="px-4 py-3 text-right">{{ record.cost }}</td>
            </tr>
          </tbody>
          <tfoot class="bg-gray-50 font-bold">
            <tr>
              <td colspan="4" class="px-4 py-3 text-right">Total:</td>
              <td class="px-4 py-3 text-right">{{ previewData.total_hours }}h</td>
              <td class="px-4 py-3 text-right">{{ previewData.total_cost }}</td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { useAppStore } from '@/stores/app'
import { reportsApi } from '@/api'

const appStore = useAppStore()

const loading = ref(false)
const previewData = ref(null)

// Get first day of current month
const firstOfMonth = new Date()
firstOfMonth.setDate(1)

const filters = ref({
  start_date: firstOfMonth.toISOString().split('T')[0],
  end_date: new Date().toISOString().split('T')[0],
  property_id: '',
  cleanup_type: ''
})

const dashboardStats = ref({
  today_hours: 0,
  today_cost: 0,
  month_hours: 0,
  month_cost: 0,
  year_hours: 0,
  year_cost: 0
})

async function fetchDashboardStats() {
  try {
    const response = await reportsApi.getDashboard()
    dashboardStats.value = response.data
  } catch (err) {
    console.error('Failed to fetch dashboard stats:', err)
  }
}

async function previewReport() {
  loading.value = true
  previewData.value = null
  
  try {
    const params = {
      start_date: filters.value.start_date,
      end_date: filters.value.end_date
    }
    if (filters.value.property_id) {
      params.property_id = filters.value.property_id
    }
    if (filters.value.cleanup_type) {
      params.cleanup_type = filters.value.cleanup_type
    }
    
    const response = await reportsApi.getPreview(params)
    previewData.value = response.data
  } catch (err) {
    alert(err.response?.data?.detail || 'Failed to generate report')
  }
  
  loading.value = false
}

async function exportExcel() {
  try {
    const params = {
      start_date: filters.value.start_date,
      end_date: filters.value.end_date
    }
    if (filters.value.property_id) {
      params.property_id = filters.value.property_id
    }
    if (filters.value.cleanup_type) {
      params.cleanup_type = filters.value.cleanup_type
    }
    
    const response = await reportsApi.exportExcel(params)
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `dc_landscaping_report_${filters.value.start_date}_${filters.value.end_date}.xlsx`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (err) {
    alert('Failed to export report')
  }
}

onMounted(() => {
  appStore.fetchProperties()
  fetchDashboardStats()
})
</script>
