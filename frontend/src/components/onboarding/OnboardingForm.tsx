'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { userApi } from '@/lib/api'
import { companyApi } from '@/lib/api'
import { supabase } from '@/lib/supabaseClient'
import { RoleType } from '@/types'
import { getRoleColor } from '@/lib/utils'

const roles: { value: RoleType; label: string; description: string }[] = [
  { value: 'CEO', label: 'CEO', description: 'Vision, strategy, and financial decisions' },
  { value: 'CTO', label: 'CTO', description: 'Technical architecture and MVP development' },
  { value: 'CMO', label: 'CMO', description: 'Marketing strategy and growth' },
]

export default function OnboardingForm() {
  const [email, setEmail] = useState('')
  const [selectedRole, setSelectedRole] = useState<RoleType | null>(null)
  const [companyName, setCompanyName] = useState('')
  const [companyDescription, setCompanyDescription] = useState('')
  const [industry, setIndustry] = useState('')
  const [stage, setStage] = useState('Idea')
  const [companyInfo, setCompanyInfo] = useState('')
  const [productOverview, setProductOverview] = useState('')
  const [techStack, setTechStack] = useState('')
  const [goToMarketStrategy, setGoToMarketStrategy] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [suggestLoading, setSuggestLoading] = useState(false)
  const [error, setError] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!email || !password || !confirmPassword || !selectedRole || !companyName) {
      setError('Please fill in all required fields')
      return
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      // 1) Create user in Supabase Auth
      const { error: signUpError } = await supabase.auth.signUp({ email, password })

      if (signUpError) {
        throw new Error(signUpError.message)
      }

      // 2) Create user profile in our backend DB (role, etc.)
      const user = await userApi.onboard(email, selectedRole)
      
      // Create company profile
      await companyApi.create({
        user_id: user.id,
        name: companyName,
        description: companyDescription,
        industry,
        stage,
        company_info: companyInfo,
        product_overview: productOverview,
        tech_stack: techStack,
        go_to_market_strategy: goToMarketStrategy,
      })
      
      // Store user data & company in localStorage
      localStorage.setItem('user', JSON.stringify(user))
      
      // Redirect to dashboard
      router.push('/dashboard')
    } catch (err: any) {
      let msg = 'Failed to create account. Please try again.'
      
      if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
        msg = 'Account creation is taking longer than expected. Your account may have been created successfully. Try logging in or wait a moment and try again.'
      } else if (err?.response?.data?.detail) {
        msg = err.response.data.detail
      } else if (err.message) {
        msg = err.message
      }
      
      setError(msg)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSuggest = async () => {
    if (!companyName) return
    try {
      setSuggestLoading(true)
      const suggestions = await companyApi.suggest({ name: companyName, description: companyDescription })
      setCompanyInfo(suggestions.company_info)
      setProductOverview(suggestions.product_overview)
      setTechStack(suggestions.tech_stack)
      setGoToMarketStrategy(suggestions.go_to_market_strategy)
    } catch (e) {
      console.error('Failed to get suggestions', e)
    } finally {
      setSuggestLoading(false)
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
            {/* Email & Password */}
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

            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label htmlFor="password" className="text-sm font-medium">
                  Password
                </label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Create a strong password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <label htmlFor="confirmPassword" className="text-sm font-medium">
                  Confirm Password
                </label>
                <Input
                  id="confirmPassword"
                  type="password"
                  placeholder="Repeat password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                />
              </div>
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

            {/* Company Name */}
            <div className="space-y-2">
              <label htmlFor="companyName" className="text-sm font-medium">
                Company / Project Name
              </label>
              <Input
                id="companyName"
                placeholder="My Awesome Startup"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                required
              />
            </div>
            {/* Company Description */}
            <div className="space-y-2">
              <label htmlFor="companyDescription" className="text-sm font-medium">
                One-line Description
              </label>
              <Input
                id="companyDescription"
                placeholder="e.g., AI-powered marketing analytics platform"
                value={companyDescription}
                onChange={(e) => setCompanyDescription(e.target.value)}
              />
            </div>
            {/* Industry & Stage */}
            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label htmlFor="industry" className="text-sm font-medium">
                  Industry
                </label>
                <Input
                  id="industry"
                  placeholder="FinTech, HealthTech, etc."
                  value={industry}
                  onChange={(e) => setIndustry(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <label htmlFor="stage" className="text-sm font-medium">
                  Stage
                </label>
                <Input
                  id="stage"
                  placeholder="Idea, Prototype, Launched"
                  value={stage}
                  onChange={(e) => setStage(e.target.value)}
                />
              </div>
            </div>

            {/* Additional Context Fields */}
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium">Additional Context (optional)</h3>
              <Button type="button" size="sm" variant="outline" onClick={handleSuggest} disabled={!companyName || suggestLoading}>
                {suggestLoading ? 'Generating...' : 'Get AI Suggestions'}
              </Button>
            </div>

            {/* Extended Context Fields */}
            <div className="space-y-2">
              <label htmlFor="companyInfo" className="text-sm font-medium">
                Company Info
              </label>
              <Input
                id="companyInfo"
                placeholder="Brief background of your company"
                value={companyInfo}
                onChange={(e) => setCompanyInfo(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="productOverview" className="text-sm font-medium">
                Product Overview
              </label>
              <Input
                id="productOverview"
                placeholder="Describe your main product"
                value={productOverview}
                onChange={(e) => setProductOverview(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="techStack" className="text-sm font-medium">
                Tech Stack
              </label>
              <Input
                id="techStack"
                placeholder="e.g., React, Next.js, Python, FastAPI"
                value={techStack}
                onChange={(e) => setTechStack(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="gtmStrategy" className="text-sm font-medium">
                Go-to-Market Strategy
              </label>
              <Input
                id="gtmStrategy"
                placeholder="e.g., target early adopters via ..."
                value={goToMarketStrategy}
                onChange={(e) => setGoToMarketStrategy(e.target.value)}
              />
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
              disabled={isLoading || !email || !password || !confirmPassword || !selectedRole || !companyName}
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