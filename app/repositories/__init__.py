"""Public API for the repositories package.

Import repository interfaces and concrete implementations from here so
callers never need to know which sub-module they live in.

    from app.repositories import ICaseRepository, MemoryCaseRepository
    from app.repositories import JsonCaseRepository, JsonCameraRepository
"""

from app.repositories.interfaces import (
    ICameraRepository,
    ICaseRepository,
    IFrameRepository,
)
from app.repositories.json_camera import JsonCameraRepository
from app.repositories.json_case import JsonCaseRepository
from app.repositories.json_frame import JsonFrameRepository
from app.repositories.memory import (
    MemoryCameraRepository,
    MemoryCaseRepository,
    MemoryFrameRepository,
)

__all__ = [
    # Interfaces
    "ICaseRepository",
    "IFrameRepository",
    "ICameraRepository",
    # In-memory implementations
    "MemoryCaseRepository",
    "MemoryFrameRepository",
    "MemoryCameraRepository",
    # JSON-file implementations
    "JsonCaseRepository",
    "JsonFrameRepository",
    "JsonCameraRepository",
]
