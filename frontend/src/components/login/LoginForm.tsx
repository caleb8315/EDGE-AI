'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { userApi } from '@/lib/api'
import { supabase } from '@/lib/supabaseClient'

export default function LoginForm() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email || !password) {
      setError('Please enter both email and password')
      return
    }
    setIsLoading(true)
    setError('')
    try {
      // 1) Authenticate with Supabase Auth
      const { error: authError } = await supabase.auth.signInWithPassword({ email, password })

      if (authError) {
        throw new Error(authError.message)
      }

      // 2) Fetch the user profile from our backend (contains role, etc.)
      const user = await userApi.getByEmail(email)

      // 3) Persist user profile locally
      localStorage.setItem('user', JSON.stringify(user))

      // 4) Navigate to dashboard
      router.push('/dashboard')
    } catch (err: any) {
      // Axios errors from backend or thrown auth errors from Supabase arrive here
      const msg = err?.response?.data?.detail || err.message || 'Login failed. Please try again or onboard as a new user.'
      setError(msg)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-md mx-auto">
      <Card>
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Welcome Back</CardTitle>
          <CardDescription>Log in with your email to continue</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium">Email</label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium">Password</label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            {error && (
              <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded">
                {error}
              </div>
            )}
            <Button type="submit" className="w-full" size="lg" disabled={isLoading || !email || !password}>
              {isLoading ? 'Signing In...' : 'Login'}
            </Button>
            <p className="text-sm text-center text-gray-600">
              New here? <a className="text-primary underline" href="/onboard">Create an account</a>
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  )
} 