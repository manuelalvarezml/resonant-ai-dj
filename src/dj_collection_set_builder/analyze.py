"""Step 1 collection analyzer. Source MP3s are never modified."""

from __future__ import annotations

import gc
import json
import os
import platform
import shutil
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dj_collection_set_builder.ingest import (
    EmptyCorpusError,
    build_track_source,
    decode_analysis_pcm,
    decode_health_check,
    discover_audio_files,
    probe_stream,
    require_ffmpeg,
    sha256_file,
)
from dj_collection_set_builder.key_estimate import estimate_key
from dj_collection_set_builder.loudness import analyze_loudness
from dj_collection_set_builder.memory import (
    WorkerMemoryExceeded,
    memory_snapshot,
    run_capped_subprocess,
    wait_for_ram_headroom,
    wait_for_ram_recovery,
)
from dj_collection_set_builder.models import (
    AnalyzerFailure,
    CollectionAnalysis,
    KeyAnalysis,
    LoudnessAnalysis,
    StreamFacts,
    TrackAnalysis,
    TrackSource,
)
from dj_collection_set_builder.rhythm import (
    build_loop_candidates,
    build_sections,
    combine_tempo_and_grids,
)


class SourceModifiedError(RuntimeError):
    """Raised if a source MP3 hash changes during analysis."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _platform_info(ffmpeg_version: str) -> dict[str, str]:
    system = platform.system()
    os_name = "macOS" if system == "Darwin" else system
    return {
        "os": os_name,
        "architecture": platform.machine(),
        "python": sys.version.split()[0],
        "ffmpeg": ffmpeg_version,
    }


def _release_heavy_memory() -> None:
    gc.collect()
    try:
        import mlx.core as mx

        mx.clear_cache()
    except Exception:
        pass


def ingest_track(
    path: Path,
    folder: Path,
    *,
    work_dir: Path,
    ffmpeg_version: str,
    ffprobe_version: str,
) -> dict:
    """Loudness, key, and stream facts only. No MLX or PyTorch."""
    warnings: list[str] = []
    failures: list[AnalyzerFailure] = []
    source = build_track_source(path, folder)
    stream = probe_stream(path, ffprobe_version)

    health_status, health_messages = decode_health_check(path)
    stream.decode_health = health_status  # type: ignore[assignment]
    stream.decoder_warnings = health_messages
    if health_status == "failed":
        failures.append(
            AnalyzerFailure(
                analyzer="ffmpeg-decode-health",
                error_type="DecodeError",
                message="; ".join(health_messages) or "decode failed",
            )
        )

    pcm = None
    sample_rate = None
    pcm_path = work_dir / f"{source.sha256_before[:16]}.wav"
    try:
        pcm, sample_rate = decode_analysis_pcm(path, pcm_path)
    except Exception as exc:
        failures.append(
            AnalyzerFailure(
                analyzer="ffmpeg-pcm-decode",
                error_type=type(exc).__name__,
                message=str(exc),
            )
        )
        warnings.append(f"Analysis PCM decode failed: {exc}")

    loudness = analyze_loudness(path, pcm, sample_rate, ffmpeg_version)
    key = estimate_key(pcm, sample_rate)
    if pcm_path.exists():
        pcm_path.unlink()
    del pcm
    gc.collect()

    return {
        "source": source.model_dump(mode="json"),
        "stream": stream.model_dump(mode="json"),
        "loudness": loudness.model_dump(mode="json"),
        "key": key.model_dump(mode="json"),
        "warnings": warnings,
        "analyzer_failures": [item.model_dump(mode="json") for item in failures],
    }


def assemble_track(
    ingest: dict,
    allin1,
    beat_result,
    *,
    path: Path,
    beat_this_version: str | None = None,
    beat_this_fallback: str | None = None,
) -> TrackAnalysis:
    from dj_collection_set_builder.engines import EngineResult, allin1_version

    if not isinstance(allin1, EngineResult):
        allin1 = EngineResult.from_dict(allin1)
    if beat_result is not None and not isinstance(beat_result, EngineResult):
        beat_this_fallback = beat_this_fallback or beat_result.get("fallback_reason")
        beat_this_version = beat_this_version or beat_result.get("tool_version")
        beat_result = EngineResult.from_dict(beat_result)

    source = TrackSource.model_validate(ingest["source"])
    stream = StreamFacts.model_validate(ingest["stream"])
    loudness = LoudnessAnalysis.model_validate(ingest["loudness"])
    key = KeyAnalysis.model_validate(ingest["key"])
    warnings = list(ingest.get("warnings") or [])
    failures = [
        AnalyzerFailure.model_validate(item)
        for item in ingest.get("analyzer_failures") or []
    ]

    if allin1.error:
        failures.append(
            AnalyzerFailure(
                analyzer="all-in-one-mlx",
                error_type="EngineError",
                message=allin1.error,
            )
        )

    beat_error = None
    if beat_this_fallback:
        warnings.append(beat_this_fallback)
    if beat_result is None:
        beat_error = "Beat This was not initialized"
    else:
        if beat_result.return_order:
            warnings.append(f"Beat This return order: {beat_result.return_order}")
        if beat_result.error:
            beat_error = beat_result.error
            failures.append(
                AnalyzerFailure(
                    analyzer="beat-this",
                    error_type="EngineError",
                    message=beat_result.error,
                )
            )

    resolved_allin1_version = allin1.tool_version or allin1_version()
    tempo, grids = combine_tempo_and_grids(
        allin1_bpm=allin1.bpm,
        allin1_beats=allin1.beats_s,
        allin1_downbeats=allin1.downbeats_s,
        allin1_version=resolved_allin1_version,
        beat_this_beats=None if beat_result is None else beat_result.beats_s,
        beat_this_downbeats=None if beat_result is None else beat_result.downbeats_s,
        beat_this_version=beat_this_version
        or (None if beat_result is None else beat_result.tool_version),
        beat_this_error=beat_error,
        allin1_error=allin1.error,
    )

    primary_downbeats = allin1.downbeats_s or (
        beat_result.downbeats_s if beat_result is not None else []
    )
    sections = build_sections(
        allin1.segments,
        primary_downbeats,
        source_tool="all-in-one-mlx",
        tool_version=resolved_allin1_version,
    )
    challenger_downbeats = (
        beat_result.downbeats_s if beat_result is not None and not beat_result.error else None
    )
    loops = build_loop_candidates(
        source.track_id,
        primary_downbeats,
        sections,
        challenger_downbeats,
    )

    sha_after = sha256_file(path)
    source.sha256_after = sha_after
    source.source_unchanged = sha_after == source.sha256_before
    if not source.source_unchanged:
        raise SourceModifiedError(
            f"Source hash changed for {path.name}: "
            f"{source.sha256_before} -> {sha_after}"
        )

    return TrackAnalysis(
        analysis_id=str(uuid.uuid4()),
        analyzed_at=_utc_now(),
        source=source,
        stream=stream,
        loudness=loudness,
        tempo=tempo,
        rhythm_grids=grids,
        key=key,
        sections=sections,
        loop_candidates=loops,
        warnings=warnings,
        analyzer_failures=failures,
    )


def analyze_track(
    path: Path,
    folder: Path,
    *,
    work_dir: Path,
    ffmpeg_version: str,
    ffprobe_version: str,
    beat_this: object | None,
) -> TrackAnalysis:
    ingest = ingest_track(
        path,
        folder,
        work_dir=work_dir,
        ffmpeg_version=ffmpeg_version,
        ffprobe_version=ffprobe_version,
    )
    from dj_collection_set_builder.engines import EngineResult, run_allin1

    allin1_work = work_dir / ingest["source"]["sha256_before"][:16]
    allin1 = run_allin1(path, allin1_work)
    _release_heavy_memory()
    fallback = None
    version = None
    if beat_this is not None:
        beat_result = beat_this.analyze(path)
        fallback = getattr(beat_this, "fallback_reason", None)
        version = getattr(beat_this, "version", None)
    else:
        beat_result = EngineResult(
            beats_s=[],
            downbeats_s=[],
            error="Beat This was not initialized",
        )
    return assemble_track(
        ingest,
        allin1,
        beat_result,
        path=path,
        beat_this_version=version,
        beat_this_fallback=fallback,
    )


DEFAULT_MAX_WORKER_RSS_MB = 7168.0


def track_needs_rerun(track: TrackAnalysis) -> bool:
    if track.analyzer_failures:
        return True
    has_allin1_grid = any(
        grid.source_tool == "all-in-one-mlx" and grid.beat_count > 0
        for grid in track.rhythm_grids
    )
    return not has_allin1_grid


def ingest_is_reusable(track: TrackAnalysis) -> bool:
    return (
        track.loudness.integrated.value is not None
        and bool(track.key.tonic)
        and bool(track.source.sha256_before)
    )


def ingest_payload_from_track(track: TrackAnalysis) -> dict:
    warnings = [
        item
        for item in track.warnings
        if "Beat This" not in item and "all-in-one" not in item.lower()
    ]
    failures = [
        item.model_dump(mode="json")
        for item in track.analyzer_failures
        if item.analyzer not in {"all-in-one-mlx", "beat-this", "ram-guard"}
    ]
    return {
        "source": track.source.model_dump(mode="json"),
        "stream": track.stream.model_dump(mode="json"),
        "loudness": track.loudness.model_dump(mode="json"),
        "key": track.key.model_dump(mode="json"),
        "warnings": warnings,
        "analyzer_failures": failures,
    }


def beat_this_is_reusable(track: TrackAnalysis) -> bool:
    return any(
        grid.source_tool == "beat-this" and grid.beat_count > 0 and grid.status != "failed"
        for grid in track.rhythm_grids
    )


def beat_result_from_track(track: TrackAnalysis):
    from dj_collection_set_builder.engines import EngineResult

    grid = next(
        (item for item in track.rhythm_grids if item.source_tool == "beat-this"),
        None,
    )
    if grid is None or grid.beat_count <= 0:
        return None
    return_order = None
    for warning in track.warnings:
        if warning.startswith("Beat This return order:"):
            return_order = warning.split(":", 1)[1].strip()
            break
    return EngineResult(
        beats_s=list(grid.beats_s),
        downbeats_s=list(grid.downbeats_s),
        tool_version=grid.tool_version,
        return_order=return_order,
        device="cpu",
    )


def analyze_folder(
    folder: Path,
    out_path: Path,
    *,
    expected_count: int | None = None,
    recursive: bool = False,
    keep_work: bool = False,
    resume: bool = False,
    retry_failed: bool = True,
    isolate_tracks: bool = True,
    max_tracks: int = 1,
    max_worker_rss_mb: float = DEFAULT_MAX_WORKER_RSS_MB,
    min_reclaimable_ram_mb: float = 2048,
    pause_between_tracks_s: float = 8,
    progress=print,
) -> CollectionAnalysis:
    folder = folder.resolve()
    out_path = out_path.resolve()
    if max_tracks < 0:
        raise ValueError("--max-tracks must be 0 or greater")
    if folder.exists() and out_path.is_relative_to(folder):
        raise ValueError("Output path must be outside the source music folder")

    ffmpeg_version, ffprobe_version = require_ffmpeg()
    files, discovery_warnings = discover_audio_files(folder, recursive=recursive)

    collection_id = str(uuid.uuid4())
    warnings = list(discovery_warnings)
    failures: list[AnalyzerFailure] = []
    tracks: list[TrackAnalysis] = []
    if expected_count is not None and len(files) != expected_count:
        warnings.append(
            f"Discovered {len(files)} audio files; expected {expected_count}."
        )

    if resume and out_path.exists():
        existing = CollectionAnalysis.model_validate_json(out_path.read_text(encoding="utf-8"))
        if Path(existing.input_folder).resolve() != folder:
            raise ValueError(
                "Resume output belongs to a different input folder: "
                f"{existing.input_folder}"
            )
        collection_id = existing.collection_id
        tracks = list(existing.tracks)
        warnings = list(existing.warnings) + [
            w for w in discovery_warnings if w not in existing.warnings
        ]
        failures = [
            item
            for item in existing.failures
            if item.analyzer not in {"track-pipeline", "ram-guard"}
        ]
        progress(f"Resuming {len(tracks)} existing track(s) from {out_path}")

    pending_retries = {
        track.source.sha256_before: track
        for track in tracks
        if retry_failed and track_needs_rerun(track)
    }
    complete_hashes = {
        track.source.sha256_before
        for track in tracks
        if track.source.sha256_before not in pending_retries
    }

    work_root = out_path.parent / ".dj-engine-work" / collection_id
    work_root.mkdir(parents=True, exist_ok=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    snapshot = memory_snapshot()
    warnings.append(
        f"RAM policy: staged workers (ingest → all-in-one → beat-this), "
        f"RSS cap {max_worker_rss_mb:.0f} MB, "
        f"min reclaimable {min_reclaimable_ram_mb:.0f} MB for demix, "
        f"max_tracks={max_tracks or 'unlimited'} "
        f"(now {snapshot.reclaimable_mb:.0f} MB reclaimable, "
        f"{snapshot.swap_used_mb:.0f} MB swap, "
        f"{snapshot.total_bytes / (1024**3):.1f} GB total)"
    )
    progress(warnings[-1])

    collection = CollectionAnalysis(
        collection_id=collection_id,
        input_folder=str(folder),
        created_at=_utc_now(),
        platform=_platform_info(ffmpeg_version),
        expected_audio_count=expected_count,
        discovered_audio_count=len(files),
        tracks=tracks,
        warnings=warnings,
        failures=failures,
    )
    dump_collection(collection, out_path)

    try:
        processed = 0
        for index, path in enumerate(files, start=1):
            digest = sha256_file(path)
            if digest in complete_hashes:
                progress(f"[{index}/{len(files)}] skip (complete) {path.name}")
                continue
            if max_tracks > 0 and processed >= max_tracks:
                warnings.append(
                    f"Stopped after {processed} new track(s) (--max-tracks {max_tracks}). "
                    "Re-run with --resume to continue."
                )
                progress(warnings[-1])
                break
            progress(f"[{index}/{len(files)}] {path.name}")
            try:
                wait_for_ram_headroom(
                    min_reclaimable_mb=min(512.0, min_reclaimable_ram_mb),
                    progress=progress,
                )
            except MemoryError as exc:
                previous = pending_retries.get(digest)
                if previous and all(item.source.sha256_before != digest for item in tracks):
                    tracks.append(previous)
                failures.append(
                    AnalyzerFailure(
                        analyzer="ram-guard",
                        error_type="MemoryError",
                        message=f"{path.name}: {exc}",
                    )
                )
                warnings.append(str(exc))
                progress(str(exc))
                break
            track_work = work_root / f"{index:02d}"
            if track_work.exists():
                shutil.rmtree(track_work, ignore_errors=True)
            track_work.mkdir(parents=True, exist_ok=True)
            try:
                if isolate_tracks:
                    track = _analyze_track_isolated(
                        path,
                        folder,
                        work_dir=track_work,
                        ffmpeg_version=ffmpeg_version,
                        ffprobe_version=ffprobe_version,
                        max_worker_rss_mb=max_worker_rss_mb,
                        min_reclaimable_ram_mb=min_reclaimable_ram_mb,
                        previous=pending_retries.get(digest),
                        progress=progress,
                    )
                else:
                    from dj_collection_set_builder.engines import BeatThisRunner

                    track = analyze_track(
                        path,
                        folder,
                        work_dir=track_work,
                        ffmpeg_version=ffmpeg_version,
                        ffprobe_version=ffprobe_version,
                        beat_this=BeatThisRunner(device="cpu"),
                    )
                tracks = [
                    item
                    for item in tracks
                    if item.source.sha256_before != track.source.sha256_before
                ]
                tracks.append(track)
                if not track_needs_rerun(track):
                    complete_hashes.add(track.source.sha256_before)
                failures.extend(track.analyzer_failures)
            except SourceModifiedError:
                raise
            except (WorkerMemoryExceeded, TimeoutError, MemoryError) as exc:
                previous = pending_retries.get(digest)
                if previous and all(item.source.sha256_before != digest for item in tracks):
                    tracks.append(previous)
                failures.append(
                    AnalyzerFailure(
                        analyzer="ram-guard",
                        error_type=type(exc).__name__,
                        message=f"{path.name}: {exc}",
                    )
                )
                warnings.append(f"Stopped {path.name} to protect host RAM: {exc}")
                progress(warnings[-1])
            except Exception as exc:
                previous = pending_retries.get(digest)
                if previous and all(item.source.sha256_before != digest for item in tracks):
                    tracks.append(previous)
                failures.append(
                    AnalyzerFailure(
                        analyzer="track-pipeline",
                        error_type=type(exc).__name__,
                        message=f"{path.name}: {exc}",
                    )
                )
                warnings.append(f"Partial failure for {path.name}: {exc}")
            finally:
                processed += 1
                if not keep_work and track_work.exists():
                    shutil.rmtree(track_work, ignore_errors=True)
            collection = collection.model_copy(
                update={"tracks": tracks, "warnings": warnings, "failures": failures}
            )
            dump_collection(collection, out_path)
            gc.collect()
            wait_for_ram_recovery(
                min_reclaimable_mb=min(1024.0, min_reclaimable_ram_mb),
                timeout_s=30,
                progress=progress,
            )
            if pause_between_tracks_s > 0 and index < len(files):
                time.sleep(pause_between_tracks_s)
    finally:
        if not keep_work and work_root.exists():
            shutil.rmtree(work_root, ignore_errors=True)

    current_failures = [item for track in tracks for item in track.analyzer_failures]
    current_failures.extend(
        item
        for item in failures
        if item.analyzer in {"track-pipeline", "ram-guard"}
    )
    collection = collection.model_copy(
        update={"tracks": tracks, "warnings": warnings, "failures": current_failures}
    )
    dump_collection(collection, out_path)
    return collection


def _analyze_track_isolated(
    path: Path,
    folder: Path,
    *,
    work_dir: Path,
    ffmpeg_version: str,
    ffprobe_version: str,
    max_worker_rss_mb: float,
    min_reclaimable_ram_mb: float,
    previous: TrackAnalysis | None = None,
    progress=print,
) -> TrackAnalysis:
    from dj_collection_set_builder.engines import EngineResult

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

    ingest_json = work_dir / "ingest.json"
    allin1_json = work_dir / "allin1.json"
    beat_json = work_dir / "beatthis.json"
    allin1_work = work_dir / "allin1-work"
    allin1_work.mkdir(parents=True, exist_ok=True)

    if previous is not None and ingest_is_reusable(previous):
        progress(f"stage ingest {path.name} skip (reuse)")
        ingest = ingest_payload_from_track(previous)
        ingest_json.write_text(json.dumps(ingest, indent=2), encoding="utf-8")
    else:
        progress(f"stage ingest {path.name}")
        _run_isolated_stage(
            "ingest",
            [
                sys.executable,
                "-m",
                "dj_collection_set_builder.track_worker",
                "--stage",
                "ingest",
                "--path",
                str(path),
                "--folder",
                str(folder),
                "--work-dir",
                str(work_dir),
                "--out",
                str(ingest_json),
                "--ffmpeg-version",
                ffmpeg_version,
                "--ffprobe-version",
                ffprobe_version,
            ],
            env=env,
            label=path.name,
            max_rss_mb=min(1536.0, max_worker_rss_mb),
            start_reclaimable_mb=min(512.0, min_reclaimable_ram_mb),
            kill_reclaimable_mb=256.0,
            timeout_s=180,
            recover_reclaimable_mb=512.0,
            progress=progress,
        )
        ingest = json.loads(ingest_json.read_text(encoding="utf-8"))

    allin1: EngineResult
    try:
        progress(f"stage allin1 {path.name}")
        wait_for_ram_headroom(
            min_reclaimable_mb=min_reclaimable_ram_mb,
            progress=progress,
        )
        _run_isolated_stage(
            "allin1",
            [
                sys.executable,
                "-m",
                "dj_collection_set_builder.track_worker",
                "--stage",
                "allin1",
                "--path",
                str(path),
                "--work-dir",
                str(allin1_work),
                "--out",
                str(allin1_json),
            ],
            env=env,
            label=path.name,
            max_rss_mb=max_worker_rss_mb,
            start_reclaimable_mb=0.0,
            kill_reclaimable_mb=max(768.0, min_reclaimable_ram_mb * 0.4),
            timeout_s=900,
            recover_reclaimable_mb=min(1536.0, min_reclaimable_ram_mb),
            progress=progress,
        )
        allin1 = EngineResult.from_dict(json.loads(allin1_json.read_text(encoding="utf-8")))
    except (WorkerMemoryExceeded, TimeoutError, MemoryError, RuntimeError) as exc:
        progress(f"All-In-One skipped or killed for {path.name}: {exc}")
        allin1 = EngineResult(beats_s=[], downbeats_s=[], error=str(exc), device="mlx")
        gc.collect()
        wait_for_ram_recovery(min_reclaimable_mb=768.0, timeout_s=45, progress=progress)
    finally:
        if allin1_work.exists():
            shutil.rmtree(allin1_work, ignore_errors=True)

    beat_result: EngineResult
    beat_fallback = None
    if previous is not None and beat_this_is_reusable(previous):
        progress(f"stage beatthis {path.name} skip (reuse)")
        reused = beat_result_from_track(previous)
        if reused is None:
            beat_result = EngineResult(beats_s=[], downbeats_s=[], error="Beat This reuse failed")
        else:
            beat_result = reused
    else:
        try:
            progress(f"stage beatthis {path.name}")
            wait_for_ram_headroom(
                min_reclaimable_mb=min(1024.0, min_reclaimable_ram_mb),
                timeout_s=60,
                progress=progress,
            )
            _run_isolated_stage(
                "beatthis",
                [
                    sys.executable,
                    "-m",
                    "dj_collection_set_builder.track_worker",
                    "--stage",
                    "beatthis",
                    "--path",
                    str(path),
                    "--out",
                    str(beat_json),
                ],
                env=env,
                label=path.name,
                max_rss_mb=min(2048.0, max_worker_rss_mb),
                start_reclaimable_mb=0.0,
                kill_reclaimable_mb=512.0,
                timeout_s=300,
                recover_reclaimable_mb=768.0,
                progress=progress,
            )
            beat_payload = json.loads(beat_json.read_text(encoding="utf-8"))
            beat_result = EngineResult.from_dict(beat_payload)
            beat_fallback = beat_payload.get("fallback_reason")
        except (WorkerMemoryExceeded, TimeoutError, MemoryError, RuntimeError) as exc:
            progress(f"Beat This skipped or killed for {path.name}: {exc}")
            beat_result = EngineResult(beats_s=[], downbeats_s=[], error=str(exc), device="cpu")
            beat_fallback = None
            gc.collect()
            wait_for_ram_recovery(min_reclaimable_mb=512.0, timeout_s=30, progress=progress)

    return assemble_track(
        ingest,
        allin1,
        beat_result,
        path=path,
        beat_this_fallback=beat_fallback,
    )


def _run_isolated_stage(
    stage: str,
    command: list[str],
    *,
    env: dict[str, str],
    label: str,
    max_rss_mb: float,
    start_reclaimable_mb: float,
    kill_reclaimable_mb: float,
    timeout_s: float,
    recover_reclaimable_mb: float,
    progress,
) -> None:
    if start_reclaimable_mb > 0:
        wait_for_ram_headroom(
            min_reclaimable_mb=start_reclaimable_mb,
            progress=progress,
        )
    completed = run_capped_subprocess(
        command,
        env=env,
        max_rss_mb=max_rss_mb,
        min_reclaimable_mb=kill_reclaimable_mb,
        timeout_s=timeout_s,
        stage=stage,
        label=label,
        progress=progress,
    )
    gc.collect()
    wait_for_ram_recovery(
        min_reclaimable_mb=recover_reclaimable_mb,
        timeout_s=45,
        progress=progress,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"{stage} worker exited {completed.returncode} for {label}")
    out = Path(command[command.index("--out") + 1])
    if not out.exists():
        raise RuntimeError(f"{stage} worker produced no JSON for {label}")


def dump_collection(collection: CollectionAnalysis, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = out_path.with_name(f".{out_path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("w", encoding="utf-8") as handle:
            handle.write(collection.model_dump_json(indent=2, by_alias=True))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, out_path)
    finally:
        temporary.unlink(missing_ok=True)
