// Case types
export interface Case {
  id: string
  subject_name: string
  approximate_age: number | null
  description: string
  last_known_location: string
  last_known_time: string
  clothing_description: string | null
  accessories: string | null
  image_url: string | null
  created_at: string
  status: "open" | "closed" | "investigating"
}

export interface CaseInput {
  subject_name: string
  approximate_age?: number
  description: string
  last_known_location: string
  last_known_time: string
  clothing_description?: string
  accessories?: string
  image_url?: string
}

// Sighting types
export interface Sighting {
  id: string
  case_id: string
  camera_name: string
  camera_location: string
  timestamp: string
  confidence_score: number
  explanation: string
  image_url: string | null
}

// Timeline types
export interface TimelineEvent {
  id: string
  case_id: string
  timestamp: string
  camera_name: string
  camera_location: string
  confidence: number
  explanation: string
}

export interface Timeline {
  events: TimelineEvent[]
  summary: string
}

// Camera recommendation types
export type UrgencyLevel = "critical" | "high" | "medium" | "low"

export interface CameraRecommendation {
  id: string
  camera_name: string
  camera_location: string
  reason: string
  urgency: UrgencyLevel
  review_before: string | null
}

// API response types
export interface ApiResponse<T> {
  data: T | null
  error: string | null
}

export interface SearchResponse {
  sightings: Sighting[]
  search_completed: boolean
}
