'use client'

import { useState, useEffect, createElement } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import ChatInterface from '@/components/dashboard/ChatInterface'
import TasksAndResources from '@/components/dashboard/TasksAndResources'
import ProactiveSuggestions from '@/components/dashboard/ProactiveSuggestions'
import CodebasePanel from '@/components/dashboard/CodebasePanel'
import { User, RoleType } from '@/types'
import { getRoleColor, getRoleDescription } from '@/lib/utils'
import { LogOut, Settings, User as UserIcon, Brain, Target, Zap, Sparkles } from 'lucide-react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import TaskList from '@/components/dashboard/TaskList'
import { supabase } from '@/lib/supabaseClient'

const roleIcons = {
  CEO: Target,
  CTO: Brain,
  CMO: Zap
}

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null)
  const [selectedAgent, setSelectedAgent] = useState<RoleType>('CEO')
  const router = useRouter()

  useEffect(() => {
    // Get user from localStorage (in a real app, you'd use proper state management)
    const userData = localStorage.getItem('user')
    if (userData) {
      const parsedUser = JSON.parse(userData)
      setUser(parsedUser)
      
      // Set default selected agent to the first AI role (not the user's role)
      const aiRoles = (['CEO', 'CTO', 'CMO'].filter(role => role !== parsedUser.role) as RoleType[])
      if (aiRoles.length > 0) {
        setSelectedAgent(aiRoles[0])
      }
    } else {
      // Redirect to onboarding if no user data
      router.push('/onboard')
    }
  }, [router])

  const handleLogout = async () => {
    await supabase.auth.signOut()
    localStorage.removeItem('user')
    router.push('/')
  }

  const handleSettings = () => {
    router.push('/settings')
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p>Loading your AI-powered startup dashboard...</p>
        </div>
      </div>
    )
  }

  const aiRoles = (['CEO', 'CTO', 'CMO'].filter(role => role !== user.role) as RoleType[])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Enhanced Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <Sparkles className="w-8 h-8 text-primary" />
              AI Startup Assistant
            </h1>
            <p className="text-gray-600 mt-1">
              Welcome back! You're the <span className="font-medium">{user.role}</span> with your intelligent AI team.
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <UserIcon className="w-4 h-4" />
              {user.email}
              <Badge className={getRoleColor(user.role)}>
                {user.role}
              </Badge>
            </div>
            <Button variant="outline" size="sm" onClick={handleSettings}>
              <Settings className="w-4 h-4 mr-2" />
              Settings
            </Button>
            <Button variant="outline" size="sm" onClick={handleLogout}>
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>

        {/* Enhanced Role Overview */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          {(['CEO', 'CTO', 'CMO'] as RoleType[]).map((role) => {
            const isUserRole = user.role === role
            const isAiRole = !isUserRole
            const RoleIcon = roleIcons[role]
            
            return (
              <Card 
                key={role}
                className={`transition-all duration-200 ${
                  isUserRole 
                    ? 'ring-2 ring-primary/50 bg-primary/5' 
                    : isAiRole 
                    ? 'hover:shadow-md cursor-pointer border-2 border-dashed border-gray-200 hover:border-primary/30' 
                    : ''
                }`}
                onClick={isAiRole ? () => setSelectedAgent(role) : undefined}
              >
                <CardHeader className="pb-3">
                  <CardTitle className="flex items-center gap-2">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      role === 'CEO' ? 'bg-purple-500' : 
                      role === 'CTO' ? 'bg-blue-500' : 'bg-green-500'
                    }`}>
                      <RoleIcon className="w-4 h-4 text-white" />
                    </div>
                    <div className="flex items-center gap-2">
                      {isAiRole && <Badge variant="secondary" className="text-xs">AI</Badge>}
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getRoleColor(role)}`}>
                        {role}
                      </span>
                      {isUserRole && <span className="text-sm text-primary font-medium">(You)</span>}
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600">{getRoleDescription(role)}</p>
                  {isAiRole && (
                    <div className="mt-3 flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="text-xs text-green-600 font-medium">AI Agent Active</span>
                    </div>
                  )}
                </CardContent>
              </Card>
            )
          })}
        </div>

        {/* Main Dashboard - 2 Column Layout */}
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column: Tasks, Resources, etc. */}
          <div className="lg:col-span-1 space-y-6">
            <TaskList user={user} />
            <TasksAndResources userId={user.id} />
            <CodebasePanel userId={user.id} />
            <ProactiveSuggestions user={user} />
          </div>

          {/* Right Column: Chat Interface with Tabs */}
          <div className="lg:col-span-2">
             <Tabs value={selectedAgent} onValueChange={(value: string) => setSelectedAgent(value as RoleType)} className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                {aiRoles.map((role) => {
                  const RoleIcon = roleIcons[role]
                  return (
                    <TabsTrigger key={role} value={role}>
                      <div className="flex items-center gap-2">
                        <RoleIcon className="w-4 h-4" />
                        <span>AI {role}</span>
                      </div>
                    </TabsTrigger>
                  )
                })}
              </TabsList>
              {aiRoles.map((role) => (
                <TabsContent key={role} value={role} className="mt-4">
                  <ChatInterface user={user} selectedAgent={role} key={role} />
                </TabsContent>
              ))}
            </Tabs>
          </div>
        </div>

        {/* AI Team Status Footer */}
        <div className="mt-12 text-center">
          <div className="inline-flex items-center gap-2 text-sm text-gray-600 bg-white px-4 py-2 rounded-full shadow-sm">
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span>AI Team Active</span>
            </div>
            <span className="text-gray-400">•</span>
            <span>{aiRoles.length} AI agents supporting your startup</span>
          </div>
        </div>
      </div>
    </div>
  )
} 