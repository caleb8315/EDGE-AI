'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { User, RoleType } from '@/types'
import type { Suggestion } from '@/types'
import { Lightbulb, TrendingUp, Users, Target, AlertCircle, CheckCircle } from 'lucide-react'
import { agentApi } from '@/lib/api'
import { taskApi } from '@/lib/api'

interface ProactiveSuggestionsProps {
  user: User
}

const suggestionIcons = {
  collaboration: Users,
  growth: TrendingUp,
  strategy: Target,
  technical: AlertCircle,
  general: Lightbulb
}

const priorityColors = {
  high: 'bg-red-100 text-red-800 border-red-200',
  medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  low: 'bg-blue-100 text-blue-800 border-blue-200'
}

export default function ProactiveSuggestions({ user }: ProactiveSuggestionsProps) {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([])
  const [loading, setLoading] = useState(true)
  const [dismissedSuggestions, setDismissedSuggestions] = useState<Set<number>>(new Set())

  useEffect(() => {
    const cacheKey = `suggestions_${user.id}`
    const cached = typeof window !== 'undefined' ? localStorage.getItem(cacheKey) : null
    if (cached) {
      try {
        const parsed = JSON.parse(cached)
        const cacheAge = Date.now() - parsed.timestamp
        const maxAge = 5 * 60 * 1000 // 5 minutes
        if (cacheAge < maxAge && Array.isArray(parsed.data)) {
          setSuggestions(parsed.data)
          setLoading(false)
        } else {
          localStorage.removeItem(cacheKey)
          fetchSuggestions()
        }
      } catch {
        fetchSuggestions()
      }
    } else {
      fetchSuggestions()
    }
  }, [user.id])

  const fetchSuggestions = async () => {
    try {
      setLoading(true)
      const response = await agentApi.getProactiveSuggestions(user.id)

      if (response && Array.isArray(response.suggestions)) {
        // Filter out suggestions that originate from the user's own role
        const filtered = response.suggestions.filter((s: Suggestion) => s.from_agent !== user.role)
        setSuggestions(filtered)
        // Cache suggestions for 5 min
        const cacheKey = `suggestions_${user.id}`
        const payload = {
          timestamp: Date.now(),
          data: filtered,
        }
        try {
          localStorage.setItem(cacheKey, JSON.stringify(payload))
        } catch {}
      } else {
        setSuggestions([])
      }
    } catch (error) {
      console.error('Failed to fetch suggestions:', error)
      setSuggestions([])
    } finally {
      setLoading(false)
    }
  }

  const dismissSuggestion = (index: number) => {
    setDismissedSuggestions(prev => new Set(prev).add(index))
  }

  const handleTakeAction = async (suggestion: Suggestion, index: number) => {
    try {
      // Create a task based on the suggestion
      const newTask = await taskApi.create({
        user_id: user.id,
        assigned_to_role: suggestion.from_agent || user.role,
        description: suggestion.message,
        status: 'pending',
      } as any)
      window.dispatchEvent(new CustomEvent('task_created', { detail: newTask }))
      dismissSuggestion(index)
    } catch (e) {
      console.error('Failed to create task from suggestion:', e)
    }
  }

  const activeSuggestions = suggestions.filter((_, index) => !dismissedSuggestions.has(index))

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="w-5 h-5" />
            AI Insights
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Lightbulb className="w-5 h-5" />
          AI Team Insights
          {activeSuggestions.length > 0 && (
            <Badge variant="secondary" className="ml-2">
              {activeSuggestions.length} new
            </Badge>
          )}
        </CardTitle>
        <p className="text-sm text-gray-600">
          Proactive suggestions from your AI team based on recent activity
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        {activeSuggestions.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <CheckCircle className="w-12 h-12 mx-auto mb-3 text-gray-400" />
            <p className="font-medium">All caught up!</p>
            <p className="text-sm">Your AI team will notify you of new insights as they arise.</p>
          </div>
        ) : (
          activeSuggestions.map((suggestion, index) => {
            const IconComponent = suggestionIcons[suggestion.type as keyof typeof suggestionIcons] || Lightbulb
            
            return (
              <div
                key={index}
                className={`p-4 rounded-lg border-l-4 ${
                  suggestion.priority === 'high' 
                    ? 'border-l-red-500 bg-red-50' 
                    : suggestion.priority === 'medium'
                    ? 'border-l-yellow-500 bg-yellow-50'
                    : 'border-l-blue-500 bg-blue-50'
                }`}
              >
                <div className="flex items-start gap-3">
                  <IconComponent className="w-5 h-5 mt-0.5 text-gray-600" />
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge 
                        variant="outline" 
                        className={priorityColors[suggestion.priority]}
                      >
                        {suggestion.priority} priority
                      </Badge>
                      {suggestion.from_agent && (
                        <Badge variant="secondary" className="text-xs">
                          From AI {suggestion.from_agent}
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-gray-700 mb-3">
                      {suggestion.message}
                    </p>
                    <div className="flex items-center gap-2">
                      <Button size="sm" variant="outline" onClick={() => handleTakeAction(suggestion, index)}>
                        Take Action
                      </Button>
                      <Button 
                        size="sm" 
                        variant="ghost"
                        onClick={() => dismissSuggestion(index)}
                      >
                        Dismiss
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            )
          })
        )}
        
        {activeSuggestions.length > 0 && (
          <div className="pt-4 border-t">
            <Button 
              variant="outline" 
              size="sm" 
              className="w-full"
              onClick={fetchSuggestions}
            >
              Refresh Suggestions
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
} 