"use client"

import { useState, useEffect, use } from "react"
import Link from "next/link"
import { Navbar } from "@/components/trace/navbar"
import { CaseSummary } from "@/components/trace/case-summary"
import { CandidateSightings } from "@/components/trace/candidate-sightings"
import { TimelinePanel } from "@/components/trace/timeline-panel"
import { CameraRecommendations } from "@/components/trace/camera-recommendations"
import {
  CaseSummarySkeleton,
  SightingsSkeleton,
  TimelineSkeleton,
  RecommendationsSkeleton,
} from "@/components/trace/loading-skeleton"
import { getCase, runFootageSearch, getTimeline, getRecommendations } from "@/lib/api"
import type { Case, Sighting, Timeline, CameraRecommendation } from "@/lib/types"
import { AlertCircle, ArrowLeft } from "lucide-react"
import { Button } from "@/components/ui/button"

interface PageProps {
  params: Promise<{ id: string }>
}

export default function CaseWorkspacePage({ params }: PageProps) {
  const { id: caseId } = use(params)

  const [caseData, setCaseData] = useState<Case | null>(null)
  const [sightings, setSightings] = useState<Sighting[]>([])
  const [timeline, setTimeline] = useState<Timeline | null>(null)
  const [recommendations, setRecommendations] = useState<CameraRecommendation[]>([])

  const [isLoadingCase, setIsLoadingCase] = useState(true)
  const [isSearching, setIsSearching] = useState(false)
  const [isLoadingTimeline, setIsLoadingTimeline] = useState(false)
  const [isLoadingRecommendations, setIsLoadingRecommendations] = useState(false)

  const [hasSearched, setHasSearched] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Load case data
  useEffect(() => {
    const fetchCase = async () => {
      setIsLoadingCase(true)
      setError(null)
      try {
        const data = await getCase(caseId)
        setCaseData(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load case")
      } finally {
        setIsLoadingCase(false)
      }
    }

    fetchCase()
  }, [caseId])

  // Run footage search
  const handleRunSearch = async () => {
    setIsSearching(true)
    setError(null)

    try {
      // Run search
      const searchResult = await runFootageSearch(caseId)
      setSightings(searchResult.sightings)
      setHasSearched(true)

      // Load timeline and recommendations in parallel
      setIsLoadingTimeline(true)
      setIsLoadingRecommendations(true)

      const [timelineData, recommendationsData] = await Promise.all([
        getTimeline(caseId).catch(() => null),
        getRecommendations(caseId).catch(() => []),
      ])

      setTimeline(timelineData)
      setRecommendations(recommendationsData)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed")
    } finally {
      setIsSearching(false)
      setIsLoadingTimeline(false)
      setIsLoadingRecommendations(false)
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="container max-w-screen-xl py-8">
        {/* Back link */}
        <Link
          href="/dashboard"
          className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors mb-6"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Dashboard
        </Link>

        {/* Error state */}
        {error && !isLoadingCase && (
          <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-6 mb-6">
            <div className="flex items-center gap-2 text-destructive mb-2">
              <AlertCircle className="h-5 w-5" />
              <span className="font-medium">Error</span>
            </div>
            <p className="text-sm text-muted-foreground">{error}</p>
          </div>
        )}

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Left column */}
          <div className="space-y-6">
            {/* Case Summary */}
            {isLoadingCase ? (
              <CaseSummarySkeleton />
            ) : caseData ? (
              <CaseSummary
                caseData={caseData}
                onRunSearch={handleRunSearch}
                isSearching={isSearching}
              />
            ) : null}

            {/* Timeline */}
            {isSearching || isLoadingTimeline ? (
              <TimelineSkeleton />
            ) : (
              <TimelinePanel timeline={timeline} hasSearched={hasSearched} />
            )}
          </div>

          {/* Right column */}
          <div className="space-y-6">
            {/* Candidate Sightings */}
            {isSearching ? (
              <SightingsSkeleton />
            ) : (
              <CandidateSightings sightings={sightings} hasSearched={hasSearched} />
            )}

            {/* Camera Recommendations */}
            {isSearching || isLoadingRecommendations ? (
              <RecommendationsSkeleton />
            ) : (
              <CameraRecommendations
                recommendations={recommendations}
                hasSearched={hasSearched}
              />
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
