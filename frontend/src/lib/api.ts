import axios from 'axios'
import { User, Agent, Task, ChatRequest, ChatResponse, RoleType } from '@/types'
import { supabase } from './supabaseClient'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000, // 10 second timeout
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth interceptor to include Supabase session token
api.interceptors.request.use(async (config) => {
  const { data: { session } } = await supabase.auth.getSession()
  if (session?.access_token) {
    config.headers.Authorization = `Bearer ${session.access_token}`
  }
  return config
}, (error) => {
  return Promise.reject(error)
})

// User API
export const userApi = {
  onboard: async (email: string, role: RoleType): Promise<User> => {
    const response = await api.post('/api/users/onboard', { email, role }, {
      timeout: 60000, // 60 seconds for onboarding (includes AI task generation)
    })
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
    const response = await api.post('/api/agents/chat-tools', chatRequest, {
      timeout: 120000, // 2 minutes for AI responses (includes codebase analysis time)
    })
    return response.data
  },

  getProactiveSuggestions: async (userId: string) => {
    const response = await api.get(`/api/agents/user/${userId}/suggestions`, {
      timeout: 60000, // 60 seconds for AI suggestion generation
    })
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

  delete: async (taskId: string): Promise<void> => {
    await api.delete(`/api/tasks/${taskId}`)
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

// Files API
export const filesApi = {
  list: async (signal?: AbortSignal): Promise<string[]> => {
    const response = await api.get('/api/files/list', { signal })
    return response.data
  },

  read: async (path: string): Promise<string> => {
    const response = await api.get('/api/files/raw', { params: { path } })
    return response.data
  },

  mkdir: async (path: string): Promise<void> => {
    await api.post('/api/files/mkdir', null, { params: { path } })
  },

  upload: async (files: FileList, directory?: string): Promise<{ uploaded_files: string[], count: number }> => {
    const formData = new FormData()
    
    // Add all files to form data
    Array.from(files).forEach(file => {
      formData.append('files', file)
    })
    
    // Add directory if specified
    if (directory) {
      formData.append('directory', directory)
    }
    
    // Get user_id from localStorage
    const userData = localStorage.getItem('user')
    if (userData) {
      const user = JSON.parse(userData)
      formData.append('user_id', user.id)
    }
    
    const response = await api.post('/api/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000, // 60 seconds for file uploads
    })
    
    return response.data
  },

  summary: async (): Promise<{
    total_files: number
    file_types: Record<string, number>
    ai_accessible_count: number
    ai_accessible_files: Array<{ path: string; type: string; size: number }>
    workspace_tools: string[]
  }> => {
    const response = await api.get('/api/files/summary')
    return response.data
  },

  getCompletedTasks: async (userId: string): Promise<string[]> => {
    const response = await api.get(`/api/files/completed-tasks/${userId}`)
    return response.data
  },
}

// Company API
export const companyApi = {
  create: async (company: {
    user_id: string
    name: string
    description?: string
    industry?: string
    stage?: string
    company_info?: string
    product_overview?: string
    tech_stack?: string
    go_to_market_strategy?: string
  }) => {
    const response = await api.post('/api/companies/', company)
    return response.data
  },
  getByUser: async (userId: string) => {
    const response = await api.get(`/api/companies/user/${userId}`)
    return response.data
  },
  update: async (
    companyId: string,
    company: Partial<{
      name: string
      description: string
      industry: string
      stage: string
      company_info: string
      product_overview: string
      tech_stack: string
      go_to_market_strategy: string
    }>
  ) => {
    const response = await api.put(`/api/companies/${companyId}`, company)
    return response.data
  },
  suggest: async (payload: { name: string; description?: string }) => {
    const response = await api.post('/api/companies/suggest', payload)
    return response.data as {
      company_info: string
      product_overview: string
      tech_stack: string
      go_to_market_strategy: string
    }
  },
  getCodebaseFiles: async (userId: string): Promise<string[]> => {
    try {
      const company = await companyApi.getByUser(userId)
      return company?.codebase_files || []
    } catch (e) {
      return []
    }
  },
} 