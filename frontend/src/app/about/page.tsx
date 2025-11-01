'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import Navbar from '@/components/navbar'
import { 
  Brain, 
  BarChart3, 
  TrendingUp, 
  Users, 
  Zap, 
  Shield,
  ArrowRight,
  Target,
  Lightbulb,
  Award
} from 'lucide-react'

export default function AboutPage() {
  return (
    <div className="min-h-screen">
      <Navbar />
      
      {/* Hero Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-primary/10 via-background to-secondary/10">
        <div className="container mx-auto text-center">
          <div className="max-w-4xl mx-auto">
            <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
              About <span className="text-primary">InvestAI</span>
            </h1>
            <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto">
              We're revolutionizing investment decision-making through the power of 
              multi-agent artificial intelligence, providing retail investors with 
              institutional-grade analysis and insights.
            </p>
          </div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="container mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="w-16 h-16 bg-primary/10 rounded-lg flex items-center justify-center mb-6">
                <Target className="h-8 w-8 text-primary" />
              </div>
              <h2 className="text-3xl md:text-4xl font-bold mb-6">Our Mission</h2>
              <p className="text-lg text-muted-foreground mb-6">
                To democratize sophisticated investment analysis by making advanced AI-powered 
                tools accessible to every investor, regardless of their experience level or 
                portfolio size.
              </p>
              <p className="text-lg text-muted-foreground">
                We believe that everyone deserves access to the same quality of market analysis 
                that was once exclusive to large financial institutions.
              </p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Card className="p-6 text-center">
                <div className="text-3xl font-bold text-primary mb-2">6</div>
                <div className="text-sm text-muted-foreground">AI Agents</div>
              </Card>
              <Card className="p-6 text-center">
                <div className="text-3xl font-bold text-primary mb-2">24/7</div>
                <div className="text-sm text-muted-foreground">Market Analysis</div>
              </Card>
              <Card className="p-6 text-center">
                <div className="text-3xl font-bold text-primary mb-2">1000+</div>
                <div className="text-sm text-muted-foreground">Data Sources</div>
              </Card>
              <Card className="p-6 text-center">
                <div className="text-3xl font-bold text-primary mb-2">99.9%</div>
                <div className="text-sm text-muted-foreground">Uptime</div>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-muted/50">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              How Our AI Agents Work Together
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Six specialized agents collaborate to provide comprehensive investment analysis
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-primary font-bold text-xl">1</span>
              </div>
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Brain className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Company Shortlisting</h3>
              <p className="text-muted-foreground">
                Analyzes your investment preferences and market conditions to identify 
                the most promising investment opportunities.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-primary font-bold text-xl">2</span>
              </div>
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Data Ingestion</h3>
              <p className="text-muted-foreground">
                Continuously collects real-time market data, financial reports, 
                news articles, and social media sentiment.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-primary font-bold text-xl">3</span>
              </div>
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Users className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Sentiment Analysis</h3>
              <p className="text-muted-foreground">
                Processes news articles, social media posts, and market commentary 
                to gauge overall market sentiment.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-primary font-bold text-xl">4</span>
              </div>
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Technical Analysis</h3>
              <p className="text-muted-foreground">
                Applies advanced technical indicators and chart patterns to 
                identify trends and potential entry/exit points.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-primary font-bold text-xl">5</span>
              </div>
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Zap className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Prediction Engine</h3>
              <p className="text-muted-foreground">
                Uses machine learning models trained on historical data to 
                forecast price movements and market trends.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-primary font-bold text-xl">6</span>
              </div>
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Shield className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Portfolio Manager</h3>
              <p className="text-muted-foreground">
                Synthesizes all analysis to provide personalized investment 
                recommendations tailored to your risk profile.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Technology Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="container mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="w-16 h-16 bg-primary/10 rounded-lg flex items-center justify-center mb-6">
                <Lightbulb className="h-8 w-8 text-primary" />
              </div>
              <h2 className="text-3xl md:text-4xl font-bold mb-6">
                Cutting-Edge Technology
              </h2>
              <div className="space-y-6">
                <div>
                  <h3 className="text-xl font-semibold mb-2">Advanced Machine Learning</h3>
                  <p className="text-muted-foreground">
                    Our models are trained on decades of market data and continuously 
                    updated with real-time information to improve accuracy.
                  </p>
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">Natural Language Processing</h3>
                  <p className="text-muted-foreground">
                    We analyze thousands of news articles, earnings calls, and social 
                    media posts to extract meaningful insights.
                  </p>
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">Real-Time Processing</h3>
                  <p className="text-muted-foreground">
                    Our infrastructure processes market data in real-time, ensuring 
                    you always have the most current analysis.
                  </p>
                </div>
              </div>
            </div>
            <div className="space-y-6">
              <Card className="p-6">
                <div className="flex items-center space-x-4">
                  <Award className="h-8 w-8 text-primary" />
                  <div>
                    <h3 className="font-semibold">Industry Recognition</h3>
                    <p className="text-sm text-muted-foreground">
                      Featured in leading fintech publications
                    </p>
                  </div>
                </div>
              </Card>
              <Card className="p-6">
                <div className="flex items-center space-x-4">
                  <Shield className="h-8 w-8 text-primary" />
                  <div>
                    <h3 className="font-semibold">Bank-Grade Security</h3>
                    <p className="text-sm text-muted-foreground">
                      Your data is protected with enterprise-level encryption
                    </p>
                  </div>
                </div>
              </Card>
              <Card className="p-6">
                <div className="flex items-center space-x-4">
                  <Zap className="h-8 w-8 text-primary" />
                  <div>
                    <h3 className="font-semibold">Lightning Fast</h3>
                    <p className="text-sm text-muted-foreground">
                      Get comprehensive analysis in seconds, not hours
                    </p>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Meet the Creator Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Meet the Creators
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              The visionaries behind this revolutionary multi-agent investment system
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {/* Photo 1 */}
            <Card className="text-center">
              <CardContent className="pt-8">
                <div className="w-48 h-48 mx-auto mb-6 rounded-full overflow-hidden bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center">
                  {/* Replace /images/creator-photo1.jpg with your actual photo path */}
                  <img 
                    src="/images/creator-photo1.jpg" 
                    alt="Creator - Innovation & Vision" 
                    className="w-full h-full object-cover" 
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                      const fallback = e.currentTarget.nextElementSibling as HTMLElement;
                      if (fallback) fallback.style.display = 'flex';
                    }} 
                  />
                  <div className="text-4xl font-bold text-primary hidden">K</div>
                </div>
                {/* <h3 className="font-semibold text-xl mb-3">Innovation & Vision</h3> */}
                <p className="text-base text-muted-foreground leading-relaxed">
                  Never Date a Co-worker

                </p>
              </CardContent>
            </Card>

            {/* Photo 2 */}
            <Card className="text-center">
              <CardContent className="pt-8">
                <div className="w-48 h-48 mx-auto mb-6 rounded-full overflow-hidden bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center">
                  {/* Replace /images/creator-photo2.jpg with your actual photo path */}
                  <img 
                    src="/images/creator-photo2.jpg" 
                    alt="Creator - Technical Excellence" 
                    className="w-full h-full object-cover" 
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                      const fallback = e.currentTarget.nextElementSibling as HTMLElement;
                      if (fallback) fallback.style.display = 'flex';
                    }} 
                  />
                  <div className="text-4xl font-bold text-primary hidden">A</div>
                </div>
                {/* <h3 className="font-semibold text-xl mb-3">Technical Excellence</h3> */}
                <p className="text-base text-muted-foreground leading-relaxed">
                  What We Do in our Lives Echoes in Eternity
                </p>
              </CardContent>
            </Card>

            {/* Photo 3 */}
            <Card className="text-center">
              <CardContent className="pt-8">
                <div className="w-48 h-48 mx-auto mb-6 rounded-full overflow-hidden bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center">
                  {/* Replace /images/creator-photo3.jpg with your actual photo path */}
                  <img 
                    src="/images/creator-photo3.jpg" 
                    alt="Creator - Research & Development" 
                    className="w-full h-full object-cover" 
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                      const fallback = e.currentTarget.nextElementSibling as HTMLElement;
                      if (fallback) fallback.style.display = 'flex';
                    }} 
                  />
                  <div className="text-4xl font-bold text-primary hidden">R</div>
                </div>
                {/* <h3 className="font-semibold text-xl mb-3">Research & Development</h3> */}
                <p className="text-base text-muted-foreground leading-relaxed">
                  Eighty percent of success is showing up.
                </p>
              </CardContent>
            </Card>

            {/* Photo 4 */}
            <Card className="text-center">
              <CardContent className="pt-8">
                <div className="w-48 h-48 mx-auto mb-6 rounded-full overflow-hidden bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center">
                  {/* Replace /images/creator-photo4.jpg with your actual photo path */}
                  <img 
                    src="/images/creator-photo4.jpg" 
                    alt="Creator - Future Vision" 
                    className="w-full h-full object-cover" 
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                      const fallback = e.currentTarget.nextElementSibling as HTMLElement;
                      if (fallback) fallback.style.display = 'flex';
                    }} 
                  />
                  <div className="text-4xl font-bold text-primary hidden">A</div>
                </div>
                {/* <h3 className="font-semibold text-xl mb-3">Future Vision</h3> */}
                <p className="text-base text-muted-foreground leading-relaxed">
                  Kamal aadmi ho yaar Cigarette nai laye
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Creator Bio Section */}
          <div className="mt-16 max-w-4xl mx-auto">
            <Card className="p-8 bg-gradient-to-br from-primary/5 to-secondary/5">
              <div className="text-center">
                <h3 className="text-2xl font-bold mb-4">About the Creator</h3>
                <p className="text-lg text-muted-foreground mb-6">
                  "We created this multi-agent investment system because we believe that everyone deserves access 
                  to sophisticated financial analysis tools. By combining the power of artificial intelligence 
                  with deep market expertise, we can democratize investment intelligence and help people make 
                  better financial decisions."
                </p>
                <div className="flex justify-center space-x-4">
                  <Badge variant="secondary" className="px-4 py-2">AI/ML Expert</Badge>
                  <Badge variant="secondary" className="px-4 py-2">FinTech Innovator</Badge>
                  <Badge variant="secondary" className="px-4 py-2">Full-Stack Developer</Badge>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-primary/10 via-background to-secondary/10">
        <div className="container mx-auto text-center">
          <div className="max-w-2xl mx-auto">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">
              Ready to Transform Your Investment Strategy?
            </h2>
            <p className="text-xl text-muted-foreground mb-8">
              Join thousands of investors who are already using AI to make smarter investment decisions.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" asChild className="text-lg px-8 py-6">
                <Link href="/auth/signup">
                  Start Free Trial <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" asChild className="text-lg px-8 py-6">
                <Link href="/auth/login">Sign In</Link>
              </Button>
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
