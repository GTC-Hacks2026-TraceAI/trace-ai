"""Runtime configuration for backend integrations."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and value:
            os.environ.setdefault(key, value)


_ROOT = Path(__file__).resolve().parents[1]
_load_env_file(_ROOT / "backend" / ".env")
_load_env_file(_ROOT / ".env")


@dataclass(frozen=True)
class NemotronSettings:
    api_key: str | None
    model: str | None
    base_url: str | None
    enabled: bool
    missing_vars: tuple[str, ...]


def get_nemotron_settings() -> NemotronSettings:
    api_key = os.getenv("NEMOTRON_API_KEY")
    model = os.getenv("NEMOTRON_MODEL")
    base_url = os.getenv("NVIDIA_API_BASE")

    missing: list[str] = []
    if not api_key:
        missing.append("NEMOTRON_API_KEY")
    if not model:
        missing.append("NEMOTRON_MODEL")
    if not base_url:
        missing.append("NVIDIA_API_BASE")

    return NemotronSettings(
        api_key=api_key,
        model=model,
        base_url=base_url,
        enabled=len(missing) == 0,
        missing_vars=tuple(missing),
    )
