"""Opt-in MAEST Discogs519 inference and compact human-review output."""

import json
from importlib.metadata import version
from pathlib import Path

MODEL = "discogs-maest-30s-pw-519l-2"
OUTPUT = "PartitionedCall/Identity_13"
AGGREGATION = "arithmetic_mean_over_30s_patches_last_patch_repeated"


def summarize_predictions(predictions, labels):
    import numpy as np

    values = np.asarray(predictions, dtype=np.float64)
    if len(labels) != 519 or len(set(labels)) != 519:
        raise ValueError("Expected 519 unique Discogs labels")
    if values.size == 0 or values.shape[-1] != 519:
        raise ValueError(f"Expected nonempty predictions ending in 519 classes, got {values.shape}")
    if not np.isfinite(values).all() or (values < 0).any() or (values > 1).any():
        raise ValueError("Expected finite sigmoid probabilities in [0, 1], not logits")
    patches = values.reshape(-1, 519)
    scores = dict(zip(labels, patches.mean(axis=0).tolist(), strict=True))
    ordered = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    return {
        "scores": scores,
        "genre_policy": "maest-top6-v1",
        "top_6": [{"genre": label, "probability": score} for label, score in ordered[:6]],
        "top_10": [{"genre": label, "probability": score} for label, score in ordered[:10]],
        "patch_count": len(patches),
        "aggregation": AGGREGATION,
    }


def analyze_genre_maest(path: Path, model_dir: Path) -> dict:
    import essentia.standard as es

    metadata = json.loads((model_dir / f"{MODEL}.json").read_text())
    if not any(item["name"] == OUTPUT and item.get("op") == "Sigmoid"
               for item in metadata["schema"]["outputs"]):
        raise ValueError("Model card does not identify the expected sigmoid output")
    audio = es.MonoLoader(filename=str(path), sampleRate=16000, resampleQuality=4)()
    if len(audio) == 0:
        raise ValueError("Decoded audio is empty")
    predictions = es.TensorflowPredictMAEST(
        graphFilename=str(model_dir / f"{MODEL}.pb"),
        output=OUTPUT, batchSize=1, patchSize=1876, patchHopSize=1875,
        lastPatchMode="repeat",
    )(audio)
    values = summarize_predictions(predictions, metadata["classes"])
    values.update(model=MODEL, output_node=OUTPUT, sample_rate_hz=16000,
                  audio_duration_s=len(audio) / 16000)
    return {
        "algorithm_id": "genre_maest",
        "implementation": "essentia-maest-discogs519-v1",
        "implementation_version": version("essentia-tensorflow"),
        "authority": "benchmark_estimate", "status": "warning", "values": values,
        "warnings": ["Independent multi-label probabilities; not calibrated certainty and do not sum to 1."],
    }


def review_document(run) -> dict:
    tracks = []
    for track in run.tracks:
        result = next(item for item in track.algorithms if item.algorithm_id == "genre_maest")
        tracks.append({
            "filename": track.source.relative_path,
            "sha256": track.source.sha256_before,
            "status": result.status,
            "genre_policy": "maest-top6-v1",
            "top_6": result.values.get("top_6", result.values.get("top_10", [])[:6]),
            "top_10": result.values.get("top_10", []),
            **({"error": result.error} if result.error else {}),
        })
    return {
        "schema": "prompt-playlist/genre-review", "schema_version": "0.1.0",
        "model": MODEL, "authority": "benchmark_estimate",
        "probability_note": "Independent model probabilities in [0,1], averaged across patches; not calibrated certainty; do not sum to 1.",
        "aggregation": AGGREGATION,
        "source_hashes_unchanged": run.source_hashes_unchanged,
        "source_inventory_unchanged": run.source_inventory_unchanged,
        "tracks": tracks,
    }
