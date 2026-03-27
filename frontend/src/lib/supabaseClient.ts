'use client'

import { createBrowserClient } from '@supabase/ssr'

// Create a client-side Supabase client
export const createBrowserSupabaseClient = () => {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}

// Client-side auth state change handler
export const onAuthStateChange = (callback: (event: string, session: any) => void) => {
  if (typeof window === 'undefined') return { data: { subscription: { unsubscribe: () => {} } } }
  
  const supabase = createBrowserSupabaseClient()
  return supabase.auth.onAuthStateChange(callback)
}
