import type {
  Case,
  CaseInput,
  Sighting,
  Timeline,
  CameraRecommendation,
  SearchResponse,
} from "./types"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || `API Error: ${response.status}`)
  }

  return response.json()
}

// Health check
export async function checkHealth(): Promise<{ status: string }> {
  return fetchApi("/health")
}

// Case operations
export async function createCase(caseData: CaseInput): Promise<Case> {
  return fetchApi("/cases", {
    method: "POST",
    body: JSON.stringify(caseData),
  })
}

export async function getCases(): Promise<Case[]> {
  return fetchApi("/cases")
}

export async function getCase(caseId: string): Promise<Case> {
  return fetchApi(`/cases/${caseId}`)
}

// Search operations
export async function runFootageSearch(caseId: string): Promise<SearchResponse> {
  return fetchApi(`/cases/${caseId}/search`, {
    method: "POST",
  })
}

// Timeline operations
export async function getTimeline(caseId: string): Promise<Timeline> {
  return fetchApi(`/cases/${caseId}/timeline`)
}

// Recommendations
export async function getRecommendations(
  caseId: string
): Promise<CameraRecommendation[]> {
  return fetchApi(`/cases/${caseId}/recommendations`)
}
