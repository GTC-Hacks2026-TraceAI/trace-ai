"use client"

import { useState, useEffect } from "react"
import { Navbar } from "@/components/trace/navbar"
import { CaseForm } from "@/components/trace/case-form"
import { CaseCard } from "@/components/trace/case-card"
import { EmptyState } from "@/components/trace/empty-state"
import { DashboardSkeleton } from "@/components/trace/loading-skeleton"
import { getCases } from "@/lib/api"
import type { Case } from "@/lib/types"
import { FolderOpen, AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function DashboardPage() {
  const [cases, setCases] = useState<Case[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchCases = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const data = await getCases()
      setCases(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load cases")
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchCases()
  }, [])

  const openCases = cases.filter((c) => c.status === "open" || c.status === "investigating")
  const closedCases = cases.filter((c) => c.status === "closed")

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="container max-w-screen-xl py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight">Investigation Dashboard</h1>
          <p className="mt-2 text-muted-foreground">
            Create new cases and manage ongoing investigations.
          </p>
        </div>

        <div className="grid gap-8 lg:grid-cols-3">
          {/* Case Creation Panel */}
          <div className="lg:col-span-1">
            <CaseForm />
          </div>

          {/* Cases List */}
          <div className="lg:col-span-2 space-y-8">
            {/* Active Cases */}
            <section>
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-amber-500" />
                Active Cases
                {openCases.length > 0 && (
                  <span className="text-sm font-normal text-muted-foreground">
                    ({openCases.length})
                  </span>
                )}
              </h2>

              {isLoading ? (
                <DashboardSkeleton />
              ) : error ? (
                <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-6">
                  <div className="flex items-center gap-2 text-destructive mb-2">
                    <AlertCircle className="h-5 w-5" />
                    <span className="font-medium">Failed to load cases</span>
                  </div>
                  <p className="text-sm text-muted-foreground mb-4">{error}</p>
                  <Button variant="outline" size="sm" onClick={fetchCases}>
                    Try Again
                  </Button>
                </div>
              ) : openCases.length === 0 ? (
                <EmptyState
                  icon={FolderOpen}
                  title="No active cases"
                  description="Create a new case using the form to start an investigation."
                />
              ) : (
                <div className="grid gap-4 md:grid-cols-2">
                  {openCases.map((caseItem) => (
                    <CaseCard key={caseItem.id} caseData={caseItem} />
                  ))}
                </div>
              )}
            </section>

            {/* Closed Cases */}
            {closedCases.length > 0 && (
              <section>
                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-green-500" />
                  Closed Cases
                  <span className="text-sm font-normal text-muted-foreground">
                    ({closedCases.length})
                  </span>
                </h2>
                <div className="grid gap-4 md:grid-cols-2">
                  {closedCases.map((caseItem) => (
                    <CaseCard key={caseItem.id} caseData={caseItem} />
                  ))}
                </div>
              </section>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
