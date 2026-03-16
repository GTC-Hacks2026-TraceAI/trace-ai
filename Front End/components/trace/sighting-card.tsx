import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { Sighting } from "@/lib/types"
import { Camera, MapPin, Clock, TrendingUp } from "lucide-react"
import { cn } from "@/lib/utils"

interface SightingCardProps {
  sighting: Sighting
  rank: number
}

export function SightingCard({ sighting, rank }: SightingCardProps) {
  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    })
  }

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
    if (score >= 0.6) return "bg-amber-500/20 text-amber-400 border-amber-500/30"
    return "bg-red-500/20 text-red-400 border-red-500/30"
  }

  const getConfidenceLabel = (score: number) => {
    if (score >= 0.8) return "High"
    if (score >= 0.6) return "Medium"
    return "Low"
  }

  return (
    <Card className={cn(
      "transition-all hover:border-primary/50",
      sighting.similarity_score >= 0.8 && "border-emerald-500/30"
    )}>
      <CardContent className="p-4">
        <div className="flex gap-4">
          {/* Thumbnail placeholder */}
          <div className="relative w-28 h-20 rounded-md bg-muted flex-shrink-0 overflow-hidden">
            <div className="w-full h-full flex items-center justify-center text-muted-foreground">
              <Camera className="h-8 w-8" />
            </div>
            <div className="absolute top-1 left-1 bg-background/90 text-xs font-bold px-1.5 py-0.5 rounded">
              #{rank}
            </div>
          </div>

          {/* Details */}
          <div className="flex-1 min-w-0 space-y-2">
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-center gap-2 text-sm font-medium truncate">
                <Camera className="h-4 w-4 flex-shrink-0 text-muted-foreground" />
                {sighting.camera_id}
              </div>
              <Badge variant="outline" className={cn("flex-shrink-0", getConfidenceColor(sighting.similarity_score))}>
                <TrendingUp className="h-3 w-3 mr-1" />
                {Math.round(sighting.similarity_score * 100)}% {getConfidenceLabel(sighting.similarity_score)}
              </Badge>
            </div>

            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <span className="flex items-center gap-1">
                <MapPin className="h-3 w-3" />
                {sighting.location}
              </span>
              <span className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {formatTime(sighting.timestamp)}
              </span>
            </div>

            <p className="text-sm text-muted-foreground line-clamp-2">
              {sighting.explanation}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
