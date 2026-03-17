"""JSON-file-backed CaseRepository.

Cases are persisted to *data/cases.json* and sightings to
*data/sightings.json* so the state survives process restarts and
is easy to inspect / edit by hand during a demo.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.models import Case, Sighting
from app.repositories.interfaces import ICaseRepository

# Default paths (relative to the project root)
_DATA_DIR = Path(__file__).parent.parent.parent / "data"
_CASES_FILE = _DATA_DIR / "cases.json"
_SIGHTINGS_FILE = _DATA_DIR / "sightings.json"


class JsonCaseRepository(ICaseRepository):
    """Reads and writes cases / sightings as pretty-printed JSON files.

    The files are created automatically on first write.  Reads are eager
    (the whole file is loaded on each call) which is fine for an MVP
    with a small number of cases.
    """

    def __init__(
        self,
        cases_path: Path = _CASES_FILE,
        sightings_path: Path = _SIGHTINGS_FILE,
    ) -> None:
        self._cases_path = cases_path
        self._sightings_path = sightings_path

    # ── helpers ───────────────────────────────────────────────────────────

    def _load_cases(self) -> dict[str, Case]:
        if not self._cases_path.exists():
            return {}
        raw: list[dict] = json.loads(self._cases_path.read_text())
        return {item["id"]: Case.model_validate(item) for item in raw}

    def _write_cases(self, cases: dict[str, Case]) -> None:
        self._cases_path.parent.mkdir(parents=True, exist_ok=True)
        data = [c.model_dump(mode="json") for c in cases.values()]
        self._cases_path.write_text(json.dumps(data, indent=2))

    def _load_sightings(self) -> dict[str, list[Sighting]]:
        if not self._sightings_path.exists():
            return {}
        raw: dict[str, list[dict]] = json.loads(self._sightings_path.read_text())
        return {
            case_id: [Sighting.model_validate(s) for s in items]
            for case_id, items in raw.items()
        }

    def _write_sightings(self, sightings: dict[str, list[Sighting]]) -> None:
        self._sightings_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            case_id: [s.model_dump(mode="json") for s in items]
            for case_id, items in sightings.items()
        }
        self._sightings_path.write_text(json.dumps(data, indent=2))

    # ── ICaseRepository ───────────────────────────────────────────────────

    def save(self, case: Case) -> Case:
        cases = self._load_cases()
        cases[case.id] = case
        self._write_cases(cases)
        return case

    def get(self, case_id: str) -> Case | None:
        return self._load_cases().get(case_id)

    def list_all(self) -> list[Case]:
        return list(self._load_cases().values())

    def save_sightings(self, case_id: str, sightings: list[Sighting]) -> None:
        all_sightings = self._load_sightings()
        all_sightings[case_id] = list(sightings)
        self._write_sightings(all_sightings)

    def get_sightings(self, case_id: str) -> list[Sighting]:
        return list(self._load_sightings().get(case_id, []))

    def clear(self) -> None:
        if self._cases_path.exists():
            self._cases_path.unlink()
        if self._sightings_path.exists():
            self._sightings_path.unlink()
