from __future__ import annotations

import hashlib
import json
import math
import shutil
import struct
import wave
from pathlib import Path

import pytest

pytest.importorskip("psutil")

from prompt_to_playlist.analysis_models import AlgorithmResult, StageMetrics
from prompt_to_playlist.analysis_pipeline import (
    analyze_folder,
    discover_audio,
    project_algorithms,
    project_pipeline,
    run_worker,
    validate_output_dir,
    validate_reuse_from,
    verify_analysis_dependencies,
)
from prompt_to_playlist.analysis_worker import run as run_analysis_worker
from prompt_to_playlist.model_assets import ASSETS, ensure_assets, required_assets, sha256_file


def metric(algorithm: str, *, wall: float = 2.0, cpu: float = 3.0, rss: float = 100.0) -> StageMetrics:
    return StageMetrics(
        algorithm_id=algorithm,
        implementation="test",
        device="cpu",
        status="passed",
        started_at="2026-01-01T00:00:00+00:00",
        finished_at="2026-01-01T00:00:02+00:00",
        wall_time_s=wall,
        cpu_user_time_s=cpu,
        cpu_system_time_s=0,
        cpu_total_time_s=cpu,
        cpu_utilization_percent=cpu / wall * 100,
        normalized_cpu_utilization_percent=cpu / wall * 10,
        peak_rss_mb=rss,
        peak_vms_mb=rss * 2,
        peak_thread_count=4,
        peak_child_process_count=1,
        host_available_ram_start_mb=8000,
        host_available_ram_min_mb=7500,
        host_swap_used_start_mb=0,
        host_swap_used_peak_mb=0,
        audio_duration_s=120,
        realtime_factor=wall / 120,
        audio_seconds_per_wall_second=120 / wall,
        exit_code=0,
        telemetry_interval_s=0.2,
        sample_count=10,
    )


def test_discovery_is_bounded_sorted_and_skips_symlinks(tmp_path):
    folder = tmp_path / "music"
    folder.mkdir()
    (folder / "B.MP3").write_bytes(b"b")
    (folder / "a.wav").write_bytes(b"a")
    (folder / ".hidden.mp3").write_bytes(b"hidden")
    (folder / "notes.txt").write_text("ignore")
    (folder / "alias.mp3").symlink_to(folder / "B.MP3")
    nested = folder / "nested"
    nested.mkdir()
    (nested / "c.flac").write_bytes(b"c")
    shallow, warnings = discover_audio(folder, recursive=False)
    assert [path.name for path in shallow] == ["a.wav", "B.MP3"]
    assert warnings == ["Skipped symlink: alias.mp3"]
    recursive, _ = discover_audio(folder, recursive=True)
    assert [str(path.relative_to(folder)) for path in recursive] == ["a.wav", "B.MP3", "nested/c.flac"]


def test_output_must_be_disjoint_and_existing_requires_resume(tmp_path):
    source = tmp_path / "music"
    source.mkdir()
    with pytest.raises(ValueError, match="separate"):
        validate_output_dir(source, source / "reports", resume=False)
    output = tmp_path / "reports"
    assert validate_output_dir(source, output, resume=False) == output.resolve()
    with pytest.raises(ValueError, match="already exists"):
        validate_output_dir(source, output, resume=False)
    assert validate_output_dir(source, output, resume=True) == output.resolve()


def test_model_groups_and_stream_hash(tmp_path):
    path = tmp_path / "asset"
    path.write_bytes(b"model")
    assert sha256_file(path) == hashlib.sha256(b"model").hexdigest()
    assets = required_assets(["semantic", "energy", "rhythm"])
    assert "discogs_effnet_pb" in assets
    assert "deam_pb" in assets
    assert "beat_this_final0" in assets


def test_dependency_preflight_is_algorithm_specific(monkeypatch):
    real_find_spec = __import__("importlib.util").util.find_spec

    def fake_find_spec(name):
        if name == "essentia":
            return None
        return real_find_spec(name)

    monkeypatch.setattr("prompt_to_playlist.analysis_pipeline.importlib.util.find_spec", fake_find_spec)
    verify_analysis_dependencies(["metadata", "loudness"])
    with pytest.raises(ValueError, match="essentia"):
        verify_analysis_dependencies(["semantic"])


def test_rhythm_preflight_requires_soundfile_fallback(monkeypatch):
    real_find_spec = __import__("importlib.util").util.find_spec

    def fake_find_spec(name):
        if name == "soundfile":
            return None
        return real_find_spec(name)

    monkeypatch.setattr("prompt_to_playlist.analysis_pipeline.importlib.util.find_spec", fake_find_spec)
    with pytest.raises(ValueError, match="soundfile"):
        verify_analysis_dependencies(["rhythm"])


def test_existing_model_asset_must_match_pinned_hash(tmp_path):
    asset = ASSETS["discogs_effnet_json"]
    (tmp_path / asset.filename).write_bytes(b"wrong")
    with pytest.raises(ValueError, match="hash mismatch"):
        ensure_assets(tmp_path, (asset.asset_id,))


def test_projection_keeps_observed_numbers_and_vm_warning():
    from prompt_to_playlist.analysis_models import DescriptorTrack, SourceRecord

    result = AlgorithmResult(
        algorithm_id="semantic",
        implementation="test",
        implementation_version="1",
        authority="benchmark_estimate",
        status="warning",
        metrics=metric("semantic", wall=2, cpu=3, rss=100),
    )
    track = DescriptorTrack(
        track_id="sha256:" + "a" * 64,
        source=SourceRecord(
            relative_path="test.wav",
            filename="test.wav",
            size_bytes=1,
            sha256_before="a" * 64,
            sha256_after="a" * 64,
            source_unchanged=True,
        ),
        duration_s=120,
        algorithms=[result],
    )
    projection = project_algorithms([track])[0]
    assert projection.algorithm_id == "semantic"
    assert projection.mean_wall_time_s_per_track == 2
    assert projection.wall_minutes_per_audio_hour == 1
    assert projection.projected_serial_minutes_per_100_tracks == pytest.approx(3.333333)
    assert projection.max_peak_rss_mb == 100
    assert "target VM" in projection.projection_warning


def test_failed_stage_attempt_is_not_used_for_capacity_projection():
    from prompt_to_playlist.analysis_models import DescriptorTrack, SourceRecord

    failed_metric = metric("rhythm", wall=1, cpu=0.5, rss=300)
    failed_metric.status = "failed"
    result = AlgorithmResult(
        algorithm_id="rhythm",
        implementation="test",
        implementation_version="1",
        authority="benchmark_estimate",
        status="failed",
        error="decoder unavailable",
        metrics=failed_metric,
    )
    track = DescriptorTrack(
        track_id="sha256:" + "a" * 64,
        source=SourceRecord(
            relative_path="test.mp3", filename="test.mp3", size_bytes=1,
            sha256_before="a" * 64, sha256_after="a" * 64, source_unchanged=True,
        ),
        duration_s=120,
        algorithms=[result],
    )
    algorithm = next(item for item in project_algorithms([track]) if item.algorithm_id == "rhythm")
    pipeline = project_pipeline([track], model_asset_cache_bytes=0)
    assert (algorithm.measured_tracks, algorithm.passed_tracks, algorithm.failed_tracks) == (1, 0, 1)
    assert algorithm.mean_wall_time_s_per_track is None
    assert algorithm.max_peak_rss_mb == 0
    assert pipeline.measured_tracks == 0
    assert pipeline.projected_serial_minutes_per_100_tracks is None


def test_combined_pipeline_projection_sums_stages_without_double_counting_audio():
    from prompt_to_playlist.analysis_models import DescriptorTrack, SourceRecord

    track = DescriptorTrack(
        track_id="sha256:" + "a" * 64,
        source=SourceRecord(
            relative_path="test.wav",
            filename="test.wav",
            size_bytes=1,
            sha256_before="a" * 64,
            sha256_after="a" * 64,
            source_unchanged=True,
        ),
        duration_s=120,
        algorithms=[
            AlgorithmResult(
                algorithm_id="metadata", implementation="test", implementation_version="1",
                authority="encoded_fact", status="passed", metrics=metric("metadata", wall=2, cpu=1, rss=50),
            ),
            AlgorithmResult(
                algorithm_id="semantic", implementation="test", implementation_version="1",
                authority="benchmark_estimate", status="warning", metrics=metric("semantic", wall=4, cpu=8, rss=1024),
            ),
        ],
    )
    projection = project_pipeline([track], model_asset_cache_bytes=123)
    assert projection.total_audio_duration_s == 120
    assert projection.total_sequential_stage_wall_time_s == 6
    assert projection.total_cpu_time_s == 9
    assert projection.wall_minutes_per_audio_hour == 3
    assert projection.projected_serial_minutes_per_100_tracks == 10
    assert projection.max_observed_stage_rss_mb == 1024
    assert projection.projected_ram_gb_per_sequential_worker_with_35pct_headroom == pytest.approx(1.35)
    assert projection.model_asset_cache_bytes == 123


def test_pipeline_defaults_to_selected_subset_and_writes_reports(tmp_path, monkeypatch):
    source = tmp_path / "music"
    source.mkdir()
    (source / "a.wav").write_bytes(b"first")
    (source / "b.wav").write_bytes(b"second")
    output = tmp_path / "output"

    def fake_worker(**kwargs):
        return AlgorithmResult(
            algorithm_id=kwargs["algorithm"],
            implementation="fake-ffprobe",
            implementation_version="1",
            authority="encoded_fact",
            status="passed",
            values={"duration_s": 120.0},
            metrics=metric(kwargs["algorithm"]),
        )

    monkeypatch.setattr("prompt_to_playlist.analysis_pipeline.run_worker", fake_worker)
    run, paths = analyze_folder(
        folder=source,
        output_dir=output,
        max_tracks=1,
        algorithms=["metadata"],
        progress=lambda _: None,
    )
    assert run.discovered_track_count == 2
    assert run.selected_track_count == 1
    assert run.source_hashes_unchanged
    assert set(paths) == {"descriptors", "performance_json", "performance_markdown"}
    assert json.loads(paths["descriptors"].read_text())["schema"] == "prompt-playlist/descriptor-run"
    performance = json.loads(paths["performance_json"].read_text())
    assert performance["pipeline_projection"]["measured_tracks"] == 1
    assert performance["artifacts"]["descriptor_json_bytes"] > 0
    assert "Per-track stage measurements" in paths["performance_markdown"].read_text()


def test_explicit_unlimited_selection_processes_every_discovered_track(tmp_path, monkeypatch):
    source = tmp_path / "music"
    source.mkdir()
    (source / "a.wav").write_bytes(b"first")
    (source / "b.wav").write_bytes(b"second")

    def fake_worker(**kwargs):
        return AlgorithmResult(
            algorithm_id=kwargs["algorithm"], implementation="fake", implementation_version="1",
            authority="encoded_fact", status="passed", values={"duration_s": 120.0},
            metrics=metric(kwargs["algorithm"]),
        )

    monkeypatch.setattr("prompt_to_playlist.analysis_pipeline.run_worker", fake_worker)
    run, _ = analyze_folder(
        folder=source,
        output_dir=tmp_path / "output",
        max_tracks=None,
        algorithms=["metadata"],
        progress=lambda _: None,
    )
    assert run.discovered_track_count == 2
    assert run.selected_track_count == 2
    assert run.selection_limit is None
    assert [track.source.filename for track in run.tracks] == ["a.wav", "b.wav"]


def test_resume_reuses_hash_and_version_verified_checkpoint(tmp_path, monkeypatch):
    source = tmp_path / "music"
    source.mkdir()
    (source / "a.wav").write_bytes(b"first")
    output = tmp_path / "output"
    calls = 0

    def fake_worker(**kwargs):
        nonlocal calls
        calls += 1
        return AlgorithmResult(
            algorithm_id=kwargs["algorithm"], implementation="fake", implementation_version="1",
            authority="encoded_fact", status="passed", values={"duration_s": 120.0},
            metrics=metric(kwargs["algorithm"]),
        )

    monkeypatch.setattr("prompt_to_playlist.analysis_pipeline.run_worker", fake_worker)
    analyze_folder(folder=source, output_dir=output, algorithms=["metadata"], progress=lambda _: None)
    run, _ = analyze_folder(
        folder=source, output_dir=output, algorithms=["metadata"], resume=True, progress=lambda _: None
    )
    assert calls == 1
    assert run.tracks[0].algorithms[0].metrics.status == "reused"


def test_resume_migrates_pre_soundfile_tool_version_checkpoint(tmp_path, monkeypatch):
    source = tmp_path / "music"
    source.mkdir()
    (source / "a.wav").write_bytes(b"first")
    output = tmp_path / "output"
    calls = 0

    def fake_worker(**kwargs):
        nonlocal calls
        calls += 1
        return AlgorithmResult(
            algorithm_id=kwargs["algorithm"], implementation="fake", implementation_version="1",
            authority="encoded_fact", status="passed", values={"duration_s": 120.0},
            metrics=metric(kwargs["algorithm"]),
        )

    base_tools = {"playlistiq_pipeline": "playlistiq-descriptors-v1", "python": "test"}
    monkeypatch.setattr("prompt_to_playlist.analysis_pipeline.run_worker", fake_worker)
    monkeypatch.setattr("prompt_to_playlist.analysis_pipeline._tool_versions", lambda: base_tools)
    analyze_folder(folder=source, output_dir=output, algorithms=["metadata"], progress=lambda _: None)
    monkeypatch.setattr(
        "prompt_to_playlist.analysis_pipeline._tool_versions",
        lambda: {**base_tools, "soundfile": "0.14.0"},
    )
    run, _ = analyze_folder(
        folder=source, output_dir=output, algorithms=["metadata"], resume=True, progress=lambda _: None
    )
    assert calls == 1
    assert run.tracks[0].algorithms[0].metrics.status == "reused"


def test_reuse_from_imports_verified_checkpoint_into_separate_output(tmp_path, monkeypatch):
    prior_source = tmp_path / "prior-music"
    current_source = tmp_path / "current-music"
    prior_source.mkdir()
    current_source.mkdir()
    (prior_source / "old-name.wav").write_bytes(b"same-audio-bytes")
    (current_source / "renamed.wav").write_bytes(b"same-audio-bytes")
    prior_output = tmp_path / "prior-output"
    current_output = tmp_path / "current-output"
    calls = 0

    def fake_worker(**kwargs):
        nonlocal calls
        calls += 1
        return AlgorithmResult(
            algorithm_id=kwargs["algorithm"], implementation="fake", implementation_version="1",
            authority="encoded_fact", status="passed", values={"duration_s": 120.0},
            metrics=metric(kwargs["algorithm"]),
        )

    monkeypatch.setattr("prompt_to_playlist.analysis_pipeline.run_worker", fake_worker)
    analyze_folder(folder=prior_source, output_dir=prior_output, algorithms=["metadata"], progress=lambda _: None)
    run, _ = analyze_folder(
        folder=current_source,
        output_dir=current_output,
        algorithms=["metadata"],
        reuse_from=[prior_output],
        resume=True,
        progress=lambda _: None,
    )
    assert calls == 1
    assert run.tracks[0].source.filename == "renamed.wav"
    assert run.tracks[0].algorithms[0].metrics.status == "reused"
    assert len(list((current_output / ".checkpoints").glob("*.json"))) == 1
    assert "Reused 1 hash/config/version-verified checkpoints" in "\n".join(run.warnings)


def test_reuse_from_rejects_unverified_or_same_output(tmp_path, monkeypatch):
    source = tmp_path / "music"
    source.mkdir()
    (source / "a.wav").write_bytes(b"first")
    prior_output = tmp_path / "prior-output"

    def fake_worker(**kwargs):
        return AlgorithmResult(
            algorithm_id=kwargs["algorithm"], implementation="fake", implementation_version="1",
            authority="encoded_fact", status="passed", values={"duration_s": 120.0},
            metrics=metric(kwargs["algorithm"]),
        )

    monkeypatch.setattr("prompt_to_playlist.analysis_pipeline.run_worker", fake_worker)
    analyze_folder(folder=source, output_dir=prior_output, algorithms=["metadata"], progress=lambda _: None)
    with pytest.raises(ValueError, match="use --resume"):
        validate_reuse_from(source, prior_output, [prior_output])

    descriptor = prior_output / "descriptor-run.json"
    payload = json.loads(descriptor.read_text())
    payload["source_hashes_unchanged"] = False
    descriptor.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="source-preservation"):
        validate_reuse_from(source, tmp_path / "new-output", [prior_output])


def test_pipeline_detects_if_source_changes_during_analysis(tmp_path, monkeypatch):
    source = tmp_path / "music"
    source.mkdir()
    audio = source / "a.wav"
    audio.write_bytes(b"first")

    def mutating_worker(**kwargs):
        kwargs["source"].write_bytes(b"changed-size")
        return AlgorithmResult(
            algorithm_id="metadata", implementation="fake", implementation_version="1",
            authority="encoded_fact", status="passed", values={"duration_s": 120.0},
            metrics=metric("metadata"),
        )

    monkeypatch.setattr("prompt_to_playlist.analysis_pipeline.run_worker", mutating_worker)
    run, _ = analyze_folder(
        folder=source, output_dir=tmp_path / "output", algorithms=["metadata"], progress=lambda _: None
    )
    assert not run.source_hashes_unchanged
    assert not run.source_inventory_unchanged
    assert "Source hash changed" in run.tracks[0].warnings[0]


def test_real_metadata_and_loudness_workers_on_synthetic_audio(tmp_path):
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        pytest.skip("FFmpeg tools are not installed")
    audio = tmp_path / "tone.wav"
    sample_rate = 16000
    with wave.open(str(audio), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        samples = [int(8000 * math.sin(2 * math.pi * 440 * i / sample_rate)) for i in range(sample_rate)]
        handle.writeframes(b"".join(struct.pack("<h", sample) for sample in samples))
    metadata = run_analysis_worker("metadata", audio, tmp_path)
    loudness = run_analysis_worker("loudness", audio, tmp_path)
    assert metadata["status"] == "passed"
    assert metadata["values"]["duration_s"] == pytest.approx(1.0)
    assert metadata["values"]["sample_rate_hz"] == sample_rate
    assert loudness["status"] == "passed"
    assert isinstance(loudness["values"]["integrated_lufs"], float)


def test_beat_this_soundfile_fallback_decodes_mp3(tmp_path, monkeypatch):
    if not shutil.which("ffmpeg"):
        pytest.skip("FFmpeg is not installed")
    pytest.importorskip("beat_this")
    pytest.importorskip("soundfile")
    import torchaudio
    from beat_this.preprocessing import load_audio

    audio = tmp_path / "tone.mp3"
    completed = __import__("subprocess").run(
        [
            "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
            "-f", "lavfi", "-i", "sine=frequency=440:duration=1",
            "-codec:a", "libmp3lame", str(audio),
        ],
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        pytest.skip("FFmpeg MP3 encoder is unavailable")

    def unavailable_torchcodec(*_args, **_kwargs):
        raise ImportError("TorchCodec is unavailable")

    monkeypatch.setattr(torchaudio, "load", unavailable_torchcodec)
    signal, sample_rate = load_audio(str(audio))
    assert sample_rate == 44100
    assert signal.shape[0] == 44100


def test_parent_memory_gate_cannot_publish_a_passing_result(tmp_path):
    source = tmp_path / "dummy.wav"
    source.write_bytes(b"not-needed-before-kill")
    result = run_worker(
        algorithm="metadata",
        source=source,
        model_dir=tmp_path,
        work_dir=tmp_path,
        cpu_threads=1,
        max_rss_mb=4096,
        min_available_ram_mb=10**9,
        timeout_s=5,
        telemetry_interval_s=0.01,
        duration_s=None,
    )
    assert result.status == "failed"
    assert result.metrics.status == "memory_exceeded"
    assert "available RAM" in (result.error or "")


def test_invalid_worker_json_is_a_failed_stage_not_a_track_crash(tmp_path, monkeypatch):
    import subprocess
    real_popen = subprocess.Popen
    def fake_popen(command, **kwargs):
        Path(command[command.index('--out')+1]).write_text('{"broken":')
        return real_popen([__import__('sys').executable,'-c','pass'], **kwargs)
    monkeypatch.setattr(subprocess,'Popen',fake_popen)
    result=run_worker(algorithm='loudness',source=tmp_path/'test.wav',model_dir=tmp_path,work_dir=tmp_path,cpu_threads=1,max_rss_mb=4096,min_available_ram_mb=1,timeout_s=10,telemetry_interval_s=.01,duration_s=1)
    assert result.status=='failed'
    assert 'invalid output' in result.error
    assert result.metrics.status=='failed'
