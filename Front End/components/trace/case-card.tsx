import Link from "next/link"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { Case } from "@/lib/types"
import { User, MapPin, Clock, ChevronRight } from "lucide-react"

interface CaseCardProps {
  caseData: Case
}

export function CaseCard({ caseData }: CaseCardProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    })
  }

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleString("en-US", {
      month: "short",
      day: "numeric",
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
    <Link href={`/cases/${caseData.id}`}>
      <Card className="transition-all hover:border-primary/50 hover:bg-accent/5 cursor-pointer group">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <CardTitle className="flex items-center gap-2 text-lg">
              <User className="h-4 w-4" />
              {caseData.subject_name}
            </CardTitle>
            <Badge variant="outline" className={statusColors[caseData.status]}>
              {caseData.status.charAt(0).toUpperCase() + caseData.status.slice(1)}
            </Badge>
          </div>
          <CardDescription>
            Created {formatDate(caseData.created_at)}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-muted-foreground line-clamp-2">
            {caseData.description}
          </p>
          <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
            <span className="flex items-center gap-1">
              <MapPin className="h-3 w-3" />
              {caseData.last_known_location}
            </span>
            <span className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {formatTime(caseData.last_known_time)}
            </span>
          </div>
          <div className="flex items-center text-sm text-primary opacity-0 group-hover:opacity-100 transition-opacity">
            View case details
            <ChevronRight className="h-4 w-4 ml-1" />
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}
