"""Tests for the repository layer (in-memory and JSON-backed implementations)."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from app.models import Camera, CameraFrame, Case, Sighting
from app.repositories import (
    JsonCameraRepository,
    JsonCaseRepository,
    JsonFrameRepository,
    MemoryCameraRepository,
    MemoryCaseRepository,
    MemoryFrameRepository,
)
from datetime import datetime, timezone


# ── helpers ────────────────────────────────────────────────────────────────────

def _case(name: str = "Jane Doe") -> Case:
    return Case(subject_name=name, description="test", clothing="red jacket")


def _sighting(case_id: str) -> Sighting:
    return Sighting(
        case_id=case_id,
        camera_id="cam-001",
        frame_id="frame-001",
        timestamp=datetime(2026, 3, 15, 8, 15, tzinfo=timezone.utc),
        location="Building A",
        similarity_score=0.85,
        explanation="visual match",
    )


def _frame(fid: str = "frame-001", cid: str = "cam-001") -> CameraFrame:
    return CameraFrame(
        id=fid,
        camera_id=cid,
        timestamp=datetime(2026, 3, 15, 8, 15, tzinfo=timezone.utc),
    )


def _camera(cid: str = "cam-001") -> Camera:
    return Camera(id=cid, name="Main Entrance", location="Building A", zone="north")


# ── MemoryCaseRepository ───────────────────────────────────────────────────────

class TestMemoryCaseRepository:
    def test_save_and_get(self):
        repo = MemoryCaseRepository()
        case = _case()
        saved = repo.save(case)
        assert saved.id == case.id
        assert repo.get(case.id) is not None
        assert repo.get(case.id).subject_name == "Jane Doe"

    def test_get_missing_returns_none(self):
        repo = MemoryCaseRepository()
        assert repo.get("nonexistent") is None

    def test_list_all(self):
        repo = MemoryCaseRepository()
        repo.save(_case("Alice"))
        repo.save(_case("Bob"))
        assert len(repo.list_all()) == 2

    def test_list_all_empty(self):
        repo = MemoryCaseRepository()
        assert repo.list_all() == []

    def test_save_sightings_and_get(self):
        repo = MemoryCaseRepository()
        case = _case()
        repo.save(case)
        sightings = [_sighting(case.id)]
        repo.save_sightings(case.id, sightings)
        result = repo.get_sightings(case.id)
        assert len(result) == 1
        assert result[0].similarity_score == pytest.approx(0.85)

    def test_get_sightings_empty(self):
        repo = MemoryCaseRepository()
        assert repo.get_sightings("unknown") == []

    def test_save_sightings_overwrites(self):
        repo = MemoryCaseRepository()
        case = _case()
        repo.save(case)
        repo.save_sightings(case.id, [_sighting(case.id)])
        # Overwrite with a different sighting
        new_sighting = Sighting(
            case_id=case.id,
            camera_id="cam-002",
            frame_id="frame-002",
            timestamp=datetime(2026, 3, 15, 9, 0, tzinfo=timezone.utc),
            location="Parking Lot",
            similarity_score=0.90,
            explanation="updated",
        )
        repo.save_sightings(case.id, [new_sighting])
        result = repo.get_sightings(case.id)
        assert len(result) == 1
        assert result[0].camera_id == "cam-002"

    def test_clear(self):
        repo = MemoryCaseRepository()
        case = _case()
        repo.save(case)
        repo.save_sightings(case.id, [_sighting(case.id)])
        repo.clear()
        assert repo.list_all() == []
        assert repo.get_sightings(case.id) == []


# ── MemoryFrameRepository ──────────────────────────────────────────────────────

class TestMemoryFrameRepository:
    def test_list_frames(self):
        frames = [_frame("frame-001", "cam-001"), _frame("frame-002", "cam-002")]
        repo = MemoryFrameRepository(frames)
        assert len(repo.list_frames()) == 2

    def test_get_frame(self):
        repo = MemoryFrameRepository([_frame("frame-001")])
        assert repo.get_frame("frame-001") is not None
        assert repo.get_frame("missing") is None

    def test_list_by_camera(self):
        frames = [
            _frame("frame-001", "cam-001"),
            _frame("frame-002", "cam-001"),
            _frame("frame-003", "cam-002"),
        ]
        repo = MemoryFrameRepository(frames)
        assert len(repo.list_by_camera("cam-001")) == 2
        assert len(repo.list_by_camera("cam-002")) == 1
        assert repo.list_by_camera("cam-999") == []

    def test_seed_replaces_data(self):
        repo = MemoryFrameRepository([_frame("frame-001")])
        repo.seed([_frame("frame-new")])
        assert repo.get_frame("frame-001") is None
        assert repo.get_frame("frame-new") is not None


# ── MemoryCameraRepository ─────────────────────────────────────────────────────

class TestMemoryCameraRepository:
    def test_list_cameras(self):
        cameras = [_camera("cam-001"), _camera("cam-002")]
        repo = MemoryCameraRepository(cameras)
        assert len(repo.list_cameras()) == 2

    def test_get_camera(self):
        repo = MemoryCameraRepository([_camera("cam-001")])
        assert repo.get_camera("cam-001") is not None
        assert repo.get_camera("cam-999") is None

    def test_seed_replaces_data(self):
        repo = MemoryCameraRepository([_camera("cam-001")])
        repo.seed([_camera("cam-new")])
        assert repo.get_camera("cam-001") is None
        assert repo.get_camera("cam-new") is not None


# ── JsonCaseRepository ─────────────────────────────────────────────────────────

class TestJsonCaseRepository:
    @pytest.fixture
    def tmp_dir(self):
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    @pytest.fixture
    def repo(self, tmp_dir):
        return JsonCaseRepository(
            cases_path=tmp_dir / "cases.json",
            sightings_path=tmp_dir / "sightings.json",
        )

    def test_save_and_get(self, repo):
        case = _case()
        repo.save(case)
        loaded = repo.get(case.id)
        assert loaded is not None
        assert loaded.subject_name == "Jane Doe"

    def test_get_missing_returns_none(self, repo):
        assert repo.get("nonexistent") is None

    def test_list_all(self, repo):
        repo.save(_case("Alice"))
        repo.save(_case("Bob"))
        assert len(repo.list_all()) == 2

    def test_persistence_across_instances(self, tmp_dir):
        cases_path = tmp_dir / "cases.json"
        sightings_path = tmp_dir / "sightings.json"
        repo1 = JsonCaseRepository(cases_path, sightings_path)
        case = _case()
        repo1.save(case)

        # A new instance reading the same files should see the data
        repo2 = JsonCaseRepository(cases_path, sightings_path)
        loaded = repo2.get(case.id)
        assert loaded is not None
        assert loaded.id == case.id

    def test_save_sightings_and_reload(self, tmp_dir):
        cases_path = tmp_dir / "cases.json"
        sightings_path = tmp_dir / "sightings.json"
        repo1 = JsonCaseRepository(cases_path, sightings_path)
        case = _case()
        repo1.save(case)
        repo1.save_sightings(case.id, [_sighting(case.id)])

        repo2 = JsonCaseRepository(cases_path, sightings_path)
        result = repo2.get_sightings(case.id)
        assert len(result) == 1
        assert result[0].similarity_score == pytest.approx(0.85)

    def test_clear_removes_files(self, tmp_dir):
        cases_path = tmp_dir / "cases.json"
        sightings_path = tmp_dir / "sightings.json"
        repo = JsonCaseRepository(cases_path, sightings_path)
        repo.save(_case())
        assert cases_path.exists()
        repo.clear()
        assert not cases_path.exists()
        assert not sightings_path.exists()


# ── JsonFrameRepository ────────────────────────────────────────────────────────

class TestJsonFrameRepository:
    @pytest.fixture
    def seed_file(self, tmp_path):
        frames = [
            {
                "id": "frame-001",
                "camera_id": "cam-001",
                "timestamp": "2026-03-15T08:15:00+00:00",
                "thumbnail_url": None,
                "metadata": {"resolution": "1080p"},
            },
            {
                "id": "frame-002",
                "camera_id": "cam-001",
                "timestamp": "2026-03-15T08:17:00+00:00",
                "thumbnail_url": None,
                "metadata": None,
            },
            {
                "id": "frame-003",
                "camera_id": "cam-002",
                "timestamp": "2026-03-15T08:20:00+00:00",
                "thumbnail_url": None,
                "metadata": None,
            },
        ]
        path = tmp_path / "seed_frames.json"
        path.write_text(json.dumps(frames))
        return path

    def test_list_frames(self, seed_file):
        repo = JsonFrameRepository(seed_file)
        assert len(repo.list_frames()) == 3

    def test_get_frame(self, seed_file):
        repo = JsonFrameRepository(seed_file)
        assert repo.get_frame("frame-001") is not None
        assert repo.get_frame("frame-001").camera_id == "cam-001"
        assert repo.get_frame("missing") is None

    def test_list_by_camera(self, seed_file):
        repo = JsonFrameRepository(seed_file)
        assert len(repo.list_by_camera("cam-001")) == 2
        assert len(repo.list_by_camera("cam-002")) == 1

    def test_missing_seed_file_is_empty(self, tmp_path):
        repo = JsonFrameRepository(tmp_path / "nonexistent.json")
        assert repo.list_frames() == []


# ── JsonCameraRepository ───────────────────────────────────────────────────────

class TestJsonCameraRepository:
    @pytest.fixture
    def seed_file(self, tmp_path):
        cameras = [
            {
                "id": "cam-001",
                "name": "Main Entrance",
                "location": "Building A",
                "zone": "north",
                "neighbors": ["cam-002"],
                "latitude": 37.77,
                "longitude": -122.41,
                "location_label": "Gate",
            },
            {
                "id": "cam-002",
                "name": "Parking Lot",
                "location": "Building A West",
                "zone": "north",
                "neighbors": ["cam-001"],
                "latitude": None,
                "longitude": None,
                "location_label": None,
            },
        ]
        path = tmp_path / "seed_cameras.json"
        path.write_text(json.dumps(cameras))
        return path

    def test_list_cameras(self, seed_file):
        repo = JsonCameraRepository(seed_file)
        assert len(repo.list_cameras()) == 2

    def test_get_camera(self, seed_file):
        repo = JsonCameraRepository(seed_file)
        cam = repo.get_camera("cam-001")
        assert cam is not None
        assert cam.name == "Main Entrance"
        assert cam.latitude == pytest.approx(37.77)
        assert repo.get_camera("cam-999") is None

    def test_missing_seed_file_is_empty(self, tmp_path):
        repo = JsonCameraRepository(tmp_path / "nonexistent.json")
        assert repo.list_cameras() == []


# ── Seed data files ────────────────────────────────────────────────────────────

class TestSeedDataFiles:
    """Smoke tests ensuring the bundled seed files are valid and loadable."""

    def test_seed_cameras_loaded(self):
        repo = JsonCameraRepository()
        cameras = repo.list_cameras()
        assert 8 <= len(cameras) <= 12
        ids = {c.id for c in cameras}
        assert "cam-001" in ids
        assert "cam-010" in ids

    def test_seed_cameras_have_coordinates(self):
        repo = JsonCameraRepository()
        for cam in repo.list_cameras():
            assert cam.latitude is not None
            assert cam.longitude is not None

    def test_seed_cameras_neighbors_are_valid(self):
        repo = JsonCameraRepository()
        all_ids = {c.id for c in repo.list_cameras()}
        for cam in repo.list_cameras():
            for nb in cam.neighbors:
                assert nb in all_ids, f"{cam.id} references unknown neighbor {nb}"

    def test_seed_frames_loaded(self):
        repo = JsonFrameRepository()
        frames = repo.list_frames()
        assert 30 <= len(frames) <= 50

    def test_seed_frames_reference_valid_cameras(self):
        frame_repo = JsonFrameRepository()
        camera_repo = JsonCameraRepository()
        camera_ids = {c.id for c in camera_repo.list_cameras()}
        for frame in frame_repo.list_frames():
            assert frame.camera_id in camera_ids, (
                f"{frame.id} references unknown camera {frame.camera_id}"
            )
