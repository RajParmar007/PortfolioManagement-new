import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { TrendingUp, TrendingDown, Minus, ArrowUpRight, ArrowDownRight } from "lucide-react"

interface StockCardProps {
  ticker: string
  decision: 'BUY' | 'SELL' | 'HOLD'
  confidence: number
  positionSize: number
  reasoning: {
    sma_signal: string
    rsi: number | string
    macd_hist: number | string
    ml_prediction: string
  }
  news?: Array<{
    title: string
    url: string
  }>
}

export function StockCard({ ticker, decision, confidence, positionSize, reasoning, news }: StockCardProps) {
  const getDecisionColor = () => {
    switch (decision) {
      case 'BUY':
        return 'bg-green-50 border-green-200'
      case 'SELL':
        return 'bg-red-50 border-red-200'
      default:
        return 'bg-blue-50 border-blue-200'
    }
  }

  const getDecisionBadgeColor = () => {
    switch (decision) {
      case 'BUY':
        return 'bg-green-500 hover:bg-green-600'
      case 'SELL':
        return 'bg-red-500 hover:bg-red-600'
      default:
        return 'bg-blue-500 hover:bg-blue-600'
    }
  }

  const getDecisionIcon = () => {
    switch (decision) {
      case 'BUY':
        return <TrendingUp className="h-4 w-4" />
      case 'SELL':
        return <TrendingDown className="h-4 w-4" />
      default:
        return <Minus className="h-4 w-4" />
    }
  }

  const getRSIColor = (rsi: number | string) => {
    if (typeof rsi === 'string') return 'text-gray-600'
    if (rsi > 70) return 'text-red-600 font-semibold'
    if (rsi < 30) return 'text-green-600 font-semibold'
    return 'text-gray-600'
  }

  const getConfidenceColor = () => {
    if (confidence >= 0.8) return 'text-green-600'
    if (confidence >= 0.6) return 'text-blue-600'
    return 'text-orange-600'
  }

  return (
    <Card className={`border-2 ${getDecisionColor()} transition-all hover:shadow-lg`}>
      <CardContent className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-6">
          <div>
            <h3 className="text-2xl font-bold text-gray-900">{ticker}</h3>
            <p className="text-sm text-gray-500 mt-1">Stock Analysis</p>
          </div>
          <Badge className={`${getDecisionBadgeColor()} text-white px-4 py-2 text-sm font-semibold flex items-center gap-2`}>
            {getDecisionIcon()}
            {decision}
          </Badge>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-white rounded-lg p-4 border border-gray-200">
            <p className="text-xs text-gray-500 uppercase tracking-wide mb-2">Confidence</p>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className={`text-2xl font-bold ${getConfidenceColor()}`}>
                  {(confidence * 100).toFixed(0)}%
                </span>
              </div>
              <Progress value={confidence * 100} className="h-2" />
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 border border-gray-200">
            <p className="text-xs text-gray-500 uppercase tracking-wide mb-2">Position Size</p>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-gray-900">{positionSize.toFixed(1)}</span>
              <span className="text-sm text-gray-500">x</span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {positionSize >= 0.8 ? 'Strong' : positionSize >= 0.6 ? 'Moderate' : 'Cautious'}
            </p>
          </div>
        </div>

        {/* Technical Indicators */}
        <div className="space-y-3 mb-6">
          <h4 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">Technical Indicators</h4>
          
          <div className="grid grid-cols-2 gap-3">
            {/* SMA Signal */}
            <div className="bg-white rounded-lg p-3 border border-gray-200">
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-500">SMA Signal</span>
                {reasoning.sma_signal.toLowerCase() === 'buy' && <ArrowUpRight className="h-4 w-4 text-green-500" />}
                {reasoning.sma_signal.toLowerCase() === 'sell' && <ArrowDownRight className="h-4 w-4 text-red-500" />}
              </div>
              <p className="text-sm font-semibold text-gray-900 mt-1 capitalize">{reasoning.sma_signal}</p>
            </div>

            {/* RSI */}
            <div className="bg-white rounded-lg p-3 border border-gray-200">
              <span className="text-xs text-gray-500">RSI (14)</span>
              <p className={`text-sm font-semibold mt-1 ${getRSIColor(reasoning.rsi)}`}>
                {typeof reasoning.rsi === 'number' ? reasoning.rsi.toFixed(2) : reasoning.rsi}
              </p>
            </div>

            {/* MACD */}
            <div className="bg-white rounded-lg p-3 border border-gray-200">
              <span className="text-xs text-gray-500">MACD Hist</span>
              <p className={`text-sm font-semibold mt-1 ${
                typeof reasoning.macd_hist === 'number' && reasoning.macd_hist > 0 
                  ? 'text-green-600' 
                  : 'text-red-600'
              }`}>
                {typeof reasoning.macd_hist === 'number' 
                  ? reasoning.macd_hist.toFixed(2) 
                  : reasoning.macd_hist}
              </p>
            </div>

            {/* ML Prediction */}
            <div className="bg-white rounded-lg p-3 border border-gray-200">
              <span className="text-xs text-gray-500">ML Prediction</span>
              <p className={`text-sm font-semibold mt-1 ${
                reasoning.ml_prediction.startsWith('+') 
                  ? 'text-green-600' 
                  : reasoning.ml_prediction.startsWith('-')
                  ? 'text-red-600'
                  : 'text-gray-600'
              }`}>
                {reasoning.ml_prediction}%
              </p>
            </div>
          </div>
        </div>

        {/* News Section */}
        {news && news.length > 0 && (
          <div className="border-t border-gray-200 pt-4">
            <h4 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">Recent News</h4>
            <div className="space-y-2">
              {news.slice(0, 3).map((item, index) => (
                <a
                  key={index}
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block text-sm text-blue-600 hover:text-blue-800 hover:underline line-clamp-2"
                >
                  • {item.title}
                </a>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
