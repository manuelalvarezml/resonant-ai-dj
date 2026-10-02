"""Boundary tests use synthetic JSON and empty audio-named files only."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from prompt_to_playlist.adapters import from_dj_collection, load_catalog, save_json
from prompt_to_playlist.models import Catalog


def dj_collection() -> dict:
    """Minimal consumed fields of a fictional stored DJ analysis artifact."""
    sha = "a" * 64
    return {
        "schema": "dj-engine/collection-analysis",
        "schema_version": "0.1.0",
        "collection_id": "synthetic-collection",
        "input_folder": "/not-a-real-folder/never-open-audio",
        "tracks": [
            {
                "schema": "dj-engine/track-analysis",
                "schema_version": "0.1.0",
                "analysis_id": "synthetic-analysis",
                "source": {
                    "track_id": f"sha256:{sha}",
                    "sha256_before": sha,
                    "sha256_after": sha,
                    "source_unchanged": True,
                    "filename": "Synthetic Dark House.mp3",
                    "path": "/not-a-real-folder/never-open-audio/synthetic.mp3",
                },
                "tempo": {
                    "selected_candidate": {
                        "value": 126.0,
                        "unit": "BPM",
                        "authority": "benchmark_estimate",
                        "status": "warning",
                        "source_tool": "synthetic-analyzer",
                        "tool_version": "test-1",
                        "model_id": "test-model",
                        "confidence": 0.7,
                        "warnings": ["Synthetic tempo estimate"],
                    }
                },
                "stream": {
                    "duration_s": 300.0,
                    "authority": "encoded_fact",
                    "status": "passed",
                    "probe_tool": "synthetic-probe",
                    "probe_version": "test-1",
                },
            }
        ],
    }


def test_import_preserves_numeric_evidence_and_never_invents_tags():
    data = dj_collection()
    before = copy.deepcopy(data)
    catalog = from_dj_collection(data)
    track = catalog.tracks[0]
    assert data == before
    assert track.track_id == "sha256:" + "a" * 64
    assert track.title == "Synthetic Dark House"
    assert track.artist is None
    assert track.tags == []
    assert track.complete_tag_axes == []
    assert track.bpm.value == 126.0
    assert track.bpm.status == "warning"
    assert track.bpm.authority == "benchmark_estimate"
    assert track.bpm.confidence == 0.7
    provenance = json.loads(track.bpm.source)
    assert provenance["source_tool"] == "synthetic-analyzer"
    assert provenance["model_id"] == "test-model"
    assert provenance["analysis_id"] == "synthetic-analysis"
    assert provenance["sha256"] == "a" * 64
    assert track.duration_s.value == 300.0
    assert track.duration_s.authority == "encoded_fact"
    assert "Synthetic tempo estimate" in track.warnings
    assert any("not reverified" in warning for warning in catalog.warnings)


@pytest.mark.parametrize("status", ["passed", "warning", "rejected", "failed", "not_run", "unknown"])
def test_import_keeps_status_instead_of_promoting_evidence(status):
    data = dj_collection()
    data["tracks"][0]["tempo"]["selected_candidate"]["status"] = status
    assert from_dj_collection(data).tracks[0].bpm.status == status


def test_missing_values_stay_unknown():
    data = dj_collection()
    selected = data["tracks"][0]["tempo"]["selected_candidate"]
    selected["value"] = None
    selected["status"] = "failed"
    data["tracks"][0]["stream"]["duration_s"] = None
    track = from_dj_collection(data).tracks[0]
    assert track.bpm is None
    assert track.duration_s is None
    assert any("unknown" in warning for warning in track.warnings)


@pytest.mark.parametrize("field,bad", [("schema", "unknown"), ("schema_version", "9.0.0")])
def test_rejects_unknown_collection_and_track_versions(field, bad):
    for target in ("collection", "track"):
        data = dj_collection()
        subject = data if target == "collection" else data["tracks"][0]
        subject[field] = bad
        with pytest.raises(ValueError, match="schema version"):
            from_dj_collection(data)


@pytest.mark.parametrize(
    "changes",
    [
        {"track_id": "wrong"},
        {"sha256_before": "not-a-hash"},
        {"sha256_after": "b" * 64},
        {"source_unchanged": False},
        {"source_unchanged": 1},
        {"sha256_after": None, "source_unchanged": True},
        {"filename": "../Synthetic.mp3"},
    ],
)
def test_rejects_inconsistent_provenance(changes):
    data = dj_collection()
    data["tracks"][0]["source"].update(changes)
    with pytest.raises(ValueError):
        from_dj_collection(data)


def test_incomplete_hash_check_stays_visible():
    data = dj_collection()
    data["tracks"][0]["source"].update(sha256_after=None, source_unchanged=None)
    assert any("incomplete" in text for text in from_dj_collection(data).tracks[0].warnings)


@pytest.mark.parametrize("value", [True, "126", float("nan"), float("inf"), -5.0, 0.0])
def test_rejects_malformed_numeric_evidence(value):
    data = dj_collection()
    data["tracks"][0]["tempo"]["selected_candidate"]["value"] = value
    with pytest.raises(ValueError):
        from_dj_collection(data)


def test_rejects_estimate_relabeling_and_duplicate_ids():
    data = dj_collection()
    data["tracks"][0]["tempo"]["selected_candidate"]["authority"] = "encoded_fact"
    with pytest.raises(ValueError, match="benchmark_estimate"):
        from_dj_collection(data)
    data = dj_collection()
    data["tracks"].append(copy.deepcopy(data["tracks"][0]))
    with pytest.raises(ValueError, match="Duplicate"):
        from_dj_collection(data)


def test_safe_native_round_trip_and_no_overwrite(tmp_path):
    catalog = from_dj_collection(dj_collection())
    output = tmp_path / "outputs" / "catalog.json"
    save_json(catalog, output)
    assert load_catalog(output) == catalog
    before = output.read_bytes()
    with pytest.raises(ValueError, match="already exists"):
        save_json(Catalog(catalog_id="empty", tracks=[]), output)
    assert output.read_bytes() == before


@pytest.mark.parametrize(
    "relative",
    ["export.MP3", "export.wav", "Music/export.json", "test_folder_10_house_tracks/new/out.json",
     "test_tracks_folder_mp3/out.json", "audio/export.json", "test_music/new_albums/out.json"],
)
def test_save_refuses_audio_targets_and_named_music_folders(tmp_path, relative):
    destination = tmp_path / relative
    with pytest.raises(ValueError):
        save_json(Catalog(catalog_id="empty", tracks=[]), destination)
    assert not destination.exists()


def test_save_refuses_arbitrary_audio_folder_and_nested_output(tmp_path):
    source_folder = tmp_path / "owned-collection"
    source_folder.mkdir()
    audio = source_folder / "synthetic.mp3"
    audio.write_bytes(b"")  # filename-only fixture: no decoding or playback
    destination = source_folder / "exports" / "catalog.json"
    with pytest.raises(ValueError, match="containing audio"):
        save_json(Catalog(catalog_id="empty", tracks=[]), destination)
    assert audio.read_bytes() == b""
    assert not destination.parent.exists()


def test_save_refuses_symlink_into_music_folder_and_broken_output_symlink(tmp_path):
    music = tmp_path / "Music"
    music.mkdir()
    link = tmp_path / "shortcut"
    link.symlink_to(music, target_is_directory=True)
    with pytest.raises(ValueError, match="music/audio"):
        save_json(Catalog(catalog_id="empty", tracks=[]), link / "out.json")
    broken = tmp_path / "broken.json"
    broken.symlink_to(tmp_path / "does-not-exist.json")
    with pytest.raises(ValueError, match="already exists"):
        save_json(Catalog(catalog_id="empty", tracks=[]), broken)
