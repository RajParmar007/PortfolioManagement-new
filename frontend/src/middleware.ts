import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  const response = NextResponse.next()
  const url = request.nextUrl.clone()
  const pathname = url.pathname
  
  // Skip middleware for static files and API routes
  if (pathname.startsWith('/_next/') || 
      pathname.startsWith('/api/') || 
      pathname.includes('.')) {
    return response
  }

  // Clean up any existing auth cookies to prevent parsing errors
  const requestHeaders = new Headers(request.headers)
  requestHeaders.delete('sb-access-token')
  requestHeaders.delete('sb-refresh-token')
  
  // Set a simple cookie to prevent auth middleware from running
  response.cookies.set('auth-removed', 'true', {
    path: '/',
    httpOnly: true,
    sameSite: 'lax',
    secure: process.env.NODE_ENV === 'production'
  })

  // Redirect any auth-related paths to the dashboard
  if (pathname.startsWith('/auth/')) {
    console.log(`Redirecting auth path to dashboard: ${pathname}`)
    url.pathname = '/dashboard'
    return NextResponse.redirect(url)
  }
  
  // Log the current path for debugging (without auth status)
  console.log(`[Middleware] Path: ${pathname}`)
  
  // Return the response with cleaned up headers
  return response
}

export const config = {
  // Only run middleware on relevant paths
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
}
