"""Freeze trusted local planner evidence and replay it without analyzer installs.

The export command is local-only. Serving accepts only its checksummed snapshot,
not feature data or model identities from a browser request. Scope-dependent
vocabulary and complete-coverage gates still use the original catalog builder.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from .estimator_profiles import PROFILES
from .feature_catalog import catalog_from_features
from .models import Catalog, SemanticAudio, Vocabulary

SCHEMA = "resonant/frozen-planner/1"
HASH = re.compile(r"[a-f0-9]{64}")
FINGERPRINT_FILES = (
    "feature_catalog.py", "estimator_profiles.py", "models.py", "search.py",
    "intent.py", "taxonomy.py", "vocabulary.py", "service.py", "translators.py",
    "semantic_audio.py", "cloud_catalog.py", "cloud_text.py", "cloud_bridge.py",
    "specialists.py", "supervised.py", "extended_labels.json", "character_bank.json", "descriptors.json",
)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def fingerprints():
    directory = Path(__file__).parent
    return {name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
            for name in FINGERPRINT_FILES}


def atomic_json(path, value):
    import os
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(f".{os.getpid()}.tmp")
    try:
        temp.write_bytes(canonical(value) + b"\n")
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)


def project_features(feature):
    """Keep exactly the planner inputs, excluding local file paths and telemetry."""
    from .supervised import SampledEstimates
    from .specialists import SpecialistEstimates
    algorithms = []
    for row in feature["algorithms"]:
        stage, values = row["algorithm_id"], row.get("values", {})
        if row["status"] not in ("passed", "warning"):
            continue
        if stage == "genre_maest":
            projected = {"scores": values["scores"]}
        elif stage == "semantic":
            projected = {"heads": {key: {"scores": head.get("scores", {})}
                                    for key, head in values.get("heads", {}).items()}}
        elif stage == "rhythm":
            projected = {"bpm": values.get("bpm")}
        elif stage == "energy":
            projected = {key: values[key] for key in
                         ("valence_mean", "valence_mean_deferred", "arousal_mean") if key in values}
        elif stage == "semantic_audio":
            projected = SemanticAudio.model_validate({key: values[key] for key in
                ("encoder_id", "sampling_policy", "segments")}).model_dump(mode="json")
        elif stage in ("emotion_music2emo", "danceability_musicnn"):
            # Optional malformed experiments retain their original fallback.
            try:
                projected = SampledEstimates.model_validate(values).model_dump(mode="json")
            except ValueError:
                continue
        elif stage in ("vocal_musicnn", "aggression_vggish", "instrument_passt"):
            try:
                projected = SpecialistEstimates.model_validate(values).model_dump(mode="json")
            except ValueError:
                continue
        else:
            continue
        algorithms.append({"algorithm_id": stage, "status": row["status"], "values": projected})
    return {"duration_s": feature.get("duration_s"), "algorithms": algorithms}


def freeze_planner(items, *, require_complete=True, planner_settings=None):
    """Validate on the source machine, preserving source/runtime provenance.

    require_complete=False exists for synthetic parity tests only; the export
    CLI always requires all eleven current local stages to be compatible.
    """
    from .specialists import LABELS, identity
    from .config import OpenAISettings
    from .web_bridge import STAGES, FEATURE_VERSION, POLICY, compatible
    if not items or len(items) > 100_000:
        raise ValueError("Publish a nonempty bounded library")
    identities = {stage: identity(stage) for stage in LABELS}
    settings = OpenAISettings.model_validate(planner_settings or {
        "model": "gpt-5.4-mini-2026-03-17", "timeout_s": 30, "intent_reasoning_effort": "low"})
    settings.key_source_file = None
    projected, sources = [], []
    seen_ids, seen_hashes = set(), set()
    for item in items:
        source_hash = item["sha256"]
        if not HASH.fullmatch(source_hash) or source_hash in seen_hashes or item["id"] in seen_ids:
            raise ValueError("Published tracks need unique IDs and SHA-256 hashes")
        seen_ids.add(item["id"]); seen_hashes.add(source_hash)
        feature = item["features"]
        if require_complete:
            indexed = {a["algorithm_id"]: a for a in feature["algorithms"]}
            if (feature.get("sha256") != source_hash or feature.get("status") != "complete"
                    or feature.get("feature_version") != FEATURE_VERSION
                    or feature.get("policy") != POLICY or not feature.get("genres")
                    or not all(stage in indexed and compatible(indexed[stage]) for stage in STAGES)):
                raise ValueError("Published library contains incomplete or incompatible analysis")
        projected.append({"id": item["id"], "sha256": source_hash,
                          "title": item["title"], "artist": item.get("artist"),
                          "features": project_features(feature)})
        sources.append({"id": item["id"], "sha256": source_hash,
                        "feature_sha256": digest(feature),
                        "feature_version": feature.get("feature_version"),
                        "models": {a["algorithm_id"]: {key: a.get("values", {}).get(key)
                                  for key in ("model_id", "encoder_id", "sampling_policy")}
                                   for a in feature["algorithms"]}})
    presets = {}
    for profile in PROFILES:
        expected_catalog, expected_vocabulary = catalog_from_features(items, estimator_profile=profile)
        catalog, vocabulary = catalog_from_features(projected, estimator_profile=profile,
                                                   published_specialist_identities=identities)
        if catalog != expected_catalog or vocabulary != expected_vocabulary:
            raise ValueError("Published projection changed planner evidence")
        presets[profile] = {"catalog": catalog.model_dump(mode="json", by_alias=True),
                            "vocabulary": vocabulary.model_dump(mode="json", by_alias=True)}
    payload = {"schema": SCHEMA, "fingerprints": fingerprints(), "sources": sources,
               "specialist_identities": identities, "items": projected, "presets": presets,
               "planner_settings": settings.model_dump(mode="json"),
               "feature_version": FEATURE_VERSION, "policy": POLICY}
    return {"payload_sha256": digest(payload), "payload": payload}


def export_release(release_dir, output_path):
    from .config import load_project_config
    release = Path(release_dir)
    public = json.loads((release / "public/catalog.json").read_text())
    items = []
    for track in public["tracks"]:
        source_hash = track["fileHash"]
        if not HASH.fullmatch(source_hash):
            raise ValueError("Invalid published source hash")
        feature = json.loads((release / "private/features" / (source_hash + ".json")).read_text())
        items.append({"id": track["id"], "sha256": source_hash, "title": track["title"],
                      "artist": track.get("artist"), "features": feature})
    configuration = load_project_config(Path(__file__).resolve().parents[2] / "playlist.toml")
    if configuration.provider != "openai" or configuration.openai is None:
        raise ValueError("Published planner requires the selected OpenAI project configuration")
    result = freeze_planner(items, planner_settings=configuration.openai.model_dump())
    atomic_json(output_path, result)
    # A saved real text cache is enough to prepare exact Linux ranking replay;
    # this does no model inference, network call or audio decoding.
    from .semantic_audio import BANK, identity as semantic_identity, text_embeddings
    from .models import SemanticQuery
    descriptions = list(BANK.values())[:2]
    semantic_query = SemanticQuery(description=descriptions[0], avoid=descriptions[1:],
                                   encoder_id=semantic_identity(),
                                   embeddings=text_embeddings(descriptions, cached_only=True))
    parity = build_parity(FrozenPlanner(result), semantic_query)
    atomic_json(Path(output_path).with_name("planner-parity.json"), parity)
    return {"tracks": len(items), "profiles": list(PROFILES), "payload_sha256": result["payload_sha256"],
            "parity_cases": len(parity["cases"])}


class FrozenPlanner:
    def __init__(self, document):
        payload = document["payload"]
        if (payload.get("schema") != SCHEMA or document.get("payload_sha256") != digest(payload)
                or payload.get("fingerprints") != fingerprints()):
            raise ValueError("Published planner snapshot failed integrity or runtime compatibility checks")
        self.payload = payload
        from .config import OpenAISettings
        settings = OpenAISettings.model_validate(payload["planner_settings"])
        if settings.key_source_file is not None:
            raise ValueError("Published planner cannot read a credential source file")
        self.planner_settings = settings
        self.snapshot_sha256 = document["payload_sha256"]
        self.items = {row["id"]: row for row in payload["items"]}
        if len(self.items) != len(payload["items"]) or set(payload["presets"]) != set(PROFILES):
            raise ValueError("Invalid published planner inventory")
        self.identities = payload["specialist_identities"]
        self.presets = {key: (Catalog.model_validate(value["catalog"]),
                              Vocabulary.model_validate(value["vocabulary"]))
                        for key, value in payload["presets"].items()}

    @classmethod
    def load(cls, path):
        return cls(json.loads(Path(path).read_text()))

    def select(self, tracks, profile="reference"):
        if profile not in PROFILES or not tracks or len(tracks) > len(self.items):
            raise ValueError("Invalid published library selection")
        selected, seen = [], set()
        for track in tracks:
            track_id = track.get("id")
            published = self.items.get(track_id)
            if (not published or track_id in seen
                    or track.get("sha256") != published["sha256"]):
                raise ValueError("Selection is not part of the published library")
            seen.add(track_id); selected.append(published)
        if [row["id"] for row in selected] == list(self.items):
            catalog, vocabulary = self.presets[profile]
            return catalog.model_copy(deep=True), vocabulary.model_copy(deep=True)
        return catalog_from_features(selected, estimator_profile=profile,
                                     published_specialist_identities=self.identities)


def build_parity(frozen, semantic_query=None):
    from .models import PlaylistQuery, Preference
    from .search import search_tracks
    tracks = [{"id": row["id"], "sha256": row["sha256"]} for row in frozen.items.values()]
    scopes = [("all", tracks), ("first", tracks[:1])]
    if len(tracks) >= 2:
        scopes.extend([("pair", [tracks[0], tracks[-1]]), ("pair-reversed", [tracks[-1], tracks[0]])])
    queries = [PlaylistQuery(limit=10), PlaylistQuery(limit=10, min_bpm=80, max_bpm=160,
               preferences=[Preference(tag="energy:low"), Preference(tag="vocals:vocal")])]
    if semantic_query is not None:
        queries.append(PlaylistQuery(limit=10, semantic=semantic_query))
    cases = []
    for profile in PROFILES:
        for scope_name, scope in scopes:
            catalog, vocabulary = frozen.select(scope, profile)
            for number, query in enumerate(queries):
                result = search_tracks(catalog, query, vocabulary)
                cases.append({"name": f"{profile}/{scope_name}/{number}", "profile": profile, "tracks": scope,
                              "query": query.model_dump(mode="json"),
                              "catalog_sha256": digest(catalog.model_dump(mode="json", by_alias=True)),
                              "vocabulary_sha256": digest(vocabulary.model_dump(mode="json", by_alias=True)),
                              "result_sha256": digest(result.model_dump(mode="json", by_alias=True))})
    return {"schema": "resonant/planner-parity/1", "snapshot_sha256": frozen.snapshot_sha256,
            "semantic_fixture": "existing cached MuQ character-bank text vectors" if semantic_query else None,
            "cases": cases}


def verify_parity(frozen, document):
    from .models import PlaylistQuery
    from .search import search_tracks
    if (document.get("schema") != "resonant/planner-parity/1"
            or document.get("snapshot_sha256") != frozen.snapshot_sha256 or not document.get("cases")):
        raise ValueError("Planner parity fixture does not match published snapshot")
    for case in document["cases"]:
        catalog, vocabulary = frozen.select(case["tracks"], case["profile"])
        result = search_tracks(catalog, PlaylistQuery.model_validate(case["query"]), vocabulary)
        for label, value in (("catalog", catalog), ("vocabulary", vocabulary), ("result", result)):
            if digest(value.model_dump(mode="json", by_alias=True)) != case[label + "_sha256"]:
                raise ValueError("Published planner parity failed")
    return len(document["cases"])
