from pathlib import Path

from dj_collection_set_builder.constants import AUTHORITY_ESTIMATE
from dj_collection_set_builder.models import (
    CollectionAnalysis,
    FeatureValue,
    GridDiagnostics,
    KeyAnalysis,
    LoopCandidate,
    LoudnessAnalysis,
    RhythmGrid,
    Section,
    StreamFacts,
    TempoAnalysis,
    TempoConsensus,
    TrackAnalysis,
    TrackSource,
)
from dj_collection_set_builder.summaries import (
    UnknownTrackError,
    find_track,
    get_track_summary,
    get_transition_windows,
)

import pytest


def _track() -> TrackAnalysis:
    shared = dict(
        authority="standardized_measurement",
        status="passed",
        source_tool="ffmpeg",
    )
    downbeats = [index * 2.0 for index in range(20)]
    return TrackAnalysis(
        analysis_id="t",
        analyzed_at="2026-09-04T00:00:00Z",
        source=TrackSource(
            track_id="sha256:abc123",
            path="example.mp3",
            filename="example.mp3",
            size_bytes=1,
            sha256_before="abc123",
            sha256_after="abc123",
            source_unchanged=True,
        ),
        stream=StreamFacts(status="passed", duration_s=180.0),
        loudness=LoudnessAnalysis(
            integrated=FeatureValue(value=-10.0, unit="LUFS", **shared),
            range=FeatureValue(value=6.0, unit="LU", **shared),
            true_peak=FeatureValue(value=-1.0, unit="dBTP", **shared),
            primary_tool={"name": "ffmpeg"},
            validator={"name": "pyloudnorm", "passed": True},
        ),
        tempo=TempoAnalysis(
            selected_candidate=FeatureValue(
                value=128.0,
                unit="BPM",
                authority=AUTHORITY_ESTIMATE,
                status="warning",
                source_tool="all-in-one-mlx",
            ),
            consensus=TempoConsensus(tolerance_bpm=0.2),
            grid_diagnostics=GridDiagnostics(),
        ),
        key=KeyAnalysis(
            standard_name="A minor",
            camelot="8A",
            strength=0.7,
        ),
        rhythm_grids=[
            RhythmGrid(
                source_tool="all-in-one-mlx",
                beats_s=list(range(80)),
                downbeats_s=downbeats,
                beat_count=80,
                downbeat_count=20,
            )
        ],
        sections=[
            Section(
                section_id="s1",
                start_s=0.0,
                end_s=32.0,
                label="intro",
                source_tool="all-in-one-mlx",
            )
        ],
        loop_candidates=[
            LoopCandidate(
                loop_id="good-8",
                track_id="sha256:abc123",
                start_downbeat_index=0,
                start_s=0.0,
                bars=8,
                end_s=16.0,
                contained_in_section_id="s1",
                crosses_novelty_boundary=False,
                rhythm_sources_agree=True,
                status="passed",
            ),
            LoopCandidate(
                loop_id="crosses",
                track_id="sha256:abc123",
                start_downbeat_index=4,
                start_s=8.0,
                bars=8,
                end_s=24.0,
                crosses_novelty_boundary=True,
                status="warning",
            ),
            LoopCandidate(
                loop_id="four-bar",
                track_id="sha256:abc123",
                start_downbeat_index=0,
                start_s=0.0,
                bars=4,
                end_s=8.0,
                crosses_novelty_boundary=False,
                status="passed",
            ),
        ],
    )


def _collection() -> CollectionAnalysis:
    return CollectionAnalysis(
        collection_id="col-1",
        input_folder="tmp",
        created_at="2026-09-04T00:00:00Z",
        platform={"os": "macOS", "architecture": "arm64", "python": "3.12.10", "ffmpeg": "8.0.1"},
        expected_audio_count=1,
        discovered_audio_count=1,
        tracks=[_track()],
    )


def test_find_track_accepts_id_hash_and_filename():
    collection = _collection()
    by_id = find_track(collection, "sha256:abc123")
    by_hash = find_track(collection, "abc123")
    by_name = find_track(collection, "example.mp3")
    assert by_id.source.filename == by_hash.source.filename == by_name.source.filename


def test_unknown_track_raises():
    with pytest.raises(UnknownTrackError):
        find_track(_collection(), "missing")


def test_summary_is_compact_and_keeps_estimate_note():
    summary = get_track_summary(_track())
    payload = summary.model_dump(mode="json")
    assert "beats_s" not in payload
    assert summary.bpm == 128.0
    assert summary.bpm_authority == AUTHORITY_ESTIMATE
    assert summary.camelot == "8A"
    assert summary.loudness_lufs == -10.0
    assert summary.preferred_loop_count == 1
    assert summary.section_count == 1
    assert "benchmark_estimate" in summary.note


def test_transition_windows_omit_full_grids_and_novelty_crossing_loops():
    windows = get_transition_windows(_track())
    payload = windows.model_dump(mode="json")
    assert "beats_s" not in payload
    assert windows.downbeat_count == 20
    assert windows.downbeat_anchors_s[:8] == [index * 2.0 for index in range(8)]
    assert windows.downbeat_anchors_s[-8:] == [index * 2.0 for index in range(12, 20)]
    assert [item["loop_id"] for item in windows.preferred_loops] == ["good-8"]
    assert windows.sections[0]["label"] == "intro"


def test_corpus_summaries_do_not_require_full_beat_arrays():
    path = Path("output/step1-collection.json")
    if not path.exists():
        return
    collection = CollectionAnalysis.model_validate_json(path.read_text(encoding="utf-8"))
    track = collection.tracks[0]
    summary = get_track_summary(track)
    windows = get_transition_windows(track)
    assert summary.filename == track.source.filename
    assert summary.duration_s == track.stream.duration_s
    assert "beats_s" not in summary.model_dump(mode="json")
    assert windows.downbeat_count == track.rhythm_grids[0].downbeat_count
