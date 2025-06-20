export type RoleType = 'CEO' | 'CTO' | 'CMO'

export interface User {
  id: string
  email: string
  role: RoleType
  created_at: string
  updated_at: string
}

export interface Agent {
  id: string
  user_id: string
  role: RoleType
  conversation_state: {
    messages: ChatMessage[]
    initialized: boolean
    context?: any
  }
  created_at: string
  updated_at: string
}

export interface Task {
  id: string
  user_id: string
  assigned_to_role: RoleType
  description: string
  status: 'pending' | 'in_progress' | 'completed'
  resources?: string[]
  created_at: string
  updated_at: string
}

export interface ChatMessage {
  message: string
  is_from_user: boolean
  timestamp: string
}

export interface ChatRequest {
  user_id: string
  role: RoleType
  message: string
  is_from_user: boolean
}

export interface ChatResponse {
  agent_role: RoleType
  message: string
  conversation_state?: any
}

export interface Suggestion {
  type: string
  message: string
  action: string
  priority: 'high' | 'medium' | 'low'
  from_agent?: RoleType | null
}

export interface Company {
  id: string
  user_id: string
  name: string
  description?: string
  industry?: string
  stage?: string
  company_info?: string
  product_overview?: string
  tech_stack?: string
  go_to_market_strategy?: string
  created_at: string
  updated_at: string
} 