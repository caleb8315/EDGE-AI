import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Brain, Users, Zap } from 'lucide-react'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        {/* Hero Section */}
        <div className="text-center max-w-4xl mx-auto mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            AI-Powered Startup Assistant
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Choose your executive role and let AI agents fill the other positions. 
            Collaborate with AI CEO, CTO, and CMO to build your startup.
          </p>
          <Link href="/onboard">
            <Button size="lg" className="text-lg px-8 py-3">
              Get Started
            </Button>
          </Link>
          <Link href="/login" className="ml-4 inline-block">
            <Button variant="outline" size="lg" className="text-lg px-8 py-3">
              Login
            </Button>
          </Link>
        </div>

        {/* Features Section */}
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          <Card>
            <CardHeader className="text-center">
              <Brain className="w-12 h-12 mx-auto mb-4 text-blue-600" />
              <CardTitle>AI-Powered Collaboration</CardTitle>
              <CardDescription>
                Work alongside intelligent AI agents that understand your business needs
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader className="text-center">
              <Users className="w-12 h-12 mx-auto mb-4 text-green-600" />
              <CardTitle>Executive Team</CardTitle>
              <CardDescription>
                Choose CEO, CTO, or CMO role while AI fills the other executive positions
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader className="text-center">
              <Zap className="w-12 h-12 mx-auto mb-4 text-purple-600" />
              <CardTitle>Real-time Insights</CardTitle>
              <CardDescription>
                Get instant feedback, task management, and strategic guidance
              </CardDescription>
            </CardHeader>
          </Card>
        </div>

        {/* Role Cards */}
        <div className="mt-16 max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-8">Choose Your Role</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="text-purple-600">CEO</CardTitle>
                <CardDescription>
                  Vision, strategy, and financial decisions
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="text-sm text-gray-600 space-y-2">
                  <li>• Strategic planning</li>
                  <li>• Investor relations</li>
                  <li>• Company culture</li>
                  <li>• Market positioning</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="text-blue-600">CTO</CardTitle>
                <CardDescription>
                  Technical architecture and MVP development
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="text-sm text-gray-600 space-y-2">
                  <li>• System design</li>
                  <li>• Technology stack</li>
                  <li>• Engineering roadmap</li>
                  <li>• Security & scalability</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="text-green-600">CMO</CardTitle>
                <CardDescription>
                  Marketing strategy and growth
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="text-sm text-gray-600 space-y-2">
                  <li>• Brand positioning</li>
                  <li>• Customer acquisition</li>
                  <li>• Content marketing</li>
                  <li>• Growth analytics</li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
} 