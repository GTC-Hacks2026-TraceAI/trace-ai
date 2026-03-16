"""Tests for the TimelineService."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.models import Camera, Sighting, Timeline, TimelineEntry
from app.services.timeline import (
    DEFAULT_MIN_CONFIDENCE,
    TimelineService,
    _build_summary,
    _confidence,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _ts(hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 3, 15, hour, minute, tzinfo=timezone.utc)


def _sighting(
    camera_id: str = "cam-001",
    frame_id: str = "frame-001",
    score: float = 0.8,
    location: str = "Building A",
    ts: datetime | None = None,
    explanation: str = "Test match",
) -> Sighting:
    return Sighting(
        case_id="case-001",
        camera_id=camera_id,
        frame_id=frame_id,
        timestamp=ts or _ts(8, 15),
        location=location,
        similarity_score=score,
        explanation=explanation,
    )


def _camera(cid: str, name: str, location: str = "Test Location") -> Camera:
    return Camera(id=cid, name=name, location=location, zone="test")


CAMERA_MAP = {
    "cam-001": _camera("cam-001", "Main Entrance", "Building A - Front Gate"),
    "cam-002": _camera("cam-002", "Parking Lot", "Building A - West Lot"),
    "cam-003": _camera("cam-003", "Library", "Building C - Main Door"),
}


# ── _confidence helper ─────────────────────────────────────────────────────────

class TestConfidenceHelper:
    def test_uses_similarity_score_from_sighting(self):
        s = _sighting(score=0.75)
        assert _confidence(s) == pytest.approx(0.75)


# ── _build_summary ─────────────────────────────────────────────────────────────

class TestBuildSummary:
    def _entry(self, camera_name: str, location: str, hour: int, minute: int = 0) -> TimelineEntry:
        return TimelineEntry(
            timestamp=_ts(hour, minute),
            camera_id="cam-001",
            camera_name=camera_name,
            location=location,
            frame_id="frame-001",
            similarity_score=0.8,
            explanation="Test match.",
        )

    def test_empty_list_returns_empty_string(self):
        assert _build_summary([]) == ""

    def test_single_entry_mentions_location_and_time(self):
        entry = self._entry("Main Entrance", "Building A - Front Gate", 8, 15)
        result = _build_summary([entry])
        assert "Main Entrance" in result
        assert "Building A - Front Gate" in result
        assert "8:15" in result

    def test_multiple_entries_mentions_from_and_to(self):
        entries = [
            self._entry("Student Union", "Student Union - 1st Floor", 15, 12),
            self._entry("East Garage", "East Garage - Level 1", 15, 21),
        ]
        result = _build_summary(entries)
        assert "Student Union" in result
        assert "East Garage" in result
        assert "3:12" in result
        assert "3:21" in result

    def test_same_location_multiple_entries(self):
        entries = [
            self._entry("Main Entrance", "Building A", 8, 0),
            self._entry("Main Entrance", "Building A", 8, 10),
        ]
        result = _build_summary(entries)
        assert "multiple times" in result
        assert "Main Entrance" in result

    def test_summary_ends_with_period(self):
        entry = self._entry("Lobby", "Ground Floor", 9, 0)
        result = _build_summary([entry])
        assert result.endswith(".")


# ── TimelineService ────────────────────────────────────────────────────────────

class TestTimelineService:
    def test_default_min_confidence(self):
        svc = TimelineService()
        assert svc.min_confidence == DEFAULT_MIN_CONFIDENCE

    def test_custom_min_confidence(self):
        svc = TimelineService(min_confidence=0.5)
        assert svc.min_confidence == 0.5

    def test_returns_timeline_model(self):
        svc = TimelineService()
        result = svc.build("case-001", "Jane Doe", [], CAMERA_MAP)
        assert isinstance(result, Timeline)
        assert result.case_id == "case-001"
        assert result.subject_name == "Jane Doe"

    def test_empty_sightings_gives_empty_entries(self):
        svc = TimelineService()
        result = svc.build("case-001", "Jane Doe", [], CAMERA_MAP)
        assert result.entries == []
        assert result.summary == ""

    def test_filters_low_confidence_sightings(self):
        svc = TimelineService(min_confidence=0.5)
        sightings = [
            _sighting(score=0.8, ts=_ts(8, 0)),
            _sighting(score=0.3, ts=_ts(8, 10)),   # below threshold
            _sighting(score=0.1, ts=_ts(8, 20)),   # below threshold
        ]
        result = svc.build("case-001", "Jane Doe", sightings, CAMERA_MAP)
        assert len(result.entries) == 1
        assert result.entries[0].similarity_score == pytest.approx(0.8)

    def test_sightings_at_threshold_are_included(self):
        svc = TimelineService(min_confidence=0.5)
        sightings = [_sighting(score=0.5)]
        result = svc.build("case-001", "Jane Doe", sightings, CAMERA_MAP)
        assert len(result.entries) == 1

    def test_entries_sorted_by_timestamp(self):
        svc = TimelineService(min_confidence=0.0)
        sightings = [
            _sighting(frame_id="f3", ts=_ts(9, 0), score=0.9),
            _sighting(frame_id="f1", ts=_ts(8, 0), score=0.7),
            _sighting(frame_id="f2", ts=_ts(8, 30), score=0.8),
        ]
        result = svc.build("case-001", "Jane Doe", sightings, CAMERA_MAP)
        timestamps = [e.timestamp for e in result.entries]
        assert timestamps == sorted(timestamps)

    def test_entry_fields_are_populated(self):
        svc = TimelineService(min_confidence=0.0)
        sightings = [_sighting(
            camera_id="cam-001",
            frame_id="frame-001",
            score=0.75,
            location="Building A - Front Gate",
            explanation="Face match 75%",
        )]
        result = svc.build("case-001", "Jane Doe", sightings, CAMERA_MAP)
        entry = result.entries[0]
        assert entry.camera_id == "cam-001"
        assert entry.camera_name == "Main Entrance"
        assert entry.location == "Building A - Front Gate"
        assert entry.frame_id == "frame-001"
        assert entry.similarity_score == pytest.approx(0.75)
        assert entry.explanation == "Face match 75%"

    def test_unknown_camera_id_gracefully_handled(self):
        svc = TimelineService(min_confidence=0.0)
        sightings = [_sighting(camera_id="cam-unknown", score=0.6)]
        result = svc.build("case-001", "Jane Doe", sightings, CAMERA_MAP)
        assert len(result.entries) == 1
        assert result.entries[0].camera_name == "Unknown"

    def test_summary_is_generated_for_multiple_entries(self):
        svc = TimelineService(min_confidence=0.0)
        sightings = [
            _sighting(camera_id="cam-001", ts=_ts(8, 15), location="Building A - Front Gate"),
            _sighting(camera_id="cam-003", ts=_ts(9, 1), location="Building C - Main Door"),
        ]
        result = svc.build("case-001", "Jane Doe", sightings, CAMERA_MAP)
        assert result.summary
        assert "Main Entrance" in result.summary
        assert "Library" in result.summary

    def test_summary_present_in_timeline(self):
        svc = TimelineService(min_confidence=0.0)
        sightings = [_sighting(score=0.9)]
        result = svc.build("case-001", "Jane Doe", sightings, CAMERA_MAP)
        assert isinstance(result.summary, str)
        assert len(result.summary) > 0

    def test_all_low_confidence_gives_empty_timeline(self):
        svc = TimelineService(min_confidence=0.8)
        sightings = [
            _sighting(score=0.5),
            _sighting(score=0.6),
        ]
        result = svc.build("case-001", "Jane Doe", sightings, CAMERA_MAP)
        assert result.entries == []
        assert result.summary == ""
