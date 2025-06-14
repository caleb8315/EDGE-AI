'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { userApi } from '@/lib/api'

export default function LoginForm() {
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email) {
      setError('Please enter your email')
      return
    }
    setIsLoading(true)
    setError('')
    try {
      const user = await userApi.getByEmail(email)
      // persist
      localStorage.setItem('user', JSON.stringify(user))
      router.push('/dashboard')
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'User not found. Please check your email or onboard as new user.')
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
            {error && (
              <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded">
                {error}
              </div>
            )}
            <Button type="submit" className="w-full" size="lg" disabled={isLoading || !email}>
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