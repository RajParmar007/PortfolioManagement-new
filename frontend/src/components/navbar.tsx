'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { BarChart3 } from 'lucide-react'

export default function Navbar() {

  return (
    <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-2">
              <BarChart3 className="h-8 w-8 text-primary" />
              <span className="font-bold text-xl">InvestAI</span>
            </Link>
          </div>

          <div className="hidden md:flex items-center space-x-8">
            <Link href="/" className="text-foreground/60 hover:text-foreground transition-colors">
              Home
            </Link>
            <Link href="/about" className="text-foreground/60 hover:text-foreground transition-colors">
              About
            </Link>
            <Link href="/dashboard" className="text-foreground/60 hover:text-foreground transition-colors">
              Dashboard
            </Link>
          </div>

          <div className="flex items-center space-x-4">
            {/* Removed authentication buttons */}
          </div>
        </div>
      </div>
    </nav>
  )
}
