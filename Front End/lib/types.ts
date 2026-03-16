// Case types
export interface Case {
  id: string
  subject_name: string
  description: string | null
  last_known_location: string | null
  clothing: string | null
  status: "open" | "closed"
  created_at: string
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
  camera_id: string
  frame_id: string
  timestamp: string
  location: string
  similarity_score: number
  explanation: string
}

// Timeline types
export interface TimelineEntry {
  timestamp: string
  camera_id: string
  camera_name: string
  location: string
  frame_id: string
  similarity_score: number
  explanation: string
}

export interface Timeline {
  case_id: string
  subject_name: string
  entries: TimelineEntry[]
  summary: string | null
}

// Camera recommendation types
export type UrgencyLevel = "high" | "medium" | "low"

export interface CameraRecommendation {
  camera_id: string
  camera_name: string
  location: string
  zone: string
  priority: number
  reason: string
  confidence: number | null
  urgency_level: UrgencyLevel | null
  review_before: string | null
}

// API response types
export interface ApiResponse<T> {
  data: T | null
  error: string | null
}

