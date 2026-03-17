"""JSON-file-backed CameraRepository.

Camera network data is loaded from *data/seed_cameras.json* at
construction time.  Like frames, cameras are read-only at runtime –
the network topology is defined by the seed file.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.models import Camera
from app.repositories.interfaces import ICameraRepository

_DATA_DIR = Path(__file__).parent.parent.parent / "data"
_SEED_FILE = _DATA_DIR / "seed_cameras.json"


class JsonCameraRepository(ICameraRepository):
    """Loads camera records from a JSON seed file.

    The file is read once at construction time so that every access
    within a request is served from memory.
    """

    def __init__(self, seed_path: Path = _SEED_FILE) -> None:
        self._cameras: dict[str, Camera] = {}
        if seed_path.exists():
            raw: list[dict] = json.loads(seed_path.read_text())
            self._cameras = {
                item["id"]: Camera.model_validate(item) for item in raw
            }

    # ── ICameraRepository ─────────────────────────────────────────────────

    def list_cameras(self) -> list[Camera]:
        return list(self._cameras.values())

    def get_camera(self, camera_id: str) -> Camera | None:
        return self._cameras.get(camera_id)
