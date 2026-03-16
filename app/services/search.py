"""Search service for matching missing-person cases against indexed camera frames.

Architecture
------------
*  ``ISearchBackend`` defines the contract that any matching backend must
   satisfy.  The current ``MockSearchBackend`` uses lightweight metadata
   heuristics (clothing colour, accessories, location, time, text tags,
   and an optional face-match placeholder).
*  ``SearchService`` is the high-level orchestrator consumed by the route
   layer.  It delegates to whichever ``ISearchBackend`` is injected.

Replacing the mock with a real vision backend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. Implement ``ISearchBackend`` with your real matcher (e.g. CLIP embeddings
   stored in FAISS / Pinecone / Qdrant).
2. In ``app/store.py``, swap ``MockSearchBackend()`` for your new class.
3. Everything else (routes, models, tests) stays the same.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

from app.models import Camera, Case, CameraFrame, Sighting

# ── Scoring weights ────────────────────────────────────────────────────────────
# Easy to tune; must sum to 1.0 so the final score stays in [0, 1].

DEFAULT_WEIGHTS: dict[str, float] = {
    "clothing_color": 0.25,
    "accessory": 0.15,
    "location": 0.15,
    "time": 0.15,
    "face_match": 0.15,
    "text_tags": 0.15,
}

# Recognised colour and accessory tokens (lowercase).
_COLORS: set[str] = {
    "red", "blue", "green", "black", "white", "brown", "yellow", "orange",
    "purple", "pink", "gray", "grey", "beige", "navy", "maroon",
}

_ACCESSORIES: set[str] = {
    "backpack", "hat", "glasses", "sunglasses", "bag", "purse",
    "umbrella", "watch", "scarf", "mask", "cap", "hoodie",
}


# ── Scoring helpers ────────────────────────────────────────────────────────────

def clothing_color_score(
    case_clothing: str | None,
    frame_colors: list[str],
) -> float:
    """Return 0-1 based on how many case clothing colours appear in the frame."""
    if not case_clothing or not frame_colors:
        return 0.0
    case_tokens = set(case_clothing.lower().split())
    case_colors = case_tokens & _COLORS
    if not case_colors:
        return 0.0
    frame_set = {c.lower() for c in frame_colors}
    matches = case_colors & frame_set
    return len(matches) / len(case_colors)


def accessory_score(
    case_clothing: str | None,
    frame_accessories: list[str],
) -> float:
    """Return 0-1 based on accessory overlap between case and frame."""
    if not case_clothing or not frame_accessories:
        return 0.0
    case_lower = case_clothing.lower()
    case_acc = {a for a in _ACCESSORIES if a in case_lower}
    if not case_acc:
        return 0.0
    frame_set = {a.lower() for a in frame_accessories}
    matches = case_acc & frame_set
    return len(matches) / len(case_acc)


def location_relevance_score(
    case_location: str | None,
    camera_location: str,
) -> float:
    """Return 0-1 based on keyword overlap between case and camera locations."""
    if not case_location:
        return 0.3  # neutral baseline when no location info
    case_tokens = set(case_location.lower().replace(",", " ").split())
    loc_tokens = set(camera_location.lower().replace(",", " ").split())
    overlap = case_tokens & loc_tokens
    if not overlap:
        return 0.1
    return min(1.0, len(overlap) / max(len(case_tokens), 1) + 0.3)


def time_relevance_score(
    frame_time: datetime,
    reference_time: datetime | None = None,
) -> float:
    """Return 0-1 based on temporal proximity to *reference_time*.

    Defaults to ``datetime.now(UTC)`` when no reference is supplied.
    Frames within the last hour score highest; beyond 24 h they score lowest.
    """
    if reference_time is None:
        reference_time = datetime.now(timezone.utc)
    delta_s = abs((reference_time - frame_time).total_seconds())
    if delta_s < 3600:
        return 1.0
    if delta_s < 86400:
        return max(0.2, 1.0 - delta_s / 86400)
    return 0.1


def text_tag_match_score(
    case_description: str | None,
    case_clothing: str | None,
    frame_tags: list[str],
) -> float:
    """Return 0-1 based on how many frame text-tags match the case text."""
    if not frame_tags:
        return 0.0
    combined = " ".join(filter(None, [case_description, case_clothing])).lower()
    if not combined:
        return 0.0
    combined_words = set(combined.replace(",", " ").split())
    matched = 0
    for tag in frame_tags:
        tag_words = set(tag.lower().split())
        if tag_words & combined_words:
            matched += 1
    return min(1.0, matched / len(frame_tags))


def compute_confidence(
    case: Case,
    frame: CameraFrame,
    camera_location: str,
    reference_time: datetime | None = None,
    weights: dict[str, float] | None = None,
) -> tuple[float, list[str]]:
    """Compute a weighted confidence score and collect matched-feature labels.

    Returns ``(confidence, matched_features)`` where *confidence* ∈ [0, 1]
    and *matched_features* lists human-readable descriptions of what matched.
    """
    w = weights or DEFAULT_WEIGHTS
    meta: dict[str, Any] = frame.metadata or {}

    features: list[str] = []
    scores: dict[str, float] = {}

    # Clothing colour
    frame_colors: list[str] = meta.get("clothing_colors", [])
    sc = clothing_color_score(case.clothing, frame_colors)
    scores["clothing_color"] = sc
    if sc > 0:
        features.append(f"matched {', '.join(frame_colors)} clothing")

    # Accessories
    frame_acc: list[str] = meta.get("accessories", [])
    sc = accessory_score(case.clothing, frame_acc)
    scores["accessory"] = sc
    if sc > 0:
        features.append(f"matched {', '.join(frame_acc)}")

    # Location
    sc = location_relevance_score(case.last_known_location, camera_location)
    scores["location"] = sc
    if sc > 0.3:
        features.append(f"location aligns with last known area ({camera_location})")

    # Time
    frame_time = frame.timestamp
    sc = time_relevance_score(frame_time, reference_time)
    scores["time"] = sc
    if sc > 0.5:
        features.append("timestamp aligns with last known sighting")

    # Face match (placeholder)
    face_score: float | None = meta.get("face_match_score")
    if face_score is not None:
        scores["face_match"] = float(face_score)
        if face_score > 0.5:
            features.append(f"face match at {face_score:.0%} confidence")
    else:
        scores["face_match"] = 0.0

    # Text tags
    frame_tags: list[str] = meta.get("text_tags", [])
    sc = text_tag_match_score(case.description, case.clothing, frame_tags)
    scores["text_tags"] = sc
    if sc > 0:
        features.append(f"matched visual tags: {', '.join(frame_tags[:3])}")

    # Weighted sum
    confidence = sum(w.get(k, 0.0) * v for k, v in scores.items())
    confidence = round(min(1.0, max(0.0, confidence)), 3)

    return confidence, features


def build_explanation(confidence: float, features: list[str]) -> str:
    """Build a human-readable explanation string for a candidate sighting."""
    if not features:
        return "Low-confidence match; insufficient distinguishing features for a strong identification."
    first = features[0]
    capitalized_first = (first[0].upper() + first[1:]) if first else first
    rest = features[1:]
    return "; ".join([capitalized_first] + rest) + "."


# ── Backend interface ──────────────────────────────────────────────────────────

class ISearchBackend(ABC):
    """Abstract search backend.

    Implement this interface to plug in a real embedding-based system
    (CLIP + FAISS, for example).  The ``SearchService`` will call
    ``rank_frames`` and convert the results into ``Sighting`` objects.
    """

    @abstractmethod
    def rank_frames(
        self,
        case: Case,
        frames: list[CameraFrame],
        camera_map: dict[str, Camera],
        *,
        max_results: int = 10,
        min_confidence: float = 0.0,
    ) -> list[Sighting]:
        """Score *frames* against *case* and return ranked sightings."""


# ── Mock backend ───────────────────────────────────────────────────────────────

class MockSearchBackend(ISearchBackend):
    """Metadata-based mock matcher.

    Uses heuristic scoring on frame metadata fields such as
    ``clothing_colors``, ``accessories``, ``text_tags``, and
    ``face_match_score``.  Designed to be replaced by a real
    vision-model backend without changing any calling code.
    """

    def __init__(
        self,
        weights: dict[str, float] | None = None,
        reference_time: datetime | None = None,
    ) -> None:
        self.weights = weights or DEFAULT_WEIGHTS
        self.reference_time = reference_time

    def rank_frames(
        self,
        case: Case,
        frames: list[CameraFrame],
        camera_map: dict[str, Camera],
        *,
        max_results: int = 10,
        min_confidence: float = 0.0,
    ) -> list[Sighting]:
        candidates: list[Sighting] = []

        for frame in frames:
            camera = camera_map.get(frame.camera_id)
            location = camera.location if camera else "Unknown"

            confidence, features = compute_confidence(
                case, frame, location,
                reference_time=self.reference_time,
                weights=self.weights,
            )

            if confidence < min_confidence:
                continue

            explanation = build_explanation(confidence, features)

            candidates.append(Sighting(
                case_id=case.id,
                camera_id=frame.camera_id,
                frame_id=frame.id,
                timestamp=frame.timestamp,
                location=location,
                similarity_score=confidence,
                explanation=explanation,
            ))

        candidates.sort(key=lambda s: s.similarity_score, reverse=True)
        return candidates[:max_results]


# ── High-level service ─────────────────────────────────────────────────────────

class SearchService:
    """Orchestrator that connects a search backend to the data layer.

    Usage::

        service = SearchService(backend=MockSearchBackend())
        sightings = service.search(case, frames, camera_map)
    """

    def __init__(self, backend: ISearchBackend) -> None:
        self.backend = backend

    def search(
        self,
        case: Case,
        frames: list[CameraFrame],
        camera_map: dict[str, Camera],
        *,
        max_results: int = 10,
        min_confidence: float = 0.0,
    ) -> list[Sighting]:
        """Run the configured backend and return ranked sightings."""
        return self.backend.rank_frames(
            case, frames, camera_map,
            max_results=max_results,
            min_confidence=min_confidence,
        )
