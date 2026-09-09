"""Validate and render a minimal declarative multi-track MixPlan."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path

from dj_collection_set_builder.constants import (
    AUTHORITY_EXECUTED,
    COLLECTION_SCHEMA,
    EVENT_MATCH_WINDOW_S,
    GAIN_DB_MAX,
    GAIN_DB_MIN,
    MIX_PLAN_SCHEMA,
    MIX_CROSSFADE_S_MAX,
    MIX_CROSSFADE_S_MIN,
    RENDER_SAMPLE_RATE_HZ,
    SCHEMA_VERSION,
    STRETCH_MAX_PERCENT,
)
from dj_collection_set_builder.ingest import require_ffmpeg, sha256_file
from dj_collection_set_builder.loudness import ffmpeg_loudnorm
from dj_collection_set_builder.models import (
    CollectionAnalysis,
    MixPlan,
    PlannedTrackSegment,
    PlannedTransition,
    RenderManifest,
    RhythmGrid,
    TrackAnalysis,
)
from dj_collection_set_builder.render import (
    RenderError,
    crossfade,
    ensure_output_path,
    house_transition,
    load_track,
    probe_duration_s,
    set_gain,
    time_stretch,
)


class MixPlanValidationError(RenderError):
    """Raised when a MixPlan cannot be executed safely and deterministically."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("Invalid MixPlan:\n- " + "\n- ".join(errors))


@dataclass(frozen=True)
class ValidatedSegment:
    plan: PlannedTrackSegment
    track: TrackAnalysis
    source_path: Path
    source_sha256: str
    start_s: float
    end_s: float
    source_bpm: float
    effective_bpm: float
    estimated_duration_s: float


@dataclass(frozen=True)
class ValidatedTransition:
    plan: PlannedTransition
    duration_s: float
    incoming_grid_duration_s: float
    grid_drift_s: float


@dataclass(frozen=True)
class ValidatedMixPlan:
    plan: MixPlan
    source_folder: Path
    output_path: Path
    segments: tuple[ValidatedSegment, ...]
    transitions: tuple[ValidatedTransition, ...]
    planned_duration_s: float
    warnings: tuple[str, ...]


def primary_grid(track: TrackAnalysis) -> RhythmGrid | None:
    return next(
        (
            grid
            for grid in track.rhythm_grids
            if grid.source_tool == "all-in-one-mlx" and grid.downbeats_s
        ),
        next((grid for grid in track.rhythm_grids if grid.downbeats_s), None),
    )


def resolve_source_path(source_folder: Path, track: TrackAnalysis) -> Path | None:
    stored = Path(track.source.path)
    candidates = [stored] if stored.is_absolute() else [source_folder.parent / stored]
    candidates.append(source_folder / track.source.filename)
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved.is_file() and resolved.is_relative_to(source_folder):
            return resolved
    return None


def _float_bpm(track: TrackAnalysis) -> float | None:
    value = track.tempo.selected_candidate.value
    try:
        bpm = float(value)
    except (TypeError, ValueError):
        return None
    return bpm if bpm > 0 else None


def validate_mix_plan(
    collection: CollectionAnalysis,
    plan: MixPlan,
    *,
    out_path: Path,
) -> ValidatedMixPlan:
    """Resolve a plan against one collection and reject unsafe or ambiguous input."""
    errors: list[str] = []
    warnings = list(plan.warnings)
    source_folder = Path(collection.input_folder).resolve()
    if not source_folder.is_dir():
        errors.append(f"Collection input folder does not exist: {source_folder}")
    try:
        resolved_output = ensure_output_path(
            out_path,
            source_folder=source_folder,
            create_parent=False,
        )
    except RenderError as exc:
        errors.append(str(exc))
        resolved_output = out_path.resolve()
    if resolved_output.suffix.lower() != ".wav":
        errors.append("The MVP set renderer requires a .wav output path")
    if collection.schema_name != COLLECTION_SCHEMA:
        errors.append(f"Unsupported collection schema: {collection.schema_name}")
    if collection.schema_version != SCHEMA_VERSION:
        errors.append(
            f"Unsupported collection schema version {collection.schema_version}; "
            f"expected {SCHEMA_VERSION}"
        )
    if plan.schema_name != MIX_PLAN_SCHEMA:
        errors.append(f"Unsupported MixPlan schema: {plan.schema_name}")
    if plan.schema_version != SCHEMA_VERSION:
        errors.append(
            f"Unsupported MixPlan schema version {plan.schema_version}; expected {SCHEMA_VERSION}"
        )

    ordered_ids = plan.ordered_track_ids
    if abs(plan.brief.target_duration_minutes * 60.0 - plan.requested_duration_s) > 0.1:
        errors.append(
            "brief.target_duration_minutes and requested_duration_s must describe "
            "the same target"
        )
    if len(ordered_ids) < 2:
        errors.append("A rendered set requires at least two ordered track IDs")
    if len(set(ordered_ids)) != len(ordered_ids):
        errors.append("ordered_track_ids must not contain duplicates")

    track_by_id = {track.source.track_id: track for track in collection.tracks}
    allowed = set(plan.brief.hard_constraints.allowed_track_ids)
    excluded = set(plan.brief.hard_constraints.excluded_track_ids)
    if allowed:
        unexpected = [track_id for track_id in ordered_ids if track_id not in allowed]
        if unexpected:
            errors.append(f"Track IDs outside brief.allowed_track_ids: {unexpected}")
    blocked = [track_id for track_id in ordered_ids if track_id in excluded]
    if blocked:
        errors.append(f"Track IDs forbidden by brief.excluded_track_ids: {blocked}")
    unknown = [track_id for track_id in ordered_ids if track_id not in track_by_id]
    if unknown:
        errors.append(f"Unknown track IDs: {unknown}")

    segment_by_track: dict[str, PlannedTrackSegment] = {}
    segment_ids = [segment.segment_id for segment in plan.segments]
    if len(set(segment_ids)) != len(segment_ids):
        errors.append("segment_id values must be unique")
    for segment in plan.segments:
        if segment.track_id in segment_by_track:
            errors.append(f"Multiple segments supplied for track {segment.track_id}")
        segment_by_track[segment.track_id] = segment
    if set(segment_by_track) != set(ordered_ids):
        missing = [track_id for track_id in ordered_ids if track_id not in segment_by_track]
        extra = [track_id for track_id in segment_by_track if track_id not in ordered_ids]
        if missing:
            errors.append(f"Missing planned segments for track IDs: {missing}")
        if extra:
            errors.append(f"Segments reference unordered track IDs: {extra}")

    expected_pairs = list(zip(ordered_ids, ordered_ids[1:]))
    transition_ids = [transition.transition_id for transition in plan.transitions]
    if len(set(transition_ids)) != len(transition_ids):
        errors.append("transition_id values must be unique")
    actual_pairs = [(item.from_track_id, item.to_track_id) for item in plan.transitions]
    if actual_pairs != expected_pairs:
        errors.append(
            "Transitions must appear once per consecutive ordered-track pair "
            f"(expected {expected_pairs}, received {actual_pairs})"
        )

    validated_segments: list[ValidatedSegment] = []
    max_stretch = min(
        STRETCH_MAX_PERCENT,
        plan.brief.hard_constraints.max_time_stretch_percent,
    )
    for track_id in ordered_ids:
        track = track_by_id.get(track_id)
        segment = segment_by_track.get(track_id)
        if track is None or segment is None:
            continue
        source_path = resolve_source_path(source_folder, track)
        if source_path is None:
            errors.append(f"Could not resolve source file for {track_id}")
            continue
        actual_sha256 = sha256_file(source_path)
        if actual_sha256 != track.source.sha256_before:
            errors.append(
                f"Source hash mismatch for {track.source.filename}: "
                f"expected {track.source.sha256_before}, found {actual_sha256}"
            )
            continue
        grid = primary_grid(track)
        if grid is None:
            errors.append(f"No downbeat grid is available for {track.source.filename}")
            continue
        if segment.end_downbeat_index <= segment.start_downbeat_index:
            errors.append(f"Segment {segment.segment_id} must end after it starts")
            continue
        if segment.end_downbeat_index >= len(grid.downbeats_s):
            errors.append(
                f"Segment {segment.segment_id} end_downbeat_index "
                f"{segment.end_downbeat_index} exceeds the {len(grid.downbeats_s)}-downbeat grid"
            )
            continue
        start_s = float(grid.downbeats_s[segment.start_downbeat_index])
        end_s = float(grid.downbeats_s[segment.end_downbeat_index])
        if start_s < 0 or end_s <= start_s:
            errors.append(f"Segment {segment.segment_id} resolves to invalid time bounds")
            continue
        if track.stream.duration_s is not None and end_s > track.stream.duration_s + 0.1:
            errors.append(f"Segment {segment.segment_id} ends beyond the source duration")
            continue
        if not GAIN_DB_MIN <= segment.gain_db <= GAIN_DB_MAX:
            errors.append(
                f"Segment {segment.segment_id} gain {segment.gain_db:g} dB is outside "
                f"[{GAIN_DB_MIN:g}, {GAIN_DB_MAX:g}]"
            )
            continue
        source_bpm = _float_bpm(track)
        if source_bpm is None:
            errors.append(f"No usable BPM is available for {track.source.filename}")
            continue
        effective_bpm = segment.target_bpm or source_bpm
        stretch_percent = abs(effective_bpm - source_bpm) / source_bpm * 100.0
        if stretch_percent > max_stretch + 1e-9:
            errors.append(
                f"Segment {segment.segment_id} stretch {stretch_percent:.2f}% exceeds "
                f"the plan maximum {max_stretch:g}%"
            )
            continue
        estimated_duration = (end_s - start_s) * source_bpm / effective_bpm
        validated_segments.append(
            ValidatedSegment(
                plan=segment,
                track=track,
                source_path=source_path,
                source_sha256=actual_sha256,
                start_s=start_s,
                end_s=end_s,
                source_bpm=source_bpm,
                effective_bpm=effective_bpm,
                estimated_duration_s=estimated_duration,
            )
        )

    validated_transitions: list[ValidatedTransition] = []
    segment_lookup = {item.plan.track_id: item for item in validated_segments}
    for transition in plan.transitions:
        outgoing = segment_lookup.get(transition.from_track_id)
        incoming = segment_lookup.get(transition.to_track_id)
        if outgoing is None or incoming is None:
            continue
        bpm_difference = abs(outgoing.effective_bpm - incoming.effective_bpm)
        if bpm_difference > 0.2:
            errors.append(
                f"Transition {transition.transition_id} BPMs differ by {bpm_difference:.2f}; "
                "set matching target_bpm values before overlapping the tracks"
            )
            continue
        outgoing_grid = primary_grid(outgoing.track)
        incoming_grid = primary_grid(incoming.track)
        outgoing_transition_start = outgoing.plan.end_downbeat_index - transition.duration_bars
        incoming_transition_end = incoming.plan.start_downbeat_index + transition.duration_bars
        if outgoing_transition_start < outgoing.plan.start_downbeat_index:
            errors.append(
                f"Transition {transition.transition_id} needs {transition.duration_bars} "
                "outgoing bars before the segment endpoint"
            )
            continue
        if (
            outgoing_grid is None
            or incoming_grid is None
            or incoming_transition_end >= len(incoming_grid.downbeats_s)
        ):
            errors.append(
                f"Transition {transition.transition_id} does not have enough detected "
                "downbeats in both adjacent segments"
            )
            continue
        outgoing_source_duration = (
            outgoing_grid.downbeats_s[outgoing.plan.end_downbeat_index]
            - outgoing_grid.downbeats_s[outgoing_transition_start]
        )
        incoming_source_duration = (
            incoming_grid.downbeats_s[incoming_transition_end]
            - incoming_grid.downbeats_s[incoming.plan.start_downbeat_index]
        )
        duration_s = outgoing_source_duration * outgoing.source_bpm / outgoing.effective_bpm
        incoming_grid_duration_s = (
            incoming_source_duration * incoming.source_bpm / incoming.effective_bpm
        )
        grid_drift_s = abs(duration_s - incoming_grid_duration_s)
        if not MIX_CROSSFADE_S_MIN <= duration_s <= MIX_CROSSFADE_S_MAX:
            errors.append(
                f"Transition {transition.transition_id} resolves to {duration_s:.2f}s, outside "
                f"[{MIX_CROSSFADE_S_MIN:g}, {MIX_CROSSFADE_S_MAX:g}]"
            )
            continue
        if grid_drift_s > EVENT_MATCH_WINDOW_S:
            errors.append(
                f"Transition {transition.transition_id} detected downbeat grids drift by "
                f"{grid_drift_s:.3f}s over {transition.duration_bars} bars; adjust target BPM "
                "or cue selection before rendering"
            )
            continue
        if duration_s >= min(outgoing.estimated_duration_s, incoming.estimated_duration_s):
            errors.append(
                f"Transition {transition.transition_id} is not shorter than both adjacent segments"
            )
            continue
        validated_transitions.append(
            ValidatedTransition(
                plan=transition,
                duration_s=duration_s,
                incoming_grid_duration_s=incoming_grid_duration_s,
                grid_drift_s=grid_drift_s,
            )
        )

    planned_duration = sum(item.estimated_duration_s for item in validated_segments) - sum(
        item.duration_s for item in validated_transitions
    )
    if planned_duration <= 0:
        errors.append("The plan resolves to a non-positive set duration")
    elif len(validated_segments) == len(ordered_ids) and len(validated_transitions) == len(
        expected_pairs
    ):
        duration_tolerance = min(
            plan.requested_duration_s * 0.10,
            max((item.duration_s for item in validated_transitions), default=0.0),
        )
        if abs(planned_duration - plan.requested_duration_s) > duration_tolerance + 0.05:
            errors.append(
                f"Planned duration {planned_duration:.2f}s is outside tolerance of requested "
                f"duration {plan.requested_duration_s:.2f}s (±{duration_tolerance:.2f}s)"
            )
    if (
        plan.estimated_duration_s is not None
        and abs(plan.estimated_duration_s - planned_duration) > 0.1
    ):
        warnings.append(
            f"Plan estimated_duration_s={plan.estimated_duration_s:.2f} was replaced by the "
            f"validator calculation {planned_duration:.2f}."
        )

    if errors:
        raise MixPlanValidationError(errors)
    return ValidatedMixPlan(
        plan=plan,
        source_folder=source_folder,
        output_path=resolved_output,
        segments=tuple(validated_segments),
        transitions=tuple(validated_transitions),
        planned_duration_s=planned_duration,
        warnings=tuple(warnings),
    )


def _executed(tool: str, arguments: dict) -> dict:
    return {
        "tool": tool,
        "tool_contract_version": "1",
        "authority": AUTHORITY_EXECUTED,
        "arguments": arguments,
    }


def render_set(
    collection: CollectionAnalysis,
    plan: MixPlan,
    *,
    out_path: Path,
) -> RenderManifest:
    """Validate and render a MixPlan to atomic 32-bit float PCM WAV output."""
    validated = validate_mix_plan(collection, plan, out_path=out_path)
    ensure_output_path(validated.output_path, source_folder=validated.source_folder)
    ffmpeg_version, _ffprobe_version = require_ffmpeg()
    work = Path(
        tempfile.mkdtemp(
            prefix=f".{validated.output_path.stem}.render-",
            dir=validated.output_path.parent,
        )
    )
    executed: list[dict] = []
    warnings = list(validated.warnings)
    rendered_segments: list[Path] = []
    try:
        for index, segment in enumerate(validated.segments):
            loaded = work / f"segment-{index:02d}-loaded.wav"
            artifact = load_track(
                segment.source_path,
                start_s=segment.start_s,
                end_s=segment.end_s,
                out_path=loaded,
                source_folder=validated.source_folder,
            )
            warnings.extend(artifact.warnings)
            executed.append(
                _executed(
                    "load_track",
                    {
                        "track_id": segment.plan.track_id,
                        "start_downbeat_index": segment.plan.start_downbeat_index,
                        "end_downbeat_index": segment.plan.end_downbeat_index,
                        "start_s": segment.start_s,
                        "end_s": segment.end_s,
                    },
                )
            )
            current = loaded
            if abs(segment.effective_bpm - segment.source_bpm) > 1e-9:
                stretched = work / f"segment-{index:02d}-stretched.wav"
                artifact = time_stretch(
                    current,
                    from_bpm=segment.source_bpm,
                    target_bpm=segment.effective_bpm,
                    out_path=stretched,
                    source_folder=validated.source_folder,
                )
                current = stretched
                warnings.extend(artifact.warnings)
                executed.append(
                    _executed(
                        "time_stretch",
                        {
                            "track_id": segment.plan.track_id,
                            "from_bpm": segment.source_bpm,
                            "target_bpm": segment.effective_bpm,
                        },
                    )
                )
            if abs(segment.plan.gain_db) > 1e-9:
                gained = work / f"segment-{index:02d}-gained.wav"
                artifact = set_gain(
                    current,
                    gain_db=segment.plan.gain_db,
                    out_path=gained,
                    source_folder=validated.source_folder,
                )
                current = gained
                warnings.extend(artifact.warnings)
                executed.append(
                    _executed(
                        "set_gain",
                        {"track_id": segment.plan.track_id, "gain_db": segment.plan.gain_db},
                    )
                )
            rendered_segments.append(current)

        current_mix = rendered_segments[0]
        for index, (incoming, transition) in enumerate(
            zip(rendered_segments[1:], validated.transitions),
            start=1,
        ):
            mixed = work / f"mix-{index:02d}.wav"
            if transition.plan.style == "house_eq_v1":
                artifact = house_transition(
                    current_mix,
                    incoming,
                    duration_s=transition.duration_s,
                    out_path=mixed,
                    source_folder=validated.source_folder,
                )
                operation_name = "house_transition"
            else:
                artifact = crossfade(
                    current_mix,
                    incoming,
                    duration_s=transition.duration_s,
                    out_path=mixed,
                    source_folder=validated.source_folder,
                )
                operation_name = "crossfade"
            current_mix = mixed
            warnings.extend(artifact.warnings)
            executed.append(
                _executed(
                    operation_name,
                    {
                        "transition_id": transition.plan.transition_id,
                        "from_track_id": transition.plan.from_track_id,
                        "to_track_id": transition.plan.to_track_id,
                        "duration_bars": transition.plan.duration_bars,
                        "duration_s": transition.duration_s,
                        "incoming_grid_duration_s": transition.incoming_grid_duration_s,
                        "grid_drift_s": transition.grid_drift_s,
                        "style": transition.plan.style,
                        "curve": transition.plan.curve,
                    },
                )
            )

        final_temporary = work / "final.wav"
        shutil.copy2(current_mix, final_temporary)
        rendered_duration = probe_duration_s(final_temporary)
        output_sha256 = sha256_file(final_temporary)
        measurement = ffmpeg_loudnorm(final_temporary, ffmpeg_version)
        source_records = []
        for item in validated.segments:
            current_sha256 = sha256_file(item.source_path)
            unchanged = current_sha256 == item.source_sha256
            source_records.append(
                {
                    "track_id": item.plan.track_id,
                    "sha256": current_sha256,
                    "source_unchanged": unchanged,
                }
            )
            if not unchanged:
                raise RenderError(
                    f"Source hash changed during set render: {item.track.source.filename}"
                )
        os.replace(final_temporary, validated.output_path)
        output_measurements = {
            "integrated_lufs": measurement.get("integrated"),
            "loudness_range_lu": measurement.get("range"),
            "true_peak_dbtp": measurement.get("true_peak"),
            "sample_rate_hz": RENDER_SAMPLE_RATE_HZ,
        }
        true_peak = measurement.get("true_peak")
        if isinstance(true_peak, (int, float)) and true_peak > -1.0:
            warnings.append(
                f"Rendered true peak is {true_peak:.2f} dBTP; mastering/headroom is not yet applied."
            )
        if abs(rendered_duration - validated.planned_duration_s) > 0.1:
            warnings.append(
                "Rendered duration differs from planned duration by "
                f"{rendered_duration - validated.planned_duration_s:+.3f}s."
            )
        return RenderManifest(
            render_id=str(uuid.uuid4()),
            plan_id=plan.plan_id,
            renderer={
                "name": "ffmpeg-set-renderer",
                "version": "mvp-1",
                "ffmpeg_version": ffmpeg_version,
            },
            source_track_hashes=source_records,
            executed_operations=executed,
            requested_duration_s=plan.requested_duration_s,
            planned_duration_s=validated.planned_duration_s,
            rendered_duration_s=rendered_duration,
            output_path=str(validated.output_path),
            output_sha256=output_sha256,
            output_measurements=output_measurements,
            status="passed",
            warnings=list(dict.fromkeys(warnings)),
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)


def write_render_manifest(
    manifest: RenderManifest,
    path: Path,
    *,
    source_folder: Path,
) -> Path:
    """Atomically persist a render manifest outside the source collection."""
    resolved = ensure_output_path(path, source_folder=source_folder)
    temporary = resolved.with_name(f".{resolved.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_text(
            manifest.model_dump_json(indent=2, by_alias=True),
            encoding="utf-8",
        )
        os.replace(temporary, resolved)
    finally:
        temporary.unlink(missing_ok=True)
    return resolved


def load_mix_plan(path: Path) -> MixPlan:
    """Load a strict MixPlan JSON document."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MixPlanValidationError([f"Could not read MixPlan JSON: {exc}"]) from exc
    try:
        return MixPlan.model_validate(payload)
    except ValueError as exc:
        raise MixPlanValidationError([str(exc)]) from exc
