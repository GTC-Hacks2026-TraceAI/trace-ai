"""Focused tests for Nemotron integration and fallbacks."""

from __future__ import annotations

from datetime import datetime, timezone

from app.config import get_nemotron_settings
from app.models import Camera, CameraFrame, Case, Sighting
from app.services.camera_recommendation import NextCameraRecommendationService
from app.services.nemotron_client import NemotronClient
from app.services.search import MockSearchBackend
from app.services.timeline import TimelineService


def _camera(cid: str = "cam-1", *, neighbors: list[str] | None = None) -> Camera:
    return Camera(
        id=cid,
        name=f"Camera {cid}",
        location="Building A",
        zone="central",
        neighbors=neighbors or [],
    )


def test_get_nemotron_settings_missing_vars(monkeypatch):
    monkeypatch.delenv("NEMOTRON_API_KEY", raising=False)
    monkeypatch.delenv("NEMOTRON_MODEL", raising=False)
    monkeypatch.delenv("NVIDIA_API_BASE", raising=False)

    settings = get_nemotron_settings()

    assert settings.enabled is False
    assert set(settings.missing_vars) == {
        "NEMOTRON_API_KEY",
        "NEMOTRON_MODEL",
        "NVIDIA_API_BASE",
    }


def test_get_nemotron_settings_enabled(monkeypatch):
    monkeypatch.setenv("NEMOTRON_API_KEY", "key")
    monkeypatch.setenv("NEMOTRON_MODEL", "model")
    monkeypatch.setenv("NVIDIA_API_BASE", "https://example.com/v1")

    settings = get_nemotron_settings()

    assert settings.enabled is True
    assert settings.missing_vars == ()


def test_nemotron_client_method_falls_back_when_request_fails(monkeypatch):
    client = NemotronClient(
        api_key="key",
        model="model",
        base_url="https://example.com/v1",
    )
    monkeypatch.setattr(
        client,
        "_chat_completion",
        lambda **kwargs: {"ok": False, "text": "", "error": "timeout"},
    )

    fallback = "Deterministic explanation."
    result = client.generate_sighting_explanation(
        fallback=fallback,
        location="Building A",
        confidence=0.8,
    )

    assert result == fallback


def test_search_backend_uses_nemotron_when_available():
    class StubNemotron:
        def generate_sighting_explanation(self, *, fallback: str, location: str, confidence: float) -> str:
            return f"Nemotron summary for {location} ({confidence:.2f})"

    case = Case(subject_name="Test Person", clothing="red jacket")
    frame = CameraFrame(
        id="frame-1",
        camera_id="cam-1",
        timestamp=datetime(2026, 3, 15, 8, 15, tzinfo=timezone.utc),
        metadata={"clothing_colors": ["red"]},
    )
    backend = MockSearchBackend(nemotron_client=StubNemotron())
    results = backend.rank_frames(case, [frame], {"cam-1": _camera("cam-1")})

    assert len(results) == 1
    assert results[0].explanation.startswith("Nemotron summary")


def test_timeline_and_recommendation_services_use_nemotron_when_available():
    class StubNemotron:
        def generate_timeline_summary(self, *, fallback: str, entry_count: int) -> str:
            return f"Nemotron timeline summary ({entry_count})."

        def generate_recommendation_reason(self, *, fallback: str) -> str:
            return "Nemotron recommendation reason."

    cam_a = _camera("cam-a", neighbors=["cam-b"])
    cam_b = _camera("cam-b")
    camera_map = {cam_a.id: cam_a, cam_b.id: cam_b}
    sightings = [
        Sighting(
            case_id="case-1",
            camera_id=cam_a.id,
            frame_id="frame-1",
            timestamp=datetime(2026, 3, 15, 8, 15, tzinfo=timezone.utc),
            location=cam_a.location,
            similarity_score=0.9,
            explanation="Deterministic explanation.",
        )
    ]

    timeline = TimelineService(nemotron_client=StubNemotron()).build(
        case_id="case-1",
        subject_name="Test Person",
        sightings=sightings,
        camera_map=camera_map,
    )
    recs = NextCameraRecommendationService(nemotron_client=StubNemotron()).recommend(
        sightings=sightings,
        camera_map=camera_map,
        cameras=[cam_a, cam_b],
        now=datetime(2026, 3, 15, 9, 15, tzinfo=timezone.utc),
    )

    assert timeline.summary == "Nemotron timeline summary (1)."
    assert recs[0].reason == "Nemotron recommendation reason."
