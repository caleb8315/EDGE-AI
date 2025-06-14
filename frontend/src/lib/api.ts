import axios from 'axios'
import { User, Agent, Task, ChatRequest, ChatResponse, RoleType } from '@/types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// User API
export const userApi = {
  onboard: async (email: string, role: RoleType): Promise<User> => {
    const response = await api.post('/api/users/onboard', { email, role })
    return response.data
  },

  getById: async (userId: string): Promise<User> => {
    const response = await api.get(`/api/users/${userId}`)
    return response.data
  },

  getByEmail: async (email: string): Promise<User> => {
    const response = await api.get(`/api/users/email/${email}`)
    return response.data
  },
}

// Agent API
export const agentApi = {
  getUserAgents: async (userId: string): Promise<Agent[]> => {
    const response = await api.get(`/api/agents/user/${userId}`)
    return response.data
  },

  chat: async (chatRequest: ChatRequest): Promise<ChatResponse> => {
    const response = await api.post('/api/agents/chat', chatRequest)
    return response.data
  },
}

// Task API
export const taskApi = {
  create: async (task: Omit<Task, 'id' | 'created_at' | 'updated_at'>): Promise<Task> => {
    const response = await api.post('/api/tasks/', task)
    return response.data
  },

  getUserTasks: async (userId: string, status?: string): Promise<Task[]> => {
    const params = status ? { status } : {}
    const response = await api.get(`/api/tasks/user/${userId}`, { params })
    return response.data
  },

  update: async (taskId: string, updates: Partial<Task>): Promise<Task> => {
    const response = await api.put(`/api/tasks/${taskId}`, updates)
    return response.data
  },

  getByRole: async (role: RoleType, userId: string): Promise<Task[]> => {
    const response = await api.get(`/api/tasks/role/${role}/user/${userId}`)
    return response.data
  },
}

// Health check
export const healthApi = {
  check: async () => {
    const response = await api.get('/health')
    return response.data
  },
} 