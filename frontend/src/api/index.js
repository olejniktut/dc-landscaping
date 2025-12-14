import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  login: (username, password) => 
    api.post('/auth/login', { username, password }),
  getMe: () => 
    api.get('/auth/me')
}

// Workers API
export const workersApi = {
  getAll: (includeInactive = false) => 
    api.get('/workers', { params: { include_inactive: includeInactive } }),
  get: (id) => 
    api.get(`/workers/${id}`),
  create: (data) => 
    api.post('/workers', data),
  update: (id, data) => 
    api.put(`/workers/${id}`, data),
  delete: (id) => 
    api.delete(`/workers/${id}`)
}

// Properties API
export const propertiesApi = {
  getAll: (includeInactive = false) => 
    api.get('/properties', { params: { include_inactive: includeInactive } }),
  get: (id) => 
    api.get(`/properties/${id}`),
  create: (data) => 
    api.post('/properties', data),
  update: (id, data) => 
    api.put(`/properties/${id}`, data),
  delete: (id) => 
    api.delete(`/properties/${id}`)
}

// Time Records API
export const timeRecordsApi = {
  getAll: (params = {}) => 
    api.get('/time-records', { params }),
  getToday: () => 
    api.get('/time-records/today'),
  get: (id) => 
    api.get(`/time-records/${id}`),
  create: (data) => 
    api.post('/time-records', data),
  start: (data) => 
    api.post('/time-records/start', data),
  stop: (data) => 
    api.post('/time-records/stop', data),
  update: (id, data) => 
    api.put(`/time-records/${id}`, data),
  delete: (id) => 
    api.delete(`/time-records/${id}`)
}

// Reports API
export const reportsApi = {
  getDashboard: () => 
    api.get('/reports/dashboard'),
  getSummary: (params) => 
    api.get('/reports/summary', { params }),
  getPreview: (params) => 
    api.get('/reports/preview', { params }),
  exportExcel: (params) => 
    api.get('/reports/export', { 
      params, 
      responseType: 'blob' 
    })
}

export default api
