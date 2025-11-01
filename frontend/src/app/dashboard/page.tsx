'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import Navbar from '@/components/navbar'
import AgentCard from '@/components/dashboard/agent-card'
import ConfigNotice from '@/components/config-notice'
import { createSupabaseClient, isSupabaseReady } from '@/lib/supabase'
import { agentAPI } from '@/lib/fastapi'
import { 
  Brain, 
  BarChart3, 
  TrendingUp, 
  Users, 
  Zap, 
  Shield,
  Play,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Settings,
  User
} from 'lucide-react'

interface AgentStatus {
  status: 'idle' | 'running' | 'completed' | 'error'
  results?: any
  error?: string
}

interface AgentStates {
  shortlisting: AgentStatus
  dataIngestion: AgentStatus
  sentimentAnalysis: AgentStatus
  technicalAnalysis: AgentStatus
  prediction: AgentStatus
  portfolioManager: AgentStatus
}

export default function DashboardPage() {
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [sector, setSector] = useState('Technology')
  const [runningComplete, setRunningComplete] = useState(false)
  const [agentStates, setAgentStates] = useState<AgentStates>({
    shortlisting: { status: 'idle' },
    dataIngestion: { status: 'idle' },
    sentimentAnalysis: { status: 'idle' },
    technicalAnalysis: { status: 'idle' },
    prediction: { status: 'idle' },
    portfolioManager: { status: 'idle' }
  })

  const router = useRouter()
  const supabase = createSupabaseClient()

  useEffect(() => {
    const getUser = async () => {
      if (!isSupabaseReady() || !supabase) {
        // Demo mode - allow access without authentication
        setUser({ email: 'demo@example.com' } as any)
        setLoading(false)
        return
      }

      try {
        const { data: { user } } = await supabase.auth.getUser()
        if (!user) {
          router.push('/auth/login')
          return
        }
        setUser(user)
      } catch (error) {
        console.error('Error getting user:', error)
        router.push('/auth/login')
      } finally {
        setLoading(false)
      }
    }

    getUser()
  }, [supabase, router])

  const updateAgentState = (agent: keyof AgentStates, update: Partial<AgentStatus>) => {
    setAgentStates(prev => ({
      ...prev,
      [agent]: { ...prev[agent], ...update }
    }))
  }

  const runAgent = async (agentType: keyof AgentStates) => {
    updateAgentState(agentType, { status: 'running', error: undefined })

    try {
      let results
      switch (agentType) {
        case 'shortlisting':
          results = await agentAPI.shortlistCompanies(sector, 15)
          break
        case 'dataIngestion':
          // This would typically use results from shortlisting
          results = await agentAPI.getStockData('AAPL') // Example ticker
          break
        case 'sentimentAnalysis':
          results = await agentAPI.runSentimentAnalysis('AAPL', [], [])
          break
        case 'technicalAnalysis':
          results = await agentAPI.runTechnicalAnalysis('AAPL', {})
          break
        case 'prediction':
          results = await agentAPI.runPredictionAnalysis('AAPL')
          break
        case 'portfolioManager':
          results = await agentAPI.getPortfolioRecommendation({})
          break
      }

      updateAgentState(agentType, { status: 'completed', results })
    } catch (error) {
      updateAgentState(agentType, { 
        status: 'error', 
        error: error instanceof Error ? error.message : 'Unknown error' 
      })
    }
  }

  const runCompleteAnalysis = async () => {
    setRunningComplete(true)
    
    try {
      // Reset all agents
      Object.keys(agentStates).forEach(agent => {
        updateAgentState(agent as keyof AgentStates, { status: 'idle' })
      })

      // Run complete analysis workflow
      const results = await agentAPI.runCompleteAnalysis(sector, {
        risk_tolerance: 'medium',
        investment_horizon: 'long_term',
        preferred_sectors: [sector]
      })

      // Update all agents as completed
      Object.keys(agentStates).forEach(agent => {
        updateAgentState(agent as keyof AgentStates, { 
          status: 'completed', 
          results: results[agent] || 'Analysis completed' 
        })
      })

    } catch (error) {
      console.error('Complete analysis failed:', error)
      // Mark all as error
      Object.keys(agentStates).forEach(agent => {
        updateAgentState(agent as keyof AgentStates, { 
          status: 'error', 
          error: 'Complete analysis failed' 
        })
      })
    } finally {
      setRunningComplete(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <div className="container mx-auto px-4 py-8">
        {/* Configuration Notice */}
        <div className="mb-6">
          <ConfigNotice />
        </div>
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold">Investment Dashboard</h1>
              <p className="text-muted-foreground">
                Welcome back, {user?.email?.split('@')[0]}! Manage your AI-powered investment analysis.
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <Button
                onClick={runCompleteAnalysis}
                disabled={runningComplete}
                size="lg"
                className="flex items-center space-x-2"
              >
                {runningComplete ? (
                  <RefreshCw className="h-4 w-4 animate-spin" />
                ) : (
                  <Play className="h-4 w-4" />
                )}
                <span>{runningComplete ? 'Running...' : 'Run Complete Analysis'}</span>
              </Button>
            </div>
          </div>

          {/* Sector Selection */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Settings className="h-5 w-5" />
                <span>Analysis Configuration</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <label htmlFor="sector" className="text-sm font-medium mb-2 block">
                    Target Sector
                  </label>
                  <Input
                    id="sector"
                    value={sector}
                    onChange={(e) => setSector(e.target.value)}
                    placeholder="Enter sector (e.g., Technology, Healthcare)"
                  />
                </div>
                <div className="flex items-center space-x-2 pt-6">
                  <Badge variant="secondary">
                    {Object.values(agentStates).filter(s => s.status === 'completed').length}/6 Completed
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="agents" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="agents">AI Agents</TabsTrigger>
            <TabsTrigger value="results">Analysis Results</TabsTrigger>
            <TabsTrigger value="profile">Profile Settings</TabsTrigger>
          </TabsList>

          <TabsContent value="agents" className="space-y-6">
            {/* AI Agents Grid */}
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              <AgentCard
                title="Company Shortlisting"
                description="Identify promising investment opportunities based on your preferences"
                icon={Brain}
                status={agentStates.shortlisting.status}
                onRun={() => runAgent('shortlisting')}
                results={agentStates.shortlisting.results}
                loading={agentStates.shortlisting.status === 'running'}
              />

              <AgentCard
                title="Data Ingestion"
                description="Collect real-time market data, news, and social sentiment"
                icon={BarChart3}
                status={agentStates.dataIngestion.status}
                onRun={() => runAgent('dataIngestion')}
                results={agentStates.dataIngestion.results}
                loading={agentStates.dataIngestion.status === 'running'}
              />

              <AgentCard
                title="Sentiment Analysis"
                description="Analyze market sentiment from news and social media"
                icon={Users}
                status={agentStates.sentimentAnalysis.status}
                onRun={() => runAgent('sentimentAnalysis')}
                results={agentStates.sentimentAnalysis.results}
                loading={agentStates.sentimentAnalysis.status === 'running'}
              />

              <AgentCard
                title="Technical Analysis"
                description="Perform advanced technical analysis and identify trends"
                icon={TrendingUp}
                status={agentStates.technicalAnalysis.status}
                onRun={() => runAgent('technicalAnalysis')}
                results={agentStates.technicalAnalysis.results}
                loading={agentStates.technicalAnalysis.status === 'running'}
              />

              <AgentCard
                title="Prediction Engine"
                description="Forecast price movements using machine learning"
                icon={Zap}
                status={agentStates.prediction.status}
                onRun={() => runAgent('prediction')}
                results={agentStates.prediction.results}
                loading={agentStates.prediction.status === 'running'}
              />

              <AgentCard
                title="Portfolio Manager"
                description="Generate personalized investment recommendations"
                icon={Shield}
                status={agentStates.portfolioManager.status}
                onRun={() => runAgent('portfolioManager')}
                results={agentStates.portfolioManager.results}
                loading={agentStates.portfolioManager.status === 'running'}
              />
            </div>
          </TabsContent>

          <TabsContent value="results" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Analysis Results</CardTitle>
                <CardDescription>
                  Comprehensive results from all AI agents
                </CardDescription>
              </CardHeader>
              <CardContent>
                {Object.values(agentStates).some(s => s.status === 'completed') ? (
                  <div className="space-y-4">
                    {Object.entries(agentStates).map(([agent, state]) => (
                      state.status === 'completed' && (
                        <div key={agent} className="border rounded-lg p-4">
                          <h3 className="font-semibold mb-2 capitalize">
                            {agent.replace(/([A-Z])/g, ' $1').trim()}
                          </h3>
                          <div className="bg-muted/50 p-3 rounded text-sm">
                            <pre className="whitespace-pre-wrap max-h-40 overflow-y-auto">
                              {typeof state.results === 'string' 
                                ? state.results 
                                : JSON.stringify(state.results, null, 2)
                              }
                            </pre>
                          </div>
                        </div>
                      )
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <AlertCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <h3 className="text-lg font-semibold mb-2">No Results Yet</h3>
                    <p className="text-muted-foreground mb-4">
                      Run individual agents or complete analysis to see results here.
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="profile" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <User className="h-5 w-5" />
                  <span>Investor Profile</span>
                </CardTitle>
                <CardDescription>
                  Configure your investment preferences for personalized analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium mb-2 block">Risk Tolerance</label>
                    <div className="flex space-x-2">
                      {['Conservative', 'Moderate', 'Aggressive'].map((risk) => (
                        <Badge key={risk} variant="outline" className="cursor-pointer">
                          {risk}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">Investment Horizon</label>
                    <div className="flex space-x-2">
                      {['Short Term', 'Medium Term', 'Long Term'].map((horizon) => (
                        <Badge key={horizon} variant="outline" className="cursor-pointer">
                          {horizon}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">Preferred Sectors</label>
                    <Input placeholder="Technology, Healthcare, Finance..." />
                  </div>
                  <Button className="w-full">Save Profile</Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
