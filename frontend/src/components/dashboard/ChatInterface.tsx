'use client'

import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { agentApi } from '@/lib/api'
import { RoleType, ChatMessage, User, ChatResponse } from '@/types'
import { getRoleColor, formatDate } from '@/lib/utils'
import { Send, Bot, User as UserIcon, Brain, Zap, Target } from 'lucide-react'

interface ChatInterfaceProps {
  user: User
  selectedAgent: RoleType
}

// Enhanced agent personalities and descriptions
const agentPersonalities = {
  CEO: {
    icon: Target,
    personality: "Strategic & Visionary",
    expertise: ["Vision & Strategy", "Fundraising", "Leadership", "Market Analysis"],
    description: "Your AI CEO partner focuses on strategic decisions, market positioning, and long-term vision.",
    color: "bg-purple-500"
  },
  CTO: {
    icon: Brain,
    personality: "Technical & Pragmatic", 
    expertise: ["Architecture", "MVP Development", "Tech Stack", "Scaling"],
    description: "Your AI CTO partner handles technical architecture, development strategy, and engineering decisions.",
    color: "bg-blue-500"
  },
  CMO: {
    icon: Zap,
    personality: "Creative & Data-Driven",
    expertise: ["Growth Strategy", "Brand Development", "Customer Acquisition", "Analytics"],
    description: "Your AI CMO partner drives growth, marketing strategy, and customer engagement.",
    color: "bg-green-500"
  }
}

export default function ChatInterface({ user, selectedAgent }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [newMessage, setNewMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [agentStatus, setAgentStatus] = useState<any>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const typingIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Load conversation history for the selected agent
    const loadHistory = async () => {
      try {
        const agents = await agentApi.getUserAgents(user.id)
        const target = agents.find(a => a.role === selectedAgent)
        if (target && target.conversation_state && Array.isArray(target.conversation_state.messages)) {
          const hist = target.conversation_state.messages || []
          setMessages(hist.slice(-10))
          setAgentStatus(target.conversation_state)
        } else {
          setMessages([])
          setAgentStatus(null)
        }
      } catch (err) {
        console.error('Failed to load conversation history:', err)
        setMessages([])
        setAgentStatus(null)
      }
    }

    loadHistory()
  }, [selectedAgent])

  // Get agent personality info
  const agentInfo = agentPersonalities[selectedAgent]
  const AgentIcon = agentInfo.icon

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!newMessage.trim() || isLoading) return

    const userMessage: ChatMessage = {
      message: newMessage,
      is_from_user: true,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setNewMessage('')
    setIsLoading(true)

    try {
      const response: ChatResponse = await agentApi.chat({
        user_id: user.id,
        role: selectedAgent,
        message: newMessage,
        is_from_user: true
      })

      // Typing animation for agent response
      const fullText = response.message
      const newMsg: ChatMessage = {
        message: '',
        is_from_user: false,
        timestamp: new Date().toISOString()
      }

      setMessages(prev => [...prev, newMsg])

      let charIndex = 0
      typingIntervalRef.current && clearInterval(typingIntervalRef.current)
      typingIntervalRef.current = setInterval(() => {
        charIndex++
        setMessages(prev => {
          const updated = [...prev]
          const lastIndex = updated.length - 1
          updated[lastIndex] = {
            ...updated[lastIndex],
            message: fullText.slice(0, charIndex)
          }
          return updated
        })
        if (charIndex >= fullText.length) {
          if (typingIntervalRef.current) clearInterval(typingIntervalRef.current)
        }
      }, 20) // typing speed ms per char

      // Update agent status if available
      if (response.conversation_state) {
        setAgentStatus(response.conversation_state)
      }
    } catch (error) {
      console.error('Failed to send message:', error)
      const errorMessage: ChatMessage = {
        message: 'Sorry, I encountered an error. Please try again.',
        is_from_user: false,
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card className="h-[700px] flex flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-full ${agentInfo.color} flex items-center justify-center`}>
              <AgentIcon className="w-5 h-5 text-white" />
            </div>
            <div>
              <CardTitle className="flex items-center gap-2">
                AI {selectedAgent}
                <Badge variant="secondary" className={getRoleColor(selectedAgent)}>
                  {agentInfo.personality}
                </Badge>
              </CardTitle>
              <p className="text-sm text-gray-600 mt-1">{agentInfo.description}</p>
            </div>
          </div>
          
          {agentStatus && (
            <div className="text-right text-sm text-gray-500">
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                Active
              </div>
              {agentStatus.message_count > 0 && (
                <div className="mt-1">
                  {agentStatus.message_count} messages
                </div>
              )}
            </div>
          )}
        </div>
        
        {/* Agent Expertise Tags */}
        <div className="flex flex-wrap gap-1 mt-3">
          {agentInfo.expertise.map((skill, index) => (
            <Badge key={index} variant="outline" className="text-xs">
              {skill}
            </Badge>
          ))}
        </div>
      </CardHeader>
      
      <CardContent className="flex-1 flex flex-col p-0 min-h-0">
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-500 py-8">
              <div className={`w-16 h-16 rounded-full ${agentInfo.color} flex items-center justify-center mx-auto mb-4`}>
                <AgentIcon className="w-8 h-8 text-white" />
              </div>
              <h3 className="font-medium mb-2">Start a conversation with your AI {selectedAgent}</h3>
              <p className="text-sm">I'm here to help with {agentInfo.expertise.slice(0, 2).join(", ").toLowerCase()} and more!</p>
              
              {/* Suggested conversation starters */}
              <div className="mt-6 space-y-2">
                <p className="text-xs font-medium text-gray-700">Try asking:</p>
                <div className="space-y-1">
                  {selectedAgent === 'CEO' && (
                    <>
                      <Button variant="ghost" size="sm" className="text-xs h-auto py-1 px-2" 
                        onClick={() => setNewMessage("What should our 6-month strategic priorities be?")}>
                        "What should our 6-month strategic priorities be?"
                      </Button>
                      <Button variant="ghost" size="sm" className="text-xs h-auto py-1 px-2"
                        onClick={() => setNewMessage("How do we identify our target market?")}>
                        "How do we identify our target market?"
                      </Button>
                    </>
                  )}
                  {selectedAgent === 'CTO' && (
                    <>
                      <Button variant="ghost" size="sm" className="text-xs h-auto py-1 px-2"
                        onClick={() => setNewMessage("What's the best tech stack for our MVP?")}>
                        "What's the best tech stack for our MVP?"
                      </Button>
                      <Button variant="ghost" size="sm" className="text-xs h-auto py-1 px-2"
                        onClick={() => setNewMessage("How do we plan for scalable architecture?")}>
                        "How do we plan for scalable architecture?"
                      </Button>
                    </>
                  )}
                  {selectedAgent === 'CMO' && (
                    <>
                      <Button variant="ghost" size="sm" className="text-xs h-auto py-1 px-2"
                        onClick={() => setNewMessage("What's our customer acquisition strategy?")}>
                        "What's our customer acquisition strategy?"
                      </Button>
                      <Button variant="ghost" size="sm" className="text-xs h-auto py-1 px-2"
                        onClick={() => setNewMessage("How do we build our brand identity?")}>
                        "How do we build our brand identity?"
                      </Button>
                    </>
                  )}
                </div>
              </div>
            </div>
          )}
          
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex gap-3 ${message.is_from_user ? 'justify-end' : 'justify-start'}`}
            >
              {!message.is_from_user && (
                <div className={`w-8 h-8 rounded-full ${agentInfo.color} flex items-center justify-center flex-shrink-0`}>
                  <AgentIcon className="w-4 h-4 text-white" />
                </div>
              )}
              
              <div className={`max-w-[75%] min-w-0 ${message.is_from_user ? 'order-first' : ''}`}>
                <div
                  className={`p-3 rounded-lg ${
                    message.is_from_user
                      ? 'bg-primary text-primary-foreground ml-auto'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap break-all">{message.message}</p>
                </div>
                <p className="text-xs text-gray-500 mt-1 px-1">
                  {formatDate(message.timestamp)}
                </p>
              </div>
              
              {message.is_from_user && (
                <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                  <UserIcon className="w-4 h-4 text-primary-foreground" />
                </div>
              )}
            </div>
          ))}
          
          {isLoading && (
            <div className="flex gap-3 justify-start">
              <div className={`w-8 h-8 rounded-full ${agentInfo.color} flex items-center justify-center`}>
                <AgentIcon className="w-4 h-4 text-white" />
              </div>
              <div className="bg-gray-100 p-3 rounded-lg">
                <div className="flex items-center space-x-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                  <span className="text-xs text-gray-600">AI {selectedAgent} is thinking...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Message Input */}
        <div className="border-t p-4">
          <form onSubmit={handleSendMessage} className="flex gap-2">
            <Input
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder={`Ask your AI ${selectedAgent} about ${agentInfo.expertise[0].toLowerCase()}...`}
              disabled={isLoading}
              className="flex-1"
            />
            <Button type="submit" disabled={isLoading || !newMessage.trim()}>
              <Send className="w-4 h-4" />
            </Button>
          </form>
          <p className="text-xs text-gray-500 mt-2">
            💡 Your AI {selectedAgent} has deep {agentInfo.expertise.join(", ").toLowerCase()} expertise
          </p>
        </div>
      </CardContent>
    </Card>
  )
} 