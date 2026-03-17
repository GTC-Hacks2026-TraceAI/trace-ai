"""Tests for the search service (scoring helpers, mock backend, and service)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.models import Camera, CameraFrame, Case, Sighting
from app.services.search import (
    DEFAULT_WEIGHTS,
    ISearchBackend,
    MockSearchBackend,
    SearchService,
    accessory_score,
    build_explanation,
    clothing_color_score,
    compute_confidence,
    location_relevance_score,
    text_tag_match_score,
    time_relevance_score,
)


# ── Test fixtures ──────────────────────────────────────────────────────────────

def _case(**overrides) -> Case:
    defaults = dict(
        subject_name="Jane Doe",
        description="Female, approx 25, brown hair",
        last_known_location="Building A lobby",
        clothing="Red jacket, blue jeans, black backpack",
    )
    defaults.update(overrides)
    return Case(**defaults)


def _frame(
    fid: str = "frame-001",
    cid: str = "cam-001",
    ts: datetime | None = None,
    **meta_overrides,
) -> CameraFrame:
    meta = {
        "resolution": "1080p",
        "clothing_colors": ["red", "blue"],
        "accessories": ["backpack"],
        "text_tags": ["red hoodie", "blue jeans", "black backpack"],
        "face_match_score": None,
    }
    meta.update(meta_overrides)
    return CameraFrame(
        id=fid,
        camera_id=cid,
        timestamp=ts or datetime(2026, 3, 15, 8, 15, tzinfo=timezone.utc),
        metadata=meta,
    )


def _camera(cid: str = "cam-001") -> Camera:
    return Camera(id=cid, name="Main Entrance", location="Building A - Front Gate", zone="north")


REF_TIME = datetime(2026, 3, 15, 9, 0, 0, tzinfo=timezone.utc)


# ── clothing_color_score ───────────────────────────────────────────────────────

class TestClothingColorScore:
    def test_full_match(self):
        assert clothing_color_score("Red jacket, blue jeans", ["red", "blue"]) == 1.0

    def test_partial_match(self):
        score = clothing_color_score("Red jacket, blue jeans", ["red", "green"])
        assert 0.0 < score < 1.0

    def test_no_match(self):
        assert clothing_color_score("Red jacket", ["green", "yellow"]) == 0.0

    def test_no_clothing(self):
        assert clothing_color_score(None, ["red"]) == 0.0

    def test_no_frame_colors(self):
        assert clothing_color_score("Red jacket", []) == 0.0

    def test_no_color_tokens_in_clothing(self):
        assert clothing_color_score("tall person, jacket, jeans", ["red"]) == 0.0


# ── accessory_score ────────────────────────────────────────────────────────────

class TestAccessoryScore:
    def test_full_match(self):
        assert accessory_score("black backpack", ["backpack"]) == 1.0

    def test_partial_match(self):
        score = accessory_score("backpack and hat", ["backpack", "glasses"])
        assert 0.0 < score < 1.0

    def test_no_match(self):
        assert accessory_score("backpack", ["sunglasses"]) == 0.0

    def test_no_clothing(self):
        assert accessory_score(None, ["backpack"]) == 0.0

    def test_no_frame_accessories(self):
        assert accessory_score("backpack", []) == 0.0


# ── location_relevance_score ───────────────────────────────────────────────────

class TestLocationRelevanceScore:
    def test_overlap(self):
        score = location_relevance_score("Building A lobby", "Building A - Front Gate")
        assert score > 0.3

    def test_no_overlap(self):
        score = location_relevance_score("Library North", "Parking Lot B")
        assert score == pytest.approx(0.1)

    def test_no_case_location(self):
        score = location_relevance_score(None, "Building A")
        assert score == pytest.approx(0.3)


# ── time_relevance_score ──────────────────────────────────────────────────────

class TestTimeRelevanceScore:
    def test_within_one_hour(self):
        frame_time = datetime(2026, 3, 15, 8, 30, tzinfo=timezone.utc)
        score = time_relevance_score(frame_time, REF_TIME)
        assert score == 1.0

    def test_several_hours_away(self):
        frame_time = datetime(2026, 3, 15, 2, 0, tzinfo=timezone.utc)
        score = time_relevance_score(frame_time, REF_TIME)
        assert 0.1 < score < 1.0

    def test_over_24h_away(self):
        frame_time = datetime(2026, 3, 13, 8, 0, tzinfo=timezone.utc)
        score = time_relevance_score(frame_time, REF_TIME)
        assert score == pytest.approx(0.1)


# ── text_tag_match_score ───────────────────────────────────────────────────────

class TestTextTagMatchScore:
    def test_full_match(self):
        score = text_tag_match_score("red hoodie", "blue jeans", ["red hoodie", "blue jeans"])
        assert score == 1.0

    def test_partial_match(self):
        score = text_tag_match_score("red hoodie", None, ["red hoodie", "green shorts"])
        assert 0.0 < score < 1.0

    def test_no_match(self):
        score = text_tag_match_score("tall person", None, ["blue shirt"])
        assert score == 0.0

    def test_no_tags(self):
        assert text_tag_match_score("red hoodie", None, []) == 0.0

    def test_no_description(self):
        assert text_tag_match_score(None, None, ["red hoodie"]) == 0.0


# ── compute_confidence ─────────────────────────────────────────────────────────

class TestComputeConfidence:
    def test_returns_score_and_features(self):
        case = _case()
        frame = _frame()
        conf, features = compute_confidence(case, frame, "Building A", reference_time=REF_TIME)
        assert 0.0 <= conf <= 1.0
        assert isinstance(features, list)

    def test_high_match_produces_features(self):
        case = _case(clothing="Red jacket, black backpack")
        frame = _frame(
            clothing_colors=["red", "black"],
            accessories=["backpack"],
            text_tags=["red jacket", "black backpack"],
            face_match_score=0.9,
        )
        conf, features = compute_confidence(
            case, frame, "Building A lobby",
            reference_time=REF_TIME,
        )
        assert conf > 0.5
        assert len(features) > 0

    def test_no_metadata_gives_low_score(self):
        case = _case()
        frame = CameraFrame(
            id="frame-bare",
            camera_id="cam-001",
            timestamp=datetime(2026, 3, 15, 8, 15, tzinfo=timezone.utc),
            metadata=None,
        )
        conf, _ = compute_confidence(case, frame, "Unknown", reference_time=REF_TIME)
        # Only time and location contribute; score should be modest
        assert conf < 0.5

    def test_face_match_score_boost(self):
        case = _case()
        frame_no_face = _frame(face_match_score=None)
        frame_face = _frame(face_match_score=0.95)
        c1, _ = compute_confidence(case, frame_no_face, "A", reference_time=REF_TIME)
        c2, _ = compute_confidence(case, frame_face, "A", reference_time=REF_TIME)
        assert c2 > c1


# ── build_explanation ──────────────────────────────────────────────────────────

class TestBuildExplanation:
    def test_with_features(self):
        result = build_explanation(0.82, ["matched red, blue clothing", "timestamp aligns with last known sighting"])
        assert "Matched red, blue clothing" in result
        assert "timestamp aligns with last known sighting" in result
        assert result.endswith(".")

    def test_no_features(self):
        result = build_explanation(0.1, [])
        assert "low-confidence" in result.lower()
        assert "insufficient" in result.lower()


# ── MockSearchBackend ──────────────────────────────────────────────────────────

class TestMockSearchBackend:
    def _camera_map(self) -> dict[str, Camera]:
        return {
            "cam-001": _camera("cam-001"),
            "cam-002": Camera(id="cam-002", name="Parking Lot", location="Building A West", zone="north"),
        }

    def _frames(self) -> list[CameraFrame]:
        return [
            _frame("frame-001", "cam-001"),
            _frame(
                "frame-002", "cam-002",
                ts=datetime(2026, 3, 15, 8, 20, tzinfo=timezone.utc),
                clothing_colors=["green"],
                accessories=[],
                text_tags=["green shirt"],
                face_match_score=None,
            ),
        ]

    def test_returns_sightings_sorted_descending(self):
        backend = MockSearchBackend(reference_time=REF_TIME)
        case = _case()
        results = backend.rank_frames(case, self._frames(), self._camera_map())
        scores = [s.similarity_score for s in results]
        assert scores == sorted(scores, reverse=True)

    def test_respects_max_results(self):
        backend = MockSearchBackend(reference_time=REF_TIME)
        case = _case()
        results = backend.rank_frames(case, self._frames(), self._camera_map(), max_results=1)
        assert len(results) == 1

    def test_respects_min_confidence(self):
        backend = MockSearchBackend(reference_time=REF_TIME)
        case = _case()
        results = backend.rank_frames(
            case, self._frames(), self._camera_map(), min_confidence=0.99,
        )
        for s in results:
            assert s.similarity_score >= 0.99

    def test_result_fields(self):
        backend = MockSearchBackend(reference_time=REF_TIME)
        case = _case()
        results = backend.rank_frames(case, self._frames(), self._camera_map())
        for s in results:
            assert isinstance(s, Sighting)
            assert s.case_id == case.id
            assert s.camera_id in ("cam-001", "cam-002")
            assert s.explanation
            assert 0.0 <= s.similarity_score <= 1.0


# ── SearchService ──────────────────────────────────────────────────────────────

class TestSearchService:
    def test_delegates_to_backend(self):
        backend = MockSearchBackend(reference_time=REF_TIME)
        service = SearchService(backend=backend)
        case = _case()
        camera_map = {"cam-001": _camera()}
        frames = [_frame()]
        results = service.search(case, frames, camera_map)
        assert len(results) >= 1
        assert all(isinstance(s, Sighting) for s in results)

    def test_custom_backend_integration(self):
        """Verify a custom ISearchBackend can be plugged in."""

        class StubBackend(ISearchBackend):
            def rank_frames(self, case, frames, camera_map, *, max_results=10, min_confidence=0.0):
                return [
                    Sighting(
                        case_id=case.id,
                        camera_id="cam-stub",
                        frame_id="frame-stub",
                        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
                        location="Stub",
                        similarity_score=0.99,
                        explanation="stub match",
                    )
                ]

        service = SearchService(backend=StubBackend())
        case = _case()
        results = service.search(case, [], {})
        assert len(results) == 1
        assert results[0].camera_id == "cam-stub"
