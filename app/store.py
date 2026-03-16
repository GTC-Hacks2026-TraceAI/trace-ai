"""Application-level store wiring.

``case_repository`` is the single source of truth for cases and sightings.
It defaults to the in-memory implementation so that the app works without
any filesystem access (and tests stay fast and isolated).

``search_service`` is the search orchestrator backed by a pluggable backend.
It defaults to the metadata-based ``MockSearchBackend``.  To use a real
vision backend, swap the backend here::

    from my_project import ClipFaissBackend
    search_service = SearchService(backend=ClipFaissBackend())

To switch to the JSON-backed case repository, replace the assignment below::

    from app.repositories import JsonCaseRepository
    case_repository: ICaseRepository = JsonCaseRepository()
"""

from __future__ import annotations

import logging

from app.config import get_nemotron_settings
from app.repositories.interfaces import ICaseRepository
from app.repositories.memory import MemoryCaseRepository
from app.services.camera_recommendation import NextCameraRecommendationService
from app.services.nemotron_client import NemotronClient
from app.services.search import MockSearchBackend, SearchService
from app.services.timeline import TimelineService

logger = logging.getLogger(__name__)


def _build_nemotron_client() -> NemotronClient | None:
    settings = get_nemotron_settings()
    if not settings.enabled:
        logger.warning(
            "Nemotron disabled; missing env vars: %s",
            ", ".join(settings.missing_vars),
        )
        return None

    return NemotronClient(
        api_key=settings.api_key or "",
        model=settings.model or "",
        base_url=settings.base_url or "",
    )


#: Active case repository – swap to JsonCaseRepository for persistence.
case_repository: ICaseRepository = MemoryCaseRepository()

#: Active search service – swap MockSearchBackend for a real vision backend.
nemotron_client = _build_nemotron_client()
search_service: SearchService = SearchService(
    backend=MockSearchBackend(nemotron_client=nemotron_client),
)

#: Timeline service – filters and enriches sightings into a movement timeline.
timeline_service: TimelineService = TimelineService(nemotron_client=nemotron_client)

#: Camera recommendation service – suggests next cameras to inspect.
camera_recommendation_service: NextCameraRecommendationService = (
    NextCameraRecommendationService(nemotron_client=nemotron_client)
)
