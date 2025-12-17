import axios from 'axios'

const api = axios.create({
  baseURL: 'https://dragon56test.pythonanywhere.com/api',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const authApi = {
  login: (username, password) => api.post('/auth/login', { username, password }),
  me: () => api.get('/auth/me'),
}

export const workersApi = {
  getAll: () => api.get('/workers'),
  create: (data) => api.post('/workers', data),
  update: (id, data) => api.put(`/workers/${id}`, data),
  delete: (id) => api.delete(`/workers/${id}`),
}

export const propertiesApi = {
  getAll: () => api.get('/properties'),
  create: (data) => api.post('/properties', data),
  update: (id, data) => api.put(`/properties/${id}`, data),
  delete: (id) => api.delete(`/properties/${id}`),
}

export const timeRecordsApi = {
  getAll: () => api.get('/time-records'),
  getToday: () => api.get('/time-records/today'),
  create: (data) => api.post('/time-records', data),
  update: (id, data) => api.put(`/time-records/${id}`, data),
  delete: (id) => api.delete(`/time-records/${id}`),
  start: (data) => api.post('/time-records/start', data),
  stop: (recordId) => api.post('/time-records/stop', { record_id: recordId }),
}

export const reportsApi = {
  getDashboard: () => api.get('/reports/dashboard'),
  getSummary: (params) => api.get('/reports/summary', { params }),
  preview: (params) => api.get('/reports/preview', { params }),
  export: (params) => api.get('/reports/export', { params, responseType: 'blob' }),
}

export default api