"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { TimelineEvent } from "./timeline-event"
import { EmptyState } from "./empty-state"
import type { Timeline } from "@/lib/types"
import { Route, Clock } from "lucide-react"

interface TimelinePanelProps {
  timeline: Timeline | null
  hasSearched: boolean
}

export function TimelinePanel({ timeline, hasSearched }: TimelinePanelProps) {
  const sortedEntries = timeline?.entries
    ? [...timeline.entries].sort(
        (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
      )
    : []

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Route className="h-5 w-5" />
          Movement Timeline
        </CardTitle>
        <CardDescription>
          Chronological tracking of subject movements
        </CardDescription>
      </CardHeader>
      <CardContent>
        {!hasSearched ? (
          <EmptyState
            icon={Clock}
            title="Timeline not available"
            description="Run a footage search to generate a movement timeline."
          />
        ) : !timeline || sortedEntries.length === 0 ? (
          <EmptyState
            icon={Route}
            title="No movement data"
            description="Not enough sightings to construct a movement timeline."
          />
        ) : (
          <div className="space-y-4">
            {timeline.summary && (
              <div className="rounded-lg bg-muted/50 p-4 text-sm">
                <p className="text-muted-foreground">{timeline.summary}</p>
              </div>
            )}
            <div className="pt-2">
              {sortedEntries.map((entry, idx) => (
                <TimelineEvent
                  key={`${entry.camera_id}-${entry.timestamp}`}
                  event={entry}
                  isLast={idx === sortedEntries.length - 1}
                />
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
