"""Compact planner lookups. Do not send full beat arrays by default."""

from __future__ import annotations

from dj_collection_set_builder.models import (
    CollectionAnalysis,
    TrackAnalysis,
    TrackSummary,
    TransitionWindows,
)


class UnknownTrackError(KeyError):
    """Raised when a track_id is not in the collection."""


def find_track(collection: CollectionAnalysis, track_id: str) -> TrackAnalysis:
    token = track_id.strip()
    matches: list[TrackAnalysis] = []
    for track in collection.tracks:
        if track.source.track_id == token:
            return track
        digest = track.source.sha256_before
        if token == digest or token == f"sha256:{digest}":
            return track
        if track.source.filename == token:
            matches.append(track)
    if len(matches) == 1:
        return matches[0]
    raise UnknownTrackError(f"Unknown track_id: {track_id}")


def get_track_summary(track: TrackAnalysis) -> TrackSummary:
    primary = next(
        (grid for grid in track.rhythm_grids if grid.source_tool == "all-in-one-mlx"),
        track.rhythm_grids[0] if track.rhythm_grids else None,
    )
    preferred = [
        loop
        for loop in track.loop_candidates
        if loop.bars in {8, 16}
        and not loop.crosses_novelty_boundary
        and loop.status in {"passed", "warning"}
    ]
    loudness = track.loudness.integrated
    return TrackSummary(
        track_id=track.source.track_id,
        filename=track.source.filename,
        duration_s=track.stream.duration_s,
        bpm=track.tempo.selected_candidate.value,
        bpm_authority=track.tempo.selected_candidate.authority,
        standard_name=track.key.standard_name,
        camelot=track.key.camelot,
        key_strength=track.key.strength,
        loudness_lufs=loudness.value,
        loudness_authority=loudness.authority,
        section_count=len(track.sections),
        preferred_loop_count=len(preferred),
        beat_count=primary.beat_count if primary else 0,
        downbeat_count=primary.downbeat_count if primary else 0,
        analyzer_failure_count=len(track.analyzer_failures),
    )


def get_transition_windows(track: TrackAnalysis, *, max_loops: int = 8) -> TransitionWindows:
    primary = next(
        (grid for grid in track.rhythm_grids if grid.source_tool == "all-in-one-mlx"),
        track.rhythm_grids[0] if track.rhythm_grids else None,
    )
    downbeats = list(primary.downbeats_s) if primary else []
    anchors = downbeats[:8]
    if len(downbeats) > 8:
        anchors.extend(downbeats[-8:])
    loops = [
        {
            "loop_id": loop.loop_id,
            "start_s": loop.start_s,
            "end_s": loop.end_s,
            "bars": loop.bars,
            "contained_in_section_id": loop.contained_in_section_id,
            "rhythm_sources_agree": loop.rhythm_sources_agree,
        }
        for loop in track.loop_candidates
        if loop.bars in {8, 16}
        and not loop.crosses_novelty_boundary
        and loop.status in {"passed", "warning"}
    ][:max_loops]
    sections = [
        {
            "section_id": section.section_id,
            "start_s": section.start_s,
            "end_s": section.end_s,
            "label": section.label,
        }
        for section in track.sections
    ]
    return TransitionWindows(
        track_id=track.source.track_id,
        filename=track.source.filename,
        primary_grid_tool=primary.source_tool if primary else None,
        downbeat_count=len(downbeats),
        downbeat_anchors_s=anchors,
        sections=sections,
        preferred_loops=loops,
    )
