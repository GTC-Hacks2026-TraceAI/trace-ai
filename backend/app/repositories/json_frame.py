"""JSON-file-backed FrameRepository.

Frame metadata is loaded from *data/seed_frames.json* at construction
time.  The repository is read-only: frames come from the seed file and
are never written back (they represent pre-indexed camera footage).
"""

from __future__ import annotations

import json
from pathlib import Path

from app.models import CameraFrame
from app.repositories.interfaces import IFrameRepository

_DATA_DIR = Path(__file__).parent.parent.parent / "data"
_SEED_FILE = _DATA_DIR / "seed_frames.json"


class JsonFrameRepository(IFrameRepository):
    """Loads frame metadata from a JSON seed file.

    The file is read once at construction time so that every access
    within a request is served from memory.
    """

    def __init__(self, seed_path: Path = _SEED_FILE) -> None:
        self._frames: dict[str, CameraFrame] = {}
        if seed_path.exists():
            raw: list[dict] = json.loads(seed_path.read_text())
            self._frames = {
                item["id"]: CameraFrame.model_validate(item) for item in raw
            }

    # ── IFrameRepository ──────────────────────────────────────────────────

    def list_frames(self) -> list[CameraFrame]:
        return list(self._frames.values())

    def get_frame(self, frame_id: str) -> CameraFrame | None:
        return self._frames.get(frame_id)

    def list_by_camera(self, camera_id: str) -> list[CameraFrame]:
        return [f for f in self._frames.values() if f.camera_id == camera_id]
