import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token
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
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  login: (email: string, password: string) =>
    api.post('/api/v1/auth/login', { email, password }),
  logout: () => api.post('/api/v1/auth/logout'),
  refreshToken: (refreshToken: string) =>
    api.post('/api/v1/auth/refresh', { refresh_token: refreshToken }),
}

// Projects API
export const projectsApi = {
  list: (params?: { status?: string; page?: number; page_size?: number }) =>
    api.get('/api/v1/projects/', { params }),
  get: (id: string) => api.get(`/api/v1/projects/${id}`),
  create: (data: any) => api.post('/api/v1/projects/', data),
  update: (id: string, data: any) => api.put(`/api/v1/projects/${id}`, data),
  delete: (id: string) => api.delete(`/api/v1/projects/${id}`),
  start: (id: string) => api.post(`/api/v1/projects/${id}/start`),
  complete: (id: string) => api.post(`/api/v1/projects/${id}/complete`),
  getStats: () => api.get('/api/v1/projects/stats/summary'),
}

// Agents API
export const agentsApi = {
  list: (projectId?: string) =>
    api.get('/api/v1/agents/', { params: { project_id: projectId } }),
  get: (id: string) => api.get(`/api/v1/agents/${id}`),
  create: (data: any) => api.post('/api/v1/agents/', data),
}

// Messages API
export const messagesApi = {
  getChannels: (projectId?: string) =>
    api.get('/api/v1/messages/channels', { params: { project_id: projectId } }),
  getMessages: (channelId: string, params?: { limit?: number; before?: string }) =>
    api.get(`/api/v1/messages/${channelId}`, { params }),
  sendMessage: (data: any) => api.post('/api/v1/messages/', data),
}

// Artifacts API
export const artifactsApi = {
  list: (params?: { project_id?: string; artifact_type?: string }) =>
    api.get('/api/v1/artifacts/', { params }),
  get: (id: string) => api.get(`/api/v1/artifacts/${id}`),
  create: (data: any) => api.post('/api/v1/artifacts/', data),
}

export default api