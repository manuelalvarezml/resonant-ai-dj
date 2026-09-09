"""Small audible diagnostics for stored benchmark-estimate downbeat grids."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from dj_collection_set_builder.ingest import sha256_file
from dj_collection_set_builder.models import CollectionAnalysis, RhythmGrid, TrackAnalysis
from dj_collection_set_builder.render import (
    RenderError,
    ensure_output_path,
    overlay_downbeat_clicks,
    probe_duration_s,
)
from dj_collection_set_builder.set_renderer import resolve_source_path


def _grid(track: TrackAnalysis, source_tool: str) -> RhythmGrid | None:
    return next(
        (
            grid
            for grid in track.rhythm_grids
            if grid.source_tool == source_tool and grid.downbeats_s
        ),
        None,
    )


def _slug(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_value.lower()).strip("-")[:64] or "track"


def render_downbeat_diagnostics(
    collection: CollectionAnalysis,
    track_ids: list[str],
    *,
    out_dir: Path,
    duration_s: float = 30.0,
    source_tool: str = "all-in-one-mlx",
) -> list[dict]:
    """Render centered excerpts for selected tracks with clicks on stored downbeats."""
    if not track_ids:
        raise RenderError("At least one track ID is required")
    if len(set(track_ids)) != len(track_ids):
        raise RenderError("Diagnostic track IDs must be unique")
    source_folder = Path(collection.input_folder).resolve()
    resolved_out_dir = out_dir.resolve()
    ensure_output_path(
        resolved_out_dir / ".downbeat-output-check.wav",
        source_folder=source_folder,
        create_parent=False,
    )
    tracks = {track.source.track_id: track for track in collection.tracks}
    unknown = [track_id for track_id in track_ids if track_id not in tracks]
    if unknown:
        raise RenderError(f"Unknown diagnostic track IDs: {unknown}")
    resolved_out_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []
    for ordinal, track_id in enumerate(track_ids, start=1):
        track = tracks[track_id]
        source_path = resolve_source_path(source_folder, track)
        if source_path is None:
            raise RenderError(f"Could not resolve source file for {track_id}")
        digest_before = sha256_file(source_path)
        if digest_before != track.source.sha256_before:
            raise RenderError(f"Source hash mismatch for {track.source.filename}")
        grid = _grid(track, source_tool)
        if grid is None:
            raise RenderError(
                f"No {source_tool} downbeat grid is available for {track.source.filename}"
            )
        source_duration = track.stream.duration_s or probe_duration_s(source_path)
        clip_duration = min(duration_s, float(source_duration))
        clip_start = max(0.0, (float(source_duration) - clip_duration) / 2.0)
        click_times = [
            float(timestamp)
            for timestamp in grid.downbeats_s
            if clip_start <= float(timestamp) < clip_start + clip_duration
        ]
        output = resolved_out_dir / (
            f"{ordinal:02d}-{_slug(Path(track.source.filename).stem)}-downbeats.wav"
        )
        artifact = overlay_downbeat_clicks(
            source_path,
            start_s=clip_start,
            duration_s=clip_duration,
            downbeats_s=list(grid.downbeats_s),
            out_path=output,
            source_folder=source_folder,
        )
        if sha256_file(source_path) != digest_before:
            raise RenderError(
                f"Source hash changed during diagnostic render: {track.source.filename}"
            )
        results.append(
            {
                "track_id": track_id,
                "filename": track.source.filename,
                "source_tool": source_tool,
                "authority": grid.authority,
                "clip_start_s": clip_start,
                "clip_duration_s": artifact.duration_s,
                "click_count": len(click_times),
                "click_source_times_s": click_times,
                "output_path": artifact.path,
                "output_sha256": artifact.sha256,
                "warnings": artifact.warnings,
            }
        )
    return results
