"""All API route handlers for Trace AI."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app import store
from app.mock import CAMERA_MAP, CAMERAS, SAMPLE_FRAMES
from app.models import (
    Camera,
    CameraFrame,
    CameraRecommendation,
    Case,
    CaseCreate,
    NextCameraRecommendation,
    Sighting,
    Timeline,
)

router = APIRouter()


# ── Cases ──────────────────────────────────────────────────────────────────────

@router.post("/cases", response_model=Case, status_code=201, tags=["cases"])
def create_case(data: CaseCreate) -> Case:
    """Create a new missing-person case."""
    case = Case(**data.model_dump())
    return store.case_repository.save(case)


@router.get("/cases", response_model=list[Case], tags=["cases"])
def list_cases() -> list[Case]:
    """Return all cases."""
    return store.case_repository.list_all()


@router.get("/cases/{case_id}", response_model=Case, tags=["cases"])
def get_case(case_id: str) -> Case:
    """Return a single case by id."""
    case = store.case_repository.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


# ── Search ─────────────────────────────────────────────────────────────────────

def _load_frames() -> list[CameraFrame]:
    """Convert raw SAMPLE_FRAMES dicts into CameraFrame model instances."""
    return [
        CameraFrame(
            id=f["frame_id"],
            camera_id=f["camera_id"],
            timestamp=f["timestamp"],
            metadata=f.get("metadata"),
        )
        for f in SAMPLE_FRAMES
    ]


@router.post("/cases/{case_id}/search", response_model=list[Sighting], tags=["search"])
def search_case(case_id: str) -> list[Sighting]:
    """Run search against indexed frame metadata and return ranked sightings."""
    case = store.case_repository.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    frames = _load_frames()
    sightings = store.search_service.search(
        case, frames, CAMERA_MAP, max_results=10,
    )
    store.case_repository.save_sightings(case_id, sightings)
    return sightings


# ── Timeline ───────────────────────────────────────────────────────────────────

@router.get("/cases/{case_id}/timeline", response_model=Timeline, tags=["timeline"])
def get_timeline(case_id: str) -> Timeline:
    """Build a movement timeline from confirmed sightings.

    Sightings are filtered for confidence, sorted chronologically, and
    enriched with camera name, location, and explanation.  A plain-English
    path summary is included in the ``summary`` field.
    """
    case = store.case_repository.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    sightings = store.case_repository.get_sightings(case_id)
    return store.timeline_service.build(
        case_id=case_id,
        subject_name=case.subject_name,
        sightings=sightings,
        camera_map=CAMERA_MAP,
    )


# ── Camera recommendations ─────────────────────────────────────────────────────

@router.get(
    "/cases/{case_id}/recommendations",
    response_model=list[NextCameraRecommendation],
    tags=["cameras"],
)
@router.get(
    "/cases/{case_id}/camera-recommendations",
    response_model=list[NextCameraRecommendation],
    tags=["cameras"],
    include_in_schema=False,
)
def recommend_cameras(case_id: str) -> list[NextCameraRecommendation]:
    """Recommend next cameras to inspect based on the movement graph."""
    case = store.case_repository.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    sightings = store.case_repository.get_sightings(case_id)
    return store.camera_recommendation_service.recommend(
        sightings=sightings,
        camera_map=CAMERA_MAP,
        cameras=CAMERAS,
    )
