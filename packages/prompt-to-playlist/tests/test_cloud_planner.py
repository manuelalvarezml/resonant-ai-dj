"""Portable serving parity, including real cached vectors without model inference."""
import copy
import json
from pathlib import Path

import pytest

from prompt_to_playlist import cloud_catalog as cloud, cloud_text, specialists, semantic_audio
from prompt_to_playlist.cloud_bridge import prompt
from prompt_to_playlist.estimator_profiles import PROFILES
from prompt_to_playlist.feature_catalog import catalog_from_features
from prompt_to_playlist.models import PlaylistQuery, Preference, SemanticQuery, Translation
from prompt_to_playlist.search import search_tracks
from test_specialists import source


def items():
    rows = [source("one", .9), source("two", .2)]
    for number, row in enumerate(rows, 1):
        row["sha256"] = str(number) * 64
    return rows


def selection(rows):
    return [{"id": row["id"], "sha256": row["sha256"]} for row in rows]


@pytest.mark.parametrize("profile", PROFILES)
@pytest.mark.parametrize("scope", [(0, 1), (1, 0), (0,), (1,)])
def test_frozen_scope_profiles_keep_exact_catalog_vocabulary_and_ranking(profile, scope, monkeypatch):
    rows = items()
    # The VA gate changes between the whole catalog and the first-only scope.
    music = next(a for a in rows[1]["features"]["algorithms"] if a["algorithm_id"] == "emotion_music2emo")
    music["values"]["valence_mean"] = 10.
    music["values"]["segments"][0]["valence"] = 10.
    document = cloud.freeze_planner(rows, require_complete=False)
    subset = [rows[index] for index in scope]
    expected, expected_vocabulary = catalog_from_features(subset, estimator_profile=profile)
    # A slim Linux host has no matching specialist packages. Any call to local
    # identity after export would silently lose selected evidence; prohibit it.
    monkeypatch.setattr(specialists, "identity", lambda _: pytest.fail("Serving queried analyzer identity"))
    actual, vocabulary = cloud.FrozenPlanner(document).select(selection(subset), profile)
    assert actual == expected
    assert vocabulary == expected_vocabulary
    for tag in ("mood:happy", "vocals:vocal", "valence:positive", "openmic:piano"):
        if tag not in {d.id for d in vocabulary.descriptors}:
            continue
        query = PlaylistQuery(preferences=[Preference(tag=tag)], limit=2)
        assert search_tracks(actual, query, vocabulary) == search_tracks(expected, query, expected_vocabulary)


def test_published_scope_keeps_independent_coverage_fallback(monkeypatch):
    rows = items()
    rows[1]["features"]["algorithms"] = [a for a in rows[1]["features"]["algorithms"]
                                          if a["algorithm_id"] != "vocal_musicnn"]
    frozen = cloud.FrozenPlanner(cloud.freeze_planner(rows, require_complete=False))
    full, _ = frozen.select(selection(rows), "quality")
    single, _ = frozen.select(selection(rows[:1]), "quality")
    assert "vocals:vocal" not in full.tracks[0].preference_scores
    assert single.tracks[0].preference_scores["vocals:vocal"].source.startswith("vocal_musicnn-v1:")


@pytest.mark.parametrize("failure", ["bytes", "runtime", "id", "hash", "duplicate", "profile", "empty"])
def test_snapshot_and_scope_fail_closed(failure):
    rows = items()
    document = cloud.freeze_planner(rows, require_complete=False)
    requested = selection(rows)
    profile = "quality"
    if failure == "bytes":
        document["payload"]["items"][0]["title"] = "changed"
    if failure == "runtime":
        document["payload"]["fingerprints"]["search.py"] = "0" * 64
        document["payload_sha256"] = cloud.digest(document["payload"])
    if failure == "id":
        requested[0]["id"] = "unpublished"
    if failure == "hash":
        requested[0]["sha256"] = "0" * 64
    if failure == "duplicate":
        requested[1] = requested[0]
    if failure == "profile":
        profile = "new"
    if failure == "empty":
        requested = []
    with pytest.raises(ValueError):
        cloud.FrozenPlanner(document).select(requested, profile)


def test_export_requires_complete_current_evidence():
    with pytest.raises(ValueError, match="incomplete or incompatible"):
        cloud.freeze_planner(items())


def test_portable_parity_replay_rejects_score_or_snapshot_change():
    frozen = cloud.FrozenPlanner(cloud.freeze_planner(items(), require_complete=False))
    parity = cloud.build_parity(frozen)
    assert cloud.verify_parity(frozen, parity) == 40
    changed = copy.deepcopy(parity)
    changed["cases"][0]["result_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="parity failed"):
        cloud.verify_parity(frozen, changed)
    changed = copy.deepcopy(parity)
    changed["snapshot_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="does not match"):
        cloud.verify_parity(frozen, changed)


def test_prompt_uses_published_titles_and_persists_replay_audit(tmp_path):
    from prompt_to_playlist.service import build_playlist
    rows = items()
    document = cloud.freeze_planner(rows, require_complete=False)
    cloud.atomic_json(tmp_path / "release/private/planner.json", document)
    catalog, vocabulary = cloud.FrozenPlanner(document).select(selection(rows), "quality")
    query = PlaylistQuery(preferences=[Preference(tag="openmic:piano")], limit=2)
    class FixedTranslator:
        def translate(self, text, vocab):
            return Translation(request_text=text, vocabulary_id=vocab.vocabulary_id, query=query,
                               provider="rules", model="fixed", prompt_version="test")
    request = {"prompt": "piano", "tracks": [{**row, "title": "Untrusted override"} for row in selection(rows)],
               "estimator_profile": "quality"}
    before = copy.deepcopy(request)
    expected = build_playlist("piano", catalog, vocabulary, FixedTranslator()).model_dump(mode="json", by_alias=True)
    result = prompt(request, release_dir=tmp_path / "release", state_dir=tmp_path / "state",
                    model_dir=tmp_path / "no-model", translator=FixedTranslator())
    assert result == expected and request == before
    audit = json.loads(next((tmp_path / "state/audits").glob("*-inputs.json")).read_text())
    assert audit["catalog"] == catalog.model_dump(mode="json", by_alias=True)
    assert audit["planner_snapshot_sha256"] == document["payload_sha256"]
    assert all(set(row) == {"id", "sha256"} for row in audit["request"]["tracks"])


def test_core_import_does_not_import_inference_stack():
    import subprocess
    import sys
    code = "import sys; import prompt_to_playlist.cloud_bridge; assert not {'torch', 'numpy', 'essentia', 'muq'} & set(sys.modules)"
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_audit_retention_bounds_pairs_and_age_without_following_links(tmp_path):
    import os
    import uuid
    from prompt_to_playlist.cloud_bridge import prune_audits
    directory = tmp_path / "state/audits"
    directory.mkdir(parents=True)
    groups = []
    for number, age in enumerate((9 * 86400, 100, 10)):
        identifier = str(uuid.uuid4())
        pair = [directory / ("playlist-" + identifier + suffix) for suffix in (".json", "-inputs.json")]
        for path in pair:
            path.write_text("{}")
            os.utime(path, (1_000_000 - age, 1_000_000 - age))
        groups.append(pair)
    unrelated = directory / "keep.txt"
    unrelated.write_text("preserve")
    outside = tmp_path / "outside.json"
    outside.write_text("preserve")
    link = directory / ("playlist-" + str(uuid.uuid4()) + ".json")
    link.symlink_to(outside)
    prune_audits(tmp_path / "state", now=1_000_000, max_pairs=1)
    assert all(not path.exists() for pair in groups[:2] for path in pair)
    assert all(path.exists() for path in groups[2])
    assert outside.read_text() == unrelated.read_text() == "preserve" and link.is_symlink()
    other_state = tmp_path / "other-state"
    other_state.mkdir()
    (other_state / "audits").symlink_to(directory, target_is_directory=True)
    prune_audits(other_state, now=10_000_000, max_pairs=0)
    assert all(path.exists() for path in groups[2])


LOCAL = Path(__file__).resolve().parents[1] / "output"


@pytest.fixture
def real_rows():
    from prompt_to_playlist.web_bridge import compatible, STAGES, FEATURE_VERSION
    directory = LOCAL / "web-features"
    if not directory.exists():
        pytest.skip("Local published evidence is not part of source distribution")
    rows = []
    for path in sorted(directory.glob("*.json")):
        if not cloud.HASH.fullmatch(path.stem):
            continue
        feature = json.loads(path.read_text())
        indexed = {a["algorithm_id"]: a for a in feature["algorithms"]}
        if (feature.get("status") == "complete" and feature.get("feature_version") == FEATURE_VERSION
                and all(stage in indexed and compatible(indexed[stage]) for stage in STAGES)):
            rows.append({"id": "real-" + path.stem, "title": "Published track " + str(len(rows)),
                         "sha256": path.stem, "features": feature})
        if len(rows) == 2:
            return rows
    pytest.skip("Two current complete local feature caches are unavailable")


def test_two_real_cached_tracks_preserve_all_profiles_and_exact_vectors(real_rows, monkeypatch):
    document = cloud.freeze_planner(real_rows)
    frozen = cloud.FrozenPlanner(document)
    expected = {profile: catalog_from_features(real_rows, estimator_profile=profile) for profile in PROFILES}
    monkeypatch.setattr(specialists, "identity", lambda _: pytest.fail("Cloud required analyzer package identity"))
    for profile in PROFILES:
        catalog, vocabulary = frozen.select(selection(real_rows), profile)
        assert (catalog, vocabulary) == expected[profile]
        for index, track in enumerate(catalog.tracks):
            raw = next(a["values"] for a in real_rows[index]["features"]["algorithms"]
                       if a["algorithm_id"] == "semantic_audio")
            assert [s.embedding for s in track.semantic_audio.segments] == [s["embedding"] for s in raw["segments"]]
        for tag in ("theme:happy", "vocals:vocal", "mood:aggressive", "openmic:piano"):
            if tag in {d.id for d in vocabulary.descriptors}:
                query = PlaylistQuery(preferences=[Preference(tag=tag)], limit=2)
                assert search_tracks(catalog, query, vocabulary) == search_tracks(expected[profile][0], query, expected[profile][1])


def test_real_text_cache_cloud_query_has_exact_vectors_and_scores(real_rows, tmp_path, monkeypatch):
    encoder = semantic_audio.identity()
    cache = LOCAL / "semantic-text-cache"
    record = next((json.loads(path.read_text()) for path in sorted(cache.glob("*.json"))
                   if json.loads(path.read_text()).get("encoder") == encoder), None)
    if record is None:
        pytest.skip("No compatible local text cache")
    text = record["text"]
    import hashlib
    key = hashlib.sha256((encoder + "\n" + text).encode()).hexdigest()
    cloud.atomic_json(tmp_path / "text-cache" / (key + ".json"), record)
    monkeypatch.setattr(semantic_audio, "load_model", lambda *a, **kw: pytest.fail("Inference must not run"))
    monkeypatch.setattr(cloud_text.subprocess, "Popen", lambda *a, **kw: pytest.fail("A cache hit must not launch a worker"))
    catalog, vocabulary = catalog_from_features(real_rows, estimator_profile="quality")
    query = PlaylistQuery(semantic=SemanticQuery(description=text), limit=2)
    actual, warnings = cloud_text.query_encoder(LOCAL / "semantic-models", tmp_path)(query, catalog, vocabulary)
    vector = semantic_audio.text_embeddings([text], cached_only=True)[0]
    expected = query.model_copy(update={"semantic": SemanticQuery(description=text, encoder_id=encoder, embeddings=[vector])})
    assert not warnings and actual == expected
    assert search_tracks(catalog, actual, vocabulary) == search_tracks(catalog, expected, vocabulary)
