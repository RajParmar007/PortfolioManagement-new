'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import Navbar from '@/components/navbar'
import { agentAPI } from '@/lib/fastapi'
import { TrendingUp, Building2, CheckCircle2, Loader2 } from 'lucide-react'

interface Company {
  symbol: string
  name?: string
  sector?: string
  [key: string]: any
}

export default function DashboardPage() {
  // Phase 1: Shortlisting State
  const [sector, setSector] = useState('Technology')
  const [companyCount, setCompanyCount] = useState<number>(10)
  const [shortlisting, setShortlisting] = useState(false)
  const [shortlistedCompanies, setShortlistedCompanies] = useState<Company[]>([])
  const [selectedCompanies, setSelectedCompanies] = useState<string[]>([])
  
  // Phase 2: Analysis State
  const [riskTolerance, setRiskTolerance] = useState<'low' | 'medium' | 'high'>('medium')
  const [timeframe, setTimeframe] = useState<number>(5)
  const [analyzing, setAnalyzing] = useState(false)
  const [analysisResults, setAnalysisResults] = useState<any>(null)
  
  // Calculate investment horizon based on timeframe
  const getInvestmentHorizon = (years: number): 'short_term' | 'medium_term' | 'long_term' => {
    if (years <= 3) return 'short_term'
    if (years <= 7) return 'medium_term'
    return 'long_term'
  }
  
  const investmentHorizon = getInvestmentHorizon(timeframe)

  // Phase 1: Shortlist Companies
  const handleShortlist = async () => {
    setShortlisting(true)
    setShortlistedCompanies([])
    setSelectedCompanies([])
    setAnalysisResults(null)
    
    try {
      const response = await agentAPI.shortlistCompanies(sector, companyCount)
      if (response.status === 'success' && response.data) {
        setShortlistedCompanies(response.data)
        // Auto-select all companies by default
        setSelectedCompanies(response.data.map((c: Company) => c.symbol))
      }
    } catch (error) {
      console.error('Error shortlisting companies:', error)
      alert('Failed to shortlist companies. Please try again.')
    } finally {
      setShortlisting(false)
    }
  }

  // Toggle company selection
  const toggleCompanySelection = (symbol: string) => {
    setSelectedCompanies(prev => 
      prev.includes(symbol) 
        ? prev.filter(s => s !== symbol)
        : [...prev, symbol]
    )
  }

  // Phase 2: Analyze Selected Companies
  const handleAnalyze = async () => {
    if (selectedCompanies.length === 0) {
      alert('Please select at least one company to analyze')
      return
    }

    setAnalyzing(true)
    setAnalysisResults(null)
    
    try {
      const response = await agentAPI.analyzeCompanies(
        selectedCompanies,
        {
          risk_tolerance: riskTolerance,
          investment_horizon: investmentHorizon,
          preferred_sectors: [sector]
        }
      )
      
      if (response.status === 'success' && response.data) {
        setAnalysisResults(response.data)
      }
    } catch (error) {
      console.error('Error analyzing companies:', error)
      alert('Failed to analyze companies. Please try again.')
    } finally {
      setAnalyzing(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Portfolio Manager</h1>
          <p className="text-gray-600">Two-step process: Shortlist companies, then analyze them</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Phase 1: Shortlisting Panel */}
          <div className="lg:col-span-1">
            <Card className="mb-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building2 className="h-5 w-5" />
                  Phase 1: Shortlist Companies
                </CardTitle>
                <CardDescription>Select sector and number of companies</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Sector</label>
                  <select 
                    className="w-full p-2 border rounded-md"
                    value={sector}
                    onChange={(e) => setSector(e.target.value)}
                    disabled={shortlisting}
                  >
                    <option value="Technology">Technology</option>
                    <option value="Finance">Finance</option>
                    <option value="Healthcare">Healthcare</option>
                    <option value="Energy">Energy</option>
                    <option value="Consumer Goods">Consumer Goods</option>
                    <option value="Industrials">Industrials</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Number of Companies</label>
                  <Input 
                    type="number"
                    value={companyCount}
                    onChange={(e) => setCompanyCount(Number(e.target.value))}
                    min="5"
                    max="50"
                    disabled={shortlisting}
                  />
                </div>

                <Button 
                  className="w-full"
                  onClick={handleShortlist}
                  disabled={shortlisting}
                >
                  {shortlisting ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Shortlisting...
                    </>
                  ) : (
                    'Shortlist Companies'
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* Phase 2: Analysis Panel */}
            {shortlistedCompanies.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5" />
                    Phase 2: Analyze
                  </CardTitle>
                  <CardDescription>Configure analysis parameters</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Risk Tolerance</label>
                    <select 
                      className="w-full p-2 border rounded-md"
                      value={riskTolerance}
                      onChange={(e) => setRiskTolerance(e.target.value as 'low' | 'medium' | 'high')}
                      disabled={analyzing}
                    >
                      <option value="low">Low Risk</option>
                      <option value="medium">Medium Risk</option>
                      <option value="high">High Risk</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Investment Timeframe (years)</label>
                    <Input 
                      type="number"
                      value={timeframe}
                      onChange={(e) => setTimeframe(Number(e.target.value))}
                      min="1"
                      max="30"
                      disabled={analyzing}
                    />
                  </div>

                  <div className="text-sm text-gray-600">
                    <p><strong>Selected:</strong> {selectedCompanies.length} companies</p>
                    <p><strong>Horizon:</strong> {investmentHorizon.replace('_', ' ')}</p>
                  </div>

                  <Button 
                    className="w-full"
                    onClick={handleAnalyze}
                    disabled={analyzing || selectedCompanies.length === 0}
                  >
                    {analyzing ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      'Run Analysis'
                    )}
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Results Panel */}
          <div className="lg:col-span-2 space-y-6">
            {/* Shortlisted Companies */}
            {shortlistedCompanies.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Shortlisted Companies</CardTitle>
                  <CardDescription>
                    Select companies to analyze (click to toggle)
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {shortlistedCompanies.map((company) => (
                      <button
                        key={company.symbol}
                        onClick={() => toggleCompanySelection(company.symbol)}
                        className={`p-3 rounded-lg border-2 transition-all text-left ${
                          selectedCompanies.includes(company.symbol)
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                        disabled={analyzing}
                      >
                        <div className="flex items-start justify-between">
                          <div>
                            <div className="font-semibold text-sm">{company.symbol}</div>
                            {company.name && (
                              <div className="text-xs text-gray-600 mt-1 line-clamp-2">
                                {company.name}
                              </div>
                            )}
                          </div>
                          {selectedCompanies.includes(company.symbol) && (
                            <CheckCircle2 className="h-4 w-4 text-blue-500 flex-shrink-0" />
                          )}
                        </div>
                      </button>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Analysis Results */}
            {analysisResults && (
              <Card>
                <CardHeader>
                  <CardTitle>Analysis Results</CardTitle>
                  <CardDescription>Complete portfolio analysis and recommendation</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Final Recommendation */}
                  {analysisResults.recommendation && (
                    <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                      <h3 className="font-semibold text-lg mb-2">Portfolio Recommendation</h3>
                      <div className="text-sm whitespace-pre-wrap">
                        {typeof analysisResults.recommendation === 'object' && analysisResults.recommendation.content
                          ? analysisResults.recommendation.content
                          : JSON.stringify(analysisResults.recommendation, null, 2)}
                      </div>
                    </div>
                  )}

                  {/* Technical Analysis */}
                  {analysisResults.technical_analysis && (
                    <div>
                      <h3 className="font-semibold mb-2">Technical Analysis</h3>
                      <div className="space-y-2">
                        {Object.entries(analysisResults.technical_analysis).map(([ticker, data]: [string, any]) => (
                          <div key={ticker} className="p-3 bg-gray-50 rounded-md">
                            <div className="font-medium">{ticker}</div>
                            <pre className="text-xs mt-1 overflow-auto">
                              {JSON.stringify(data, null, 2)}
                            </pre>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Sentiment Analysis */}
                  {analysisResults.sentiment_analysis && (
                    <div>
                      <h3 className="font-semibold mb-2">Sentiment Analysis</h3>
                      <div className="space-y-2">
                        {Object.entries(analysisResults.sentiment_analysis).map(([ticker, data]: [string, any]) => (
                          <div key={ticker} className="p-3 bg-gray-50 rounded-md">
                            <div className="font-medium">{ticker}</div>
                            <pre className="text-xs mt-1 overflow-auto">
                              {JSON.stringify(data, null, 2)}
                            </pre>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Prediction Analysis */}
                  {analysisResults.prediction_analysis && (
                    <div>
                      <h3 className="font-semibold mb-2">Price Predictions</h3>
                      <div className="space-y-2">
                        {Object.entries(analysisResults.prediction_analysis).map(([ticker, data]: [string, any]) => (
                          <div key={ticker} className="p-3 bg-gray-50 rounded-md">
                            <div className="font-medium">{ticker}</div>
                            <pre className="text-xs mt-1 overflow-auto">
                              {JSON.stringify(data, null, 2)}
                            </pre>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Empty State */}
            {shortlistedCompanies.length === 0 && !analysisResults && (
              <Card>
                <CardContent className="py-12">
                  <div className="text-center text-gray-400">
                    <Building2 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Start by shortlisting companies from your preferred sector</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
