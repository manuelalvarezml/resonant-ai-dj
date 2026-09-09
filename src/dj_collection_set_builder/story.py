"""Deterministic story-arc ordering. No audio is rendered."""

from __future__ import annotations

from dj_collection_set_builder.compatibility import score_transition
from dj_collection_set_builder.constants import (
    TEMPO_WAVE_CLIMB_DENOMINATOR,
    TEMPO_WAVE_CLIMB_NUMERATOR,
)
from dj_collection_set_builder.models import TrackAnalysis


def _bpm(track: TrackAnalysis) -> float | None:
    value = track.tempo.selected_candidate.value
    if value is None:
        return None
    bpm = float(value)
    return bpm if bpm > 0 else None


def tempo_wave_climb_count(track_count: int) -> int:
    if track_count <= 1:
        return track_count
    return max(1, (track_count * TEMPO_WAVE_CLIMB_NUMERATOR) // TEMPO_WAVE_CLIMB_DENOMINATOR)


def propose_tempo_wave_order(
    tracks: list[TrackAnalysis],
    *,
    climb_count: int | None = None,
    policy: str = "rekordbox-related-2",
) -> list[TrackAnalysis]:
    """Greedy tempo-wave order: climb, then descend, preferring Related 2 matches."""
    if not tracks:
        return []
    climb = climb_count if climb_count is not None else tempo_wave_climb_count(len(tracks))
    remaining = list(tracks)
    remaining.sort(key=lambda item: (_bpm(item) is None, _bpm(item) or 0.0, item.source.filename))
    order = [remaining.pop(0)]
    while remaining:
        climbing = len(order) < climb
        previous = order[-1]
        previous_bpm = _bpm(previous)
        target = "up" if climbing else "down"
        ranked: list[tuple[int, float, str, TrackAnalysis]] = []
        for candidate in remaining:
            next_bpm = _bpm(candidate)
            monotonic = True
            if previous_bpm is not None and next_bpm is not None:
                if climbing and next_bpm + 1e-6 < previous_bpm:
                    monotonic = False
                if not climbing and next_bpm - 1e-6 > previous_bpm:
                    monotonic = False
            transition = score_transition(
                previous,
                candidate,
                policy=policy,
                story_target=target,
            )
            ranked.append(
                (
                    0 if monotonic else 1,
                    -transition.score,
                    candidate.source.filename,
                    candidate,
                )
            )
        ranked.sort()
        chosen = ranked[0][3]
        remaining = [
            item for item in remaining if item.source.track_id != chosen.source.track_id
        ]
        order.append(chosen)
    return order
