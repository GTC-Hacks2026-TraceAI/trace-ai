"""Timeline service for Trace AI.

Takes ranked candidate sightings and produces an investigator-friendly
movement timeline, sorted by time, filtered for confidence, and enriched
with a plain-English path summary.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.models import Camera, Sighting, Timeline, TimelineEntry

# Default minimum confidence threshold.  Sightings below this value are
# treated as too uncertain to include in the timeline.
DEFAULT_MIN_CONFIDENCE: float = 0.3


@runtime_checkable
class _HasConfidence(Protocol):
    """Duck-type protocol for objects that carry either similarity_score or
    confidence_score so the service can work with both ``Sighting`` and
    ``CandidateSighting`` objects without a hard dependency on the latter."""

    @property
    def confidence_score(self) -> float: ...  # noqa: E704


def _confidence(sighting: Sighting) -> float:
    """Return the confidence value regardless of which attribute name is used."""
    # CandidateSighting uses ``confidence_score``; plain Sighting uses ``similarity_score``.
    if isinstance(sighting, _HasConfidence):
        return sighting.confidence_score  # type: ignore[attr-defined]
    return sighting.similarity_score


def _build_summary(entries: list[TimelineEntry]) -> str:
    """Infer a plain-English path summary from a sorted list of timeline entries.

    Examples
    --------
    - No entries: returns an empty string.
    - Single entry: "Subject was observed at Main Entrance at 08:15 AM."
    - Multiple entries: "Subject was likely observed moving from Main Entrance
      to Transit Stop between 08:15 AM and 09:01 AM."
    """
    if not entries:
        return ""

    def _fmt_time(ts) -> str:  # noqa: ANN001
        return ts.strftime("%I:%M %p").lstrip("0")

    first = entries[0]
    last = entries[-1]

    if len(entries) == 1:
        return (
            f"Subject was observed at {first.camera_name} "
            f"({first.location}) at {_fmt_time(first.timestamp)}."
        )

    if first.location == last.location:
        return (
            f"Subject was observed multiple times at {first.camera_name} "
            f"({first.location}) between {_fmt_time(first.timestamp)} "
            f"and {_fmt_time(last.timestamp)}."
        )

    return (
        f"Subject was likely observed moving from {first.camera_name} "
        f"({first.location}) to {last.camera_name} ({last.location}) "
        f"between {_fmt_time(first.timestamp)} and {_fmt_time(last.timestamp)}."
    )


class TimelineService:
    """Build an investigator-friendly movement timeline from ranked sightings.

    Parameters
    ----------
    min_confidence:
        Sightings whose confidence/similarity score is strictly below this
        value are excluded.  Defaults to ``DEFAULT_MIN_CONFIDENCE`` (0.3).

    Usage::

        service = TimelineService()
        timeline = service.build(
            case_id="abc",
            subject_name="Jane Doe",
            sightings=ranked_sightings,
            camera_map=CAMERA_MAP,
        )
    """

    def __init__(self, min_confidence: float = DEFAULT_MIN_CONFIDENCE) -> None:
        self.min_confidence = min_confidence

    def build(
        self,
        case_id: str,
        subject_name: str,
        sightings: list[Sighting],
        camera_map: dict[str, Camera],
    ) -> Timeline:
        """Convert ranked sightings into a sorted, filtered timeline.

        Steps
        -----
        1. Drop sightings whose confidence is below *min_confidence*.
        2. Sort the remaining sightings by timestamp (ascending).
        3. Enrich each entry with camera name, location, confidence, and
           explanation from the camera map.
        4. Generate a plain-English path summary.

        Returns
        -------
        :class:`~app.models.Timeline`
            A timeline ready for frontend rendering, including a ``summary``
            field with the inferred movement description.
        """
        # Step 1: filter out low-confidence sightings
        accepted = [s for s in sightings if _confidence(s) >= self.min_confidence]

        # Step 2: sort chronologically
        accepted.sort(key=lambda s: s.timestamp)

        # Step 3: build enriched timeline entries
        entries: list[TimelineEntry] = []
        for sighting in accepted:
            camera = camera_map.get(sighting.camera_id)
            camera_name = camera.name if camera else "Unknown"
            location = sighting.location or (camera.location if camera else "Unknown")

            entries.append(TimelineEntry(
                timestamp=sighting.timestamp,
                camera_id=sighting.camera_id,
                camera_name=camera_name,
                location=location,
                frame_id=sighting.frame_id,
                similarity_score=_confidence(sighting),
                explanation=sighting.explanation,
            ))

        # Step 4: infer path summary
        summary = _build_summary(entries)

        return Timeline(
            case_id=case_id,
            subject_name=subject_name,
            entries=entries,
            summary=summary,
        )
