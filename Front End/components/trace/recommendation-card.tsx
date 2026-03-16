import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { CameraRecommendation, UrgencyLevel } from "@/lib/types"
import { Camera, MapPin, Clock, AlertTriangle } from "lucide-react"
import { cn } from "@/lib/utils"

interface RecommendationCardProps {
  recommendation: CameraRecommendation
}

const urgencyConfig: Record<UrgencyLevel, { color: string; label: string }> = {
  critical: {
    color: "bg-red-500/20 text-red-400 border-red-500/30",
    label: "Critical",
  },
  high: {
    color: "bg-orange-500/20 text-orange-400 border-orange-500/30",
    label: "High",
  },
  medium: {
    color: "bg-amber-500/20 text-amber-400 border-amber-500/30",
    label: "Medium",
  },
  low: {
    color: "bg-blue-500/20 text-blue-400 border-blue-500/30",
    label: "Low",
  },
}

export function RecommendationCard({ recommendation }: RecommendationCardProps) {
  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    })
  }

  const urgency = urgencyConfig[recommendation.urgency]

  return (
    <Card className={cn(
      "transition-all",
      recommendation.urgency === "critical" && "border-red-500/30",
      recommendation.urgency === "high" && "border-orange-500/30"
    )}>
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-4 mb-3">
          <div className="flex items-center gap-2">
            <Camera className="h-4 w-4 text-muted-foreground" />
            <span className="font-medium">{recommendation.camera_name}</span>
          </div>
          <Badge variant="outline" className={cn("flex-shrink-0", urgency.color)}>
            <AlertTriangle className="h-3 w-3 mr-1" />
            {urgency.label}
          </Badge>
        </div>

        <div className="flex items-center gap-1 text-sm text-muted-foreground mb-2">
          <MapPin className="h-3 w-3" />
          {recommendation.camera_location}
        </div>

        <p className="text-sm text-muted-foreground mb-3">
          {recommendation.reason}
        </p>

        {recommendation.review_before && (
          <div className="flex items-center gap-2 text-xs text-amber-400">
            <Clock className="h-3 w-3" />
            Review before: {formatTime(recommendation.review_before)}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
