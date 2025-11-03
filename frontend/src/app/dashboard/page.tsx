'use client'

import { useState, useMemo } from 'react'
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
  // Sector mapping
  const SECTOR_OPTIONS = useMemo(() => ({
    "ms_technology": "Technology",
    "ms_financial_services": "Financial Services",
    "ms_healthcare": "Healthcare",
    "ms_consumer_cyclical": "Consumer Cyclical",
    "ms_communication_services": "Communication Services",
    "ms_industrials": "Industrials",
    "ms_consumer_defensive": "Consumer Defensive",
    "ms_utilities": "Utilities",
    "ms_real_estate": "Real Estate",
    "ms_basic_materials": "Basic Materials",
    "ms_energy": "Energy",
  }), [])

  // Phase 1: Shortlisting State
  const [sector, setSector] = useState('ms_technology')
  const [companyCount, setCompanyCount] = useState<number>(10)
  const [shortlisting, setShortlisting] = useState(false)
  const [shortlistedCompanies, setShortlistedCompanies] = useState<Company[]>([])
  const [selectedCompanies, setSelectedCompanies] = useState<string[]>([])
  
  // Analysis State
  const [analyzing, setAnalyzing] = useState(false)
  const [analysisResults, setAnalysisResults] = useState<any>(null)

  // Phase 1: Shortlist Companies
  const handleShortlist = async () => {
    setShortlisting(true)
    setShortlistedCompanies([])
    setSelectedCompanies([])
    setAnalysisResults(null)
    
    try {
      // Convert the sector key to the display name for the API if needed
      const sectorName = SECTOR_OPTIONS[sector as keyof typeof SECTOR_OPTIONS] || sector;
      const response = await agentAPI.shortlistCompanies(sectorName, companyCount)
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

  // Format recommendation text
  const formatRecommendation = (text: string) => {
    return text
      .replace(/\\n/g, '\n')  // Convert literal \n to actual newlines
      .replace(/\\"/g, '"')   // Convert escaped quotes to actual quotes
      .replace(/={20,}/g, '')  // Remove long sequences of = symbols
      .replace(/-{20,}/g, '')  // Remove long sequences of - symbols
      .trim()
  }

  // Analyze Selected Companies
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
          risk_tolerance: 'medium',
          investment_horizon: 'medium_term',
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
          <p className="text-gray-600">Shortlist companies and run AI-powered analysis</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Phase 1: Shortlisting Panel */}
          <div className="lg:col-span-1">
            <Card className="mb-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building2 className="h-5 w-5" />
                  Shortlist Companies
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
                    {Object.entries(SECTOR_OPTIONS).map(([value, label]) => (
                      <option key={value} value={value}>
                        {label}
                      </option>
                    ))}
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

            {/* Run Analysis Button */}
            {shortlistedCompanies.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5" />
                    Run Analysis
                  </CardTitle>
                  <CardDescription>
                    {selectedCompanies.length} {selectedCompanies.length === 1 ? 'company' : 'companies'} selected
                  </CardDescription>
                </CardHeader>
                <CardContent>
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
                    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
                      <h3 className="font-bold text-xl mb-4 text-gray-800">📊 Portfolio Recommendation</h3>
                      <div className="prose prose-sm max-w-none">
                        <div className="text-gray-700 whitespace-pre-wrap leading-relaxed text-sm break-words overflow-hidden">
                          {(() => {
                            const content = typeof analysisResults.recommendation === 'object' && analysisResults.recommendation.content
                              ? analysisResults.recommendation.content
                              : JSON.stringify(analysisResults.recommendation, null, 2);
                            return formatRecommendation(content);
                          })()}
                        </div>
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
