"""Next-camera recommendation service for Trace AI.

Given a set of sightings and a camera graph, recommends which cameras
investigators should inspect next.  Uses deterministic heuristics:

1. **Movement direction** – infer likely direction from zone progression
   of the most recent sightings (north → central → south or vice-versa).
2. **Adjacency ranking** – cameras adjacent to the latest sightings are
   ranked highest, with un-visited cameras preferred.
3. **Confidence propagation** – the sighting confidence that leads to a
   recommendation is carried through.
4. **Urgency** – when the elapsed time since a sighting approaches the
   footage-retention window the recommendation reason flags urgency and
   a ``review_before`` deadline is surfaced.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional
from typing import TYPE_CHECKING

from app.models import Camera, NextCameraRecommendation, RetentionUrgency, Sighting

if TYPE_CHECKING:
    from app.services.nemotron_client import NemotronClient

# Zones ordered from north to south.  Used to infer travel direction.
_ZONE_ORDER: list[str] = ["north", "central", "south"]

# Default footage-retention window in hours.  Used when a camera does not
# specify its own ``retention_hours``.
DEFAULT_RETENTION_HOURS: float = 72.0

# Fraction thresholds for urgency levels.
_URGENCY_HIGH: float = 0.75   # ≥ 75 % of retention elapsed → high
_URGENCY_MED: float = 0.50    # ≥ 50 % of retention elapsed → medium
_URGENCY_FRACTION: float = _URGENCY_HIGH  # kept for backward compatibility


def _zone_index(zone: str) -> int:
    """Return the ordinal position of *zone* in the north→south axis."""
    try:
        return _ZONE_ORDER.index(zone.lower())
    except ValueError:
        return 1  # default to central for unknown zones


def _infer_direction(sightings: list[Sighting], camera_map: dict[str, Camera]) -> Optional[int]:
    """Infer movement direction from the two most recent sightings.

    Returns
    -------
    +1  if the subject appears to be moving south (increasing zone index),
    -1  if the subject appears to be moving north (decreasing zone index),
    None if direction cannot be determined (same zone or insufficient data).
    """
    if len(sightings) < 2:
        return None

    recent = sorted(sightings, key=lambda s: s.timestamp, reverse=True)
    cam_latest = camera_map.get(recent[0].camera_id)
    cam_prev = camera_map.get(recent[1].camera_id)

    if not cam_latest or not cam_prev:
        return None

    diff = _zone_index(cam_latest.zone) - _zone_index(cam_prev.zone)
    if diff > 0:
        return 1   # moving south
    if diff < 0:
        return -1  # moving north
    return None


def _is_urgent(
    sighting_ts: datetime,
    now: datetime,
    retention_hours: float,
) -> bool:
    """Return True when the elapsed time since *sighting_ts* exceeds the
    urgency fraction of the retention window."""
    elapsed = (now - sighting_ts).total_seconds() / 3600.0
    return elapsed >= retention_hours * _URGENCY_FRACTION


def _urgency_level(
    sighting_ts: datetime,
    now: datetime,
    retention_hours: float,
) -> RetentionUrgency:
    """Return the retention urgency level based on how much of the window has elapsed.

    Returns
    -------
    RetentionUrgency.high   – ≥ 75 % of the retention window has elapsed
    RetentionUrgency.medium – ≥ 50 % (but < 75 %) of the window has elapsed
    RetentionUrgency.low    – < 50 % of the window has elapsed
    """
    elapsed_fraction = (now - sighting_ts).total_seconds() / 3600.0 / retention_hours
    if elapsed_fraction >= _URGENCY_HIGH:
        return RetentionUrgency.high
    if elapsed_fraction >= _URGENCY_MED:
        return RetentionUrgency.medium
    return RetentionUrgency.low


def _review_before_dt(sighting_ts: datetime, retention_hours: float) -> datetime:
    """Return the datetime by which footage from *sighting_ts* must be reviewed."""
    return sighting_ts + timedelta(hours=retention_hours)


class NextCameraRecommendationService:
    """Recommend next cameras to inspect based on the camera graph and sightings.

    Parameters
    ----------
    retention_hours:
        Footage-retention window in hours.  When the time since the most
        recent sighting exceeds 75 % of this value the recommendation
        includes an urgency warning.
    """

    def __init__(
        self,
        retention_hours: float = DEFAULT_RETENTION_HOURS,
        nemotron_client: "NemotronClient | None" = None,
    ) -> None:
        self.retention_hours = retention_hours
        self.nemotron_client = nemotron_client

    def recommend(
        self,
        sightings: list[Sighting],
        camera_map: dict[str, Camera],
        cameras: list[Camera],
        now: datetime | None = None,
    ) -> list[NextCameraRecommendation]:
        """Return a ranked list of cameras to inspect next.

        Parameters
        ----------
        sightings:
            All sightings for a case (may be empty for cold start).
        camera_map:
            Mapping of camera ID → Camera for the entire network.
        cameras:
            Ordered list of all cameras in the network.
        now:
            Current timestamp used for urgency calculations.  Defaults to
            ``datetime.now(timezone.utc)`` when not supplied.
        """
        if now is None:
            now = datetime.now(timezone.utc)

        if not sightings:
            return self._cold_start(cameras)

        return self._rank_from_sightings(sightings, camera_map, cameras, now)

    # ------------------------------------------------------------------
    # Cold start – no sightings yet
    # ------------------------------------------------------------------

    @staticmethod
    def _cold_start(cameras: list[Camera]) -> list[NextCameraRecommendation]:
        """When there are no sightings, recommend the first three cameras."""
        recs: list[NextCameraRecommendation] = []
        for i, cam in enumerate(cameras[:3]):
            recs.append(NextCameraRecommendation(
                camera_id=cam.id,
                camera_name=cam.name,
                location=cam.location,
                zone=cam.zone,
                priority=i + 1,
                reason="Starting recommendation – no sightings yet",
                latitude=cam.latitude,
                longitude=cam.longitude,
            ))
        return recs

    # ------------------------------------------------------------------
    # Sighting-based recommendations
    # ------------------------------------------------------------------

    def _rank_from_sightings(
        self,
        sightings: list[Sighting],
        camera_map: dict[str, Camera],
        cameras: list[Camera],
        now: datetime,
    ) -> list[NextCameraRecommendation]:
        direction = _infer_direction(sightings, camera_map)
        seen_ids = {s.camera_id for s in sightings}

        # Focus on the three most recent sightings.
        latest = sorted(sightings, key=lambda s: s.timestamp, reverse=True)[:3]

        scored: list[tuple[float, NextCameraRecommendation]] = []
        added: set[str] = set()

        for rank, sighting in enumerate(latest, 1):
            camera = camera_map.get(sighting.camera_id)
            if not camera:
                continue

            # Use per-camera retention if available, else fall back to global.
            eff_retention = (
                camera.retention_hours
                if camera.retention_hours is not None
                else self.retention_hours
            )

            for nb_id in camera.neighbors:
                if nb_id in seen_ids or nb_id in added:
                    continue
                nb = camera_map.get(nb_id)
                if not nb:
                    continue

                score = self._score_candidate(
                    nb, camera, sighting, rank, direction, camera_map,
                )
                reason = self._build_reason(
                    nb, camera, sighting, direction, now, eff_retention,
                )
                if self.nemotron_client is not None:
                    reason = self.nemotron_client.generate_recommendation_reason(
                        fallback=reason,
                    )
                confidence = round(
                    min(1.0, sighting.similarity_score * score), 2,
                )

                scored.append((score, NextCameraRecommendation(
                    camera_id=nb.id,
                    camera_name=nb.name,
                    location=nb.location,
                    zone=nb.zone,
                    priority=1,  # placeholder – assigned after sorting
                    reason=reason,
                    confidence=confidence,
                    latitude=nb.latitude,
                    longitude=nb.longitude,
                    urgency_level=_urgency_level(sighting.timestamp, now, eff_retention),
                    review_before=_review_before_dt(sighting.timestamp, eff_retention),
                )))
                added.add(nb_id)

        # Sort by descending score, then assign priority 1..N.
        scored.sort(key=lambda t: t[0], reverse=True)
        recs: list[NextCameraRecommendation] = []
        for i, (_, rec) in enumerate(scored, 1):
            rec.priority = i
            recs.append(rec)

        return recs

    # ------------------------------------------------------------------
    # Scoring / reason helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _score_candidate(
        candidate: Camera,
        source: Camera,
        sighting: Sighting,
        recency_rank: int,
        direction: int | None,
        camera_map: dict[str, Camera],
    ) -> float:
        """Compute a heuristic score for *candidate* camera (higher is better).

        Components:
        - recency bonus (most-recent sighting → highest base)
        - direction bonus (camera in predicted direction)
        - confidence from the originating sighting
        """
        # Base: prefer neighbours of the most-recent sighting.
        base = 1.0 / recency_rank

        # Direction bonus
        dir_bonus = 0.0
        if direction is not None:
            src_idx = _zone_index(source.zone)
            cand_idx = _zone_index(candidate.zone)
            if (cand_idx - src_idx) * direction > 0:
                # Candidate is in the predicted direction
                dir_bonus = 0.3
            elif cand_idx == src_idx:
                dir_bonus = 0.1  # same zone – small bonus

        # Confidence from sighting
        conf_bonus = sighting.similarity_score * 0.3

        return base + dir_bonus + conf_bonus

    def _build_reason(
        self,
        candidate: Camera,
        source: Camera,
        sighting: Sighting,
        direction: int | None,
        now: datetime,
        retention_hours: float | None = None,
    ) -> str:
        """Build a human-readable reason for the recommendation."""
        if retention_hours is None:
            retention_hours = self.retention_hours

        time_str = sighting.timestamp.strftime("%H:%M")
        reason = (
            f"Recommended because it is adjacent to {source.name}, "
            f"where the subject was spotted at {time_str}"
        )

        # Direction context
        if direction is not None:
            dir_label = "south" if direction > 0 else "north"
            src_idx = _zone_index(source.zone)
            cand_idx = _zone_index(candidate.zone)
            if (cand_idx - src_idx) * direction > 0:
                reason += (
                    f", and lies along the likely path heading {dir_label} "
                    f"toward {candidate.location}"
                )

        reason += "."

        # Urgency
        level = _urgency_level(sighting.timestamp, now, retention_hours)
        if level == RetentionUrgency.high:
            hours_left = max(
                0.0,
                retention_hours
                - (now - sighting.timestamp).total_seconds() / 3600.0,
            )
            reason += f" URGENT: footage may expire in ~{hours_left:.0f}h"
        elif level == RetentionUrgency.medium:
            hours_left = max(
                0.0,
                retention_hours
                - (now - sighting.timestamp).total_seconds() / 3600.0,
            )
            reason += f" CAUTION: footage expires in ~{hours_left:.0f}h"

        return reason
