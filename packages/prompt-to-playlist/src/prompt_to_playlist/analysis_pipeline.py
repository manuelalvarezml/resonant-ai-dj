"""Bounded, resumable, metrics-first PlaylistIQ descriptor pipeline."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import platform
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from typing import Any

from .analysis_models import (
    ModelAssetRecord,
    AlgorithmProjection,
    AlgorithmResult,
    DescriptorRun,
    DescriptorTrack,
    HostProfile,
    PipelineProjection,
    SourceRecord,
    StageMetrics,
)
from .model_assets import default_model_dir, ensure_assets, required_assets, sha256_file

PIPELINE_VERSION = "playlistiq-descriptors-v1"
DEFAULT_ALGORITHMS = ("metadata", "loudness", "key", "rhythm", "semantic", "energy", "genre_maest")
from .specialists import STAGES as SPECIALIST_STAGES
ALGORITHMS = (*SPECIALIST_STAGES, *DEFAULT_ALGORITHMS, "semantic_audio", "emotion_music2emo", "danceability_musicnn", "estimator_reference")
SUPPORTED_SUFFIXES = frozenset({".mp3", ".wav", ".wave", ".flac", ".m4a", ".aac", ".ogg", ".oga", ".opus", ".aif", ".aiff", ".alac"})


def verify_analysis_dependencies(algorithms: list[str]) -> None:
    required = {"numpy", "psutil"}
    if set(algorithms) & {"vocal_musicnn", "aggression_vggish"}: required.add("essentia")
    if "instrument_passt" in algorithms: required.update({"hear21passt", "timm", "torch", "torchaudio"})
    if "key_sheetsage2" in algorithms: required.update({"torch", "torchaudio", "soundfile", "transformers", "pretty_midi", "mir_eval"})
    if set(algorithms) & {"key", "semantic", "energy", "genre_maest"}:
        required.add("essentia")
    if "semantic_audio" in algorithms:
        required.update({"muq", "torch", "transformers"})
    if "emotion_music2emo" in algorithms:
        required.update({"torch", "transformers", "soundfile", "music21", "pretty_midi", "mir_eval", "yaml"})
    if set(algorithms) & {"danceability_musicnn", "estimator_reference"}:
        required.add("essentia")
    if "rhythm" in algorithms:
        required.update({"beat_this", "soundfile", "torch", "torchaudio"})
    missing = sorted(module for module in required if importlib.util.find_spec(module) is None)
    if missing:
        raise ValueError(
            "Audio analysis dependencies are missing "
            f"({', '.join(missing)}). Run: uv sync --extra analysis"
        )


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def discover_audio(folder: Path, *, recursive: bool) -> tuple[list[Path], list[str]]:
    folder = folder.expanduser().resolve()
    if not folder.is_dir():
        raise NotADirectoryError(str(folder))
    iterator = folder.rglob("*") if recursive else folder.iterdir()
    paths: list[Path] = []
    warnings: list[str] = []
    for path in iterator:
        relative = path.relative_to(folder)
        if any(part.startswith(".") for part in relative.parts):
            continue
        if path.is_symlink():
            warnings.append(f"Skipped symlink: {relative}")
            continue
        if path.is_file() and path.suffix.casefold() in SUPPORTED_SUFFIXES:
            paths.append(path)
    paths.sort(key=lambda item: str(item.relative_to(folder)).casefold())
    if not paths:
        raise ValueError("The selected folder contains no supported audio files")
    return paths, warnings


def inventory(folder: Path, *, recursive: bool) -> list[tuple[str, int]]:
    paths, _ = discover_audio(folder, recursive=recursive)
    return [(str(path.relative_to(folder)), path.stat().st_size) for path in paths]


def validate_output_dir(source_folder: Path, output_dir: Path, *, resume: bool) -> Path:
    source = source_folder.expanduser().resolve()
    spelled = output_dir.expanduser()
    resolved = spelled.resolve()
    if resolved == source or resolved.is_relative_to(source) or source.is_relative_to(resolved):
        raise ValueError("Output directory must be separate from and outside the selected music folder")
    if os.path.lexists(spelled):
        if spelled.is_symlink() or not spelled.is_dir():
            raise ValueError("Output directory must be a real directory, not a file or symlink")
        if not resume:
            raise ValueError("Output directory already exists; pass --resume to reuse verified checkpoints")
    else:
        resolved.mkdir(parents=True)
    return resolved


def validate_reuse_from(
    source_folder: Path,
    output_dir: Path,
    reuse_from: list[Path] | None,
) -> list[Path]:
    """Return verified checkpoint directories from prior descriptor outputs."""
    source = source_folder.expanduser().resolve()
    output = output_dir.expanduser().resolve()
    roots: list[Path] = []
    seen: set[Path] = set()
    for supplied in reuse_from or []:
        prior = supplied.expanduser()
        resolved = prior.resolve()
        if resolved in seen:
            continue
        if prior.is_symlink() or not resolved.is_dir():
            raise ValueError(f"Reuse source must be a real prior output directory: {supplied}")
        if resolved == output:
            raise ValueError("Reuse source and output directory must be different; use --resume for the same output")
        if resolved == source or resolved.is_relative_to(source):
            raise ValueError("Reuse source must be outside the selected music folder")
        descriptor_path = resolved / "descriptor-run.json"
        checkpoint_root = resolved / ".checkpoints"
        if checkpoint_root.is_symlink() or not checkpoint_root.is_dir() or not descriptor_path.is_file():
            raise ValueError(f"Reuse source is missing descriptor-run.json or .checkpoints: {supplied}")
        try:
            prior_run = DescriptorRun.model_validate_json(descriptor_path.read_text(encoding="utf-8"))
        except (ValueError, OSError) as exc:
            raise ValueError(f"Reuse source has an invalid descriptor run: {supplied}") from exc
        if not prior_run.source_hashes_unchanged or not prior_run.source_inventory_unchanged:
            raise ValueError(f"Reuse source did not pass source-preservation gates: {supplied}")
        roots.append(checkpoint_root)
        seen.add(resolved)
    return roots


def _host_profile() -> HostProfile:
    import psutil

    return HostProfile(
        platform=platform.system(),
        platform_release=platform.release(),
        machine=platform.machine(),
        processor=platform.processor() or "unknown",
        python_version=platform.python_version(),
        logical_cpu_count=psutil.cpu_count(logical=True) or 1,
        physical_cpu_count=psutil.cpu_count(logical=False),
        total_ram_mb=psutil.virtual_memory().total / (1024 * 1024),
    )


def _tool_versions() -> dict[str, str]:
    result = {"playlistiq_pipeline": PIPELINE_VERSION, "python": platform.python_version()}
    for package in ("prompt-to-playlist", "essentia-tensorflow", "beat-this", "soundfile", "torch", "torchaudio", "numpy", "psutil"):
        try:
            result[package] = version(package)
        except Exception:
            result[package] = "unavailable"
    for tool in ("ffmpeg", "ffprobe"):
        executable = shutil.which(tool)
        if not executable:
            result[tool] = "unavailable"
            continue
        completed = subprocess.run([executable, "-version"], capture_output=True, text=True, timeout=5, check=False)
        result[tool] = (completed.stdout.splitlines() or ["unavailable"])[0][:500]
    return result


def _terminate_tree(process) -> None:
    import psutil

    try:
        root = psutil.Process(process.pid)
        children = root.children(recursive=True)
    except psutil.Error:
        children = []
        root = None
    for item in children:
        try:
            item.terminate()
        except psutil.Error:
            pass
    if root is not None:
        try:
            root.terminate()
        except psutil.Error:
            pass
    _, alive = psutil.wait_procs(children + ([root] if root else []), timeout=3)
    for item in alive:
        try:
            item.kill()
        except psutil.Error:
            pass


def _process_sample(pid: int) -> dict[str, float | int | None]:
    import psutil

    try:
        root = psutil.Process(pid)
        processes = [root, *root.children(recursive=True)]
    except psutil.Error:
        return {"rss": 0, "vms": 0, "threads": 0, "children": 0, "user": 0.0, "system": 0.0, "read": None, "write": None}
    rss = vms = threads = 0
    user = system = 0.0
    read_bytes = write_bytes = 0
    io_available = False
    live = 0
    for process in processes:
        try:
            memory = process.memory_info()
            cpu = process.cpu_times()
            rss += memory.rss
            vms += memory.vms
            threads += process.num_threads()
            user += cpu.user
            system += cpu.system
            live += 1
            try:
                io = process.io_counters()
                read_bytes += io.read_bytes
                write_bytes += io.write_bytes
                io_available = True
            except (psutil.AccessDenied, AttributeError, NotImplementedError):
                pass
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return {
        "rss": rss,
        "vms": vms,
        "threads": threads,
        "children": max(0, live - 1),
        "user": user,
        "system": system,
        "read": read_bytes if io_available else None,
        "write": write_bytes if io_available else None,
    }


def run_worker(
    *,
    algorithm: str,
    source: Path,
    model_dir: Path,
    work_dir: Path,
    cpu_threads: int,
    max_rss_mb: float,
    min_available_ram_mb: float,
    timeout_s: float,
    telemetry_interval_s: float,
    duration_s: float | None,
) -> AlgorithmResult:
    import psutil

    started_at = utc_now()
    start = time.monotonic()
    virtual_start = psutil.virtual_memory()
    swap_start = psutil.swap_memory()
    worker_output = work_dir / f"{source.name}.{algorithm}.{os.getpid()}.{time.time_ns()}.json"
    environment = os.environ.copy()
    environment.update(
        {
            "PLAYLISTIQ_CPU_THREADS": str(cpu_threads),
            "OMP_NUM_THREADS": str(cpu_threads),
            "OPENBLAS_NUM_THREADS": str(cpu_threads),
            "MKL_NUM_THREADS": str(cpu_threads),
            "VECLIB_MAXIMUM_THREADS": str(cpu_threads),
            "NUMEXPR_NUM_THREADS": str(cpu_threads),
            "TF_NUM_INTRAOP_THREADS": str(cpu_threads),
            "TF_NUM_INTEROP_THREADS": "1",
            "TF_CPP_MIN_LOG_LEVEL": "2",
        }
    )
    command = [
        sys.executable,
        "-m",
        "prompt_to_playlist.analysis_worker",
        "--algorithm",
        algorithm,
        "--source",
        str(source),
        "--model-dir",
        str(model_dir),
        "--out",
        str(worker_output),
    ]
    status = "passed"
    error = None
    peak_rss = peak_vms = 0
    peak_threads = peak_children = 0
    max_user = max_system = 0.0
    max_read = max_write = None
    available_min = virtual_start.available
    swap_peak = swap_start.used
    samples = 0
    exit_code = None
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        process = subprocess.Popen(command, env=environment, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr)
        try:
            while True:
                sample = _process_sample(process.pid)
                memory = psutil.virtual_memory()
                swap = psutil.swap_memory()
                samples += 1
                peak_rss = max(peak_rss, int(sample["rss"] or 0))
                peak_vms = max(peak_vms, int(sample["vms"] or 0))
                peak_threads = max(peak_threads, int(sample["threads"] or 0))
                peak_children = max(peak_children, int(sample["children"] or 0))
                max_user = max(max_user, float(sample["user"] or 0))
                max_system = max(max_system, float(sample["system"] or 0))
                max_read = max(int(sample["read"] or 0), max_read or 0) if sample["read"] is not None else max_read
                max_write = max(int(sample["write"] or 0), max_write or 0) if sample["write"] is not None else max_write
                available_min = min(available_min, memory.available)
                swap_peak = max(swap_peak, swap.used)
                exit_code = process.poll()
                if exit_code is not None:
                    break
                elapsed = time.monotonic() - start
                if elapsed > timeout_s:
                    status = "timeout"
                    error = f"Worker exceeded {timeout_s:.1f} seconds"
                    _terminate_tree(process)
                    exit_code = process.wait()
                    break
                if peak_rss / (1024 * 1024) > max_rss_mb:
                    status = "memory_exceeded"
                    error = f"Worker exceeded {max_rss_mb:.0f} MB RSS"
                    _terminate_tree(process)
                    exit_code = process.wait()
                    break
                if memory.available / (1024 * 1024) < min_available_ram_mb:
                    status = "memory_exceeded"
                    error = f"Host available RAM fell below {min_available_ram_mb:.0f} MB"
                    _terminate_tree(process)
                    exit_code = process.wait()
                    break
                time.sleep(telemetry_interval_s)
        finally:
            if process.poll() is None:
                _terminate_tree(process)
                process.wait()
        stderr.seek(0)
        stderr_tail = stderr.read()[-4000:].decode("utf-8", errors="replace").strip()
    finished_at = utc_now()
    wall = max(0.0, time.monotonic() - start)
    if status == "passed" and exit_code:
        status = "failed"
    cpu_total = max_user + max_system
    logical_cpus = psutil.cpu_count(logical=True) or 1
    raw_cpu = (cpu_total / wall * 100.0) if wall else 0.0
    metric = StageMetrics(
        algorithm_id=algorithm,
        implementation=algorithm,
        device="cpu",
        status=status,
        started_at=started_at,
        finished_at=finished_at,
        wall_time_s=wall,
        cpu_user_time_s=max_user,
        cpu_system_time_s=max_system,
        cpu_total_time_s=cpu_total,
        cpu_utilization_percent=raw_cpu,
        normalized_cpu_utilization_percent=raw_cpu / logical_cpus,
        peak_rss_mb=peak_rss / (1024 * 1024),
        peak_vms_mb=peak_vms / (1024 * 1024),
        peak_thread_count=peak_threads,
        peak_child_process_count=peak_children,
        io_read_bytes=max_read,
        io_write_bytes=max_write,
        host_available_ram_start_mb=virtual_start.available / (1024 * 1024),
        host_available_ram_min_mb=available_min / (1024 * 1024),
        host_swap_used_start_mb=swap_start.used / (1024 * 1024),
        host_swap_used_peak_mb=swap_peak / (1024 * 1024),
        audio_duration_s=duration_s,
        realtime_factor=(wall / duration_s) if duration_s else None,
        audio_seconds_per_wall_second=(duration_s / wall) if duration_s and wall else None,
        exit_code=exit_code,
        telemetry_interval_s=telemetry_interval_s,
        sample_count=samples,
        error=error or (stderr_tail if status != "passed" and stderr_tail else None),
    )
    try:
        if worker_output.is_file():
            try:
                payload = json.loads(worker_output.read_text(encoding="utf-8"))
                result = AlgorithmResult.model_validate(payload)
            except (ValueError, TypeError):
                result = AlgorithmResult(
                    algorithm_id=algorithm, implementation=algorithm,
                    implementation_version=PIPELINE_VERSION, authority="benchmark_estimate",
                    status="failed", error=f"{algorithm}: worker returned incomplete or invalid output. Retry this feature.",
                )
        else:
            result = AlgorithmResult(
                algorithm_id=algorithm,
                implementation=algorithm,
                implementation_version=PIPELINE_VERSION,
                authority="benchmark_estimate" if algorithm not in {"metadata", "loudness"} else ("encoded_fact" if algorithm == "metadata" else "standardized_measurement"),
                status="failed",
                error=metric.error or f"Worker exited {exit_code} without an output",
            )
        metric.implementation = result.implementation
        if duration_s is None and algorithm == "metadata":
            observed_duration = result.values.get("duration_s")
            if isinstance(observed_duration, (int, float)) and observed_duration > 0:
                metric.audio_duration_s = float(observed_duration)
                metric.realtime_factor = wall / float(observed_duration)
                metric.audio_seconds_per_wall_second = float(observed_duration) / wall if wall else None
        if result.status == "failed" and metric.status == "passed":
            metric.status = "failed"
            metric.error = result.error
        if metric.status in {"failed", "timeout", "memory_exceeded"} and result.status != "failed":
            result.status = "failed"
            result.error = metric.error or f"Worker metric status: {metric.status}"
        result.metrics = metric
        return result
    finally:
        worker_output.unlink(missing_ok=True)


def _atomic_json(path: Path, value: Any) -> None:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    with temporary.open("x", encoding="utf-8") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)


def _checkpoint_digest(algorithm: str, source_hash: str, cpu_threads: int, tool_versions: dict[str, str], asset_hashes: dict[str, str]) -> str:
    data = {
        "pipeline": PIPELINE_VERSION,
        "algorithm": algorithm,
        **({"specialist_identity": __import__("prompt_to_playlist.specialists", fromlist=["identity"]).identity(algorithm)} if algorithm in SPECIALIST_STAGES else {}),
        **({"supervised_identity": __import__("prompt_to_playlist.supervised", fromlist=["identity"]).identity()} if algorithm in ("emotion_music2emo", "danceability_musicnn", "estimator_reference") else {}),
        **({"semantic_policy": "selected-v4"} if algorithm == "semantic" else {}),
        **({"semantic_audio_identity": __import__("prompt_to_playlist.semantic_audio", fromlist=["identity"]).identity(), "sampling": "muq-3x10s-v1", "bank": __import__("prompt_to_playlist.semantic_audio", fromlist=["bank_identity"]).bank_identity()} if algorithm == "semantic_audio" else {}),
        "source_hash": source_hash,
        "cpu_threads": cpu_threads,
        "tools": tool_versions,
        "assets": asset_hashes,
    }
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def _load_checkpoint(path: Path, digest: str) -> AlgorithmResult | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("checkpoint_digest") != digest:
            return None
        result = AlgorithmResult.model_validate(data["result"])
        if result.status == "failed":
            return None
        if result.metrics:
            result.metrics.status = "reused"
        return result
    except (ValueError, OSError, KeyError):
        return None


def _load_compatible_checkpoint(
    path: Path,
    *,
    algorithm: str,
    source_hash: str,
    cpu_threads: int,
    tools: dict[str, str],
    asset_hashes: dict[str, str],
) -> AlgorithmResult | None:
    digest = _checkpoint_digest(algorithm, source_hash, cpu_threads, tools, asset_hashes)
    result = _load_checkpoint(path, digest)
    if result is not None or "soundfile" not in tools:
        return result
    legacy_tools = {key: value for key, value in tools.items() if key != "soundfile"}
    legacy_digest = _checkpoint_digest(algorithm, source_hash, cpu_threads, legacy_tools, asset_hashes)
    return _load_checkpoint(path, legacy_digest)


def _descriptor_document(results: list[AlgorithmResult]) -> list[str]:
    indexed = {item.algorithm_id: item for item in results if item.status != "failed"}
    terms: list[str] = []
    metadata = indexed.get("metadata")
    if metadata:
        tags = metadata.values.get("encoded_tags") or {}
        if tags.get("genre"):
            terms.append(f"encoded genre {tags['genre']}")
    rhythm = indexed.get("rhythm")
    if rhythm and isinstance(rhythm.values.get("bpm"), (int, float)):
        terms.append(f"tempo {rhythm.values['bpm']:.2f} bpm")
    key = indexed.get("key")
    if key and key.values.get("standard_key"):
        terms.append(f"key {key.values['standard_key']}")
    maest = indexed.get("genre_maest")
    if maest and maest.values.get("scores"):
        from .feature_catalog import top_genres
        for item in top_genres(maest.values["scores"]):
            terms.append(f"genre {item['genre']} score {item['probability']:.4f} maest-top6-v1")
    semantic = indexed.get("semantic")
    if semantic:
        heads = semantic.values.get("heads") or {}
        positive_labels = {
            "mood_happy": "happy",
            "mood_sad": "sad",
            "mood_relaxed": "relaxed",
            "mood_aggressive": "aggressive",
            "danceability": "danceable",
            "vocal_profile": "voice",
        }
        for name, positive_label in positive_labels.items():
            scores = (heads.get(name) or {}).get("scores") or {}
            score = scores.get(positive_label)
            if isinstance(score, (int, float)):
                terms.append(f"{positive_label} probability {score:.4f}")
        instrumental = ((heads.get("vocal_profile") or {}).get("scores") or {}).get("instrumental")
        if isinstance(instrumental, (int, float)):
            terms.append(f"instrumental probability {instrumental:.4f}")
    energy = indexed.get("energy")
    if energy and isinstance(energy.values.get("arousal_mean"), (int, float)):
        terms.append(f"arousal raw {energy.values['arousal_mean']:.4f} expected scale 1 to 9")
    loudness = indexed.get("loudness")
    if loudness and isinstance(loudness.values.get("integrated_lufs"), (int, float)):
        terms.append(f"integrated loudness {loudness.values['integrated_lufs']:.2f} LUFS")
    return terms


def project_algorithms(tracks: list[DescriptorTrack]) -> list[AlgorithmProjection]:
    output: list[AlgorithmProjection] = []
    for algorithm in ALGORITHMS:
        results = [result for track in tracks for result in track.algorithms if result.algorithm_id == algorithm and result.metrics]
        successful_results = [
            result for result in results
            if result.status != "failed" and result.metrics and result.metrics.status not in {"failed", "timeout", "memory_exceeded"}
        ]
        metrics = [result.metrics for result in successful_results if result.metrics]
        if not results:
            continue
        wall = [item.wall_time_s for item in metrics]
        audio = sum(item.audio_duration_s or 0 for item in metrics)
        total_wall = sum(wall)
        total_cpu = sum(item.cpu_total_time_s for item in metrics)
        peak_rss = max((item.peak_rss_mb for item in metrics), default=0.0)
        ram_worker = peak_rss * 1.35 / 1024 if peak_rss else 0.0
        def workers(gb: int) -> int:
            return max(0, math.floor((gb * 0.75) / ram_worker)) if ram_worker else 0
        output.append(
            AlgorithmProjection(
                algorithm_id=algorithm,
                measured_tracks=len(results),
                passed_tracks=len(successful_results),
                failed_tracks=sum(result.status == "failed" for result in results),
                total_audio_duration_s=audio,
                total_wall_time_s=total_wall,
                mean_wall_time_s_per_track=statistics.fmean(wall) if wall else None,
                median_wall_time_s_per_track=statistics.median(wall) if wall else None,
                max_wall_time_s_per_track=max(wall) if wall else None,
                total_cpu_time_s=total_cpu,
                mean_cpu_utilization_percent=statistics.fmean(item.cpu_utilization_percent for item in metrics) if metrics else None,
                max_cpu_utilization_percent=max((item.cpu_utilization_percent for item in metrics), default=None),
                mean_normalized_cpu_utilization_percent=statistics.fmean(item.normalized_cpu_utilization_percent for item in metrics) if metrics else None,
                max_peak_rss_mb=peak_rss,
                max_peak_thread_count=max((item.peak_thread_count for item in metrics), default=0),
                wall_minutes_per_audio_hour=(total_wall / audio * 60) if audio else None,
                cpu_core_hours_per_audio_hour=(total_cpu / audio) if audio else None,
                projected_serial_minutes_per_100_tracks=(statistics.fmean(wall) * 100 / 60) if wall else None,
                projected_ram_gb_per_worker_with_35pct_headroom=ram_worker,
                memory_limited_workers_8gb=workers(8),
                memory_limited_workers_16gb=workers(16),
                memory_limited_workers_32gb=workers(32),
                projection_warning="Only successful stage measurements are projected; failed attempts remain in per-track telemetry. The projection extrapolates a small local sample linearly, and VM CPU architecture, storage, throttling, model warm-up, and parallel contention require measurement on the target VM.",
            )
        )
    return output


def project_pipeline(tracks: list[DescriptorTrack], *, model_asset_cache_bytes: int) -> PipelineProjection:
    per_track_wall: list[float] = []
    total_cpu = 0.0
    total_audio = 0.0
    max_rss = 0.0
    for track in tracks:
        if not track.algorithms or any(
            result.status == "failed" or (
                result.metrics and result.metrics.status in {"failed", "timeout", "memory_exceeded"}
            )
            for result in track.algorithms
        ):
            continue
        metrics = [result.metrics for result in track.algorithms if result.metrics]
        if not metrics:
            continue
        per_track_wall.append(sum(item.wall_time_s for item in metrics))
        total_cpu += sum(item.cpu_total_time_s for item in metrics)
        max_rss = max(max_rss, *(item.peak_rss_mb for item in metrics))
        duration = track.duration_s or next((item.audio_duration_s for item in metrics if item.audio_duration_s), 0.0)
        total_audio += duration or 0.0
    total_wall = sum(per_track_wall)
    ram_worker = max_rss * 1.35 / 1024 if max_rss else 0.0

    def workers(gb: int) -> int:
        return max(0, math.floor((gb * 0.75) / ram_worker)) if ram_worker else 0

    return PipelineProjection(
        measured_tracks=len(per_track_wall),
        total_audio_duration_s=total_audio,
        total_sequential_stage_wall_time_s=total_wall,
        total_cpu_time_s=total_cpu,
        mean_sequential_wall_time_s_per_track=statistics.fmean(per_track_wall) if per_track_wall else None,
        median_sequential_wall_time_s_per_track=statistics.median(per_track_wall) if per_track_wall else None,
        max_sequential_wall_time_s_per_track=max(per_track_wall) if per_track_wall else None,
        mean_cpu_utilization_percent=(total_cpu / total_wall * 100) if total_wall else None,
        max_observed_stage_rss_mb=max_rss,
        wall_minutes_per_audio_hour=(total_wall / total_audio * 60) if total_audio else None,
        cpu_core_hours_per_audio_hour=(total_cpu / total_audio) if total_audio else None,
        projected_serial_minutes_per_100_tracks=(statistics.fmean(per_track_wall) * 100 / 60) if per_track_wall else None,
        projected_ram_gb_per_sequential_worker_with_35pct_headroom=ram_worker,
        memory_limited_workers_8gb=workers(8),
        memory_limited_workers_16gb=workers(16),
        memory_limited_workers_32gb=workers(32),
        model_asset_cache_bytes=model_asset_cache_bytes,
        projection_warning="Only tracks whose requested stages all succeeded are included. The pipeline projection sums their sequential stage measurements, excludes parallel contention, and is not a target-VM benchmark.",
    )


def _performance_markdown(run: DescriptorRun, *, descriptor_bytes: int) -> str:
    pipeline = run.pipeline_projection
    output_kib_per_track = descriptor_bytes / max(1, run.selected_track_count) / 1024
    lines = [
        "# PlaylistIQ descriptor performance report",
        "",
        f"Run `{run.run_id}` processed {run.selected_track_count} of {run.discovered_track_count} discovered tracks.",
        f"Host: {run.host.machine}, {run.host.logical_cpu_count} logical CPUs, {run.host.total_ram_mb / 1024:.1f} GB RAM. Workers requested {run.cpu_threads_per_worker} CPU threads.",
        "",
        "## Combined sequential pipeline projection",
        "",
        f"- Measured tracks: {pipeline.measured_tracks}",
        f"- Measured audio: {pipeline.total_audio_duration_s / 60:.2f} minutes",
        f"- Total stage wall time: {pipeline.total_sequential_stage_wall_time_s:.2f} seconds",
        f"- Mean full-pipeline wall time per track: {pipeline.mean_sequential_wall_time_s_per_track or 0:.2f} seconds",
        f"- Wall minutes per audio hour: {pipeline.wall_minutes_per_audio_hour or 0:.2f}",
        f"- Projected serial time per 100 same-length tracks: {pipeline.projected_serial_minutes_per_100_tracks or 0:.2f} minutes",
        f"- Peak observed sequential-stage RSS: {pipeline.max_observed_stage_rss_mb:.1f} MB",
        f"- Projected RAM per worker with 35% headroom: {pipeline.projected_ram_gb_per_sequential_worker_with_35pct_headroom:.2f} GB",
        f"- Memory-limited workers on 8/16/32 GB hosts with 25% reserved: {pipeline.memory_limited_workers_8gb}/{pipeline.memory_limited_workers_16gb}/{pipeline.memory_limited_workers_32gb}",
        f"- Pinned model cache: {pipeline.model_asset_cache_bytes / (1024 * 1024):.2f} MiB",
        f"- Descriptor JSON: {descriptor_bytes} bytes total; {output_kib_per_track:.2f} KiB per measured track",
        "",
        "## Algorithm totals and projections",
        "",
        "Only successful stages are included in projections. Failed attempts remain in the per-track table and failure count.",
        "",
        "| Algorithm | Tracks | Wall s/track | CPU % | Peak RSS MB | Min/audio hour | Min/100 tracks | RAM/worker GB | 8/16/32GB memory workers |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in run.algorithm_projections:
        worker_counts = f"{item.memory_limited_workers_8gb}/{item.memory_limited_workers_16gb}/{item.memory_limited_workers_32gb}"
        lines.append(
            f"| {item.algorithm_id} | {item.measured_tracks} | {item.mean_wall_time_s_per_track or 0:.2f} | {item.mean_cpu_utilization_percent or 0:.1f} | {item.max_peak_rss_mb:.1f} | {item.wall_minutes_per_audio_hour or 0:.2f} | {item.projected_serial_minutes_per_100_tracks or 0:.2f} | {item.projected_ram_gb_per_worker_with_35pct_headroom:.2f} | {worker_counts} |"
        )
    lines.extend([
        "",
        "CPU percent is measured process-tree CPU seconds divided by wall time and may exceed 100% when multiple cores are used. The normalized value is also retained in JSON.",
        "The CPU-thread value is a runtime request, not a guarantee; measured CPU percentage and peak thread count are authoritative.",
        "RAM/worker adds 35% to the observed process-tree peak; worker counts reserve 25% of VM RAM for the OS and orchestration.",
        "RSS is the capacity-planning RAM figure. macOS virtual memory size can be enormous and is retained only as raw telemetry in JSON.",
        f"Peaks are sampled every {min((result.metrics.telemetry_interval_s for track in run.tracks for result in track.algorithms if result.metrics), default=0):.2f} seconds, so very short spikes can be missed.",
        "These are linear projections from the measured sample, not VM benchmarks. Benchmark the chosen VM before committing capacity.",
        "",
        "## Per-track stage measurements",
        "",
        "| Track | Algorithm | Status | Wall s | CPU s | CPU % | Peak RSS MB | RTF | Min available RAM MB | Peak swap MB |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for track in run.tracks:
        for result in track.algorithms:
            metric = result.metrics
            if not metric:
                continue
            lines.append(
                f"| {track.source.filename.replace('|', '/')} | {result.algorithm_id} | {result.status}/{metric.status} | {metric.wall_time_s:.2f} | {metric.cpu_total_time_s:.2f} | {metric.cpu_utilization_percent:.1f} | {metric.peak_rss_mb:.1f} | {metric.realtime_factor or 0:.4f} | {metric.host_available_ram_min_mb:.0f} | {metric.host_swap_used_peak_mb:.0f} |"
            )
    lines.extend(["", f"Failures: {run.failure_count}. Source hashes unchanged: {run.source_hashes_unchanged}.", ""])
    return "\n".join(lines)


def analyze_folder(
    *,
    folder: Path,
    output_dir: Path,
    recursive: bool = False,
    source_name: str | None = None,
    max_tracks: int | None = 1,
    algorithms: list[str] | None = None,
    model_dir: Path | None = None,
    resume: bool = False,
    reuse_from: list[Path] | None = None,
    cpu_threads: int = 4,
    max_worker_rss_mb: float = 4096,
    min_available_ram_mb: float = 1024,
    worker_timeout_s: float = 1800,
    telemetry_interval_s: float = 0.2,
    progress=print,
) -> tuple[DescriptorRun, dict[str, Path]]:
    started_at = utc_now()
    source_folder = folder.expanduser().resolve()
    reuse_checkpoint_roots = validate_reuse_from(source_folder, output_dir, reuse_from)
    output = validate_output_dir(source_folder, output_dir, resume=resume)
    selected_algorithms = algorithms or list(DEFAULT_ALGORITHMS)
    unknown = sorted(set(selected_algorithms) - set(ALGORITHMS))
    if unknown:
        raise ValueError(f"Unknown algorithms: {', '.join(unknown)}")
    selected_algorithms = [item for item in ALGORITHMS if item in selected_algorithms]
    if not selected_algorithms:
        raise ValueError("Select at least one algorithm")
    verify_analysis_dependencies(selected_algorithms)
    if max_tracks is not None and max_tracks < 1:
        raise ValueError("max_tracks must be positive or None for an explicit all-track run")
    if cpu_threads < 1:
        raise ValueError("cpu_threads must be positive")
    all_paths, discovery_warnings = discover_audio(source_folder, recursive=recursive)
    initial_inventory = [(str(path.relative_to(source_folder)), path.stat().st_size) for path in all_paths]
    candidates = [p for p in all_paths if p.name == source_name] if source_name is not None else all_paths
    if source_name is not None and len(candidates) != 1: raise ValueError("Select exactly one discovered source by name")
    selected_paths = candidates[:max_tracks] if max_tracks is not None else candidates
    model_root = (model_dir or default_model_dir()).expanduser().resolve()
    asset_paths, assets = ensure_assets(model_root, required_assets(selected_algorithms))
    if set(selected_algorithms) & {"emotion_music2emo", "danceability_musicnn"}:
        from .supervised import verify_assets, manifest
        verify_assets()
        for item in manifest()['assets']:
            assets.append(ModelAssetRecord(asset_id='supervised_'+item['path'].replace('/', '_'), filename=item['path'], url=item['url'], sha256=item['sha256'], size_bytes=item['size_bytes'], downloaded=False, preparation_wall_time_s=0.0))
    if "semantic_audio" in selected_algorithms:
        from .semantic_audio import model_manifest
        for item in model_manifest()['assets']:
            assets.append(ModelAssetRecord(asset_id='semantic_audio_'+item['path'].replace('/','_'),filename=item['path'],url=item['url'],sha256=item['sha256'],size_bytes=item['size_bytes'],downloaded=False,preparation_wall_time_s=0.0))
    from .specialists import verify_assets as verify_specialists, stage_assets
    for stage in selected_algorithms:
        if stage in SPECIALIST_STAGES:
            verify_specialists(stage)
            for item in stage_assets(stage):
                if not any(a.asset_id == "specialist_"+item["path"] for a in assets):
                    assets.append(ModelAssetRecord(asset_id="specialist_"+item["path"],filename=item["path"],url=item["url"],sha256=item["sha256"],size_bytes=item["size_bytes"],downloaded=False,preparation_wall_time_s=0.0))
    asset_hashes = {item.asset_id: item.sha256 for item in assets}
    tools = _tool_versions()
    if set(selected_algorithms) & {"emotion_music2emo", "danceability_musicnn", "estimator_reference"}:
        for package in ('transformers', 'music21', 'pretty-midi', 'mir-eval', 'librosa', 'PyYAML', 'setuptools'):
            try: tools[package] = version(package)
            except Exception: tools[package] = 'unavailable'
    host = _host_profile()
    work = output / ".work"
    checkpoints = output / ".checkpoints"
    work.mkdir(exist_ok=True)
    checkpoints.mkdir(exist_ok=True)
    external_reuse_count = 0
    tracks: list[DescriptorTrack] = []
    for index, source in enumerate(selected_paths, start=1):
        relative = str(source.relative_to(source_folder))
        before = sha256_file(source)
        progress(f"PlaylistIQ track {index}/{len(selected_paths)}: {relative}")
        results: list[AlgorithmResult] = []
        duration = None
        for algorithm in selected_algorithms:
            config_digest = _checkpoint_digest(algorithm, before, cpu_threads, tools, asset_hashes)
            checkpoint = checkpoints / f"{before}.{algorithm}.json"
            result = None
            reuse_origin = None
            if resume:
                result = _load_compatible_checkpoint(
                    checkpoint,
                    algorithm=algorithm,
                    source_hash=before,
                    cpu_threads=cpu_threads,
                    tools=tools,
                    asset_hashes=asset_hashes,
                )
                if result is not None:
                    reuse_origin = "local output"
            if result is None:
                for reuse_root in reuse_checkpoint_roots:
                    candidate = reuse_root / checkpoint.name
                    result = _load_compatible_checkpoint(
                        candidate,
                        algorithm=algorithm,
                        source_hash=before,
                        cpu_threads=cpu_threads,
                        tools=tools,
                        asset_hashes=asset_hashes,
                    )
                    if result is not None:
                        reuse_origin = str(reuse_root.parent)
                        external_reuse_count += 1
                        break
            if result is not None:
                # Normalize legacy/imported checkpoint identity into this output.
                _atomic_json(checkpoint, {"checkpoint_digest": config_digest, "result": result.model_dump(mode="json")})
            if result is None and algorithm == "semantic_audio" and checkpoint.is_file():
                from .semantic_audio import audio_compatible, save_audio_cache
                try:
                    prior=json.loads(checkpoint.read_text())["result"]
                    if prior.get("status") in ("passed","warning") and audio_compatible(prior.get("values",{})):
                        save_audio_cache(before,prior["values"])
                except (OSError,ValueError,KeyError,TypeError):pass
            if result is None:
                progress(f"  {algorithm}: running")
                result = run_worker(
                    algorithm=algorithm,
                    source=source,
                    model_dir=model_root,
                    work_dir=work,
                    cpu_threads=cpu_threads,
                    max_rss_mb=max_worker_rss_mb,
                    min_available_ram_mb=min_available_ram_mb,
                    timeout_s=worker_timeout_s,
                    telemetry_interval_s=telemetry_interval_s,
                    duration_s=duration,
                )
                if result.status != "failed":
                    _atomic_json(checkpoint, {"checkpoint_digest": config_digest, "result": result.model_dump(mode="json")})
            else:
                progress(f"  {algorithm}: reused verified checkpoint from {reuse_origin}")
            results.append(result)
            if algorithm == "metadata" and isinstance(result.values.get("duration_s"), (int, float)):
                duration = float(result.values["duration_s"])
            metric = result.metrics
            if metric:
                progress(f"  {algorithm}: {result.status}, wall={metric.wall_time_s:.2f}s cpu={metric.cpu_utilization_percent:.1f}% peak_rss={metric.peak_rss_mb:.1f}MB")
        after = sha256_file(source)
        tracks.append(
            DescriptorTrack(
                track_id=f"sha256:{before}",
                source=SourceRecord(
                    relative_path=relative,
                    filename=source.name,
                    size_bytes=source.stat().st_size,
                    sha256_before=before,
                    sha256_after=after,
                    source_unchanged=before == after,
                ),
                duration_s=duration,
                algorithms=results,
                descriptor_document=_descriptor_document(results),
                warnings=[] if before == after else ["Source hash changed during analysis."],
            )
        )
    final_inventory = inventory(source_folder, recursive=recursive)
    projections = project_algorithms(tracks)
    model_asset_cache_bytes = sum(item.size_bytes for item in assets)
    pipeline_projection = project_pipeline(tracks, model_asset_cache_bytes=model_asset_cache_bytes)
    failure_count = sum(result.status == "failed" for track in tracks for result in track.algorithms)
    identity = {
        "started_at": started_at,
        "source_folder": str(source_folder),
        "tracks": [track.track_id for track in tracks],
        "algorithms": selected_algorithms,
        "pipeline": PIPELINE_VERSION,
    }
    run_id = "descriptor-run:" + hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:20]
    run = DescriptorRun(
        run_id=run_id,
        started_at=started_at,
        finished_at=utc_now(),
        source_folder=str(source_folder),
        recursive=recursive,
        selected_track_count=len(tracks),
        discovered_track_count=len(all_paths),
        selection_limit=max_tracks,
        algorithms_requested=selected_algorithms,
        cpu_threads_per_worker=cpu_threads,
        max_worker_rss_mb=max_worker_rss_mb,
        worker_timeout_s=worker_timeout_s,
        host=host,
        tool_versions=tools,
        model_assets=assets,
        tracks=tracks,
        algorithm_projections=projections,
        pipeline_projection=pipeline_projection,
        source_inventory_unchanged=initial_inventory == final_inventory,
        source_hashes_unchanged=all(track.source.source_unchanged for track in tracks),
        failure_count=failure_count,
        warnings=discovery_warnings + ([
            f"Reused {external_reuse_count} hash/config/version-verified checkpoints from prior descriptor output."
        ] if reuse_checkpoint_roots else []) + ["VM projections are linear estimates from this host and sample, not cloud benchmarks."],
    )
    descriptor_path = output / "descriptor-run.json"
    performance_json = output / "performance-report.json"
    performance_md = output / "performance-report.md"
    _atomic_json(descriptor_path, run.model_dump(mode="json", by_alias=True))
    descriptor_bytes = descriptor_path.stat().st_size
    _atomic_json(
        performance_json,
        {
            "schema": "prompt-playlist/performance-report",
            "schema_version": "0.1.0",
            "run_id": run.run_id,
            "host": run.host.model_dump(mode="json"),
            "requested_cpu_threads_per_worker": run.cpu_threads_per_worker,
            "pipeline_projection": run.pipeline_projection.model_dump(mode="json"),
            "algorithm_projections": [item.model_dump(mode="json") for item in run.algorithm_projections],
            "artifacts": {
                "descriptor_json_bytes": descriptor_bytes,
                "descriptor_json_bytes_per_track": descriptor_bytes / max(1, run.selected_track_count),
                "projected_descriptor_json_mb_per_100_tracks": descriptor_bytes / max(1, run.selected_track_count) * 100 / (1024 * 1024),
            },
            "track_metrics": [
                {"track_id": track.track_id, "filename": track.source.filename, "stages": [result.metrics.model_dump(mode="json") for result in track.algorithms if result.metrics]}
                for track in run.tracks
            ],
        },
    )
    temporary_md = performance_md.with_name(f".{performance_md.name}.tmp-{os.getpid()}")
    temporary_md.write_text(_performance_markdown(run, descriptor_bytes=descriptor_bytes), encoding="utf-8")
    temporary_md.replace(performance_md)
    try:
        work.rmdir()
    except OSError:
        pass
    paths = {"descriptors": descriptor_path, "performance_json": performance_json, "performance_markdown": performance_md}
    if "genre_maest" in selected_algorithms:
        from .genre_maest import review_document
        paths["genre_top10"] = output / "genre-top10.json"
        _atomic_json(paths["genre_top10"], review_document(run))
    return run, paths
