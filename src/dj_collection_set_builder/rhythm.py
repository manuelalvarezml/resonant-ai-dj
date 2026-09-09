"""Rhythm diagnostics, consensus, sections, and downbeat-derived loop candidates."""

from __future__ import annotations

import math

import numpy as np

from dj_collection_set_builder.constants import (
    AUTHORITY_ESTIMATE,
    EVENT_MATCH_WINDOW_S,
    LOOP_BAR_SIZES,
    STATUS_PASSED,
    STATUS_REJECTED,
    STATUS_WARNING,
    TEMPO_CONSENSUS_TOLERANCE_BPM,
)
from dj_collection_set_builder.models import (
    FeatureValue,
    GridDiagnostics,
    LoopCandidate,
    RhythmChallenger,
    RhythmGrid,
    Section,
    TempoAnalysis,
    TempoConsensus,
    failed_feature,
)


def _as_float_list(values) -> list[float]:
    return [float(value) for value in list(values or [])]


def bpm_from_intervals(events_s: list[float]) -> float | None:
    if len(events_s) < 2:
        return None
    intervals = np.diff(np.asarray(events_s, dtype=float))
    intervals = intervals[intervals > 0]
    if intervals.size == 0:
        return None
    median = float(np.median(intervals))
    if median <= 0:
        return None
    return 60.0 / median


def is_half_double(bpm_a: float | None, bpm_b: float | None, tolerance_bpm: float) -> bool:
    if bpm_a is None or bpm_b is None:
        return False
    if bpm_a <= 0 or bpm_b <= 0:
        return False
    return (
        abs(bpm_a - (2.0 * bpm_b)) <= tolerance_bpm
        or abs(bpm_b - (2.0 * bpm_a)) <= tolerance_bpm
    )


def event_f1(reference: list[float], estimate: list[float], window_s: float = EVENT_MATCH_WINDOW_S) -> float | None:
    if not reference or not estimate:
        return None
    ref = np.asarray(reference, dtype=float)
    est = np.asarray(estimate, dtype=float)
    matched_ref: set[int] = set()
    true_positives = 0
    for time in est:
        deltas = np.abs(ref - time)
        index = int(np.argmin(deltas))
        if deltas[index] <= window_s and index not in matched_ref:
            matched_ref.add(index)
            true_positives += 1
    precision = true_positives / len(est)
    recall = true_positives / len(ref)
    if precision + recall == 0:
        return 0.0
    return float(2 * precision * recall / (precision + recall))


def nearest_event_index(events: list[float], time_s: float) -> int | None:
    if not events:
        return None
    array = np.asarray(events, dtype=float)
    return int(np.argmin(np.abs(array - time_s)))


def has_nearby_event(events: list[float], time_s: float, window_s: float = EVENT_MATCH_WINDOW_S) -> bool:
    if not events:
        return False
    return min(abs(event - time_s) for event in events) <= window_s


def grid_diagnostics(beats_s: list[float]) -> GridDiagnostics:
    if len(beats_s) < 2:
        return GridDiagnostics()
    beats = np.asarray(beats_s, dtype=float)
    intervals = np.diff(beats)
    intervals = intervals[intervals > 0]
    if intervals.size == 0:
        return GridDiagnostics()
    median_interval = float(np.median(intervals))
    instant_bpm = 60.0 / intervals
    grid = beats[0] + np.arange(len(beats)) * median_interval
    residuals_ms = (beats - grid) * 1000.0
    return GridDiagnostics(
        median_interval_s=median_interval,
        tempo_variability_bpm=float(np.std(instant_bpm)),
        fixed_grid_residual_ms_p50=float(np.percentile(np.abs(residuals_ms), 50)),
        fixed_grid_residual_ms_p95=float(np.percentile(np.abs(residuals_ms), 95)),
        end_drift_ms=float((beats[-1] - grid[-1]) * 1000.0),
    )


def downbeat_phase_warning(
    primary_downbeats: list[float],
    challenger_downbeats: list[float],
    beats_s: list[float],
) -> bool:
    if not primary_downbeats or not challenger_downbeats:
        return False
    primary = np.asarray(primary_downbeats, dtype=float)
    residuals = []
    for time in challenger_downbeats:
        residuals.append(abs(time - primary[np.argmin(np.abs(primary - time))]))
    median_residual = float(np.median(residuals))
    beat_interval = None
    if len(beats_s) >= 2:
        beat_interval = float(np.median(np.diff(np.asarray(beats_s, dtype=float))))
    if beat_interval and beat_interval > 0:
        return median_residual > (0.15 * beat_interval)
    return median_residual > EVENT_MATCH_WINDOW_S


def _segment_field(segment, name: str):
    if isinstance(segment, dict):
        return segment[name]
    return getattr(segment, name)


def build_sections(
    segments,
    downbeats_s: list[float],
    *,
    source_tool: str,
    tool_version: str | None,
) -> list[Section]:
    sections: list[Section] = []
    for index, segment in enumerate(segments or [], start=1):
        start_s = float(_segment_field(segment, "start"))
        end_s = float(_segment_field(segment, "end"))
        label = str(_segment_field(segment, "label") or "")
        start_idx = nearest_event_index(downbeats_s, start_s)
        end_idx = nearest_event_index(downbeats_s, end_s)
        sections.append(
            Section(
                section_id=f"section-{index:02d}",
                start_s=start_s,
                end_s=end_s,
                start_downbeat_index=start_idx,
                end_downbeat_index=end_idx,
                label=label or None,
                authority=AUTHORITY_ESTIMATE,
                source_tool=source_tool,
                tool_version=tool_version,
                warnings=["Section labels are structural estimates, not loop instructions."],
            )
        )
    return sections


def containing_section(start_s: float, end_s: float, sections: list[Section]) -> Section | None:
    contained = [
        section
        for section in sections
        if start_s >= section.start_s - 1e-6 and end_s <= section.end_s + 1e-6
    ]
    if not contained:
        return None
    return min(contained, key=lambda section: section.end_s - section.start_s)


def crosses_section_boundary(start_s: float, end_s: float, sections: list[Section]) -> bool:
    for section in sections:
        for boundary in (section.start_s, section.end_s):
            if start_s + 1e-6 < boundary < end_s - 1e-6:
                return True
    return False


def build_loop_candidates(
    track_id: str,
    downbeats_s: list[float],
    sections: list[Section],
    challenger_downbeats: list[float] | None,
) -> list[LoopCandidate]:
    candidates: list[LoopCandidate] = []
    if len(downbeats_s) < 5:
        return candidates
    for start_index, start_s in enumerate(downbeats_s):
        for bars in LOOP_BAR_SIZES:
            end_index = start_index + bars
            if end_index >= len(downbeats_s):
                continue
            end_s = downbeats_s[end_index]
            section = containing_section(start_s, end_s, sections)
            engines_agree = None
            if challenger_downbeats is not None:
                engines_agree = has_nearby_event(
                    challenger_downbeats, start_s
                ) and has_nearby_event(challenger_downbeats, end_s)
            crosses = crosses_section_boundary(start_s, end_s, sections)
            if engines_agree is False:
                status = STATUS_REJECTED
            elif section is not None and not crosses:
                status = STATUS_PASSED
            else:
                status = STATUS_WARNING
            candidates.append(
                LoopCandidate(
                    loop_id=f"loop-{start_index:03d}-{bars}",
                    track_id=track_id,
                    start_downbeat_index=start_index,
                    start_s=float(start_s),
                    bars=bars,
                    end_s=float(end_s),
                    contained_in_section_id=section.section_id if section else None,
                    crosses_novelty_boundary=crosses,
                    rhythm_sources_agree=engines_agree,
                    status=status,
                )
            )
    return candidates


def combine_tempo_and_grids(
    *,
    allin1_bpm: float | None,
    allin1_beats: list[float],
    allin1_downbeats: list[float],
    allin1_version: str | None,
    beat_this_beats: list[float] | None,
    beat_this_downbeats: list[float] | None,
    beat_this_version: str | None,
    beat_this_error: str | None,
    allin1_error: str | None,
) -> tuple[TempoAnalysis, list[RhythmGrid]]:
    allin1_beats = _as_float_list(allin1_beats)
    allin1_downbeats = _as_float_list(allin1_downbeats)
    beat_this_beats = _as_float_list(beat_this_beats) if beat_this_beats is not None else None
    beat_this_downbeats = (
        _as_float_list(beat_this_downbeats) if beat_this_downbeats is not None else None
    )

    allin1_interval_bpm = bpm_from_intervals(allin1_beats)
    selected_bpm = float(allin1_bpm) if allin1_bpm is not None else allin1_interval_bpm
    selected_tool = "all-in-one-mlx"
    selected_version = allin1_version
    if selected_bpm is None and beat_this_beats:
        selected_bpm = bpm_from_intervals(beat_this_beats)
        selected_tool = "beat-this"
        selected_version = beat_this_version

    if selected_bpm is None:
        selected = failed_feature(
            unit="BPM",
            source_tool=selected_tool,
            tool_version=selected_version,
            message=allin1_error or "No tempo candidate could be derived",
        )
    else:
        selected = FeatureValue(
            value=float(selected_bpm),
            unit="BPM",
            authority=AUTHORITY_ESTIMATE,
            status=STATUS_WARNING,
            source_tool=selected_tool,
            tool_version=selected_version,
            model_id="harmonix-all" if selected_tool == "all-in-one-mlx" else "final0",
            parameters={"note": "Tempo remains a benchmark_estimate even when engines agree."},
            warnings=["Tempo is a benchmark estimate, not a musical fact."],
        )

    alternates: list[FeatureValue] = []
    beat_this_bpm = bpm_from_intervals(beat_this_beats) if beat_this_beats else None
    if beat_this_bpm is not None:
        alternates.append(
            FeatureValue(
                value=float(beat_this_bpm),
                unit="BPM",
                authority=AUTHORITY_ESTIMATE,
                status=STATUS_WARNING,
                source_tool="beat-this-derived",
                tool_version=beat_this_version,
                parameters={"method": "median-beat-interval", "dbn": False},
                warnings=["Derived from Beat This beat intervals."],
            )
        )
    if allin1_interval_bpm is not None and (
        selected_bpm is None or not math.isclose(allin1_interval_bpm, float(selected_bpm), abs_tol=0.05)
    ):
        alternates.append(
            FeatureValue(
                value=float(allin1_interval_bpm),
                unit="BPM",
                authority=AUTHORITY_ESTIMATE,
                status=STATUS_WARNING,
                source_tool="all-in-one-mlx-derived",
                tool_version=allin1_version,
                parameters={"method": "median-beat-interval"},
            )
        )

    difference = None
    if selected_bpm is not None and beat_this_bpm is not None:
        difference = abs(float(selected_bpm) - float(beat_this_bpm))
    half_double = is_half_double(selected_bpm, beat_this_bpm, TEMPO_CONSENSUS_TOLERANCE_BPM)
    agrees = None
    if difference is not None:
        agrees = difference <= TEMPO_CONSENSUS_TOLERANCE_BPM

    diagnostics_source = allin1_beats or (beat_this_beats or [])
    tempo = TempoAnalysis(
        selected_candidate=selected,
        alternates=alternates,
        consensus=TempoConsensus(
            difference_bpm=difference,
            half_double_ambiguity=half_double,
            agrees_within_tolerance=agrees,
            tolerance_bpm=TEMPO_CONSENSUS_TOLERANCE_BPM,
        ),
        grid_diagnostics=grid_diagnostics(diagnostics_source),
    )

    grids: list[RhythmGrid] = []
    if allin1_beats or allin1_error:
        challenger = None
        if beat_this_beats is not None:
            challenger = RhythmChallenger(
                source_tool="beat-this",
                tool_version=beat_this_version,
                beat_match_f1=event_f1(allin1_beats, beat_this_beats),
                downbeat_match_f1=event_f1(allin1_downbeats, beat_this_downbeats or []),
                phase_warning=downbeat_phase_warning(
                    allin1_downbeats, beat_this_downbeats or [], allin1_beats
                ),
            )
        warnings = ["Beat and downbeat times are benchmark estimates."]
        if allin1_error:
            warnings.append(allin1_error)
        if beat_this_error:
            warnings.append(beat_this_error)
        grids.append(
            RhythmGrid(
                authority=AUTHORITY_ESTIMATE,
                status=STATUS_WARNING if allin1_beats else "failed",
                source_tool="all-in-one-mlx",
                tool_version=allin1_version,
                tempo_bpm=float(selected_bpm) if selected_bpm is not None else None,
                meter_numerator=4,
                beats_s=allin1_beats,
                downbeats_s=allin1_downbeats,
                beat_count=len(allin1_beats),
                downbeat_count=len(allin1_downbeats),
                challenger=challenger,
                warnings=warnings,
            )
        )
    if beat_this_beats:
        grids.append(
            RhythmGrid(
                authority=AUTHORITY_ESTIMATE,
                status=STATUS_WARNING,
                source_tool="beat-this",
                tool_version=beat_this_version,
                tempo_bpm=beat_this_bpm,
                meter_numerator=4,
                beats_s=beat_this_beats,
                downbeats_s=beat_this_downbeats or [],
                beat_count=len(beat_this_beats),
                downbeat_count=len(beat_this_downbeats or []),
                warnings=["Independent rhythm challenger. DBN postprocessor disabled."],
            )
        )
    return tempo, grids
