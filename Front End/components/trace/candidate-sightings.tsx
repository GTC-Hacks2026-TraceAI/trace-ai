"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { SightingCard } from "./sighting-card"
import { EmptyState } from "./empty-state"
import type { Sighting } from "@/lib/types"
import { Eye, Camera } from "lucide-react"

interface CandidateSightingsProps {
  sightings: Sighting[]
  hasSearched: boolean
}

export function CandidateSightings({ sightings, hasSearched }: CandidateSightingsProps) {
  const sortedSightings = [...sightings].sort(
    (a, b) => b.confidence_score - a.confidence_score
  )

  const highConfidence = sortedSightings.filter((s) => s.confidence_score >= 0.8)
  const otherSightings = sortedSightings.filter((s) => s.confidence_score < 0.8)

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Eye className="h-5 w-5" />
          Candidate Sightings
        </CardTitle>
        <CardDescription>
          {sightings.length > 0
            ? `${sightings.length} potential matches found • ${highConfidence.length} high confidence`
            : "Potential matches will appear here after searching"}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {!hasSearched ? (
          <EmptyState
            icon={Camera}
            title="No search performed"
            description="Run a footage search to find potential sightings of the subject."
          />
        ) : sightings.length === 0 ? (
          <EmptyState
            icon={Eye}
            title="No sightings found"
            description="The search did not find any potential matches in the indexed footage."
          />
        ) : (
          <div className="space-y-4">
            {highConfidence.length > 0 && (
              <div className="space-y-3">
                <h4 className="text-sm font-medium text-emerald-400">
                  High Confidence Matches
                </h4>
                {highConfidence.map((sighting, idx) => (
                  <SightingCard
                    key={sighting.id}
                    sighting={sighting}
                    rank={idx + 1}
                  />
                ))}
              </div>
            )}

            {otherSightings.length > 0 && (
              <div className="space-y-3">
                {highConfidence.length > 0 && (
                  <h4 className="text-sm font-medium text-muted-foreground pt-2">
                    Other Matches
                  </h4>
                )}
                {otherSightings.map((sighting, idx) => (
                  <SightingCard
                    key={sighting.id}
                    sighting={sighting}
                    rank={highConfidence.length + idx + 1}
                  />
                ))}
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
