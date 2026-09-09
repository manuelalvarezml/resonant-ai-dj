"""JSON boundaries: native catalogs, a read-only DJ importer, and safe exports.

The importer deliberately knows only the DJ JSON contract. It never imports
the engine, resolves source audio paths, or estimates semantic descriptors.
"""

from __future__ import annotations

import json
import math
import os
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from .models import Catalog, CatalogTrack, NumericEvidence

DJ_SCHEMA = "dj-engine/collection-analysis"
DJ_TRACK_SCHEMA = "dj-engine/track-analysis"
DJ_VERSION = "0.1.0"
_AUDIO_SUFFIXES = frozenset(
    ".mp3 .wav .wave .aif .aiff .aifc .flac .m4a .m4b .aac .ogg .oga "
    ".opus .wma .alac .ape .dsf .dff .mid .midi .au .snd .caf .mp4 .webm".split()
)
_MUSIC_DIRECTORIES = frozenset(
    {"music", "audio", "songs", "tracks", "test_folder_10_house_tracks", "test_tracks_folder_mp3"}
)
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def load_catalog(path: Path) -> Catalog:
    """Load the native catalog format; use explicit ``import-dj`` for DJ JSON."""
    return Catalog.model_validate_json(Path(path).read_text(encoding="utf-8"))


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a nonempty string")
    return value


def _warnings(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"{label} must be a list of strings")
    return list(value)


def _schema(data: dict[str, Any], expected: str, label: str) -> None:
    if data.get("schema") != expected or data.get("schema_version") != DJ_VERSION:
        raise ValueError(f"{label} must use {expected} schema version {DJ_VERSION}")


def _positive_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite positive number or null")
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{label} must be a finite positive number or null")
    return float(value)


def _provenance(base: dict[str, str], **details: Any) -> str:
    return json.dumps({**base, **details}, sort_keys=True, ensure_ascii=False, allow_nan=False)


def from_dj_collection(data: dict) -> Catalog:
    """Import stored numeric evidence without reading any source audio.

    Hashes are checked for consistency *within the artifact*, not reverified
    against files. An incomplete hash check remains a warning. A reported
    change or conflicting hash is rejected. Rejected/failed numeric evidence
    keeps its original status; the search layer decides eligibility.
    """
    data = _object(data, "DJ collection")
    _schema(data, DJ_SCHEMA, "DJ collection")
    collection_id = _text(data.get("collection_id"), "collection_id")
    raw_tracks = data.get("tracks")
    if not isinstance(raw_tracks, list):
        raise ValueError("tracks must be a list")
    catalog_warnings = _warnings(data.get("warnings", []), "collection warnings")
    catalog_warnings.extend(
        [
            "Imported from stored DJ analysis JSON; source audio hashes were not reverified.",
            "No genre, mood, energy, or vocal tags are inferred from DJ analysis or filenames.",
        ]
    )
    tracks: list[CatalogTrack] = []
    for index, raw in enumerate(raw_tracks):
        label = f"tracks[{index}]"
        raw = _object(raw, label)
        _schema(raw, DJ_TRACK_SCHEMA, label)
        analysis_id = _text(raw.get("analysis_id"), f"{label}.analysis_id")
        source = _object(raw.get("source"), f"{label}.source")
        sha = source.get("sha256_before")
        if not isinstance(sha, str) or not _SHA256.fullmatch(sha):
            raise ValueError(f"{label}.source.sha256_before must be a lowercase SHA-256 digest")
        track_id = _text(source.get("track_id"), f"{label}.source.track_id")
        if track_id != f"sha256:{sha}":
            raise ValueError(f"{label}.source.track_id does not match sha256_before")
        sha_after = source.get("sha256_after")
        if sha_after is not None and sha_after != sha:
            raise ValueError(f"{label} source hashes disagree")
        unchanged = source.get("source_unchanged")
        if unchanged is not None and type(unchanged) is not bool:
            raise ValueError(f"{label}.source.source_unchanged must be boolean or null")
        if unchanged is False:
            raise ValueError(f"{label} reports changed source audio")
        if unchanged is True and sha_after is None:
            raise ValueError(f"{label} claims unchanged source without sha256_after")
        filename = _text(source.get("filename"), f"{label}.source.filename")
        if "/" in filename or "\\" in filename or filename in {".", ".."}:
            raise ValueError(f"{label}.source.filename must be a filename, not a path")
        warnings = _warnings(raw.get("warnings", []), f"{label}.warnings")
        if sha_after is None or unchanged is not True:
            warnings.append("Source hash verification was incomplete in the imported DJ artifact.")
        warnings.append("Display title comes from the source filename; artist and semantic tags are unknown.")
        base = {
            "schema": DJ_SCHEMA,
            "schema_version": DJ_VERSION,
            "collection_id": collection_id,
            "analysis_id": analysis_id,
            "sha256": sha,
        }
        bpm = None
        tempo = _object(raw.get("tempo", {}), f"{label}.tempo")
        selected = tempo.get("selected_candidate")
        if selected is not None:
            selected = _object(selected, f"{label}.tempo.selected_candidate")
            warnings.extend(_warnings(selected.get("warnings", []), f"{label}.tempo warnings"))
            if selected.get("value") is not None:
                if selected.get("unit") != "BPM":
                    raise ValueError(f"{label}.tempo.selected_candidate.unit must be BPM")
                if selected.get("authority") != "benchmark_estimate":
                    raise ValueError(f"{label} DJ tempo must retain benchmark_estimate authority")
                bpm = NumericEvidence(
                    value=_positive_number(selected["value"], f"{label}.bpm"),
                    authority=selected["authority"],
                    status=selected.get("status"),
                    confidence=selected.get("confidence"),
                    source=_provenance(
                        base,
                        field="tempo.selected_candidate",
                        source_tool=selected.get("source_tool"),
                        tool_version=selected.get("tool_version"),
                        model_id=selected.get("model_id"),
                    ),
                )
        if bpm is None:
            warnings.append("No stored BPM value is available; tempo remains unknown.")
        duration = None
        stream = _object(raw.get("stream", {}), f"{label}.stream")
        if stream.get("duration_s") is not None:
            duration = NumericEvidence(
                value=_positive_number(stream["duration_s"], f"{label}.duration_s"),
                authority=stream.get("authority"),
                status=stream.get("status"),
                source=_provenance(
                    base,
                    field="stream.duration_s",
                    source_tool=stream.get("probe_tool"),
                    tool_version=stream.get("probe_version"),
                ),
            )
        tracks.append(
            CatalogTrack(
                track_id=track_id,
                title=Path(filename).stem,
                bpm=bpm,
                duration_s=duration,
                warnings=list(dict.fromkeys(warnings)),
            )
        )
    return Catalog(catalog_id=f"dj:{collection_id}", tracks=tracks, warnings=catalog_warnings)


def _safe_output_path(path: Path) -> Path:
    original = Path(path).expanduser()
    if os.path.lexists(original):
        raise ValueError(f"Output already exists: {original}")
    resolved = original.resolve()
    if resolved.suffix.casefold() in _AUDIO_SUFFIXES:
        raise ValueError("JSON output must not use an audio or media file extension")
    # Check both spelled and resolved names, so aliases into Music are covered.
    for candidate in (original.absolute(), resolved):
        if any(part.casefold() in _MUSIC_DIRECTORIES for part in candidate.parent.parts):
            raise ValueError("JSON output must be outside music/audio folders")
    for parent in resolved.parents:
        if parent.is_dir() and any(
            child.suffix.casefold() in _AUDIO_SUFFIXES and (child.is_file() or child.is_symlink())
            for child in parent.iterdir()
        ):
            raise ValueError(f"JSON output must be outside folders containing audio files: {parent}")
    return resolved


def save_json(value: BaseModel, path: Path) -> None:
    """Write a new JSON file outside music folders; never replace an output.

    Serialization and safety checks precede directory creation. Exclusive file
    creation also prevents an output appearing after the initial check from
    being overwritten. This function does not open or modify any audio file.
    """
    payload = value.model_dump_json(by_alias=True, indent=2) + "\n"
    destination = _safe_output_path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("x", encoding="utf-8") as handle:
        handle.write(payload)
