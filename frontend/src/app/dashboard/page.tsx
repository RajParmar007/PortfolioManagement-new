'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import Navbar from '@/components/navbar'
import AgentCard from '@/components/dashboard/agent-card'
import { agentAPI } from '@/lib/fastapi'
import { Brain, BarChart3, Users, Shield } from 'lucide-react'

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
  // User preferences state
  const [sector, setSector] = useState('Technology')
  const [riskTolerance, setRiskTolerance] = useState<'low' | 'medium' | 'high'>('medium')
  const [initialInvestment, setInitialInvestment] = useState<number>(10000)
  const [investmentGoal, setInvestmentGoal] = useState<number>(50000)
  const [timeframe, setTimeframe] = useState<number>(5)
  
  // Calculate investment horizon based on timeframe
  const getInvestmentHorizon = (years: number): 'short_term' | 'medium_term' | 'long_term' => {
    if (years <= 3) return 'short_term'
    if (years <= 7) return 'medium_term'
    return 'long_term'
  }
  
  const investmentHorizon = getInvestmentHorizon(timeframe)
  
  // Agent states
  const [runningComplete, setRunningComplete] = useState(false)
  const [agentStates, setAgentStates] = useState<AgentStates>({
    shortlisting: { status: 'idle' },
    dataIngestion: { status: 'idle' },
    sentimentAnalysis: { status: 'idle' },
    technicalAnalysis: { status: 'idle' },
    prediction: { status: 'idle' },
    portfolioManager: { status: 'idle' }
  })

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
          results = await agentAPI.shortlistCompanies({ 
            sector, 
            limit: 15,
            risk_tolerance: riskTolerance,
            investment_horizon: investmentHorizon
          })
          break
        case 'dataIngestion':
          results = await agentAPI.getStockData(['AAPL'])
          break
        case 'sentimentAnalysis':
          results = await agentAPI.runSentimentAnalysis(['AAPL'])
          break
        case 'technicalAnalysis':
          results = await agentAPI.runTechnicalAnalysis(['AAPL'])
          break
        case 'prediction':
          results = await agentAPI.runPredictionAnalysis(['AAPL'])
          break
        case 'portfolioManager':
          results = await agentAPI.getPortfolioRecommendation({
            risk_tolerance: riskTolerance,
            investment_horizon: investmentHorizon,
            preferred_sectors: [sector],
            initial_investment: initialInvestment,
            investment_goal: investmentGoal,
            timeframe_years: timeframe
          })
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
      const results = await agentAPI.runCompleteAnalysis({
        sector,
        risk_tolerance: riskTolerance,
        investment_horizon: investmentHorizon,
        preferred_sectors: [sector],
        initial_investment: initialInvestment,
        investment_goal: investmentGoal,
        timeframe_years: timeframe
      })

      // Update all agents as completed
      Object.keys(agentStates).forEach(agent => {
        updateAgentState(agent as keyof AgentStates, { 
          status: 'completed', 
          results: results[agent] || 'Analysis completed' 
        })
      })
    } catch (error) {
      console.error('Error running complete analysis:', error)
    } finally {
      setRunningComplete(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Portfolio Manager</h1>
          <p className="text-gray-600">Get personalized investment recommendations based on your preferences</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Input Panel */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle>Investment Preferences</CardTitle>
                <CardDescription>Configure your investment strategy</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Sector</label>
                  <select 
                    className="w-full p-2 border rounded-md"
                    value={sector}
                    onChange={(e) => setSector(e.target.value)}
                  >
                    <option value="Technology">Technology</option>
                    <option value="Finance">Finance</option>
                    <option value="Healthcare">Healthcare</option>
                    <option value="Energy">Energy</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Risk Tolerance</label>
                  <select 
                    className="w-full p-2 border rounded-md"
                    value={riskTolerance}
                    onChange={(e) => setRiskTolerance(e.target.value as 'low' | 'medium' | 'high')}
                  >
                    <option value="low">Low Risk</option>
                    <option value="medium">Medium Risk</option>
                    <option value="high">High Risk</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Initial Investment ($)</label>
                  <Input 
                    type="number"
                    value={initialInvestment}
                    onChange={(e) => setInitialInvestment(Number(e.target.value))}
                    min="1000"
                    step="1000"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Investment Goal ($)</label>
                  <Input 
                    type="number"
                    value={investmentGoal}
                    onChange={(e) => setInvestmentGoal(Number(e.target.value))}
                    min={initialInvestment}
                    step="1000"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Timeframe (years)</label>
                  <Input 
                    type="number"
                    value={timeframe}
                    onChange={(e) => setTimeframe(Number(e.target.value))}
                    min="1"
                    max="30"
                  />
                </div>

                <Button 
                  className="w-full mt-2"
                  onClick={runCompleteAnalysis}
                  disabled={runningComplete}
                >
                  {runningComplete ? 'Analyzing...' : 'Generate Portfolio'}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Results Panel */}
          <div className="lg:col-span-3 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <AgentCard
                title="Company Shortlisting"
                description="Top companies in selected sector"
                status={agentStates.shortlisting.status}
                onRun={() => runAgent('shortlisting')}
                icon={Users}
              />
              <AgentCard
                title="Market Analysis"
                description="Technical and sentiment analysis"
                status={agentStates.technicalAnalysis.status}
                onRun={() => runAgent('technicalAnalysis')}
                icon={BarChart3}
              />
              <AgentCard
                title="Price Prediction"
                description="AI-powered price forecasts"
                status={agentStates.prediction.status}
                onRun={() => runAgent('prediction')}
                icon={Brain}
              />
              <AgentCard
                title="Portfolio"
                description="Personalized recommendations"
                status={agentStates.portfolioManager.status}
                onRun={() => runAgent('portfolioManager')}
                icon={Shield}
              />
            </div>

            {/* Results Display */}
            <Card>
              <CardHeader>
                <CardTitle>Analysis Results</CardTitle>
                <CardDescription>Detailed analysis and recommendations will appear here</CardDescription>
              </CardHeader>
              <CardContent>
                {Object.entries(agentStates).map(([key, agent]) => (
                  agent.status === 'completed' && agent.results && (
                    <div key={key} className="mb-4 p-3 bg-gray-50 rounded-md">
                      <h3 className="font-medium capitalize">
                        {key.replace(/([A-Z])/g, ' $1').trim()}
                      </h3>
                      <div className="text-sm mt-1 text-gray-600">
                        {typeof agent.results === 'string' 
                          ? agent.results 
                          : JSON.stringify(agent.results, null, 2)
                        }
                      </div>
                    </div>
                  )
                ))}
                {!Object.values(agentStates).some(a => a.status === 'completed') && (
                  <div className="text-center py-8 text-gray-400">
                    Run an analysis to see results here
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}
