'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { userApi } from '@/lib/api'
import { RoleType } from '@/types'
import { getRoleColor, getRoleDescription } from '@/lib/utils'

const roles: { value: RoleType; label: string; description: string }[] = [
  { value: 'CEO', label: 'CEO', description: 'Vision, strategy, and financial decisions' },
  { value: 'CTO', label: 'CTO', description: 'Technical architecture and MVP development' },
  { value: 'CMO', label: 'CMO', description: 'Marketing strategy and growth' },
]

export default function OnboardingForm() {
  const [email, setEmail] = useState('')
  const [selectedRole, setSelectedRole] = useState<RoleType | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!email || !selectedRole) {
      setError('Please fill in all fields')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      const user = await userApi.onboard(email, selectedRole)
      
      // Store user data in localStorage for now (you might want to use a proper state management solution)
      localStorage.setItem('user', JSON.stringify(user))
      
      // Redirect to dashboard
      router.push('/dashboard')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create account. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Welcome to AI Startup Assistant</CardTitle>
          <CardDescription>
            Enter your email and choose your executive role to get started
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email Input */}
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium">
                Email Address
              </label>
              <Input
                id="email"
                type="email"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            {/* Role Selection */}
            <div className="space-y-4">
              <label className="text-sm font-medium">Choose Your Role</label>
              <div className="grid gap-4">
                {roles.map((role) => (
                  <div
                    key={role.value}
                    className={`p-4 border rounded-lg cursor-pointer transition-all ${
                      selectedRole === role.value
                        ? 'border-primary bg-primary/5 ring-2 ring-primary/20'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setSelectedRole(role.value)}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="flex items-center gap-3">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${getRoleColor(role.value)}`}>
                            {role.label}
                          </span>
                          <span className="font-medium">{role.label} - Chief Executive Officer</span>
                        </div>
                        <p className="text-sm text-gray-600 mt-1">{role.description}</p>
                      </div>
                      <div className={`w-4 h-4 rounded-full border-2 ${
                        selectedRole === role.value
                          ? 'border-primary bg-primary'
                          : 'border-gray-300'
                      }`}>
                        {selectedRole === role.value && (
                          <div className="w-full h-full rounded-full bg-white scale-50"></div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded">
                {error}
              </div>
            )}

            {/* Submit Button */}
            <Button 
              type="submit" 
              className="w-full" 
              size="lg"
              disabled={isLoading || !email || !selectedRole}
            >
              {isLoading ? 'Creating Account...' : 'Start Building Your Startup'}
            </Button>
          </form>

          {/* Info */}
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>What happens next?</strong> We'll create AI agents for the other executive roles 
              and generate initial tasks to help you get started with your startup journey.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 