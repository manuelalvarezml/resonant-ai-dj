"""Folder-import safety and evidence tests; synthetic bytes, mocked FFprobe only."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from prompt_to_playlist import folder_catalog
from prompt_to_playlist.folder_catalog import FolderImportManifest, import_mp3_folder
from prompt_to_playlist.models import Descriptor, Vocabulary
from prompt_to_playlist.vocabulary import load_vocabulary


@pytest.fixture
def folder(tmp_path, monkeypatch):
    source = tmp_path / "source"
    source.mkdir()
    monkeypatch.setattr(folder_catalog.shutil, "which", lambda _: "/synthetic/ffprobe")
    monkeypatch.setattr(folder_catalog, "_ffprobe_version", lambda *_: "ffprobe version synthetic-test")
    return source


def audio(folder, name="track.mp3", content=b"synthetic mp3 bytes"):
    path = folder / name
    path.write_bytes(content)
    return path


def probe(monkeypatch, *, tags=None, duration="300.1", container="mp3"):
    data = {"format_name": container, "duration": duration, "tags": tags or {}}
    monkeypatch.setattr(folder_catalog, "_probe_file", lambda *_: data)
    return data


def test_import_preserves_embedded_evidence_and_no_inferred_semantics(folder, monkeypatch):
    path = audio(folder, "dark high energy house.mp3")
    original = path.read_bytes()
    probe(monkeypatch, tags={"title": "Encoded Title", "artist": "Encoded Artist", "genre": "House", "TBPM": "126", "mood": "dark", "energyLevel": "7"})
    catalog, manifest = import_mp3_folder(folder, load_vocabulary())
    track = catalog.tracks[0]
    entry = manifest.entries[0]
    sha = hashlib.sha256(original).hexdigest()
    assert track.track_id == "sha256:" + sha
    assert track.title == "Encoded Title"
    assert track.artist == "Encoded Artist"
    assert [(tag.tag, tag.authority, tag.status) for tag in track.tags] == [("genre:house", "encoded_fact", "warning")]
    assert json.loads(track.tags[0].source)["encoded_value"] == "House"
    assert track.bpm.value == 126.0
    assert track.bpm.authority == "benchmark_estimate"
    assert track.bpm.status == "warning"
    assert track.duration_s.value == 300.1
    assert track.duration_s.authority == "encoded_fact"
    assert track.complete_tag_axes == []
    assert entry.sha256_before == entry.sha256_after == sha
    assert entry.source_unchanged is True
    assert entry.field_sources["title"].startswith("encoded_fact:")
    assert "mood" not in entry.encoded_tags
    assert "mood" in entry.observed_tag_keys
    assert manifest.source_hashes_unchanged is True
    assert manifest.source_inventory_unchanged is True
    assert manifest.coverage["tracks_with_mood"] == 0
    assert manifest.coverage["tracks_with_energy"] == 0
    assert list(folder.iterdir()) == [path]
    assert path.read_bytes() == original
    assert FolderImportManifest.model_validate_json(manifest.model_dump_json(by_alias=True)) == manifest


def test_missing_metadata_stays_missing_and_filename_only_displays(folder, monkeypatch):
    audio(folder, "warm vocal ambient 130.mp3")
    probe(monkeypatch, duration=None)
    catalog, manifest = import_mp3_folder(folder, load_vocabulary())
    track = catalog.tracks[0]
    assert track.title == "warm vocal ambient 130"
    assert track.artist is None and track.bpm is None and track.duration_s is None
    assert track.tags == []
    assert manifest.coverage["tracks_with_embedded_title"] == 0
    assert manifest.entries[0].field_sources["title"].startswith("display fallback")


@pytest.mark.parametrize("raw", ["0", "-1", "NaN", "Infinity", "125 bpm", "", "unknown"])
def test_invalid_bpm_is_not_musical_evidence(folder, monkeypatch, raw):
    audio(folder)
    probe(monkeypatch, tags={"BPM": raw})
    catalog, _ = import_mp3_folder(folder, load_vocabulary())
    assert catalog.tracks[0].bpm is None


def test_conflicting_bpm_and_text_tags_are_not_silently_selected(folder, monkeypatch):
    audio(folder)
    probe(monkeypatch, tags={"bpm": "120", "TBPM": "125", "title": "One", "TITLE": "Two", "artist": "A", "ARTIST": "B"})
    catalog, manifest = import_mp3_folder(folder, load_vocabulary())
    track = catalog.tracks[0]
    assert track.bpm is None and track.artist is None
    assert track.title == "track"
    assert any("Conflicting embedded title" in warning for warning in track.warnings)
    assert manifest.coverage["tracks_with_embedded_title"] == 0


def test_agreeing_bpm_aliases_are_one_estimate(folder, monkeypatch):
    audio(folder)
    probe(monkeypatch, tags={"bpm": "120", "TBPM": "120.0"})
    catalog, _ = import_mp3_folder(folder, load_vocabulary())
    assert catalog.tracks[0].bpm.value == 120.0


def test_genre_uses_whole_exact_alias_then_delimiters_not_substrings(folder, monkeypatch):
    audio(folder)
    vocabulary = load_vocabulary()
    vocabulary.descriptors.append(Descriptor(id="genre:deep_house", description="Encoded annotation", aliases=["Deep House"]))
    probe(monkeypatch, tags={"genre": "Deep House; DISCO, Techno/Unknown; dark; Disco Italo-Disco"})
    catalog, manifest = import_mp3_folder(folder, vocabulary)
    assert [tag.tag for tag in catalog.tracks[0].tags] == ["genre:deep_house", "genre:disco", "genre:techno"]
    assert manifest.entries[0].unmapped_genres == ["Unknown", "dark", "Disco Italo-Disco"]
    assert "genre:house" not in manifest.entries[0].mapped_genres
    assert catalog.tracks[0].complete_tag_axes == []


def test_whole_alias_with_slash_is_not_broken_apart(folder, monkeypatch):
    audio(folder)
    vocabulary = load_vocabulary()
    vocabulary.descriptors[3].aliases.append("Rap/Hip Hop")
    probe(monkeypatch, tags={"genre": "Rap/Hip Hop"})
    catalog, manifest = import_mp3_folder(folder, vocabulary)
    assert [tag.tag for tag in catalog.tracks[0].tags] == ["genre:hip_hop"]
    assert manifest.entries[0].unmapped_genres == []


def test_duplicate_sources_have_one_stable_id_and_all_aliases(folder, monkeypatch):
    first = audio(folder, "a.mp3")
    second = audio(folder, "b.MP3")
    probe(monkeypatch, tags={"title": "Same"})
    catalog, manifest = import_mp3_folder(folder, load_vocabulary())
    assert len(catalog.tracks) == 1
    assert [entry.status for entry in manifest.entries] == ["imported", "duplicate"]
    assert manifest.aliases[catalog.tracks[0].track_id] == [str(first), str(second)]
    assert manifest.coverage["mp3_files"] == 2
    assert manifest.coverage["duplicate_files"] == 1
    assert any("duplicate" in warning for warning in catalog.warnings)


def test_stable_track_and_catalog_ids_ignore_renaming(folder, monkeypatch):
    path = audio(folder)
    probe(monkeypatch, tags={"title": "Same"})
    catalog, _ = import_mp3_folder(folder, load_vocabulary())
    path.rename(folder / "renamed.mp3")
    other, _ = import_mp3_folder(folder, load_vocabulary())
    assert catalog == other


def test_nonrecursive_regular_mp3_only_and_symlinks_are_reported(folder, monkeypatch):
    path = audio(folder)
    audio(folder, "notes.txt", b"do not read")
    nested = folder / "nested"
    nested.mkdir()
    audio(nested, "hidden.mp3", b"do not read")
    (folder / "alias.mp3").symlink_to(path)
    (folder / "broken.mp3").symlink_to(folder / "absent.mp3")
    calls = []
    monkeypatch.setattr(folder_catalog, "_probe_file", lambda path, *_: calls.append(path) or {"tags": {}})
    catalog, manifest = import_mp3_folder(folder, load_vocabulary())
    assert len(catalog.tracks) == 1
    assert calls == [path]
    assert manifest.coverage["skipped_entries"] == 4
    assert all(entry.sha256_before is None for entry in manifest.entries if entry.status == "skipped")


def test_hashes_bracket_entire_import_and_changed_sources_are_excluded(folder, monkeypatch):
    first = audio(folder, "a.mp3", b"first")
    audio(folder, "b.mp3", b"second")
    def fake_probe(path, *_):
        if path.name == "b.mp3":
            first.write_bytes(b"external concurrent edit")
        return {"tags": {}}
    monkeypatch.setattr(folder_catalog, "_probe_file", fake_probe)
    catalog, manifest = import_mp3_folder(folder, load_vocabulary())
    assert len(catalog.tracks) == 1
    changed = manifest.entries[0]
    assert changed.status == "changed" and changed.source_unchanged is False
    assert changed.track_id not in {track.track_id for track in catalog.tracks}
    assert manifest.source_hashes_unchanged is False
    assert manifest.coverage["failed_files"] == 1


def test_missing_source_after_probe_is_excluded(folder, monkeypatch):
    path = audio(folder)
    def fake_probe(*_):
        path.unlink()
        return {"tags": {}}
    monkeypatch.setattr(folder_catalog, "_probe_file", fake_probe)
    catalog, manifest = import_mp3_folder(folder, load_vocabulary())
    assert catalog.tracks == []
    assert manifest.entries[0].status == "failed"
    assert manifest.source_hashes_unchanged is False
    assert manifest.source_inventory_unchanged is False


def test_probe_failure_is_reported_and_still_hashes_after(folder, monkeypatch):
    audio(folder)
    def fail(*_):
        raise ValueError("FFprobe failed (exit 1)")
    monkeypatch.setattr(folder_catalog, "_probe_file", fail)
    catalog, manifest = import_mp3_folder(folder, load_vocabulary())
    assert catalog.tracks == []
    assert manifest.entries[0].status == "failed"
    assert manifest.entries[0].source_unchanged is True
    assert manifest.entries[0].errors == ["FFprobe failed (exit 1)"]
    assert manifest.source_hashes_unchanged is True


def test_inventory_change_is_visible_without_silently_importing_new_file(folder, monkeypatch):
    audio(folder)
    def fake_probe(*_):
        audio(folder, "new.mp3", b"new")
        return {"tags": {}}
    monkeypatch.setattr(folder_catalog, "_probe_file", fake_probe)
    catalog, manifest = import_mp3_folder(folder, load_vocabulary())
    assert len(catalog.tracks) == 1
    assert manifest.source_inventory_unchanged is False
    assert any("inventory changed" in warning for warning in catalog.warnings)


def test_non_mp3_container_is_visible_without_audio_decode(folder, monkeypatch):
    audio(folder)
    probe(monkeypatch, container="mov,mp4,m4a,3gp,3g2,mj2")
    catalog, manifest = import_mp3_folder(folder, load_vocabulary())
    assert len(catalog.tracks) == 1
    assert manifest.entries[0].container_format.startswith("mov")
    assert any("different container" in warning for warning in catalog.tracks[0].warnings)


def test_large_display_tags_are_bounded_but_manifest_retains_original(folder, monkeypatch):
    audio(folder)
    probe(monkeypatch, tags={"title": "A" * 1000, "artist": "B" * 1000})
    catalog, manifest = import_mp3_folder(folder, load_vocabulary())
    assert len(catalog.tracks[0].title) == len(catalog.tracks[0].artist) == 500
    assert len(manifest.entries[0].encoded_tags["title"]) == 1000


@pytest.mark.parametrize("duration", [None, "0", "-1", "NaN", True, {}, []])
def test_unknown_or_bad_duration_does_not_invent_a_value(folder, monkeypatch, duration):
    audio(folder)
    probe(monkeypatch, duration=duration)
    catalog, _ = import_mp3_folder(folder, load_vocabulary())
    assert catalog.tracks[0].duration_s is None


@pytest.mark.parametrize("timeout", [0, -1, 61, float("nan"), float("inf"), True, "10"])
def test_timeout_bounds_are_validated(folder, timeout):
    with pytest.raises(ValueError, match="timeout_s"):
        import_mp3_folder(folder, load_vocabulary(), timeout_s=timeout)


def test_missing_ffprobe_is_explicit_and_no_source_reads(folder, monkeypatch):
    audio(folder)
    monkeypatch.setattr(folder_catalog.shutil, "which", lambda _: None)
    monkeypatch.setattr(folder_catalog, "_sha256", lambda _: pytest.fail("must validate dependency first"))
    with pytest.raises(ValueError, match="requires FFprobe"):
        import_mp3_folder(folder, load_vocabulary())


def test_ffprobe_is_local_bounded_subprocess_without_shell_or_stdin(tmp_path, monkeypatch):
    path = tmp_path / "literal $(name);.mp3"
    def fake_run(args, **kwargs):
        assert args[0] == "/synthetic/ffprobe"
        assert args[-1] == str(path)
        assert args[args.index("-protocol_whitelist") + 1] == "file"
        assert args[args.index("-probesize") + 1] == "1048576"
        assert args[args.index("-analyzeduration") + 1] == "1000000"
        assert "-show_entries" in args and "-show_packets" not in args and "-show_frames" not in args
        assert kwargs["timeout"] == 7.0 and kwargs["shell"] is False
        assert kwargs["stdin"] == subprocess.DEVNULL
        kwargs["stdout"].write(json.dumps({"format": {"tags": {"title": "Literal"}}}).encode())
        return SimpleNamespace(returncode=0)
    monkeypatch.setattr(folder_catalog.subprocess, "run", fake_run)
    assert folder_catalog._probe_file(path, "/synthetic/ffprobe", 7.0) == {"tags": {"title": "Literal"}}


@pytest.mark.parametrize("failure", ["timeout", "exit", "invalid_json", "missing_format", "large"])
def test_ffprobe_failures_are_bounded_and_explicit(tmp_path, monkeypatch, failure):
    monkeypatch.setattr(folder_catalog, "_PROBE_OUTPUT_LIMIT", 100)
    def fake_run(args, **kwargs):
        if failure == "timeout":
            raise subprocess.TimeoutExpired(args, kwargs["timeout"])
        kwargs["stdout"].write({"invalid_json": b"oops", "missing_format": b"{}", "large": b"x" * 101}.get(failure, b""))
        return SimpleNamespace(returncode=1 if failure == "exit" else 0)
    monkeypatch.setattr(folder_catalog.subprocess, "run", fake_run)
    with pytest.raises(ValueError):
        folder_catalog._probe_file(tmp_path / "synthetic.mp3", "ffprobe", 1.0)


def test_sha256_refuses_symlinks_and_streams_regular_files(folder):
    path = audio(folder, content=b"x" * (folder_catalog._HASH_BUFFER + 100))
    assert folder_catalog._sha256(path) == hashlib.sha256(path.read_bytes()).hexdigest()
    link = folder / "link.mp3"
    link.symlink_to(path)
    with pytest.raises((OSError, ValueError)):
        folder_catalog._sha256(link)


def test_empty_folder_is_explicit_and_does_not_run_probe(folder, monkeypatch):
    audio(folder, "notes.txt")
    monkeypatch.setattr(folder_catalog, "_ffprobe_version", lambda *_: pytest.fail("no files to import"))
    with pytest.raises(ValueError, match="no regular"):
        import_mp3_folder(folder, load_vocabulary())


def test_ffprobe_version_is_recorded_once_before_source_reads(folder, monkeypatch):
    audio(folder, "a.mp3", b"first")
    audio(folder, "b.mp3", b"second")
    calls = []
    monkeypatch.setattr(folder_catalog, "_ffprobe_version", lambda *_: calls.append("version") or "ffprobe version 8.0.1")
    original_hash = folder_catalog._sha256
    monkeypatch.setattr(folder_catalog, "_sha256", lambda path: calls.append("hash") or original_hash(path))
    probe(monkeypatch)
    _, manifest = import_mp3_folder(folder, load_vocabulary())
    assert calls[0] == "version" and calls.count("version") == 1
    assert manifest.ffprobe_version == "ffprobe version 8.0.1"


def test_ffprobe_version_query_has_short_bound_and_no_shell(tmp_path, monkeypatch):
    def fake_run(args, **kwargs):
        assert args == ["ffprobe", "-version"]
        assert kwargs["timeout"] == 5.0 and kwargs["shell"] is False
        assert kwargs["stdin"] == subprocess.DEVNULL
        kwargs["stdout"].write(b"ffprobe version 8.0.1 test\nconfiguration details not persisted\n")
        return SimpleNamespace(returncode=0)
    monkeypatch.setattr(folder_catalog.subprocess, "run", fake_run)
    assert folder_catalog._ffprobe_version("ffprobe", 10.0) == "ffprobe version 8.0.1 test"


@pytest.mark.parametrize("result", ["failure", "unknown", "timeout"])
def test_ffprobe_version_failure_is_explicit(tmp_path, monkeypatch, result):
    def fake_run(args, **kwargs):
        if result == "timeout":
            raise subprocess.TimeoutExpired(args, kwargs["timeout"])
        kwargs["stdout"].write(b"unknown tool")
        return SimpleNamespace(returncode=1 if result == "failure" else 0)
    monkeypatch.setattr(folder_catalog.subprocess, "run", fake_run)
    with pytest.raises(ValueError, match="FFprobe"):
        folder_catalog._ffprobe_version("ffprobe", 10.0)
