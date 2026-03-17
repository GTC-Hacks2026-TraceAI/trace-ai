"""In-memory repository implementations.

These are the default repositories used at runtime and in tests.
Data lives only in process memory – ideal for a demo or test run where
you do not want filesystem side-effects.
"""

from __future__ import annotations

from app.models import Camera, CameraFrame, Case, Sighting
from app.repositories.interfaces import (
    ICameraRepository,
    ICaseRepository,
    IFrameRepository,
)


class MemoryCaseRepository(ICaseRepository):
    """Stores cases and sightings in plain Python dicts."""

    def __init__(self) -> None:
        self._cases: dict[str, Case] = {}
        self._sightings: dict[str, list[Sighting]] = {}

    def save(self, case: Case) -> Case:
        self._cases[case.id] = case
        return case

    def get(self, case_id: str) -> Case | None:
        return self._cases.get(case_id)

    def list_all(self) -> list[Case]:
        return list(self._cases.values())

    def save_sightings(self, case_id: str, sightings: list[Sighting]) -> None:
        self._sightings[case_id] = list(sightings)

    def get_sightings(self, case_id: str) -> list[Sighting]:
        return list(self._sightings.get(case_id, []))

    def clear(self) -> None:
        self._cases.clear()
        self._sightings.clear()


class MemoryFrameRepository(IFrameRepository):
    """Stores frame metadata in a plain Python dict, keyed by frame id."""

    def __init__(self, frames: list[CameraFrame] | None = None) -> None:
        self._frames: dict[str, CameraFrame] = (
            {f.id: f for f in frames} if frames else {}
        )

    def seed(self, frames: list[CameraFrame]) -> None:
        """Bulk-load frames (replaces any existing data)."""
        self._frames = {f.id: f for f in frames}

    def list_frames(self) -> list[CameraFrame]:
        return list(self._frames.values())

    def get_frame(self, frame_id: str) -> CameraFrame | None:
        return self._frames.get(frame_id)

    def list_by_camera(self, camera_id: str) -> list[CameraFrame]:
        return [f for f in self._frames.values() if f.camera_id == camera_id]


class MemoryCameraRepository(ICameraRepository):
    """Stores camera records in a plain Python dict, keyed by camera id."""

    def __init__(self, cameras: list[Camera] | None = None) -> None:
        self._cameras: dict[str, Camera] = (
            {c.id: c for c in cameras} if cameras else {}
        )

    def seed(self, cameras: list[Camera]) -> None:
        """Bulk-load cameras (replaces any existing data)."""
        self._cameras = {c.id: c for c in cameras}

    def list_cameras(self) -> list[Camera]:
        return list(self._cameras.values())

    def get_camera(self, camera_id: str) -> Camera | None:
        return self._cameras.get(camera_id)
