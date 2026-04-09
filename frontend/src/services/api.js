import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  login: (data) => api.post('/api/login', data),
  register: (data) => api.post('/api/register', data),
  logout: () => api.post('/api/logout'),
  forgotPassword: (email) => api.post('/api/forgot-password', { email }),
  resetPassword: (token, newPassword) => api.post('/api/reset-password', { token, new_password: newPassword }),
  verifyEmail: (token) => api.get(`/api/verify-email/${token}`),
}

export const userAPI = {
  getProfile: () => api.get('/api/profile'),
  updateProfile: (data) => api.put('/api/profile', data),
  uploadPhoto: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/api/upload-photo', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  deletePhoto: () => api.delete('/api/delete-photo'),
  getActivityLogs: () => api.get('/api/activity-logs'),
}

export const flightsAPI = {
  searchFlights: (params) => api.get('/api/flights/search', { params }),
  getAirports: () => api.get('/api/flights/airports'),
  getAircraft: () => api.get('/api/flights/aircraft'),
  getAircraftById: (id) => api.get(`/api/flights/aircraft/${id}`),
  createAircraft: (data) => api.post('/api/flights/aircraft', data),
  updateAircraft: (id, data) => api.put(`/api/flights/aircraft/${id}`, data),
}

export const adminAPI = {
  getStaffList: () => api.get('/api/admin/staff-list'),
  deactivateStaff: (staffId, reason) => api.post('/api/admin/deactivate-staff', { staff_id: staffId, reason }),
  activateStaff: (staffId, reason) => api.post('/api/admin/activate-staff', { staff_id: staffId, reason }),
  getAllUsers: () => api.get('/api/admin/users'),
}

export default api