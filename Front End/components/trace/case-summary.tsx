"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Spinner } from "@/components/ui/spinner"
import type { Case } from "@/lib/types"
import { User, MapPin, Clock, Shirt, Backpack, Search } from "lucide-react"

interface CaseSummaryProps {
  caseData: Case
  onRunSearch: () => void
  isSearching: boolean
}

export function CaseSummary({ caseData, onRunSearch, isSearching }: CaseSummaryProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "numeric",
      minute: "2-digit",
    })
  }

  const statusColors = {
    open: "bg-amber-500/20 text-amber-400 border-amber-500/30",
    investigating: "bg-blue-500/20 text-blue-400 border-blue-500/30",
    closed: "bg-green-500/20 text-green-400 border-green-500/30",
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="flex items-center gap-2 text-xl">
              <User className="h-5 w-5" />
              {caseData.subject_name}
            </CardTitle>
            <CardDescription>
              Case opened {formatDate(caseData.created_at)}
            </CardDescription>
          </div>
          <Badge variant="outline" className={statusColors[caseData.status]}>
            {caseData.status.charAt(0).toUpperCase() + caseData.status.slice(1)}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <MapPin className="h-4 w-4" />
              Last Known Location
            </div>
            <p className="font-medium">{caseData.last_known_location}</p>
          </div>
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Clock className="h-4 w-4" />
              Last Seen
            </div>
            <p className="font-medium">{formatDate(caseData.last_known_time)}</p>
          </div>
        </div>

        {caseData.approximate_age && (
          <div className="space-y-1">
            <div className="text-sm text-muted-foreground">Age</div>
            <p className="font-medium">Approximately {caseData.approximate_age} years old</p>
          </div>
        )}

        <div className="space-y-1">
          <div className="text-sm text-muted-foreground">Description</div>
          <p className="text-sm leading-relaxed">{caseData.description}</p>
        </div>

        {(caseData.clothing_description || caseData.accessories) && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {caseData.clothing_description && (
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Shirt className="h-4 w-4" />
                  Clothing
                </div>
                <p className="text-sm">{caseData.clothing_description}</p>
              </div>
            )}
            {caseData.accessories && (
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Backpack className="h-4 w-4" />
                  Accessories
                </div>
                <p className="text-sm">{caseData.accessories}</p>
              </div>
            )}
          </div>
        )}

        <Button onClick={onRunSearch} disabled={isSearching} className="w-full md:w-auto">
          {isSearching ? (
            <>
              <Spinner className="mr-2 h-4 w-4" />
              Searching Footage...
            </>
          ) : (
            <>
              <Search className="mr-2 h-4 w-4" />
              Run Footage Search
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  )
}
