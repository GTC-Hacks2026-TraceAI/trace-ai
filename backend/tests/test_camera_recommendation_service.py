"""Tests for the NextCameraRecommendationService."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.models import Camera, NextCameraRecommendation, RetentionUrgency, Sighting
from app.services.camera_recommendation import (
    DEFAULT_RETENTION_HOURS,
    NextCameraRecommendationService,
    _infer_direction,
    _is_urgent,
    _urgency_level,
    _review_before_dt,
    _zone_index,
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


def _camera(
    cid: str,
    name: str,
    location: str = "Test Location",
    zone: str = "central",
    neighbors: list[str] | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
) -> Camera:
    return Camera(
        id=cid,
        name=name,
        location=location,
        zone=zone,
        neighbors=neighbors or [],
        latitude=latitude,
        longitude=longitude,
    )


# Small campus camera graph for testing
CAM_A = _camera("cam-A", "North Gate", "Building A", "north", ["cam-B", "cam-C"], 40.0, -74.0)
CAM_B = _camera("cam-B", "Parking", "Building A Lot", "north", ["cam-A", "cam-D"])
CAM_C = _camera("cam-C", "Hallway", "Building B", "central", ["cam-A", "cam-D", "cam-E"])
CAM_D = _camera("cam-D", "Cafeteria", "Building A GF", "central", ["cam-B", "cam-C"])
CAM_E = _camera("cam-E", "South Exit", "Building B Rear", "south", ["cam-C"])

ALL_CAMERAS = [CAM_A, CAM_B, CAM_C, CAM_D, CAM_E]
CAMERA_MAP = {c.id: c for c in ALL_CAMERAS}


# ── _zone_index ────────────────────────────────────────────────────────────────

class TestZoneIndex:
    def test_known_zones(self):
        assert _zone_index("north") == 0
        assert _zone_index("central") == 1
        assert _zone_index("south") == 2

    def test_case_insensitive(self):
        assert _zone_index("North") == 0
        assert _zone_index("SOUTH") == 2

    def test_unknown_zone_defaults_to_central(self):
        assert _zone_index("unknown") == 1


# ── _infer_direction ───────────────────────────────────────────────────────────

class TestInferDirection:
    def test_moving_south(self):
        sightings = [
            _sighting(camera_id="cam-A", ts=_ts(8, 0)),   # north
            _sighting(camera_id="cam-C", ts=_ts(8, 10)),  # central
        ]
        assert _infer_direction(sightings, CAMERA_MAP) == 1  # south

    def test_moving_north(self):
        sightings = [
            _sighting(camera_id="cam-E", ts=_ts(8, 0)),   # south
            _sighting(camera_id="cam-C", ts=_ts(8, 10)),  # central
        ]
        assert _infer_direction(sightings, CAMERA_MAP) == -1  # north

    def test_same_zone_returns_none(self):
        sightings = [
            _sighting(camera_id="cam-A", ts=_ts(8, 0)),   # north
            _sighting(camera_id="cam-B", ts=_ts(8, 10)),  # north
        ]
        assert _infer_direction(sightings, CAMERA_MAP) is None

    def test_single_sighting_returns_none(self):
        sightings = [_sighting(camera_id="cam-A")]
        assert _infer_direction(sightings, CAMERA_MAP) is None

    def test_empty_sightings_returns_none(self):
        assert _infer_direction([], CAMERA_MAP) is None

    def test_unknown_camera_returns_none(self):
        sightings = [
            _sighting(camera_id="cam-unknown", ts=_ts(8, 0)),
            _sighting(camera_id="cam-A", ts=_ts(8, 10)),
        ]
        assert _infer_direction(sightings, CAMERA_MAP) is None


# ── _is_urgent ─────────────────────────────────────────────────────────────────

class TestIsUrgent:
    def test_within_safe_window(self):
        now = _ts(8, 0)
        sighting_ts = now - timedelta(hours=10)
        assert _is_urgent(sighting_ts, now, 72.0) is False

    def test_at_urgency_threshold(self):
        now = _ts(8, 0)
        sighting_ts = now - timedelta(hours=54)  # 75% of 72h
        assert _is_urgent(sighting_ts, now, 72.0) is True

    def test_past_urgency_threshold(self):
        now = _ts(8, 0)
        sighting_ts = now - timedelta(hours=60)
        assert _is_urgent(sighting_ts, now, 72.0) is True

    def test_custom_retention_hours(self):
        now = _ts(8, 0)
        sighting_ts = now - timedelta(hours=20)
        # 20h elapsed, 75% of 24h = 18h → urgent
        assert _is_urgent(sighting_ts, now, 24.0) is True


# ── NextCameraRecommendationService ───────────────────────────────────────────

class TestNextCameraRecommendationService:
    def test_default_retention_hours(self):
        svc = NextCameraRecommendationService()
        assert svc.retention_hours == DEFAULT_RETENTION_HOURS

    def test_custom_retention_hours(self):
        svc = NextCameraRecommendationService(retention_hours=24.0)
        assert svc.retention_hours == 24.0

    # ── Cold start ─────────────────────────────────────────────────────

    def test_cold_start_returns_first_three_cameras(self):
        svc = NextCameraRecommendationService()
        recs = svc.recommend([], CAMERA_MAP, ALL_CAMERAS, now=_ts(10))
        assert len(recs) == 3
        assert recs[0].camera_id == "cam-A"
        assert recs[1].camera_id == "cam-B"
        assert recs[2].camera_id == "cam-C"

    def test_cold_start_priorities_ascending(self):
        svc = NextCameraRecommendationService()
        recs = svc.recommend([], CAMERA_MAP, ALL_CAMERAS, now=_ts(10))
        priorities = [r.priority for r in recs]
        assert priorities == [1, 2, 3]

    def test_cold_start_reason(self):
        svc = NextCameraRecommendationService()
        recs = svc.recommend([], CAMERA_MAP, ALL_CAMERAS, now=_ts(10))
        for rec in recs:
            assert "no sightings" in rec.reason.lower()

    def test_cold_start_includes_coordinates(self):
        svc = NextCameraRecommendationService()
        recs = svc.recommend([], CAMERA_MAP, ALL_CAMERAS, now=_ts(10))
        # cam-A has coordinates
        assert recs[0].latitude == 40.0
        assert recs[0].longitude == -74.0
        # cam-B has no coordinates
        assert recs[1].latitude is None
        assert recs[1].longitude is None

    def test_cold_start_fewer_than_three_cameras(self):
        svc = NextCameraRecommendationService()
        recs = svc.recommend([], CAMERA_MAP, ALL_CAMERAS[:2], now=_ts(10))
        assert len(recs) == 2

    # ── After sightings ───────────────────────────────────────────────

    def test_recommends_adjacent_unseen_cameras(self):
        svc = NextCameraRecommendationService()
        sightings = [_sighting(camera_id="cam-A", ts=_ts(8, 0))]
        recs = svc.recommend(sightings, CAMERA_MAP, ALL_CAMERAS, now=_ts(8, 30))
        rec_ids = {r.camera_id for r in recs}
        # cam-A neighbours are cam-B, cam-C; neither has been seen
        assert "cam-B" in rec_ids
        assert "cam-C" in rec_ids
        # cam-A itself should NOT be recommended (already seen)
        assert "cam-A" not in rec_ids

    def test_does_not_recommend_already_seen_cameras(self):
        svc = NextCameraRecommendationService()
        sightings = [
            _sighting(camera_id="cam-A", ts=_ts(8, 0)),
            _sighting(camera_id="cam-B", ts=_ts(8, 10)),
        ]
        recs = svc.recommend(sightings, CAMERA_MAP, ALL_CAMERAS, now=_ts(8, 30))
        rec_ids = {r.camera_id for r in recs}
        assert "cam-A" not in rec_ids
        assert "cam-B" not in rec_ids

    def test_recommendations_have_required_fields(self):
        svc = NextCameraRecommendationService()
        sightings = [_sighting(camera_id="cam-A", ts=_ts(8, 0))]
        recs = svc.recommend(sightings, CAMERA_MAP, ALL_CAMERAS, now=_ts(8, 30))
        for rec in recs:
            assert isinstance(rec, NextCameraRecommendation)
            assert rec.camera_id
            assert rec.camera_name
            assert rec.location
            assert rec.zone
            assert rec.priority >= 1
            assert rec.reason

    def test_priorities_are_sequential(self):
        svc = NextCameraRecommendationService()
        sightings = [_sighting(camera_id="cam-C", ts=_ts(8, 0))]
        recs = svc.recommend(sightings, CAMERA_MAP, ALL_CAMERAS, now=_ts(8, 30))
        priorities = [r.priority for r in recs]
        assert priorities == list(range(1, len(recs) + 1))

    def test_reason_mentions_adjacent_camera(self):
        svc = NextCameraRecommendationService()
        sightings = [_sighting(camera_id="cam-A", ts=_ts(8, 0))]
        recs = svc.recommend(sightings, CAMERA_MAP, ALL_CAMERAS, now=_ts(8, 30))
        for rec in recs:
            assert "North Gate" in rec.reason  # cam-A name

    def test_confidence_is_present(self):
        svc = NextCameraRecommendationService()
        sightings = [_sighting(camera_id="cam-A", score=0.9, ts=_ts(8, 0))]
        recs = svc.recommend(sightings, CAMERA_MAP, ALL_CAMERAS, now=_ts(8, 30))
        for rec in recs:
            assert rec.confidence is not None
            assert 0.0 <= rec.confidence <= 1.0

    def test_direction_boost_south(self):
        """When subject moves north→central, cameras further south score higher."""
        svc = NextCameraRecommendationService()
        sightings = [
            _sighting(camera_id="cam-A", ts=_ts(8, 0)),   # north
            _sighting(camera_id="cam-C", ts=_ts(8, 10)),  # central → direction = south
        ]
        recs = svc.recommend(sightings, CAMERA_MAP, ALL_CAMERAS, now=_ts(8, 30))
        rec_ids = [r.camera_id for r in recs]
        # cam-E (south, neighbour of cam-C) should be present and
        # should rank higher than cam-D (central, neighbour of cam-C/cam-B)
        if "cam-E" in rec_ids and "cam-D" in rec_ids:
            assert rec_ids.index("cam-E") < rec_ids.index("cam-D")

    def test_direction_boost_north(self):
        """When subject moves south→central, cameras further north score higher."""
        svc = NextCameraRecommendationService()
        sightings = [
            _sighting(camera_id="cam-E", ts=_ts(8, 0)),   # south
            _sighting(camera_id="cam-C", ts=_ts(8, 10)),  # central → direction = north
        ]
        recs = svc.recommend(sightings, CAMERA_MAP, ALL_CAMERAS, now=_ts(8, 30))
        rec_ids = [r.camera_id for r in recs]
        # cam-A (north) should be recommended via cam-C's neighbours
        assert "cam-A" in rec_ids

    def test_unknown_camera_in_sighting_is_skipped(self):
        svc = NextCameraRecommendationService()
        sightings = [_sighting(camera_id="cam-unknown", ts=_ts(8, 0))]
        recs = svc.recommend(sightings, CAMERA_MAP, ALL_CAMERAS, now=_ts(8, 30))
        assert recs == []

    # ── Urgency ────────────────────────────────────────────────────────

    def test_urgency_in_reason_when_near_retention(self):
        svc = NextCameraRecommendationService(retention_hours=24.0)
        sighting_ts = _ts(8, 0)
        now = sighting_ts + timedelta(hours=20)  # > 75% of 24h
        sightings = [_sighting(camera_id="cam-A", ts=sighting_ts)]
        recs = svc.recommend(sightings, CAMERA_MAP, ALL_CAMERAS, now=now)
        assert any("URGENT" in r.reason for r in recs)

    def test_no_urgency_when_within_safe_window(self):
        svc = NextCameraRecommendationService(retention_hours=72.0)
        sightings = [_sighting(camera_id="cam-A", ts=_ts(8, 0))]
        now = _ts(8, 0) + timedelta(hours=2)
        recs = svc.recommend(sightings, CAMERA_MAP, ALL_CAMERAS, now=now)
        assert not any("URGENT" in r.reason for r in recs)

    def test_reason_mentions_direction(self):
        svc = NextCameraRecommendationService()
        sightings = [
            _sighting(camera_id="cam-A", ts=_ts(8, 0)),   # north
            _sighting(camera_id="cam-C", ts=_ts(8, 10)),  # central
        ]
        recs = svc.recommend(sightings, CAMERA_MAP, ALL_CAMERAS, now=_ts(8, 30))
        # At least one rec in the direction should mention it
        direction_reasons = [r for r in recs if "heading" in r.reason.lower()]
        assert len(direction_reasons) >= 1


# ── _urgency_level ─────────────────────────────────────────────────────────────

class TestUrgencyLevel:
    def test_low_urgency_below_50_percent(self):
        now = _ts(8, 0)
        sighting_ts = now - timedelta(hours=10)  # 10/72 ≈ 14 % elapsed
        assert _urgency_level(sighting_ts, now, 72.0) == RetentionUrgency.low

    def test_medium_urgency_at_50_percent(self):
        now = _ts(8, 0)
        sighting_ts = now - timedelta(hours=36)  # 50 % of 72h
        assert _urgency_level(sighting_ts, now, 72.0) == RetentionUrgency.medium

    def test_medium_urgency_between_50_and_75_percent(self):
        now = _ts(8, 0)
        sighting_ts = now - timedelta(hours=48)  # 66 % of 72h
        assert _urgency_level(sighting_ts, now, 72.0) == RetentionUrgency.medium

    def test_high_urgency_at_75_percent(self):
        now = _ts(8, 0)
        sighting_ts = now - timedelta(hours=54)  # 75 % of 72h
        assert _urgency_level(sighting_ts, now, 72.0) == RetentionUrgency.high

    def test_high_urgency_past_75_percent(self):
        now = _ts(8, 0)
        sighting_ts = now - timedelta(hours=60)  # 83 % of 72h
        assert _urgency_level(sighting_ts, now, 72.0) == RetentionUrgency.high

    def test_high_urgency_custom_retention(self):
        now = _ts(8, 0)
        sighting_ts = now - timedelta(hours=20)  # 83 % of 24h
        assert _urgency_level(sighting_ts, now, 24.0) == RetentionUrgency.high

    def test_low_urgency_short_window_early(self):
        now = _ts(8, 0)
        sighting_ts = now - timedelta(hours=1)  # 8 % of 12h
        assert _urgency_level(sighting_ts, now, 12.0) == RetentionUrgency.low


# ── _review_before_dt ──────────────────────────────────────────────────────────

class TestReviewBeforeDt:
    def test_adds_retention_hours_to_timestamp(self):
        sighting_ts = _ts(8, 0)
        result = _review_before_dt(sighting_ts, 24.0)
        assert result == sighting_ts + timedelta(hours=24)

    def test_short_retention(self):
        sighting_ts = _ts(10, 30)
        result = _review_before_dt(sighting_ts, 12.0)
        assert result == sighting_ts + timedelta(hours=12)


# ── Retention fields in recommendations ────────────────────────────────────────

class TestRetentionFieldsInRecommendations:
    def test_recommendations_have_urgency_level(self):
        svc = NextCameraRecommendationService()
        sightings = [_sighting(camera_id="cam-A", ts=_ts(8, 0))]
        recs = svc.recommend(sightings, CAMERA_MAP, ALL_CAMERAS, now=_ts(8, 30))
        for rec in recs:
            assert rec.urgency_level is not None
            assert isinstance(rec.urgency_level, RetentionUrgency)

    def test_recommendations_have_review_before(self):
        svc = NextCameraRecommendationService()
        sightings = [_sighting(camera_id="cam-A", ts=_ts(8, 0))]
        recs = svc.recommend(sightings, CAMERA_MAP, ALL_CAMERAS, now=_ts(8, 30))
        for rec in recs:
            assert rec.review_before is not None

    def test_review_before_equals_sighting_plus_retention(self):
        svc = NextCameraRecommendationService(retention_hours=48.0)
        sighting_ts = _ts(8, 0)
        sightings = [_sighting(camera_id="cam-A", ts=sighting_ts)]
        recs = svc.recommend(sightings, CAMERA_MAP, ALL_CAMERAS, now=_ts(8, 30))
        expected = sighting_ts + timedelta(hours=48)
        for rec in recs:
            assert rec.review_before == expected

    def test_cold_start_urgency_level_is_none(self):
        svc = NextCameraRecommendationService()
        recs = svc.recommend([], CAMERA_MAP, ALL_CAMERAS, now=_ts(10))
        for rec in recs:
            assert rec.urgency_level is None

    def test_cold_start_review_before_is_none(self):
        svc = NextCameraRecommendationService()
        recs = svc.recommend([], CAMERA_MAP, ALL_CAMERAS, now=_ts(10))
        for rec in recs:
            assert rec.review_before is None

    def test_high_urgency_level_when_near_retention(self):
        svc = NextCameraRecommendationService(retention_hours=24.0)
        sighting_ts = _ts(8, 0)
        now = sighting_ts + timedelta(hours=20)  # 83 % of 24h
        sightings = [_sighting(camera_id="cam-A", ts=sighting_ts)]
        recs = svc.recommend(sightings, CAMERA_MAP, ALL_CAMERAS, now=now)
        assert all(r.urgency_level == RetentionUrgency.high for r in recs)

    def test_low_urgency_level_when_early(self):
        svc = NextCameraRecommendationService(retention_hours=72.0)
        sightings = [_sighting(camera_id="cam-A", ts=_ts(8, 0))]
        now = _ts(8, 0) + timedelta(hours=2)  # 3 % of 72h
        recs = svc.recommend(sightings, CAMERA_MAP, ALL_CAMERAS, now=now)
        assert all(r.urgency_level == RetentionUrgency.low for r in recs)

    def test_medium_urgency_reason_has_caution(self):
        svc = NextCameraRecommendationService(retention_hours=72.0)
        sighting_ts = _ts(8, 0)
        now = sighting_ts + timedelta(hours=48)  # 66 % of 72h → medium
        sightings = [_sighting(camera_id="cam-A", ts=sighting_ts)]
        recs = svc.recommend(sightings, CAMERA_MAP, ALL_CAMERAS, now=now)
        assert any("CAUTION" in r.reason for r in recs)

    def test_per_camera_retention_hours_used(self):
        """Camera-specific retention_hours overrides the service default."""
        short_cam = Camera(
            id="cam-X", name="Short Retention Cam", location="Zone X",
            zone="north", neighbors=["cam-Y"], retention_hours=6.0,
        )
        neighbour = Camera(
            id="cam-Y", name="Neighbour Cam", location="Zone Y",
            zone="north", neighbors=["cam-X"],
        )
        local_map = {"cam-X": short_cam, "cam-Y": neighbour}
        local_cams = [short_cam, neighbour]

        svc = NextCameraRecommendationService(retention_hours=72.0)
        sighting_ts = _ts(8, 0)
        # 5h elapsed: 83 % of cam-X's 6h window → high; only 7 % of 72h → low
        now = sighting_ts + timedelta(hours=5)
        sightings = [_sighting(camera_id="cam-X", ts=sighting_ts)]
        recs = svc.recommend(sightings, local_map, local_cams, now=now)
        assert len(recs) == 1
        # Must use cam-X's 6h retention, not the 72h default
        assert recs[0].urgency_level == RetentionUrgency.high
        assert recs[0].review_before == sighting_ts + timedelta(hours=6)
