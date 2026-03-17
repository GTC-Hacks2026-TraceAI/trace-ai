"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { Navbar } from "@/components/trace/navbar"
import { CaseCard } from "@/components/trace/case-card"
import { EmptyState } from "@/components/trace/empty-state"
import { DashboardSkeleton } from "@/components/trace/loading-skeleton"
import { getCases } from "@/lib/api"
import type { Case } from "@/lib/types"
import { FolderOpen, AlertCircle, Plus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default function CasesPage() {
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

  const allCases = cases
  const openCases = cases.filter((c) => c.status === "open")
  const investigatingCases = cases.filter((c) => c.status === "investigating")
  const closedCases = cases.filter((c) => c.status === "closed")

  const renderCaseList = (caseList: Case[]) => {
    if (caseList.length === 0) {
      return (
        <EmptyState
          icon={FolderOpen}
          title="No cases found"
          description="There are no cases matching this filter."
        />
      )
    }

    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {caseList.map((caseItem) => (
          <CaseCard key={caseItem.id} caseData={caseItem} />
        ))}
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="container max-w-screen-xl py-8">
        <div className="flex items-start justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">All Cases</h1>
            <p className="mt-2 text-muted-foreground">
              View and manage all investigation cases.
            </p>
          </div>
          <Link href="/dashboard">
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              New Case
            </Button>
          </Link>
        </div>

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
        ) : (
          <Tabs defaultValue="all">
            <TabsList>
              <TabsTrigger value="all">
                All ({allCases.length})
              </TabsTrigger>
              <TabsTrigger value="open">
                Open ({openCases.length})
              </TabsTrigger>
              <TabsTrigger value="investigating">
                Investigating ({investigatingCases.length})
              </TabsTrigger>
              <TabsTrigger value="closed">
                Closed ({closedCases.length})
              </TabsTrigger>
            </TabsList>
            <div className="mt-6">
              <TabsContent value="all">
                {renderCaseList(allCases)}
              </TabsContent>
              <TabsContent value="open">
                {renderCaseList(openCases)}
              </TabsContent>
              <TabsContent value="investigating">
                {renderCaseList(investigatingCases)}
              </TabsContent>
              <TabsContent value="closed">
                {renderCaseList(closedCases)}
              </TabsContent>
            </div>
          </Tabs>
        )}
      </main>
    </div>
  )
}
