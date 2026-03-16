"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { RecommendationCard } from "./recommendation-card"
import { EmptyState } from "./empty-state"
import type { CameraRecommendation } from "@/lib/types"
import { Compass, Video } from "lucide-react"

interface CameraRecommendationsProps {
  recommendations: CameraRecommendation[]
  hasSearched: boolean
}

export function CameraRecommendations({
  recommendations,
  hasSearched,
}: CameraRecommendationsProps) {
  const sortedRecommendations = [...recommendations].sort(
    (a, b) => a.priority - b.priority
  )

  const highCount = recommendations.filter((r) => r.urgency_level === "high").length

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Compass className="h-5 w-5" />
          Next Camera Recommendations
        </CardTitle>
        <CardDescription>
          {recommendations.length > 0
            ? `${recommendations.length} cameras to review • ${highCount} high priority`
            : "Recommended cameras to check next"}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {!hasSearched ? (
          <EmptyState
            icon={Video}
            title="No recommendations yet"
            description="Run a footage search to get camera recommendations."
          />
        ) : recommendations.length === 0 ? (
          <EmptyState
            icon={Compass}
            title="No recommendations"
            description="No additional cameras recommended for review at this time."
          />
        ) : (
          <div className="space-y-3">
            {sortedRecommendations.map((rec) => (
              <RecommendationCard key={rec.camera_id} recommendation={rec} />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
