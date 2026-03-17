import { Badge } from "@/components/ui/badge"
import type { TimelineEntry } from "@/lib/types"
import { MapPin } from "lucide-react"
import { cn } from "@/lib/utils"

interface TimelineEventProps {
  event: TimelineEntry
  isLast: boolean
}

export function TimelineEvent({ event, isLast }: TimelineEventProps) {
  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
    })
  }

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return "bg-emerald-500"
    if (score >= 0.6) return "bg-amber-500"
    return "bg-red-500"
  }

  return (
    <div className="flex gap-4">
      {/* Timeline connector */}
      <div className="flex flex-col items-center">
        <div className={cn("w-3 h-3 rounded-full", getConfidenceColor(event.similarity_score))} />
        {!isLast && <div className="w-0.5 flex-1 bg-border mt-1" />}
      </div>

      {/* Event content */}
      <div className={cn("flex-1 pb-6", isLast && "pb-0")}>
        <div className="flex items-center gap-2 mb-1">
          <span className="font-medium">{formatTime(event.timestamp)}</span>
          <Badge variant="outline" className="text-xs">
            {Math.round(event.similarity_score * 100)}%
          </Badge>
        </div>
        <div className="flex items-center gap-1 text-sm text-muted-foreground mb-1">
          <MapPin className="h-3 w-3" />
          {event.location}
          <span className="text-xs">({event.camera_name})</span>
        </div>
        <p className="text-sm text-muted-foreground">{event.explanation}</p>
      </div>
    </div>
  )
}
