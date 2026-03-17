"""All Pydantic models and request schemas for Trace AI."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

# Validation bounds
_MAX_AGE = 150
_MAX_HEIGHT_CM = 300.0
_MAX_WEIGHT_KG = 500.0
_MAX_SEARCH_RESULTS = 100


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uid() -> str:
    return str(uuid4())


# ── Request schemas ────────────────────────────────────────────────────────────

class CaseCreate(BaseModel):
    subject_name: str
    description: Optional[str] = None
    last_known_location: Optional[str] = None
    clothing: Optional[str] = None


# ── Enumerations ───────────────────────────────────────────────────────────────

class CaseStatus(str, Enum):
    open = "open"
    closed = "closed"


class RetentionUrgency(str, Enum):
    """Urgency level for reviewing camera footage before it is overwritten."""

    low = "low"
    medium = "medium"
    high = "high"


# ── Core domain models (used by existing routes) ───────────────────────────────

class Case(BaseModel):
    id: str = Field(default_factory=_uid)
    subject_name: str
    description: Optional[str] = None
    last_known_location: Optional[str] = None
    clothing: Optional[str] = None
    status: CaseStatus = CaseStatus.open
    created_at: datetime = Field(default_factory=_now)


class Sighting(BaseModel):
    id: str = Field(default_factory=_uid)
    case_id: str
    camera_id: str
    frame_id: str
    timestamp: datetime
    location: str
    similarity_score: float = Field(ge=0.0, le=1.0)
    explanation: str


class TimelineEntry(BaseModel):
    timestamp: datetime
    camera_id: str
    camera_name: str
    location: str
    frame_id: str
    similarity_score: float
    explanation: str


class Timeline(BaseModel):
    case_id: str
    subject_name: str
    entries: list[TimelineEntry]
    summary: Optional[str] = None


class Camera(BaseModel):
    id: str
    name: str
    location: str
    zone: str
    neighbors: list[str] = Field(default_factory=list)
    latitude: Optional[float] = Field(default=None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(default=None, ge=-180.0, le=180.0)
    location_label: Optional[str] = None
    retention_hours: Optional[float] = Field(
        default=None,
        gt=0.0,
        description="How many hours of footage this camera retains before overwriting.",
    )


class CameraRecommendation(BaseModel):
    camera_id: str
    camera_name: str
    location: str
    zone: str
    priority: int
    reason: str


# ── Extended / richer models ───────────────────────────────────────────────────

class MissingPersonCase(BaseModel):
    """Enriched missing-person case with audit timestamps."""

    id: str = Field(default_factory=_uid)
    subject_name: str
    description: Optional[str] = None
    last_known_location: Optional[str] = None
    clothing: Optional[str] = None
    status: CaseStatus = CaseStatus.open
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class SubjectProfile(BaseModel):
    """Detailed physical profile of a missing person linked to a case."""

    id: str = Field(default_factory=_uid)
    case_id: str
    full_name: str
    age: Optional[int] = Field(default=None, ge=0, le=_MAX_AGE)
    gender: Optional[str] = None
    height_cm: Optional[float] = Field(default=None, ge=0.0, le=_MAX_HEIGHT_CM)
    weight_kg: Optional[float] = Field(default=None, ge=0.0, le=_MAX_WEIGHT_KG)
    hair_color: Optional[str] = None
    eye_color: Optional[str] = None
    distinguishing_features: Optional[str] = None
    last_known_location: Optional[str] = None
    clothing_description: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=_now)


class SubjectImageReference(BaseModel):
    """Reference to an image used for identifying the subject."""

    id: str = Field(default_factory=_uid)
    case_id: str
    filename: str
    description: Optional[str] = None
    uploaded_at: datetime = Field(default_factory=_now)


class CameraFrame(BaseModel):
    """A single frame extracted from camera footage."""

    id: str
    camera_id: str
    timestamp: datetime
    thumbnail_url: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


class CandidateSighting(BaseModel):
    """A candidate sighting with confidence scoring and explanation."""

    id: str = Field(default_factory=_uid)
    case_id: str
    camera_id: str
    frame_id: str
    timestamp: datetime
    location: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    explanation: str
    matched_features: list[str] = Field(default_factory=list)
    reviewed: bool = False


class TimelineEvent(BaseModel):
    """A single event in a subject's movement timeline."""

    id: str = Field(default_factory=_uid)
    case_id: str
    timestamp: datetime
    camera_id: str
    camera_name: str
    location: str
    frame_id: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    event_type: str = "sighting"
    notes: Optional[str] = None


class SearchRequest(BaseModel):
    """Input schema for initiating a camera-network search."""

    case_id: str
    image_reference_ids: list[str] = Field(default_factory=list)
    description: Optional[str] = None
    clothing: Optional[str] = None
    min_confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    max_results: int = Field(default=10, ge=1, le=_MAX_SEARCH_RESULTS)


class SearchResponse(BaseModel):
    """Result of a camera-network search, wrapping ranked candidate sightings."""

    case_id: str
    total_candidates: int
    sightings: list[CandidateSighting]
    searched_at: datetime = Field(default_factory=_now)


class NextCameraRecommendation(BaseModel):
    """Recommended next camera to inspect, optionally with geographic coordinates."""

    camera_id: str
    camera_name: str
    location: str
    zone: str
    priority: int = Field(ge=1)
    reason: str
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    latitude: Optional[float] = Field(default=None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(default=None, ge=-180.0, le=180.0)
    urgency_level: Optional[RetentionUrgency] = Field(
        default=None,
        description="How urgently the footage at this camera should be reviewed.",
    )
    review_before: Optional[datetime] = Field(
        default=None,
        description="Footage from the originating sighting expires at this time.",
    )
