"""Discover source files, hash them, and collect stream facts. Never write into the source folder."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from dj_collection_set_builder.constants import (
    ANALYSIS_CHANNELS,
    ANALYSIS_SAMPLE_RATE_HZ,
    AUTHORITY_ENCODED_FACT,
    STATUS_FAILED,
    STATUS_NOT_RUN,
    STATUS_PASSED,
    STATUS_WARNING,
    SUPPORTED_AUDIO_EXTENSIONS,
)
from dj_collection_set_builder.models import StreamFacts, TrackSource


class EmptyCorpusError(ValueError):
    """Raised when a folder contains no supported audio files."""


class MissingFFmpegError(RuntimeError):
    """Raised when ffmpeg/ffprobe is not available."""


@dataclass(frozen=True)
class DiscoveredFile:
    path: Path
    relative_path: str
    warning: str | None = None


def require_ffmpeg() -> tuple[str, str]:
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        raise MissingFFmpegError(
            "ffmpeg and ffprobe must be on PATH. V1 uses the local Homebrew build."
        )
    return _tool_version("ffmpeg"), _tool_version("ffprobe")


def _tool_version(name: str) -> str:
    output = subprocess.check_output([name, "-version"], text=True, stderr=subprocess.STDOUT)
    first = output.splitlines()[0]
    parts = first.split()
    if len(parts) >= 3:
        return parts[2]
    return first.strip()


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def discover_audio_files(
    folder: Path,
    *,
    recursive: bool = False,
) -> tuple[list[Path], list[str]]:
    folder = folder.resolve()
    if not folder.is_dir():
        raise NotADirectoryError(str(folder))

    iterator = folder.rglob("*") if recursive else folder.iterdir()
    audio: list[Path] = []
    warnings: list[str] = []
    for path in sorted(iterator, key=lambda item: str(item).lower()):
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue
        suffix = path.suffix.lower()
        if suffix in SUPPORTED_AUDIO_EXTENSIONS:
            audio.append(path)
            continue
        warnings.append(f"Skipped unsupported file: {path.name}")

    if not audio:
        raise EmptyCorpusError(f"No supported audio files found in {folder}")
    return audio, warnings


def relative_source_path(path: Path, folder: Path) -> str:
    path = path.resolve()
    folder = folder.resolve()
    try:
        return str(path.relative_to(folder.parent))
    except ValueError:
        return str(path)


def build_track_source(path: Path, folder: Path) -> TrackSource:
    digest = sha256_file(path)
    return TrackSource(
        track_id=f"sha256:{digest}",
        path=relative_source_path(path, folder),
        filename=path.name,
        size_bytes=path.stat().st_size,
        sha256_before=digest,
        sha256_after=None,
        source_unchanged=None,
    )


def _parse_int(value: object) -> int | None:
    if value in (None, "", "N/A"):
        return None
    try:
        return int(float(str(value)))
    except (TypeError, ValueError):
        return None


def _parse_float(value: object) -> float | None:
    if value in (None, "", "N/A"):
        return None
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None


def probe_stream(path: Path, probe_version: str) -> StreamFacts:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(path),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        return StreamFacts(
            authority=AUTHORITY_ENCODED_FACT,
            status=STATUS_FAILED,
            probe_tool="ffprobe",
            probe_version=probe_version,
            decoder_warnings=[completed.stderr.strip() or "ffprobe failed"],
        )

    payload = json.loads(completed.stdout or "{}")
    audio_stream = next(
        (
            stream
            for stream in payload.get("streams", [])
            if stream.get("codec_type") == "audio"
        ),
        {},
    )
    fmt = payload.get("format", {})
    bit_rate = _parse_int(audio_stream.get("bit_rate") or fmt.get("bit_rate"))
    return StreamFacts(
        authority=AUTHORITY_ENCODED_FACT,
        status=STATUS_PASSED,
        probe_tool="ffprobe",
        probe_version=probe_version,
        codec=audio_stream.get("codec_name"),
        sample_rate_hz=_parse_int(audio_stream.get("sample_rate")),
        channels=_parse_int(audio_stream.get("channels")),
        channel_layout=audio_stream.get("channel_layout"),
        bit_rate_bps=bit_rate,
        # ffprobe's sample_fmt describes decoded sample representation, not
        # whether an MP3 stream is CBR/VBR. Leave this unknown until a real
        # bitrate-mode detector is added.
        bit_rate_mode=None,
        duration_s=_parse_float(audio_stream.get("duration") or fmt.get("duration")),
        decode_health=STATUS_NOT_RUN,
        decoder_warnings=[],
    )


def decode_health_check(path: Path) -> tuple[str, list[str]]:
    command = [
        "ffmpeg",
        "-v",
        "error",
        "-i",
        str(path),
        "-f",
        "null",
        "-",
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    messages = [
        line.strip()
        for line in completed.stderr.splitlines()
        if line.strip()
    ]
    if completed.returncode != 0:
        return STATUS_FAILED, messages or ["ffmpeg decode failed"]
    if messages:
        return STATUS_WARNING, messages
    return STATUS_PASSED, []


def decode_analysis_pcm(path: Path, destination: Path) -> tuple[object, int]:
    """Decode to a temporary 44.1 kHz stereo float32 WAV outside the source folder."""
    import soundfile as sf

    destination.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(path),
        "-ar",
        str(ANALYSIS_SAMPLE_RATE_HZ),
        "-ac",
        str(ANALYSIS_CHANNELS),
        "-c:a",
        "pcm_f32le",
        str(destination),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "ffmpeg PCM decode failed")
    pcm, sample_rate = sf.read(str(destination), dtype="float32", always_2d=True)
    return pcm, int(sample_rate)
