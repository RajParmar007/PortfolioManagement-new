'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { LucideIcon } from 'lucide-react'

interface AgentCardProps {
  title: string
  description: string
  icon: LucideIcon
  status: 'idle' | 'running' | 'completed' | 'error'
  onRun: () => void
  results?: any
  loading?: boolean
}

const statusColors = {
  idle: 'bg-gray-100 text-gray-800',
  running: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  error: 'bg-red-100 text-red-800'
}

const statusText = {
  idle: 'Ready',
  running: 'Running...',
  completed: 'Completed',
  error: 'Error'
}

export default function AgentCard({
  title,
  description,
  icon: Icon,
  status,
  onRun,
  results,
  loading = false
}: AgentCardProps) {
  return (
    <Card className="h-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
              <Icon className="h-5 w-5 text-primary" />
            </div>
            <div>
              <CardTitle className="text-lg">{title}</CardTitle>
              <Badge className={statusColors[status]} variant="secondary">
                {statusText[status]}
              </Badge>
            </div>
          </div>
        </div>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <Button 
            onClick={onRun} 
            disabled={loading || status === 'running'}
            className="w-full"
          >
            {loading || status === 'running' ? 'Running...' : 'Run Analysis'}
          </Button>
          
          {results && status === 'completed' && (
            <div className="bg-muted/50 p-3 rounded-md">
              <h4 className="font-medium text-sm mb-2">Results:</h4>
              <div className="text-xs text-muted-foreground">
                {typeof results === 'string' ? (
                  <p className="truncate">{results}</p>
                ) : (
                  <pre className="whitespace-pre-wrap max-h-20 overflow-y-auto">
                    {JSON.stringify(results, null, 2)}
                  </pre>
                )}
              </div>
            </div>
          )}
          
          {status === 'error' && (
            <div className="bg-destructive/10 p-3 rounded-md">
              <p className="text-destructive text-sm">
                Analysis failed. Please try again.
              </p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
