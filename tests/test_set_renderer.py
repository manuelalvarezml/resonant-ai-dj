import json
import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from dj_collection_set_builder.constants import AUTHORITY_ESTIMATE
from dj_collection_set_builder.ingest import sha256_file
from dj_collection_set_builder.models import (
    CollectionAnalysis,
    FeatureValue,
    GridDiagnostics,
    KeyAnalysis,
    LoudnessAnalysis,
    MixBrief,
    MixPlan,
    PlannedTrackSegment,
    PlannedTransition,
    RhythmGrid,
    StreamFacts,
    TempoAnalysis,
    TempoConsensus,
    TrackAnalysis,
    TrackSource,
)
from dj_collection_set_builder.set_renderer import (
    MixPlanValidationError,
    render_set,
    validate_mix_plan,
    write_render_manifest,
)
from dj_collection_set_builder.render_cli import app


def _write_sine(path: Path, *, frequency: int, duration_s: float = 6.0) -> Path:
    completed = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency={frequency}:sample_rate=44100:duration={duration_s}",
            "-ac",
            "2",
            "-c:a",
            "pcm_f32le",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return path


def _track(path: Path, music: Path, *, index: int) -> TrackAnalysis:
    digest = sha256_file(path)
    measured = dict(
        authority="standardized_measurement",
        status="passed",
        source_tool="ffmpeg",
        tool_version="test",
    )
    return TrackAnalysis(
        analysis_id=f"analysis-{index}",
        analyzed_at="2026-09-04T00:00:00Z",
        source=TrackSource(
            track_id=f"sha256:{digest}",
            path=str(path.relative_to(music.parent)),
            filename=path.name,
            size_bytes=path.stat().st_size,
            sha256_before=digest,
            sha256_after=digest,
            source_unchanged=True,
        ),
        stream=StreamFacts(
            status="passed",
            duration_s=6.0,
            sample_rate_hz=44100,
            channels=2,
        ),
        loudness=LoudnessAnalysis(
            integrated=FeatureValue(value=-18.0, unit="LUFS", **measured),
            range=FeatureValue(value=0.0, unit="LU", **measured),
            true_peak=FeatureValue(value=-18.0, unit="dBTP", **measured),
            primary_tool={"name": "ffmpeg"},
            validator={"name": "test", "passed": True},
        ),
        tempo=TempoAnalysis(
            selected_candidate=FeatureValue(
                value=240.0,
                unit="BPM",
                authority=AUTHORITY_ESTIMATE,
                status="warning",
                source_tool="test-grid",
            ),
            consensus=TempoConsensus(tolerance_bpm=0.2),
            grid_diagnostics=GridDiagnostics(),
        ),
        rhythm_grids=[
            RhythmGrid(
                source_tool="all-in-one-mlx",
                tool_version="test",
                beats_s=[step * 0.25 for step in range(25)],
                downbeats_s=[float(step) for step in range(7)],
                beat_count=25,
                downbeat_count=7,
            )
        ],
        key=KeyAnalysis(
            tonic="A",
            mode="minor",
            standard_name="A minor",
            camelot="8A",
            strength=0.9,
        ),
    )


def _collection_and_plan(tmp_path: Path) -> tuple[CollectionAnalysis, MixPlan, Path]:
    music = tmp_path / "music"
    music.mkdir()
    tracks = [
        _track(_write_sine(music / "a.wav", frequency=220), music, index=1),
        _track(_write_sine(music / "b.wav", frequency=330), music, index=2),
        _track(_write_sine(music / "c.wav", frequency=440), music, index=3),
    ]
    collection = CollectionAnalysis(
        collection_id="collection-test",
        input_folder=str(music),
        created_at="2026-09-04T00:00:00Z",
        platform={
            "os": "test",
            "architecture": "test",
            "python": "3.12",
            "ffmpeg": "test",
        },
        discovered_audio_count=3,
        tracks=tracks,
    )
    ids = [track.source.track_id for track in tracks]
    plan = MixPlan(
        plan_id="plan-test",
        brief=MixBrief(
            request_text="Synthetic three-track set.",
            target_duration_minutes=10.0 / 60.0,
        ),
        ordered_track_ids=ids,
        segments=[
            PlannedTrackSegment(
                segment_id=f"segment-{index}",
                track_id=track_id,
                start_downbeat_index=0,
                end_downbeat_index=6,
                gain_db=-1.0 if index == 2 else 0.0,
            )
            for index, track_id in enumerate(ids, start=1)
        ],
        transitions=[
            PlannedTransition(
                transition_id="transition-1",
                from_track_id=ids[0],
                to_track_id=ids[1],
                duration_bars=4,
            ),
            PlannedTransition(
                transition_id="transition-2",
                from_track_id=ids[1],
                to_track_id=ids[2],
                duration_bars=4,
            ),
        ],
        requested_duration_s=10.0,
        estimated_duration_s=10.0,
    )
    return collection, plan, music


def test_validate_and_render_three_track_set(tmp_path: Path):
    collection, plan, music = _collection_and_plan(tmp_path)
    before = {
        track.source.track_id: sha256_file(music / track.source.filename)
        for track in collection.tracks
    }
    out = tmp_path / "renders" / "mini-set.wav"
    validated = validate_mix_plan(collection, plan, out_path=out)
    assert validated.planned_duration_s == pytest.approx(10.0)

    manifest = render_set(collection, plan, out_path=out)
    manifest_path = write_render_manifest(
        manifest,
        tmp_path / "renders" / "mini-set.manifest.json",
        source_folder=music,
    )

    assert out.exists()
    assert manifest_path.exists()
    assert manifest.status == "passed"
    assert manifest.rendered_duration_s == pytest.approx(10.0, abs=0.1)
    assert manifest.output_sha256 == sha256_file(out)
    assert manifest.output_measurements["integrated_lufs"] is not None
    assert manifest.output_measurements["true_peak_dbtp"] is not None
    assert [item["tool"] for item in manifest.executed_operations].count("load_track") == 3
    assert [item["tool"] for item in manifest.executed_operations].count("crossfade") == 2
    assert all(item["source_unchanged"] for item in manifest.source_track_hashes)
    assert json.loads(manifest_path.read_text(encoding="utf-8"))["schema"] == (
        "dj-engine/render-manifest"
    )
    after = {
        track.source.track_id: sha256_file(music / track.source.filename)
        for track in collection.tracks
    }
    assert after == before


def test_transition_duration_uses_detected_downbeat_grid_not_rounded_bpm(tmp_path: Path):
    collection, plan, _music = _collection_and_plan(tmp_path)
    for track in collection.tracks:
        grid = track.rhythm_grids[0]
        grid.downbeats_s = [step * 0.99 for step in range(7)]
    validated = validate_mix_plan(collection, plan, out_path=tmp_path / "mini-set.wav")
    assert validated.transitions[0].duration_s == pytest.approx(3.96)
    assert validated.transitions[0].grid_drift_s == pytest.approx(0.0)


def test_house_transition_style_is_executed(tmp_path: Path):
    collection, plan, _music = _collection_and_plan(tmp_path)
    styled = plan.model_copy(
        update={
            "transitions": [
                transition.model_copy(update={"style": "house_eq_v1"})
                for transition in plan.transitions
            ]
        }
    )
    manifest = render_set(collection, styled, out_path=tmp_path / "house-set.wav")
    tools = [item["tool"] for item in manifest.executed_operations]
    assert tools.count("house_transition") == 2
    assert any("house-eq-v1" in warning for warning in manifest.warnings)


def test_validation_refuses_source_folder_output_without_creating_parent(tmp_path: Path):
    collection, plan, music = _collection_and_plan(tmp_path)
    forbidden_parent = music / "created-before-refusal"
    with pytest.raises(MixPlanValidationError, match="outside the source music folder"):
        validate_mix_plan(
            collection,
            plan,
            out_path=forbidden_parent / "mini-set.wav",
        )
    assert not forbidden_parent.exists()


def test_validation_rejects_changed_source_hash(tmp_path: Path):
    collection, plan, music = _collection_and_plan(tmp_path)
    with (music / collection.tracks[0].source.filename).open("ab") as handle:
        handle.write(b"changed")
    with pytest.raises(MixPlanValidationError, match="Source hash mismatch"):
        validate_mix_plan(collection, plan, out_path=tmp_path / "mini-set.wav")


def test_validation_rejects_nonconsecutive_transition(tmp_path: Path):
    collection, plan, _music = _collection_and_plan(tmp_path)
    ids = plan.ordered_track_ids
    broken = plan.model_copy(
        update={
            "transitions": [
                PlannedTransition(
                    transition_id="wrong",
                    from_track_id=ids[0],
                    to_track_id=ids[2],
                    duration_bars=4,
                )
            ]
        }
    )
    with pytest.raises(MixPlanValidationError, match="Transitions must appear once"):
        validate_mix_plan(collection, broken, out_path=tmp_path / "mini-set.wav")


def test_dj_render_set_command_writes_audio_and_manifest(tmp_path: Path):
    collection, plan, _music = _collection_and_plan(tmp_path)
    analysis_path = tmp_path / "collection.json"
    plan_path = tmp_path / "plan.json"
    out = tmp_path / "renders" / "cli-set.wav"
    analysis_path.write_text(
        collection.model_dump_json(indent=2, by_alias=True),
        encoding="utf-8",
    )
    plan_path.write_text(
        plan.model_dump_json(indent=2, by_alias=True),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        [
            "set",
            "--analysis",
            str(analysis_path),
            "--plan",
            str(plan_path),
            "--out",
            str(out),
        ],
    )

    assert result.exit_code == 0, result.output
    assert out.exists()
    assert out.with_suffix(".manifest.json").exists()
    payload = json.loads(result.output.split("\nWrote manifest", 1)[0])
    assert payload["status"] == "passed"


def test_dj_render_downbeat_clicks_writes_one_center_clip_per_planned_track(
    tmp_path: Path,
):
    collection, plan, music = _collection_and_plan(tmp_path)
    analysis_path = tmp_path / "collection.json"
    plan_path = tmp_path / "plan.json"
    out_dir = tmp_path / "downbeat-clicks"
    analysis_path.write_text(
        collection.model_dump_json(indent=2, by_alias=True),
        encoding="utf-8",
    )
    plan_path.write_text(
        plan.model_dump_json(indent=2, by_alias=True),
        encoding="utf-8",
    )
    before = {
        track.source.track_id: sha256_file(music / track.source.filename)
        for track in collection.tracks
    }

    result = CliRunner().invoke(
        app,
        [
            "downbeat-clicks",
            "--analysis",
            str(analysis_path),
            "--plan",
            str(plan_path),
            "--out-dir",
            str(out_dir),
            "--duration",
            "4",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert len(payload) == 3
    assert all(item["click_count"] == 4 for item in payload)
    assert len(list(out_dir.glob("*.wav"))) == 3
    assert all(item["clip_duration_s"] == pytest.approx(4.0, abs=0.05) for item in payload)
    after = {
        track.source.track_id: sha256_file(music / track.source.filename)
        for track in collection.tracks
    }
    assert after == before
