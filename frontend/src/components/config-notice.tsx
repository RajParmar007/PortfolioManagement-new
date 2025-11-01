'use client'

import { AlertCircle, ExternalLink } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { isSupabaseReady } from '@/lib/supabase'

export default function ConfigNotice() {
  if (isSupabaseReady()) {
    return null
  }

  return (
    <Card className="border-orange-200 bg-orange-50 dark:border-orange-800 dark:bg-orange-950">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2 text-orange-800 dark:text-orange-200">
          <AlertCircle className="h-5 w-5" />
          <span>Configuration Required</span>
        </CardTitle>
        <CardDescription className="text-orange-700 dark:text-orange-300">
          Supabase authentication is not configured. Some features will be limited.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="text-sm text-orange-700 dark:text-orange-300">
          <p className="mb-2">To enable full functionality:</p>
          <ol className="list-decimal list-inside space-y-1 ml-4">
            <li>Create a Supabase project at supabase.com</li>
            <li>Copy your project URL and anon key</li>
            <li>Update the .env.local file with your credentials</li>
            <li>Restart the development server</li>
          </ol>
        </div>
        <div className="flex space-x-2">
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => window.open('https://supabase.com', '_blank')}
            className="text-orange-700 border-orange-300 hover:bg-orange-100"
          >
            <ExternalLink className="h-4 w-4 mr-2" />
            Go to Supabase
          </Button>
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => window.open('https://github.com/your-repo/blob/main/SETUP.md', '_blank')}
            className="text-orange-700 border-orange-300 hover:bg-orange-100"
          >
            Setup Guide
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
