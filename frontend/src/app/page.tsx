import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import Navbar from '@/components/navbar'
import ConfigNotice from '@/components/config-notice'
import { 
  BarChart3, 
  Brain, 
  TrendingUp, 
  Shield, 
  Zap, 
  Users,
  ArrowRight,
  CheckCircle
} from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen">
      <Navbar />
      
      {/* Configuration Notice */}
      <div className="container mx-auto px-4 py-4">
        <ConfigNotice />
      </div>
      
      {/* Hero Section */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-primary/10 via-background to-secondary/10">
        <div className="container mx-auto text-center">
          <div className="max-w-4xl mx-auto">
            <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
              AI-Powered Investment
              <span className="text-primary block">Intelligence</span>
            </h1>
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Harness the power of multiple AI agents to analyze markets, predict trends, 
              and optimize your investment portfolio with unprecedented precision.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" asChild className="text-lg px-8 py-6">
                <Link href="/auth/signup">
                  Get Started <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" asChild className="text-lg px-8 py-6">
                <Link href="/about">Learn More</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Multi-Agent Investment System
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Our AI agents work together to provide comprehensive investment analysis
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="border-2 hover:border-primary/50 transition-colors">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <Brain className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Company Shortlisting Agent</CardTitle>
                <CardDescription>
                  Intelligently identifies and ranks potential investment opportunities 
                  based on your preferences and market conditions.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-2 hover:border-primary/50 transition-colors">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <BarChart3 className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Data Ingestion Agent</CardTitle>
                <CardDescription>
                  Continuously collects and processes real-time market data, 
                  news, and social sentiment from multiple sources.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-2 hover:border-primary/50 transition-colors">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <TrendingUp className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Technical Analysis Agent</CardTitle>
                <CardDescription>
                  Performs advanced technical analysis using multiple indicators 
                  to identify trends and trading signals.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-2 hover:border-primary/50 transition-colors">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <Users className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Sentiment Analysis Agent</CardTitle>
                <CardDescription>
                  Analyzes market sentiment from news articles, social media, 
                  and financial reports to gauge market mood.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-2 hover:border-primary/50 transition-colors">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <Zap className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Prediction Agent</CardTitle>
                <CardDescription>
                  Uses machine learning models to forecast stock prices 
                  and market movements with high accuracy.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-2 hover:border-primary/50 transition-colors">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <Shield className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Portfolio Manager Agent</CardTitle>
                <CardDescription>
                  Synthesizes all analysis to provide personalized investment 
                  recommendations and portfolio optimization.
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-muted/50">
        <div className="container mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold mb-6">
                Why Choose Our Platform?
              </h2>
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <CheckCircle className="h-6 w-6 text-primary mt-0.5" />
                  <div>
                    <h3 className="font-semibold mb-1">Multi-Agent Intelligence</h3>
                    <p className="text-muted-foreground">
                      Six specialized AI agents working in harmony to analyze every aspect of your investments.
                    </p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <CheckCircle className="h-6 w-6 text-primary mt-0.5" />
                  <div>
                    <h3 className="font-semibold mb-1">Real-Time Analysis</h3>
                    <p className="text-muted-foreground">
                      Get up-to-the-minute market insights and recommendations based on live data.
                    </p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <CheckCircle className="h-6 w-6 text-primary mt-0.5" />
                  <div>
                    <h3 className="font-semibold mb-1">Personalized Recommendations</h3>
                    <p className="text-muted-foreground">
                      Tailored investment strategies based on your risk tolerance and goals.
                    </p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <CheckCircle className="h-6 w-6 text-primary mt-0.5" />
                  <div>
                    <h3 className="font-semibold mb-1">Comprehensive Coverage</h3>
                    <p className="text-muted-foreground">
                      From technical analysis to sentiment tracking, we cover all investment angles.
                    </p>
                  </div>
                </div>
              </div>
            </div>
            <div className="lg:pl-12">
              <Card className="p-8 bg-gradient-to-br from-primary/5 to-secondary/5 border-2">
                <CardHeader className="text-center pb-6">
                  <CardTitle className="text-2xl mb-2">Ready to Start?</CardTitle>
                  <CardDescription className="text-lg">
                    Join thousands of investors who trust our AI-powered platform
                  </CardDescription>
                </CardHeader>
                <CardContent className="text-center">
                  <Button size="lg" asChild className="w-full text-lg py-6">
                    <Link href="/auth/signup">
                      Create Your Account <ArrowRight className="ml-2 h-5 w-5" />
                    </Link>
                  </Button>
                  <p className="text-sm text-muted-foreground mt-4">
                    No credit card required • Free trial available
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-12 px-4 sm:px-6 lg:px-8">
        <div className="container mx-auto">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="md:col-span-2">
              <div className="flex items-center space-x-2 mb-4">
                <BarChart3 className="h-8 w-8 text-primary" />
                <span className="font-bold text-xl">InvestAI</span>
              </div>
              <p className="text-muted-foreground mb-4">
                Empowering investors with AI-driven insights and multi-agent intelligence 
                for smarter investment decisions.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Platform</h3>
              <ul className="space-y-2 text-muted-foreground">
                <li><Link href="/dashboard" className="hover:text-foreground">Dashboard</Link></li>
                <li><Link href="/about" className="hover:text-foreground">About</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Account</h3>
              <ul className="space-y-2 text-muted-foreground">
                <li><Link href="/auth/login" className="hover:text-foreground">Sign In</Link></li>
                <li><Link href="/auth/signup" className="hover:text-foreground">Sign Up</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t mt-8 pt-8 text-center text-muted-foreground">
            <p>&copy; 2024 InvestAI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
