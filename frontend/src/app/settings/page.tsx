"use client"

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { companyApi } from '@/lib/api'
import { User, Company } from '@/types'

export default function SettingsPage() {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [company, setCompany] = useState<Company | null>(null)

  const [companyName, setCompanyName] = useState('')
  const [companyDescription, setCompanyDescription] = useState('')
  const [industry, setIndustry] = useState('')
  const [stage, setStage] = useState('')
  const [companyInfo, setCompanyInfo] = useState('')
  const [productOverview, setProductOverview] = useState('')
  const [techStack, setTechStack] = useState('')
  const [goToMarketStrategy, setGoToMarketStrategy] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Load user & company info on mount
  useEffect(() => {
    const storedUser = localStorage.getItem('user')
    if (!storedUser) {
      router.push('/onboard')
      return
    }
    const parsedUser: User = JSON.parse(storedUser)
    setUser(parsedUser)

    ;(async () => {
      try {
        const comp = await companyApi.getByUser(parsedUser.id)
        if (comp) {
          setCompany(comp)
          setCompanyName(comp.name || '')
          setCompanyDescription(comp.description || '')
          setIndustry(comp.industry || '')
          setStage(comp.stage || '')
          setCompanyInfo(comp.company_info || '')
          setProductOverview(comp.product_overview || '')
          setTechStack(comp.tech_stack || '')
          setGoToMarketStrategy(comp.go_to_market_strategy || '')
        }
      } catch (e) {
        console.error(e)
      }
    })()
  }, [router])

  const handleSave = async () => {
    if (!user) return
    setIsSaving(true)
    setError('')
    setSuccess('')
    try {
      if (company) {
        // update
        const updated = await companyApi.update(company.id, {
          name: companyName,
          description: companyDescription,
          industry,
          stage,
          company_info: companyInfo,
          product_overview: productOverview,
          tech_stack: techStack,
          go_to_market_strategy: goToMarketStrategy,
        })
        setCompany(updated)
      } else {
        // create
        const created = await companyApi.create({
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
        setCompany(created)
      }
      setSuccess('Saved successfully')
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Failed to save changes')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <Card className="max-w-xl mx-auto">
          <CardHeader>
            <CardTitle>Startup Settings</CardTitle>
            <CardDescription>Update your project information anytime</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="space-y-2">
                <label htmlFor="companyName" className="text-sm font-medium">Company / Project Name</label>
                <Input id="companyName" value={companyName} onChange={(e) => setCompanyName(e.target.value)} />
              </div>
              <div className="space-y-2">
                <label htmlFor="companyDescription" className="text-sm font-medium">Description</label>
                <Input id="companyDescription" value={companyDescription} onChange={(e) => setCompanyDescription(e.target.value)} />
              </div>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label htmlFor="industry" className="text-sm font-medium">Industry</label>
                  <Input id="industry" value={industry} onChange={(e) => setIndustry(e.target.value)} />
                </div>
                <div className="space-y-2">
                  <label htmlFor="stage" className="text-sm font-medium">Stage</label>
                  <Input id="stage" value={stage} onChange={(e) => setStage(e.target.value)} />
                </div>
              </div>

              {/* Extended Context Fields */}
              <div className="space-y-2">
                <label htmlFor="companyInfo" className="text-sm font-medium">Company Info</label>
                <Input id="companyInfo" value={companyInfo} onChange={(e) => setCompanyInfo(e.target.value)} />
              </div>
              <div className="space-y-2">
                <label htmlFor="productOverview" className="text-sm font-medium">Product Overview</label>
                <Input id="productOverview" value={productOverview} onChange={(e) => setProductOverview(e.target.value)} />
              </div>
              <div className="space-y-2">
                <label htmlFor="techStack" className="text-sm font-medium">Tech Stack</label>
                <Input id="techStack" value={techStack} onChange={(e) => setTechStack(e.target.value)} />
              </div>
              <div className="space-y-2">
                <label htmlFor="gtmStrategy" className="text-sm font-medium">Go-to-Market Strategy</label>
                <Input id="gtmStrategy" value={goToMarketStrategy} onChange={(e) => setGoToMarketStrategy(e.target.value)} />
              </div>

              {error && <p className="text-sm text-red-600">{error}</p>}
              {success && <p className="text-sm text-green-600">{success}</p>}

              <Button onClick={handleSave} disabled={isSaving || !companyName} className="w-full">
                {isSaving ? 'Saving...' : 'Save Changes'}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
} 