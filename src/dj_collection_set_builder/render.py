"""FFmpeg render tools. Source MP3s are never modified; outputs stay outside the music folder."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

from dj_collection_set_builder.constants import (
    DOWNBEAT_CLICK_DURATION_MS,
    DOWNBEAT_CLICK_FREQUENCY_HZ,
    DOWNBEAT_DIAGNOSTIC_MAX_DURATION_S,
    EQ_GAIN_DB_MAX,
    EQ_GAIN_DB_MIN,
    EQ_HIGH_HZ,
    EQ_LOW_HZ,
    EQ_MID_HZ,
    GAIN_DB_MAX,
    GAIN_DB_MIN,
    HOUSE_TRANSITION_CROSSOVER_HZ,
    HOUSE_TRANSITION_VERSION,
    LOOP_EDGE_CROSSFADE_MS,
    LOOP_REPETITIONS_MAX,
    LOW_CUT_HZ_DEFAULT,
    LOW_CUT_HZ_MAX,
    LOW_CUT_HZ_MIN,
    MIX_CROSSFADE_S_MAX,
    MIX_CROSSFADE_S_MIN,
    RENDER_CHANNELS,
    RENDER_SAMPLE_RATE_HZ,
    STRETCH_MAX_PERCENT,
)
from dj_collection_set_builder.ingest import sha256_file
from dj_collection_set_builder.models import RenderArtifact


class RenderError(ValueError):
    """Raised when a render tool is given out-of-bounds or invalid arguments."""


def _run_ffmpeg(arguments: list[str]) -> None:
    command = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *arguments]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RenderError(completed.stderr.strip() or "ffmpeg render failed")


def probe_duration_s(path: Path) -> float:
    completed = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RenderError(completed.stderr.strip() or "ffprobe duration failed")
    return float(completed.stdout.strip())


def ensure_output_path(
    out_path: Path,
    *,
    source_folder: Path | None = None,
    create_parent: bool = True,
) -> Path:
    out_path = out_path.resolve()
    if source_folder is not None:
        folder = source_folder.resolve()
        if out_path.is_relative_to(folder):
            raise RenderError("Render outputs must stay outside the source music folder")
    if create_parent:
        out_path.parent.mkdir(parents=True, exist_ok=True)
    return out_path


def _ensure_output_path(out_path: Path, *, source_folder: Path | None = None) -> Path:
    return ensure_output_path(out_path, source_folder=source_folder)


def _artifact(path: Path, *, artifact_id: str, tool: str, warnings: list[str] | None = None) -> RenderArtifact:
    return RenderArtifact(
        artifact_id=artifact_id,
        path=str(path),
        duration_s=probe_duration_s(path),
        sha256=sha256_file(path),
        tool=tool,
        warnings=list(warnings or []),
    )


def load_track(
    source: Path,
    *,
    start_s: float,
    end_s: float,
    out_path: Path,
    source_folder: Path | None = None,
) -> RenderArtifact:
    if end_s <= start_s:
        raise RenderError("end_s must be greater than start_s")
    if start_s < 0:
        raise RenderError("start_s must be >= 0")
    source = source.resolve()
    digest_before = sha256_file(source)
    out_path = _ensure_output_path(out_path, source_folder=source_folder)
    duration = end_s - start_s
    _run_ffmpeg(
        [
            "-i",
            str(source),
            "-ss",
            f"{start_s:.6f}",
            "-t",
            f"{duration:.6f}",
            "-ar",
            str(RENDER_SAMPLE_RATE_HZ),
            "-ac",
            str(RENDER_CHANNELS),
            "-c:a",
            "pcm_f32le",
            str(out_path),
        ]
    )
    if sha256_file(source) != digest_before:
        raise RenderError(f"Source hash changed while loading {source.name}")
    return _artifact(out_path, artifact_id=out_path.stem, tool="load_track")


def set_gain(
    source: Path,
    *,
    gain_db: float,
    out_path: Path,
    source_folder: Path | None = None,
) -> RenderArtifact:
    if not GAIN_DB_MIN <= gain_db <= GAIN_DB_MAX:
        raise RenderError(f"gain_db {gain_db} outside [{GAIN_DB_MIN}, {GAIN_DB_MAX}]")
    warnings = []
    if gain_db > 0:
        warnings.append("Positive gain is allowed but pending listening tests for mix-bus headroom.")
    out_path = _ensure_output_path(out_path, source_folder=source_folder)
    _run_ffmpeg(
        [
            "-i",
            str(source),
            "-af",
            f"volume={gain_db}dB",
            "-c:a",
            "pcm_f32le",
            str(out_path),
        ]
    )
    return _artifact(out_path, artifact_id=out_path.stem, tool="set_gain", warnings=warnings)


def time_stretch(
    source: Path,
    *,
    from_bpm: float,
    target_bpm: float,
    out_path: Path,
    source_folder: Path | None = None,
) -> RenderArtifact:
    if from_bpm <= 0 or target_bpm <= 0:
        raise RenderError("BPM values must be positive")
    percent = abs(target_bpm - from_bpm) / from_bpm * 100.0
    if percent > STRETCH_MAX_PERCENT + 1e-9:
        raise RenderError(
            f"Stretch {percent:.2f}% exceeds v1 maximum {STRETCH_MAX_PERCENT:g}%"
        )
    tempo = target_bpm / from_bpm
    out_path = _ensure_output_path(out_path, source_folder=source_folder)
    _run_ffmpeg(
        [
            "-i",
            str(source),
            "-af",
            f"atempo={tempo:.8f}",
            "-c:a",
            "pcm_f32le",
            str(out_path),
        ]
    )
    return _artifact(
        out_path,
        artifact_id=out_path.stem,
        tool="time_stretch",
        warnings=[
            "Pitch-preserving stretch uses FFmpeg atempo. Rubber Band remains a later quality comparison."
        ],
    )


def loop_audio(
    source: Path,
    *,
    repetitions: int,
    out_path: Path,
    crossfade_ms: float = LOOP_EDGE_CROSSFADE_MS,
    work_dir: Path | None = None,
    source_folder: Path | None = None,
) -> RenderArtifact:
    if repetitions < 1 or repetitions > LOOP_REPETITIONS_MAX:
        raise RenderError(f"repetitions must be 1..{LOOP_REPETITIONS_MAX}")
    if crossfade_ms < 4 or crossfade_ms > 40:
        raise RenderError("loop edge crossfade_ms must be between 4 and 40")
    out_path = _ensure_output_path(out_path, source_folder=source_folder)
    if repetitions == 1:
        shutil.copy2(source, out_path)
        return _artifact(out_path, artifact_id=out_path.stem, tool="loop")
    duration = probe_duration_s(source)
    fade_s = crossfade_ms / 1000.0
    if fade_s >= duration:
        raise RenderError("loop edge crossfade must be shorter than the source clip")
    work = (work_dir or out_path.parent).resolve()
    work.mkdir(parents=True, exist_ok=True)
    current = Path(source)
    temps: list[Path] = []
    for index in range(repetitions - 1):
        nxt = work / f"{out_path.stem}.loop{index}.wav"
        _run_ffmpeg(
            [
                "-i",
                str(current),
                "-i",
                str(source),
                "-filter_complex",
                f"acrossfade=d={fade_s:.6f}:c1=tri:c2=tri",
                "-c:a",
                "pcm_f32le",
                str(nxt),
            ]
        )
        temps.append(nxt)
        current = nxt
    if current.resolve() != out_path.resolve():
        shutil.copy2(current, out_path)
    for temp in temps:
        if temp.resolve() != out_path.resolve():
            temp.unlink(missing_ok=True)
    return _artifact(
        out_path,
        artifact_id=out_path.stem,
        tool="loop",
        warnings=[f"Loop-edge crossfade {crossfade_ms:g} ms (loop-edge-v1)."],
    )


def crossfade(
    outgoing: Path,
    incoming: Path,
    *,
    duration_s: float,
    out_path: Path,
    source_folder: Path | None = None,
) -> RenderArtifact:
    if not MIX_CROSSFADE_S_MIN <= duration_s <= MIX_CROSSFADE_S_MAX:
        raise RenderError(
            f"crossfade duration must be {MIX_CROSSFADE_S_MIN:g}–{MIX_CROSSFADE_S_MAX:g} s"
        )
    out_dur = probe_duration_s(outgoing)
    in_dur = probe_duration_s(incoming)
    if duration_s >= min(out_dur, in_dur):
        raise RenderError("crossfade duration must be shorter than both clips")
    out_path = _ensure_output_path(out_path, source_folder=source_folder)
    _run_ffmpeg(
        [
            "-i",
            str(outgoing),
            "-i",
            str(incoming),
            "-filter_complex",
            f"acrossfade=d={duration_s:.6f}:c1=tri:c2=tri",
            "-c:a",
            "pcm_f32le",
            str(out_path),
        ]
    )
    return _artifact(out_path, artifact_id=out_path.stem, tool="crossfade")


def house_transition(
    outgoing: Path,
    incoming: Path,
    *,
    duration_s: float,
    out_path: Path,
    source_folder: Path | None = None,
) -> RenderArtifact:
    """Mix a house transition with a midpoint bass handoff and broad high-band fades."""
    if not MIX_CROSSFADE_S_MIN <= duration_s <= MIX_CROSSFADE_S_MAX:
        raise RenderError(
            f"transition duration must be {MIX_CROSSFADE_S_MIN:g}–"
            f"{MIX_CROSSFADE_S_MAX:g} s"
        )
    outgoing_duration = probe_duration_s(outgoing)
    incoming_duration = probe_duration_s(incoming)
    if duration_s >= min(outgoing_duration, incoming_duration):
        raise RenderError("transition duration must be shorter than both clips")
    out_path = _ensure_output_path(out_path, source_folder=source_folder)

    prefix_duration = outgoing_duration - duration_s
    midpoint = duration_s / 2.0
    bass_handoff_duration = min(duration_s / 8.0, 3.0)
    bass_out_start = midpoint - bass_handoff_duration
    bass_in_end = midpoint + bass_handoff_duration
    crossover = HOUSE_TRANSITION_CROSSOVER_HZ
    graph = (
        f"[0:a]asplit=2[out_prefix_source][out_tail_source];"
        f"[out_prefix_source]atrim=end={prefix_duration:.6f},"
        "asetpts=PTS-STARTPTS[out_prefix];"
        f"[out_tail_source]atrim=start={prefix_duration:.6f},"
        "asetpts=PTS-STARTPTS,"
        f"acrossover=split={crossover:.2f}:order=4th[out_low_0][out_high_0];"
        f"[out_low_0]volume='if(lt(t,{bass_out_start:.6f}),1,"
        f"if(lt(t,{midpoint:.6f}),({midpoint:.6f}-t)/"
        f"{bass_handoff_duration:.6f},0))':eval=frame[out_low];"
        f"[out_high_0]volume='if(lt(t,{midpoint:.6f}),1,"
        f"max(0,({duration_s:.6f}-t)/{midpoint:.6f}))':eval=frame[out_high];"
        "[1:a]asplit=2[in_transition_source][in_remainder_source];"
        f"[in_transition_source]atrim=end={duration_s:.6f},"
        "asetpts=PTS-STARTPTS,"
        f"acrossover=split={crossover:.2f}:order=4th[in_low_0][in_high_0];"
        f"[in_low_0]volume='if(lt(t,{midpoint:.6f}),0,"
        f"if(lt(t,{bass_in_end:.6f}),(t-{midpoint:.6f})/"
        f"{bass_handoff_duration:.6f},1))':eval=frame[in_low];"
        f"[in_high_0]volume='if(lt(t,{midpoint:.6f}),t/"
        f"{midpoint:.6f},1)':eval=frame[in_high];"
        "[out_low][out_high][in_low][in_high]"
        "amix=inputs=4:duration=longest:normalize=0[transition];"
        f"[in_remainder_source]atrim=start={duration_s:.6f},"
        "asetpts=PTS-STARTPTS[in_remainder];"
        "[out_prefix][transition][in_remainder]concat=n=3:v=0:a=1[out]"
    )
    _run_ffmpeg(
        [
            "-i",
            str(outgoing),
            "-i",
            str(incoming),
            "-filter_complex",
            graph,
            "-map",
            "[out]",
            "-ar",
            str(RENDER_SAMPLE_RATE_HZ),
            "-ac",
            str(RENDER_CHANNELS),
            "-c:a",
            "pcm_f32le",
            str(out_path),
        ]
    )
    return _artifact(
        out_path,
        artifact_id=out_path.stem,
        tool="house_transition",
        warnings=[
            f"{HOUSE_TRANSITION_VERSION}: {crossover:g} Hz midpoint bass handoff; "
            "pending listening validation."
        ],
    )


def overlay_downbeat_clicks(
    source: Path,
    *,
    start_s: float,
    duration_s: float,
    downbeats_s: list[float],
    out_path: Path,
    source_folder: Path | None = None,
) -> RenderArtifact:
    """Render a source excerpt with short audible clicks at supplied absolute times."""
    if start_s < 0:
        raise RenderError("start_s must be >= 0")
    if duration_s <= 0 or duration_s > DOWNBEAT_DIAGNOSTIC_MAX_DURATION_S:
        raise RenderError(
            f"duration_s must be > 0 and <= {DOWNBEAT_DIAGNOSTIC_MAX_DURATION_S:g}"
        )
    relative = [
        float(value) - start_s
        for value in downbeats_s
        if start_s <= float(value) < start_s + duration_s
    ]
    if not relative:
        raise RenderError("No detected downbeats fall inside the requested diagnostic excerpt")
    out_path = _ensure_output_path(out_path, source_folder=source_folder)

    sample_count = int(round(duration_s * RENDER_SAMPLE_RATE_HZ))
    click_track = np.zeros(sample_count, dtype=np.float32)
    click_length = max(
        1,
        int(round(DOWNBEAT_CLICK_DURATION_MS / 1000.0 * RENDER_SAMPLE_RATE_HZ)),
    )
    time_axis = np.arange(click_length, dtype=np.float32) / RENDER_SAMPLE_RATE_HZ
    envelope = np.exp(-time_axis * 75.0)
    click = (
        0.7
        * np.sin(2.0 * np.pi * DOWNBEAT_CLICK_FREQUENCY_HZ * time_axis)
        * envelope
    ).astype(np.float32)
    for timestamp in relative:
        start_sample = int(round(timestamp * RENDER_SAMPLE_RATE_HZ))
        if start_sample >= sample_count:
            continue
        usable = min(click_length, sample_count - start_sample)
        click_track[start_sample : start_sample + usable] += click[:usable]

    with tempfile.TemporaryDirectory(prefix=f".{out_path.stem}.clicks-", dir=out_path.parent) as work:
        click_path = Path(work) / "clicks.wav"
        sf.write(click_path, click_track, RENDER_SAMPLE_RATE_HZ, subtype="FLOAT")
        _run_ffmpeg(
            [
                "-i",
                str(source),
                "-i",
                str(click_path),
                "-filter_complex",
                f"[0:a]atrim=start={start_s:.6f}:duration={duration_s:.6f},"
                "asetpts=PTS-STARTPTS,volume=0.65[base];"
                "[base][1:a]amix=inputs=2:duration=first:normalize=0[out]",
                "-map",
                "[out]",
                "-ar",
                str(RENDER_SAMPLE_RATE_HZ),
                "-ac",
                str(RENDER_CHANNELS),
                "-c:a",
                "pcm_f32le",
                str(out_path),
            ]
        )
    return _artifact(
        out_path,
        artifact_id=out_path.stem,
        tool="downbeat_click_overlay",
        warnings=["Clicks mark benchmark_estimate downbeats, not user-verified facts."],
    )


def eq_band(
    source: Path,
    *,
    band: str,
    gain_db: float,
    out_path: Path,
    source_folder: Path | None = None,
) -> RenderArtifact:
    if not EQ_GAIN_DB_MIN <= gain_db <= EQ_GAIN_DB_MAX:
        raise RenderError(f"EQ gain_db {gain_db} outside [{EQ_GAIN_DB_MIN}, {EQ_GAIN_DB_MAX}]")
    centers = {"low": EQ_LOW_HZ, "mid": EQ_MID_HZ, "high": EQ_HIGH_HZ}
    if band not in centers:
        raise RenderError("band must be low, mid, or high")
    out_path = _ensure_output_path(out_path, source_folder=source_folder)
    _run_ffmpeg(
        [
            "-i",
            str(source),
            "-af",
            f"equalizer=f={centers[band]}:t=q:w=1:g={gain_db}",
            "-c:a",
            "pcm_f32le",
            str(out_path),
        ]
    )
    return _artifact(
        out_path,
        artifact_id=out_path.stem,
        tool="eq_band",
        warnings=["EQ crossovers are eq-crossover-v1 pending listening tests."],
    )


def low_cut(
    source: Path,
    *,
    cutoff_hz: float = LOW_CUT_HZ_DEFAULT,
    out_path: Path,
    source_folder: Path | None = None,
) -> RenderArtifact:
    if not LOW_CUT_HZ_MIN <= cutoff_hz <= LOW_CUT_HZ_MAX:
        raise RenderError(f"cutoff_hz must be {LOW_CUT_HZ_MIN:g}–{LOW_CUT_HZ_MAX:g}")
    out_path = _ensure_output_path(out_path, source_folder=source_folder)
    _run_ffmpeg(
        [
            "-i",
            str(source),
            "-af",
            f"highpass=f={cutoff_hz}:poles=2",
            "-c:a",
            "pcm_f32le",
            str(out_path),
        ]
    )
    return _artifact(out_path, artifact_id=out_path.stem, tool="low_cut")


def render_segment(
    source: Path,
    *,
    operations: list[dict],
    out_path: Path,
    work_dir: Path | None = None,
    source_folder: Path | None = None,
) -> RenderArtifact:
    """Apply a sequence of single-source render ops. Crossfade stays a two-input tool."""
    out_path = _ensure_output_path(out_path, source_folder=source_folder)
    if not operations:
        shutil.copy2(source, out_path)
        return _artifact(out_path, artifact_id=out_path.stem, tool="render_segment")
    work = (work_dir or out_path.parent / f"{out_path.stem}.work").resolve()
    work.mkdir(parents=True, exist_ok=True)
    current = Path(source)
    temps: list[Path] = []
    last: RenderArtifact | None = None
    try:
        for index, operation in enumerate(operations):
            op_name = operation.get("op")
            nxt = work / f"step-{index:02d}-{op_name}.wav"
            if op_name == "set_gain":
                last = set_gain(
                    current,
                    gain_db=float(operation["gain_db"]),
                    out_path=nxt,
                    source_folder=source_folder,
                )
            elif op_name == "time_stretch":
                last = time_stretch(
                    current,
                    from_bpm=float(operation["from_bpm"]),
                    target_bpm=float(operation["target_bpm"]),
                    out_path=nxt,
                    source_folder=source_folder,
                )
            elif op_name == "eq_band":
                last = eq_band(
                    current,
                    band=str(operation["band"]),
                    gain_db=float(operation["gain_db"]),
                    out_path=nxt,
                    source_folder=source_folder,
                )
            elif op_name == "low_cut":
                last = low_cut(
                    current,
                    cutoff_hz=float(operation.get("cutoff_hz", LOW_CUT_HZ_DEFAULT)),
                    out_path=nxt,
                    source_folder=source_folder,
                )
            elif op_name == "loop":
                last = loop_audio(
                    current,
                    repetitions=int(operation["repetitions"]),
                    out_path=nxt,
                    crossfade_ms=float(operation.get("crossfade_ms", LOOP_EDGE_CROSSFADE_MS)),
                    work_dir=work,
                    source_folder=source_folder,
                )
            else:
                raise RenderError(f"Unsupported render_segment op: {op_name}")
            current = nxt
            temps.append(nxt)
        shutil.copy2(current, out_path)
    finally:
        for temp in temps:
            if temp.resolve() != out_path.resolve():
                temp.unlink(missing_ok=True)
    warnings = list(last.warnings) if last is not None else []
    warnings.append("render_segment chains single-source ops only; crossfade is separate.")
    return _artifact(out_path, artifact_id=out_path.stem, tool="render_segment", warnings=warnings)
