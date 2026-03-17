import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Shield, Search, Clock, Target, ArrowRight, Camera, Brain, Users } from "lucide-react"

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border/40">
        <div className="container flex h-16 max-w-screen-xl items-center justify-between">
          <div className="flex items-center gap-2">
            <Shield className="h-7 w-7 text-primary" />
            <span className="text-xl font-semibold">Trace AI</span>
          </div>
          <Link href="/dashboard">
            <Button variant="outline">Launch Dashboard</Button>
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container max-w-screen-xl py-24 md:py-32">
        <div className="flex flex-col items-center text-center">
          <div className="mb-6 inline-flex items-center rounded-full border border-border/60 bg-muted/50 px-4 py-1.5 text-sm text-muted-foreground">
            <Camera className="mr-2 h-4 w-4" />
            AI-Powered Surveillance Analysis
          </div>
          <h1 className="text-balance text-4xl font-bold tracking-tight md:text-6xl lg:text-7xl">
            Find Missing Persons
            <span className="block text-muted-foreground">Faster</span>
          </h1>
          <p className="mt-6 max-w-2xl text-pretty text-lg text-muted-foreground md:text-xl">
            Trace AI is an investigative triage platform that helps authorities locate missing people 
            by intelligently analyzing indexed security footage and providing prioritized leads.
          </p>
          <div className="mt-10 flex flex-col gap-4 sm:flex-row">
            <Link href="/dashboard">
              <Button size="lg" className="gap-2">
                Launch Dashboard
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Problem Statement */}
      <section className="border-y border-border/40 bg-muted/30">
        <div className="container max-w-screen-xl py-20">
          <div className="mx-auto max-w-3xl text-center">
            <h2 className="text-2xl font-semibold md:text-3xl">
              The Problem
            </h2>
            <p className="mt-4 text-muted-foreground leading-relaxed">
              When someone goes missing, every minute counts. Investigators often face 
              <span className="font-medium text-foreground"> hundreds of hours </span> 
              of surveillance footage from dozens of cameras. Manual review is 
              time-consuming and error-prone, causing critical leads to be missed 
              during the golden hours of a search.
            </p>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="container max-w-screen-xl py-24">
        <div className="text-center mb-16">
          <h2 className="text-2xl font-semibold md:text-3xl">How It Works</h2>
          <p className="mt-2 text-muted-foreground">
            Three steps to accelerate your investigation
          </p>
        </div>
        <div className="grid gap-8 md:grid-cols-3">
          <Card className="bg-card/50">
            <CardContent className="pt-6">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                <Users className="h-6 w-6 text-primary" />
              </div>
              <div className="mb-2 text-sm font-medium text-muted-foreground">Step 1</div>
              <h3 className="text-lg font-semibold">Input Case Details</h3>
              <p className="mt-2 text-sm text-muted-foreground">
                Enter the missing person&apos;s description, last known location, time last seen, 
                and any distinguishing characteristics like clothing or accessories.
              </p>
            </CardContent>
          </Card>
          <Card className="bg-card/50">
            <CardContent className="pt-6">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                <Brain className="h-6 w-6 text-primary" />
              </div>
              <div className="mb-2 text-sm font-medium text-muted-foreground">Step 2</div>
              <h3 className="text-lg font-semibold">AI Searches Footage</h3>
              <p className="mt-2 text-sm text-muted-foreground">
                Our AI analyzes indexed camera frames, matching against the subject&apos;s 
                description to identify potential sightings across all available footage.
              </p>
            </CardContent>
          </Card>
          <Card className="bg-card/50">
            <CardContent className="pt-6">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                <Target className="h-6 w-6 text-primary" />
              </div>
              <div className="mb-2 text-sm font-medium text-muted-foreground">Step 3</div>
              <h3 className="text-lg font-semibold">Receive Prioritized Leads</h3>
              <p className="mt-2 text-sm text-muted-foreground">
                Get ranked candidate sightings, a movement timeline, and recommendations 
                for which cameras to check next—focusing your team&apos;s effort where it matters most.
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Features */}
      <section className="border-t border-border/40 bg-muted/30">
        <div className="container max-w-screen-xl py-24">
          <div className="text-center mb-16">
            <h2 className="text-2xl font-semibold md:text-3xl">Key Capabilities</h2>
          </div>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            <div className="flex flex-col items-center text-center p-6">
              <Search className="h-8 w-8 text-primary mb-4" />
              <h3 className="font-semibold">Intelligent Search</h3>
              <p className="mt-2 text-sm text-muted-foreground">
                AI-powered matching across indexed surveillance frames
              </p>
            </div>
            <div className="flex flex-col items-center text-center p-6">
              <Clock className="h-8 w-8 text-primary mb-4" />
              <h3 className="font-semibold">Movement Timeline</h3>
              <p className="mt-2 text-sm text-muted-foreground">
                Chronological tracking of subject movements
              </p>
            </div>
            <div className="flex flex-col items-center text-center p-6">
              <Target className="h-8 w-8 text-primary mb-4" />
              <h3 className="font-semibold">Confidence Scoring</h3>
              <p className="mt-2 text-sm text-muted-foreground">
                Ranked results to prioritize high-probability leads
              </p>
            </div>
            <div className="flex flex-col items-center text-center p-6">
              <Camera className="h-8 w-8 text-primary mb-4" />
              <h3 className="font-semibold">Camera Recommendations</h3>
              <p className="mt-2 text-sm text-muted-foreground">
                Guidance on which cameras to check next
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="container max-w-screen-xl py-24">
        <div className="rounded-2xl border border-border/40 bg-card/50 p-12 text-center">
          <h2 className="text-2xl font-semibold md:text-3xl">
            Ready to accelerate your investigation?
          </h2>
          <p className="mt-4 text-muted-foreground max-w-xl mx-auto">
            Start using Trace AI to reduce the time spent reviewing footage 
            and focus on what matters—finding the missing person.
          </p>
          <Link href="/dashboard">
            <Button size="lg" className="mt-8 gap-2">
              Launch Dashboard
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border/40">
        <div className="container max-w-screen-xl py-8">
          <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Shield className="h-5 w-5" />
              <span className="text-sm">Trace AI — Investigative Triage Platform</span>
            </div>
            <p className="text-xs text-muted-foreground">
              Built for public safety and campus security teams.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
