from pathlib import Path

from dj_collection_set_builder.analyze import (
    assemble_track,
    beat_this_is_reusable,
    ingest_is_reusable,
    ingest_payload_from_track,
    track_needs_rerun,
)
from dj_collection_set_builder.constants import AUTHORITY_ESTIMATE
from dj_collection_set_builder.engines import EngineResult
from dj_collection_set_builder.ingest import sha256_file
from dj_collection_set_builder.memory import memory_snapshot
from dj_collection_set_builder.models import (
    AnalyzerFailure,
    FeatureValue,
    GridDiagnostics,
    KeyAnalysis,
    LoudnessAnalysis,
    RhythmGrid,
    StreamFacts,
    TempoAnalysis,
    TempoConsensus,
    TrackAnalysis,
    TrackSource,
)


def _track(**kwargs) -> TrackAnalysis:
    shared = dict(
        authority="standardized_measurement",
        status="passed",
        source_tool="ffmpeg",
        tool_version="8.0.1",
    )
    defaults = dict(
        analysis_id="t",
        analyzed_at="2026-09-03T00:00:00Z",
        source=TrackSource(
            track_id="sha256:x",
            path="a.mp3",
            filename="a.mp3",
            size_bytes=1,
            sha256_before="x",
            sha256_after="x",
            source_unchanged=True,
        ),
        stream=StreamFacts(status="passed"),
        loudness=LoudnessAnalysis(
            integrated=FeatureValue(value=-10.0, unit="LUFS", **shared),
            range=FeatureValue(value=5.0, unit="LU", **shared),
            true_peak=FeatureValue(value=-1.0, unit="dBTP", **shared),
            primary_tool={"name": "ffmpeg"},
            validator={"name": "pyloudnorm", "passed": True},
        ),
        tempo=TempoAnalysis(
            selected_candidate=FeatureValue(
                value=126.0,
                unit="BPM",
                authority=AUTHORITY_ESTIMATE,
                status="warning",
                source_tool="all-in-one-mlx",
            ),
            consensus=TempoConsensus(tolerance_bpm=0.2),
            grid_diagnostics=GridDiagnostics(),
        ),
        key=KeyAnalysis(),
        rhythm_grids=[
            RhythmGrid(
                source_tool="all-in-one-mlx",
                beats_s=[0.0, 0.5],
                downbeats_s=[0.0],
                beat_count=2,
                downbeat_count=1,
            )
        ],
    )
    defaults.update(kwargs)
    return TrackAnalysis(**defaults)


def test_complete_track_does_not_need_rerun():
    assert track_needs_rerun(_track()) is False


def test_failed_allin1_needs_rerun():
    track = _track(
        analyzer_failures=[
            AnalyzerFailure(analyzer="all-in-one-mlx", error_type="OSError", message="ENOSPC")
        ],
        rhythm_grids=[
            RhythmGrid(source_tool="all-in-one-mlx", beat_count=0, downbeat_count=0, status="failed")
        ],
    )
    assert track_needs_rerun(track) is True


def test_partial_track_reuses_ingest_and_beat_this():
    track = _track(
        key=KeyAnalysis(tonic="B", mode="minor", standard_name="B minor", camelot="10A"),
        analyzer_failures=[
            AnalyzerFailure(analyzer="all-in-one-mlx", error_type="EngineError", message="RSS cap")
        ],
        rhythm_grids=[
            RhythmGrid(source_tool="all-in-one-mlx", beat_count=0, downbeat_count=0, status="failed"),
            RhythmGrid(
                source_tool="beat-this",
                beats_s=[0.0, 0.5, 1.0],
                downbeats_s=[0.0],
                beat_count=3,
                downbeat_count=1,
            ),
        ],
        warnings=["Beat This return order: postprocessor-beats-then-downbeats"],
    )
    assert ingest_is_reusable(track) is True
    assert beat_this_is_reusable(track) is True
    payload = ingest_payload_from_track(track)
    assert payload["key"]["tonic"] == "B"
    assert payload["analyzer_failures"] == []


def test_memory_snapshot_reads_this_machine():
    snapshot = memory_snapshot()
    assert snapshot.total_bytes >= 8 * 1024**3
    assert snapshot.reclaimable_bytes >= 0
    assert snapshot.swap_used_bytes >= 0


def test_engine_result_roundtrip_keeps_segments():
    original = EngineResult(
        beats_s=[0.0, 0.5],
        downbeats_s=[0.0],
        bpm=128.0,
        segments=[{"start": 0.0, "end": 8.0, "label": "intro"}],
        extra={"model": "harmonix-all"},
        tool_version="0.0-test",
    )
    restored = EngineResult.from_dict(original.as_dict())
    assert restored.bpm == 128.0
    assert restored.segments[0]["label"] == "intro"


def test_assemble_track_from_staged_payloads(tmp_path: Path):
    mp3 = tmp_path / "a.mp3"
    mp3.write_bytes(b"not-audio")
    digest = sha256_file(mp3)
    base = _track()
    ingest = {
        "source": {
            **base.source.model_dump(mode="json"),
            "path": str(mp3),
            "filename": mp3.name,
            "sha256_before": digest,
        },
        "stream": base.stream.model_dump(mode="json"),
        "loudness": base.loudness.model_dump(mode="json"),
        "key": base.key.model_dump(mode="json"),
        "warnings": [],
        "analyzer_failures": [],
    }
    allin1 = EngineResult(
        beats_s=[0.0, 0.5, 1.0],
        downbeats_s=[0.0],
        bpm=128.0,
        segments=[{"start": 0.0, "end": 8.0, "label": "intro"}],
        tool_version="0.0-test",
    )
    beat = EngineResult(
        beats_s=[0.0, 0.5, 1.0],
        downbeats_s=[0.0],
        tool_version="0.0-test",
        return_order="postprocessor-beats-then-downbeats",
    )
    track = assemble_track(ingest, allin1, beat, path=mp3)
    assert track.source.source_unchanged is True
    assert track.tempo.selected_candidate.value == 128.0
    assert track.sections
    assert track_needs_rerun(track) is False


def test_max_tracks_stops_after_one_new_file(tmp_path: Path, monkeypatch):
    from dj_collection_set_builder.analyze import analyze_folder

    music = tmp_path / "music"
    music.mkdir()
    (music / "a.mp3").write_bytes(b"one")
    (music / "b.mp3").write_bytes(b"two")
    calls: list[str] = []

    def fake_isolated(path, folder, **kwargs):
        calls.append(path.name)
        digest = sha256_file(path)
        track = _track()
        return track.model_copy(
            update={
                "source": track.source.model_copy(
                    update={
                        "filename": path.name,
                        "path": str(path),
                        "sha256_before": digest,
                        "sha256_after": digest,
                    }
                )
            }
        )

    monkeypatch.setattr(
        "dj_collection_set_builder.analyze._analyze_track_isolated",
        fake_isolated,
    )
    monkeypatch.setattr(
        "dj_collection_set_builder.analyze.wait_for_ram_headroom",
        lambda **kwargs: None,
    )
    monkeypatch.setattr(
        "dj_collection_set_builder.analyze.wait_for_ram_recovery",
        lambda **kwargs: None,
    )

    out = tmp_path / "out.json"
    collection = analyze_folder(
        music,
        out,
        max_tracks=1,
        pause_between_tracks_s=0,
        min_reclaimable_ram_mb=0,
        keep_work=True,
    )
    assert calls == ["a.mp3"]
    assert len(collection.tracks) == 1
    assert any("--max-tracks 1" in item for item in collection.warnings)
