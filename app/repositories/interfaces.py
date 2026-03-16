"""Abstract repository interfaces for Trace AI.

Keeping these interfaces separate from their implementations means the
persistence layer can be swapped (in-memory ↔ JSON ↔ SQLite …) without
touching any business logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.models import Camera, CameraFrame, Case, Sighting


class ICaseRepository(ABC):
    """Persistence contract for missing-person cases and their sightings."""

    @abstractmethod
    def save(self, case: Case) -> Case:
        """Persist a case and return it (with any generated fields applied)."""

    @abstractmethod
    def get(self, case_id: str) -> Case | None:
        """Return the case with the given id, or *None* if not found."""

    @abstractmethod
    def list_all(self) -> list[Case]:
        """Return all stored cases."""

    @abstractmethod
    def save_sightings(self, case_id: str, sightings: list[Sighting]) -> None:
        """Overwrite the sightings list for a given case."""

    @abstractmethod
    def get_sightings(self, case_id: str) -> list[Sighting]:
        """Return the sightings stored for a given case (empty list if none)."""

    @abstractmethod
    def clear(self) -> None:
        """Remove all cases and sightings (useful for testing)."""


class IFrameRepository(ABC):
    """Read-only contract for indexed camera-frame metadata."""

    @abstractmethod
    def list_frames(self) -> list[CameraFrame]:
        """Return all indexed frames."""

    @abstractmethod
    def get_frame(self, frame_id: str) -> CameraFrame | None:
        """Return the frame with the given id, or *None* if not found."""

    @abstractmethod
    def list_by_camera(self, camera_id: str) -> list[CameraFrame]:
        """Return all frames captured by the specified camera."""


class ICameraRepository(ABC):
    """Read-only contract for the camera network."""

    @abstractmethod
    def list_cameras(self) -> list[Camera]:
        """Return all cameras in the network."""

    @abstractmethod
    def get_camera(self, camera_id: str) -> Camera | None:
        """Return the camera with the given id, or *None* if not found."""
