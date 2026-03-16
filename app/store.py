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

from app.repositories.interfaces import ICaseRepository
from app.repositories.memory import MemoryCaseRepository
from app.services.search import ISearchBackend, MockSearchBackend, SearchService
from app.services.camera_recommendation import NextCameraRecommendationService
from app.services.timeline import TimelineService

#: Active case repository – swap to JsonCaseRepository for persistence.
case_repository: ICaseRepository = MemoryCaseRepository()

#: Active search service – swap MockSearchBackend for a real vision backend.
search_service: SearchService = SearchService(backend=MockSearchBackend())

#: Timeline service – filters and enriches sightings into a movement timeline.
timeline_service: TimelineService = TimelineService()

#: Camera recommendation service – suggests next cameras to inspect.
camera_recommendation_service: NextCameraRecommendationService = (
    NextCameraRecommendationService()
)
