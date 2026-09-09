"""Explicit, read-only folder import using bounded FFprobe metadata reads.

This optional adapter needs an FFprobe executable, but no Python audio/ML
package. It never decodes samples, classifies songs, or writes into the input
folder. Embedded tags are annotations, not verified musical facts.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import shutil
import stat
import subprocess
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from pydantic import Field

from .models import Catalog, CatalogTrack, NumericEvidence, StrictModel, TagEvidence, Vocabulary

IMPORT_VERSION = "mp3-metadata-v1"
_HASH_BUFFER = 1024 * 1024
_PROBE_OUTPUT_LIMIT = 4 * 1024 * 1024
_IMPORTED_KEYS = frozenset({"title", "artist", "genre", "bpm", "tbpm", "tempo"})


class FolderImportEntry(StrictModel):
    path: str
    filename: str
    status: Literal["pending", "imported", "duplicate", "skipped", "failed", "changed"]
    track_id: str | None = None
    sha256_before: str | None = None
    sha256_after: str | None = None
    source_unchanged: bool | None = None
    container_format: str | None = None
    encoded_tags: dict[str, str] = Field(default_factory=dict)
    observed_tag_keys: list[str] = Field(default_factory=list)
    mapped_genres: list[str] = Field(default_factory=list)
    unmapped_genres: list[str] = Field(default_factory=list)
    field_sources: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class FolderImportManifest(StrictModel):
    schema_name: Literal["prompt-playlist/folder-import"] = Field(
        default="prompt-playlist/folder-import", alias="schema"
    )
    schema_version: Literal["0.1.0"] = "0.1.0"
    importer_version: Literal["mp3-metadata-v1"] = IMPORT_VERSION
    source_folder: str
    catalog_id: str
    vocabulary_id: str
    vocabulary_digest: str
    ffprobe_executable: str
    ffprobe_version: str
    probe_timeout_s: float
    started_at: str
    finished_at: str
    source_inventory_unchanged: bool
    source_hashes_unchanged: bool
    entries: list[FolderImportEntry]
    # Every imported ID has its source paths; multiple paths explicitly report duplicates.
    aliases: dict[str, list[str]]
    coverage: dict[str, int]
    tag_key_coverage: dict[str, int]
    warnings: list[str]


def _sha256(path: Path) -> str:
    """Hash in small buffers and refuse symlink/nonregular file reads."""
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    with os.fdopen(descriptor, "rb") as handle:
        if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
            raise ValueError("Source must remain a regular file")
        digest = hashlib.sha256()
        for block in iter(lambda: handle.read(_HASH_BUFFER), b""):
            digest.update(block)
    return digest.hexdigest()


def _probe_file(path: Path, ffprobe: str, timeout_s: float) -> dict[str, Any]:
    # Local file protocol only: a misleading extension must not cause network access.
    args = [
        ffprobe, "-v", "error", "-protocol_whitelist", "file", "-probesize", "1048576",
        "-analyzeduration", "1000000", "-show_entries", "format=format_name,duration:format_tags",
        "-of", "json", str(path),
    ]
    # Bounded memory even for very large embedded tags. Temporary output is outside
    # the music folder, deleted on success/failure, and never delivered as an artifact.
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        try:
            completed = subprocess.run(
                args, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                timeout=timeout_s, check=False, shell=False,
            )
        except subprocess.TimeoutExpired as error:
            raise ValueError(f"FFprobe exceeded {timeout_s:g} seconds") from error
        if completed.returncode:
            # Do not expose arbitrary embedded data or unbounded diagnostic output.
            raise ValueError(f"FFprobe failed (exit {completed.returncode})")
        stdout.seek(0)
        payload = stdout.read(_PROBE_OUTPUT_LIMIT + 1)
    if len(payload) > _PROBE_OUTPUT_LIMIT:
        raise ValueError("FFprobe metadata exceeds the 4 MiB response limit")
    try:
        data = json.loads(payload)
    except (ValueError, UnicodeDecodeError) as error:
        raise ValueError("FFprobe returned invalid JSON metadata") from error
    if not isinstance(data, dict) or not isinstance(data.get("format"), dict):
        raise ValueError("FFprobe returned no format metadata")
    return data["format"]


def _ffprobe_version(ffprobe: str, timeout_s: float) -> str:
    """Record the installed optional tool once, before any source reads."""
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        try:
            completed = subprocess.run(
                [ffprobe, "-version"], stdin=subprocess.DEVNULL, stdout=stdout,
                stderr=stderr, timeout=min(timeout_s, 5.0), check=False, shell=False,
            )
        except subprocess.TimeoutExpired as error:
            raise ValueError("FFprobe version query timed out") from error
        stdout.seek(0)
        first_line = stdout.readline(1000).decode("utf-8", errors="replace").strip()
    if completed.returncode or not first_line.startswith("ffprobe version "):
        raise ValueError("FFprobe did not report a valid version")
    return first_line[:500]


def _positive(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        return None
    try:
        number = float(value)
    except (ValueError, TypeError, OverflowError):
        return None
    return number if math.isfinite(number) and number > 0 else None


def _provenance(entry: FolderImportEntry, field: str, value: str | None = None) -> str:
    result = {"adapter": IMPORT_VERSION, "sha256": entry.sha256_before, "field": field}
    if value is not None:
        result["encoded_value"] = value[:180]
        if len(value) > 180:
            result["full_value"] = "folder-import manifest encoded_tags"
    return json.dumps(result, ensure_ascii=False, sort_keys=True)


def _values(tags: dict[str, str], names: set[str]) -> list[tuple[str, str]]:
    return [(key, value.strip()) for key, value in tags.items()
            if key.casefold() in names and value.strip()]


def _display_text(entry: FolderImportEntry, name: str) -> str | None:
    values = _values(entry.encoded_tags, {name})
    if not values:
        return None
    if len({value for _, value in values}) > 1:
        entry.warnings.append(f"Conflicting embedded {name} tags; {name} remains unknown.")
        return None
    key, value = values[0]
    entry.field_sources[name] = f"encoded_fact: ffprobe.format.tags.{key}"
    if len(value) > 500:
        entry.warnings.append(f"Display {name} truncated to 500 characters; full tag retained in manifest.")
    return value[:500]


def _track_from_metadata(
    entry: FolderImportEntry, data: dict[str, Any], genre_lookup: dict[str, str]
) -> CatalogTrack:
    raw_tags = data.get("tags", {})
    if not isinstance(raw_tags, dict):
        raise ValueError("FFprobe tags must be an object")
    if any(not isinstance(key, str) or not isinstance(value, str) for key, value in raw_tags.items()):
        raise ValueError("FFprobe tags must contain text keys and values")
    entry.observed_tag_keys = sorted(raw_tags)
    entry.encoded_tags = {key: value for key, value in sorted(raw_tags.items())
                          if key.casefold() in _IMPORTED_KEYS}
    container = data.get("format_name")
    entry.container_format = container if isinstance(container, str) else None
    if container is not None and container != "mp3":
        entry.warnings.append(f"MP3 filename contains a different container: {container}.")
    title = _display_text(entry, "title")
    if title is None:
        title = Path(entry.filename).stem[:500].strip() or f"Untitled {entry.sha256_before[:12]}"
        entry.field_sources["title"] = "display fallback: source filename; no musical inference"
        entry.warnings.append("Embedded title unavailable; display title comes from the source filename.")
    artist = _display_text(entry, "artist")
    bpm_values = _values(entry.encoded_tags, {"bpm", "tbpm", "tempo"})
    valid_bpms = {_positive(value) for _, value in bpm_values}
    bpm = None
    if bpm_values:
        if None in valid_bpms or len(valid_bpms) != 1:
            entry.warnings.append("Invalid or conflicting embedded BPM annotations; tempo remains unknown.")
        else:
            key, raw = bpm_values[0]
            bpm = NumericEvidence(
                value=next(iter(valid_bpms)), authority="benchmark_estimate", status="warning",
                source=_provenance(entry, f"ffprobe.format.tags.{key}", raw),
            )
            entry.field_sources["bpm"] = f"benchmark_estimate: ffprobe.format.tags.{key}"
            entry.warnings.append("BPM is an embedded annotation; it has not been estimated or verified here.")
    duration = None
    duration_value = _positive(data.get("duration"))
    if duration_value is not None:
        duration = NumericEvidence(
            value=duration_value, authority="encoded_fact", status="warning",
            source=_provenance(entry, "ffprobe.format.duration", str(data["duration"])),
        )
        entry.field_sources["duration_s"] = "encoded_fact: ffprobe.format.duration"
    else:
        entry.warnings.append("Container duration is missing or invalid; duration remains unknown.")
    tags: list[TagEvidence] = []
    for key, raw in _values(entry.encoded_tags, {"genre"}):
        # Match whole aliases first: e.g. 'Rap/Hip Hop' need not mean two tags.
        components = [raw] if raw.casefold() in genre_lookup else re.split(r"[;,/]", raw)
        for component in components:
            term = component.strip()
            if not term:
                continue
            descriptor = genre_lookup.get(term.casefold())
            if descriptor is None:
                if term not in entry.unmapped_genres:
                    entry.unmapped_genres.append(term)
            elif descriptor not in entry.mapped_genres:
                entry.mapped_genres.append(descriptor)
                tags.append(TagEvidence(
                    tag=descriptor, authority="encoded_fact", status="warning",
                    source=_provenance(entry, f"ffprobe.format.tags.{key}", raw),
                ))
    if tags:
        entry.warnings.append("Genre tags reproduce embedded annotations; they are not reviewed musical labels.")
    if entry.unmapped_genres:
        entry.warnings.append("Some embedded genres have no exact vocabulary alias; see the import manifest.")
    return CatalogTrack(
        track_id=entry.track_id, title=title, artist=artist, bpm=bpm, duration_s=duration,
        tags=tags, complete_tag_axes=[], warnings=list(entry.warnings),
    )


def import_mp3_folder(
    folder: Path, vocabulary: Vocabulary, *, ffprobe: str = "ffprobe", timeout_s: float = 10.0
) -> tuple[Catalog, FolderImportManifest]:
    """Import one explicit folder nonrecursively, returning catalog and manifest.

    All regular MP3-named files are hashed before probing, then all are hashed
    again after probing. Changed/unreadable files cannot enter the catalog.
    Duplicate content gets one stable ID with every source alias in the manifest.
    Other entries and symlinks are reported as skipped; no symlink is followed.
    Callers persist returned models outside source folders using ``save_json``.
    """
    if isinstance(timeout_s, bool) or not isinstance(timeout_s, (float, int)) or not math.isfinite(timeout_s) or not 0 < timeout_s <= 60:
        raise ValueError("timeout_s must be a finite number greater than 0 and at most 60")
    source = Path(folder).expanduser().resolve(strict=True)
    if not source.is_dir():
        raise ValueError("Explicit source folder must be a directory")
    vocabulary = Vocabulary.model_validate(vocabulary.model_dump())
    executable = shutil.which(ffprobe)
    if executable is None:
        raise ValueError("Folder import requires FFprobe; install FFmpeg or pass an executable path")
    genre_lookup = {term.strip().casefold(): descriptor.id for descriptor in vocabulary.descriptors
                    if descriptor.id.startswith("genre:")
                    for term in [descriptor.id, *descriptor.aliases]}
    started = datetime.now(timezone.utc).isoformat()
    inventory = sorted(source.iterdir(), key=lambda path: path.name)
    if not any(not path.name.startswith(".") and path.is_file() and not path.is_symlink() and path.suffix.casefold() == ".mp3"
               for path in inventory):
        raise ValueError("Source folder contains no regular, nonsymlink MP3-named files")
    probe_version = _ffprobe_version(executable, float(timeout_s))
    entries: list[FolderImportEntry] = []
    for path in inventory:
        entry = FolderImportEntry(path=str(path), filename=path.name, status="pending")
        entries.append(entry)
        if path.name.startswith(".") or path.is_symlink() or not path.is_file() or path.suffix.casefold() != ".mp3":
            entry.status = "skipped"
            entry.warnings.append("Only visible regular, non-symlink MP3-named files in this folder are imported.")
            continue
        try:
            entry.sha256_before = _sha256(path)
            entry.track_id = f"sha256:{entry.sha256_before}"
        except (OSError, ValueError) as error:
            entry.status = "failed"
            entry.errors.append(f"Initial hash failed: {type(error).__name__}")
    proposed: dict[str, CatalogTrack] = {}
    for entry in entries:
        if entry.status != "pending":
            continue
        try:
            path = Path(entry.path)
            if path.is_symlink() or not path.is_file():
                raise ValueError("Source is no longer a regular nonsymlink file")
            proposed[entry.path] = _track_from_metadata(entry, _probe_file(path, executable, float(timeout_s)), genre_lookup)
        except (OSError, ValueError) as error:
            entry.status = "failed"
            entry.errors.append(str(error))
    # Postflight covers the entire operation, not only each individual probe.
    for entry in entries:
        if entry.sha256_before is None:
            continue
        try:
            entry.sha256_after = _sha256(Path(entry.path))
            entry.source_unchanged = entry.sha256_after == entry.sha256_before
            if not entry.source_unchanged:
                entry.status = "changed"
                entry.errors.append("Source bytes changed during import; track excluded.")
        except (OSError, ValueError) as error:
            entry.status = "failed"
            entry.errors.append(f"Final hash failed: {type(error).__name__}")
    inventory_unchanged = [path.name for path in inventory] == sorted(path.name for path in source.iterdir())
    tracks: dict[str, CatalogTrack] = {}
    aliases: dict[str, list[str]] = {}
    for entry in entries:
        if entry.status != "pending" or entry.source_unchanged is not True:
            continue
        aliases.setdefault(entry.track_id, []).append(entry.path)
        if entry.track_id in tracks:
            entry.status = "duplicate"
            entry.warnings.append("Identical source bytes share one catalog ID; all aliases are retained.")
        else:
            tracks[entry.track_id] = proposed[entry.path]
            entry.status = "imported"
    ordered_tracks = [tracks[track_id] for track_id in sorted(tracks)]
    digest = hashlib.sha256("\n".join(sorted(tracks)).encode()).hexdigest()
    catalog_id = f"folder:sha256:{digest}"
    coverage = {
        "entries_seen": len(entries),
        "mp3_files": sum(entry.status != "skipped" for entry in entries),
        "catalog_tracks": len(tracks),
        "duplicate_files": sum(entry.status == "duplicate" for entry in entries),
        "skipped_entries": sum(entry.status == "skipped" for entry in entries),
        "failed_files": sum(entry.status in {"failed", "changed"} for entry in entries),
        "tracks_with_embedded_title": sum(entry.status == "imported" and entry.field_sources.get("title", "").startswith("encoded_fact:") for entry in entries),
        "tracks_with_artist": sum(track.artist is not None for track in ordered_tracks),
        "tracks_with_bpm": sum(track.bpm is not None for track in ordered_tracks),
        "tracks_with_duration": sum(track.duration_s is not None for track in ordered_tracks),
        "tracks_with_encoded_genre": sum(entry.status == "imported" and bool(_values(entry.encoded_tags, {"genre"})) for entry in entries),
        "tracks_with_mapped_genre": sum(bool(track.tags) for track in ordered_tracks),
        "tracks_with_unmapped_genre": sum(entry.status == "imported" and bool(entry.unmapped_genres) for entry in entries),
        "tracks_with_complete_genre_axis": 0,
        "tracks_with_mood": 0,
        "tracks_with_energy": 0,
        "tracks_with_vocals": 0,
    }
    warnings = [
        "Imported container metadata only; no sample decoding, audio analysis, or semantic inference.",
        "Genre annotations are encoded tags, not reviewed musical facts; no tag axis is complete.",
        "BPM annotations remain benchmark_estimate; FFprobe duration is not a verified decoded timeline.",
    ]
    if coverage["duplicate_files"]:
        warnings.append(f"{coverage['duplicate_files']} duplicate file(s) share catalog IDs; see manifest aliases.")
    if coverage["failed_files"]:
        warnings.append(f"{coverage['failed_files']} failed/changed file(s) excluded; see manifest errors.")
    if not inventory_unchanged:
        warnings.append("Source directory inventory changed during import; newly appearing files were not imported.")
    catalog = Catalog(catalog_id=catalog_id, tracks=ordered_tracks, warnings=warnings)
    key_coverage = Counter(key for entry in entries for key in {key.casefold() for key in entry.observed_tag_keys})
    manifest = FolderImportManifest(
        source_folder=str(source), catalog_id=catalog_id, vocabulary_id=vocabulary.vocabulary_id,
        vocabulary_digest=hashlib.sha256(vocabulary.model_dump_json(by_alias=True).encode()).hexdigest(),
        ffprobe_executable=executable, ffprobe_version=probe_version,
        probe_timeout_s=float(timeout_s), started_at=started,
        finished_at=datetime.now(timezone.utc).isoformat(), source_inventory_unchanged=inventory_unchanged,
        source_hashes_unchanged=all(entry.source_unchanged is True for entry in entries if entry.status != "skipped"),
        entries=entries, aliases=aliases, coverage=coverage,
        tag_key_coverage=dict(sorted(key_coverage.items())), warnings=warnings,
    )
    return catalog, manifest
