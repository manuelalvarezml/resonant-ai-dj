"""Short-lived workers for one PlaylistIQ descriptor algorithm and one track."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path
from typing import Any

import numpy as np

WORKER_VERSION = "playlistiq-analysis-worker-v1"


def _package_version(name: str) -> str:
    try:
        return version(name)
    except Exception:
        return "unavailable"


def _positive_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) and number > 0 else None


def analyze_metadata(path: Path, _: Path) -> dict[str, Any]:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise RuntimeError("ffprobe is required and was not found on PATH")
    command = [
        ffprobe,
        "-v",
        "error",
        "-protocol_whitelist",
        "file",
        "-show_entries",
        "format=format_name,duration,bit_rate:format_tags=title,artist,album,genre,bpm,tbpm,tempo:stream=index,codec_type,codec_name,sample_rate,channels,channel_layout,bit_rate",
        "-of",
        "json",
        str(path),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False, timeout=30)
    if completed.returncode:
        raise RuntimeError(f"ffprobe failed with exit {completed.returncode}")
    payload = json.loads(completed.stdout)
    fmt = payload.get("format") or {}
    stream = next((item for item in payload.get("streams", []) if item.get("codec_type") == "audio"), {})
    tags = fmt.get("tags") if isinstance(fmt.get("tags"), dict) else {}
    return {
        "algorithm_id": "metadata",
        "implementation": "ffprobe",
        "implementation_version": _tool_version(ffprobe),
        "authority": "encoded_fact",
        "status": "passed",
        "values": {
            "container_format": fmt.get("format_name"),
            "duration_s": _positive_float(stream.get("duration") or fmt.get("duration")),
            "codec": stream.get("codec_name"),
            "sample_rate_hz": int(stream["sample_rate"]) if str(stream.get("sample_rate", "")).isdigit() else None,
            "channels": stream.get("channels"),
            "channel_layout": stream.get("channel_layout"),
            "bit_rate_bps": int(stream.get("bit_rate") or fmt.get("bit_rate")) if str(stream.get("bit_rate") or fmt.get("bit_rate") or "").isdigit() else None,
            "encoded_tags": {str(key): str(value) for key, value in sorted(tags.items())},
        },
        "warnings": ["Encoded metadata is source evidence, not verified musical truth."],
    }


def _tool_version(executable: str) -> str:
    completed = subprocess.run([executable, "-version"], capture_output=True, text=True, check=False, timeout=5)
    return (completed.stdout.splitlines() or ["unknown"])[0][:500]


def analyze_loudness(path: Path, _: Path) -> dict[str, Any]:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required and was not found on PATH")
    command = [
        ffmpeg,
        "-nostdin",
        "-hide_banner",
        "-loglevel",
        "info",
        "-protocol_whitelist",
        "file,pipe,fd",
        "-i",
        str(path),
        "-af",
        "loudnorm=I=-24:LRA=7:TP=-2:print_format=json",
        "-f",
        "null",
        "-",
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False, timeout=1800)
    if completed.returncode:
        raise RuntimeError(f"ffmpeg loudnorm analysis failed with exit {completed.returncode}")
    blocks = re.findall(r"\{\s*\"input_i\".*?\}", completed.stderr, flags=re.DOTALL)
    if not blocks:
        raise RuntimeError("ffmpeg loudnorm returned no measurement JSON")
    measured = json.loads(blocks[-1])
    values = {
        "integrated_lufs": float(measured["input_i"]),
        "loudness_range_lu": float(measured["input_lra"]),
        "true_peak_dbtp": float(measured["input_tp"]),
        "relative_threshold_lufs": float(measured["input_thresh"]),
    }
    return {
        "algorithm_id": "loudness",
        "implementation": "ffmpeg-loudnorm",
        "implementation_version": _tool_version(ffmpeg),
        "authority": "standardized_measurement",
        "status": "passed",
        "values": values,
        "warnings": ["Loudness is retained for playback/mix preparation and is not semantic energy."],
    }


_CAMELOT = {
    ("C", "major"): "8B", ("G", "major"): "9B", ("D", "major"): "10B", ("A", "major"): "11B",
    ("E", "major"): "12B", ("B", "major"): "1B", ("F#", "major"): "2B", ("C#", "major"): "3B",
    ("G#", "major"): "4B", ("D#", "major"): "5B", ("A#", "major"): "6B", ("F", "major"): "7B",
    ("A", "minor"): "8A", ("E", "minor"): "9A", ("B", "minor"): "10A", ("F#", "minor"): "11A",
    ("C#", "minor"): "12A", ("G#", "minor"): "1A", ("D#", "minor"): "2A", ("A#", "minor"): "3A",
    ("F", "minor"): "4A", ("C", "minor"): "5A", ("G", "minor"): "6A", ("D", "minor"): "7A",
}
_FLAT_TO_SHARP = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}


def analyze_key(path: Path, _: Path) -> dict[str, Any]:
    import essentia.standard as es

    audio = es.MonoLoader(filename=str(path), sampleRate=44100, resampleQuality=4)()
    tonic, mode, strength = es.KeyExtractor(
        profileType="edma", hpcpSize=36, sampleRate=44100, averageDetuningCorrection=True
    )(audio)
    tonic = str(tonic)
    mode = str(mode).lower()
    normalized_tonic = _FLAT_TO_SHARP.get(tonic, tonic)
    warnings = ["Global key is a benchmark estimate and may hide modulation."]
    if float(strength) < 0.35:
        warnings.append("Key strength is below 0.35; treat this estimate as weak.")
    return {
        "algorithm_id": "key",
        "implementation": "essentia-key-extractor",
        "implementation_version": _package_version("essentia-tensorflow"),
        "authority": "benchmark_estimate",
        "status": "warning",
        "values": {
            "tonic": tonic,
            "mode": mode,
            "standard_key": f"{tonic} {mode}",
            "camelot": _CAMELOT.get((normalized_tonic, mode)),
            "strength": float(strength),
            "sample_rate_hz": 44100,
            "profile": "edma",
            "hpcp_size": 36,
        },
        "warnings": warnings,
    }


def _event_list(values: Any) -> list[float]:
    return [float(item) for item in np.asarray(values).reshape(-1).tolist()]


def rhythm_diagnostics(beats, bpm):
    intervals = np.diff(np.asarray(beats, dtype=float))
    intervals = intervals[np.isfinite(intervals) & (intervals > 0)]
    if not len(intervals) or bpm is None: return {}
    return {"diagnostics_policy": "beat-interval-spread-v1",
            "beat_interval_p10_s": float(np.quantile(intervals, .1)),
            "beat_interval_median_s": float(np.median(intervals)),
            "beat_interval_p90_s": float(np.quantile(intervals, .9)),
            "tempo_candidates_bpm": [float(v) for v in (bpm/2, bpm, bpm*2) if 20 <= v <= 400],
            "tempo_diagnostic_note": "Half/double-time hypotheses and interval spread; neither is calibrated confidence or proof of the perceived tempo."}


def analyze_rhythm(path: Path, model_dir: Path) -> dict[str, Any]:
    import torch
    from beat_this.inference import File2Beats

    torch.set_num_threads(max(1, int(os.environ.get("PLAYLISTIQ_CPU_THREADS", "1"))))
    torch.set_num_interop_threads(1)
    checkpoint = model_dir / "final0.ckpt"
    if not checkpoint.is_file():
        raise RuntimeError(f"Pinned Beat This checkpoint is missing: {checkpoint}")
    estimator = File2Beats(checkpoint_path=str(checkpoint), device="cpu", dbn=False)
    first, second = estimator(str(path))
    first_list, second_list = _event_list(first), _event_list(second)
    if first_list and second_list and len(first_list) < len(second_list) * 0.6:
        downbeats, beats = first_list, second_list
        return_order = "heuristic-swapped"
    else:
        beats, downbeats = first_list, second_list
        return_order = "beats-then-downbeats"
    intervals = np.diff(np.asarray(beats, dtype=float))
    intervals = intervals[intervals > 0]
    bpm = float(60.0 / np.median(intervals)) if intervals.size else None
    return {
        "algorithm_id": "rhythm",
        "implementation": "beat-this-final0-cpu",
        "implementation_version": _package_version("beat-this"),
        "authority": "benchmark_estimate",
        "status": "warning" if bpm else "failed",
        "values": {
            "bpm": bpm,
            **rhythm_diagnostics(beats, bpm),
            "beat_count": len(beats),
            "downbeat_count": len(downbeats),
            "beats_s": beats,
            "downbeats_s": downbeats,
            "return_order": return_order,
            "checkpoint_sha256": "8c328b45f59d8dd3dff219253ff6a8d6482be57d0133a29140e2febbf8eb8331",
            "device": "cpu",
            "dbn": False,
        },
        "warnings": ["Tempo, beats, and downbeats are benchmark estimates, not musical facts."],
    }


def _load_metadata(model_dir: Path, name: str) -> dict[str, Any]:
    with (model_dir / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def _mean_predictions(predictions: Any, labels: list[str]) -> dict[str, float]:
    array = np.asarray(predictions, dtype=float)
    if array.ndim == 1:
        array = array.reshape(1, -1)
    means = np.mean(array, axis=0)
    if len(means) != len(labels):
        raise RuntimeError(f"Model returned {len(means)} values for {len(labels)} labels")
    return {label: float(value) for label, value in zip(labels, means, strict=True)}


def _head_predictions(embeddings: Any, model_dir: Path, stem: str) -> dict[str, Any]:
    import essentia.standard as es

    metadata = _load_metadata(model_dir, f"{stem}.json")
    output = metadata["schema"]["outputs"][0]["name"]
    predictions = es.TensorflowPredict2D(
        graphFilename=str(model_dir / f"{stem}.pb"), output=output
    )(embeddings)
    scores = _mean_predictions(predictions, metadata["classes"])
    ordered = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    return {
        "scores": scores,
        "top_label": ordered[0][0],
        "top_score": ordered[0][1],
        "margin": ordered[0][1] - ordered[1][1] if len(ordered) > 1 else None,
        "frame_count": int(np.asarray(predictions).shape[0]),
        "aggregation": "arithmetic_mean_over_model_patches",
        "score_kind": "uncalibrated_classifier_support",
        "temporal_summary": {label: {"p10": float(np.quantile(np.asarray(predictions)[:, i], .1)), "p90": float(np.quantile(np.asarray(predictions)[:, i], .9))} for i, label in enumerate(metadata["classes"])},
    }


def analyze_semantic(path: Path, model_dir: Path, *, include_legacy_vocals=True) -> dict[str, Any]:
    import essentia.standard as es

    audio = es.MonoLoader(filename=str(path), sampleRate=16000, resampleQuality=4)()
    embeddings = es.TensorflowPredictEffnetDiscogs(
        graphFilename=str(model_dir / "discogs-effnet-bs64-1.pb"),
        output="PartitionedCall:1",
        batchSize=64,
        lastPatchMode="repeat",
    )(audio)
    heads = {
        "mood_theme": _head_predictions(embeddings, model_dir, "mtg_jamendo_moodtheme-discogs-effnet-1"),
        "instruments": _head_predictions(embeddings, model_dir, "mtg_jamendo_instrument-discogs-effnet-1"),
        "danceability": _head_predictions(embeddings, model_dir, "danceability-discogs-effnet-1"),
        **({"vocal_profile": _head_predictions(embeddings, model_dir, "voice_instrumental-discogs-effnet-1")} if include_legacy_vocals else {}),
        "mood_happy": _head_predictions(embeddings, model_dir, "mood_happy-discogs-effnet-1"),
        "mood_sad": _head_predictions(embeddings, model_dir, "mood_sad-discogs-effnet-1"),
        "mood_relaxed": _head_predictions(embeddings, model_dir, "mood_relaxed-discogs-effnet-1"),
        "mood_aggressive": _head_predictions(embeddings, model_dir, "mood_aggressive-discogs-effnet-1"),
    }
    return {
        "algorithm_id": "semantic",
        "implementation": "essentia-discogs-effnet-expanded-v3" if include_legacy_vocals else "essentia-discogs-effnet-selected-v4",
        "implementation_version": _package_version("essentia-tensorflow"),
        "authority": "benchmark_estimate",
        "status": "warning",
        "values": {
            "embedding_model": "discogs-effnet-bs64-1",
            "embedding_shape": list(np.asarray(embeddings).shape),
            "sample_rate_hz": 16000,
            "heads": heads,
        },
        "warnings": [
            "Probabilities are model estimates; thresholds are not calibrated on this library.",
            "No semantic axis is complete until human-reviewed evaluation supports it.",
        ],
    }


def analyze_energy(path: Path, model_dir: Path) -> dict[str, Any]:
    import essentia.standard as es

    audio = es.MonoLoader(filename=str(path), sampleRate=16000, resampleQuality=4)()
    embeddings = es.TensorflowPredictMusiCNN(
        graphFilename=str(model_dir / "msd-musicnn-1.pb"), output="model/dense/BiasAdd"
    )(audio)
    predictions = es.TensorflowPredict2D(
        graphFilename=str(model_dir / "deam-msd-musicnn-2.pb"), output="model/Identity"
    )(embeddings)
    metadata = _load_metadata(model_dir, "deam-msd-musicnn-2.json")
    scores = _mean_predictions(predictions, metadata["classes"])
    return {
        "algorithm_id": "energy",
        "implementation": "essentia-deam-msd-musicnn",
        "implementation_version": _package_version("essentia-tensorflow"),
        "authority": "benchmark_estimate",
        "status": "warning",
        "values": {
            "energy_candidate": "arousal",
            "arousal_mean": scores["arousal"],
            "valence_mean": scores["valence"],
            "valence_mean_deferred": scores["valence"],
            "expected_output_scale": "DEAM 1-9; raw mean retained without clipping or calibration",
            "prediction_frame_count": int(np.asarray(predictions).shape[0]),
            "embedding_shape": list(np.asarray(embeddings).shape),
            "aggregation": "arithmetic_mean_over_model_patches",
            "sample_rate_hz": 16000,
        },
        "warnings": [
            "Arousal is an energy candidate, not yet a calibrated PlaylistIQ energy score.",
            "Valence describes estimated musical positivity, not the listener's feelings; the historical deferred field is retained for compatibility.",
        ],
    }


from .genre_maest import analyze_genre_maest
from .semantic_audio import analyze_semantic_audio, encode_text_worker, prepare_bank_worker
from .supervised import analyze_music2emo, analyze_danceability, analyze_reference


from .specialists import analyze_vocal, analyze_aggression, analyze_instruments, analyze_key as analyze_specialist_key

def analyze_current_semantic(path, model_dir):
    return analyze_semantic(path, model_dir, include_legacy_vocals=False)


ALGORITHMS = {
    "vocal_musicnn": analyze_vocal,
    "aggression_vggish": analyze_aggression,
    "instrument_passt": analyze_instruments,
    "key_sheetsage2": analyze_specialist_key,
    "emotion_music2emo": analyze_music2emo,
    "danceability_musicnn": analyze_danceability,
    "estimator_reference": analyze_reference,
    "semantic_audio": analyze_semantic_audio,
    "semantic_text": encode_text_worker,
    "semantic_bank": prepare_bank_worker,
    "genre_maest": analyze_genre_maest,
    "metadata": analyze_metadata,
    "loudness": analyze_loudness,
    "key": analyze_key,
    "rhythm": analyze_rhythm,
    "semantic": analyze_current_semantic,
    "energy": analyze_energy,
}


def run(algorithm: str, source: Path, model_dir: Path) -> dict[str, Any]:
    try:
        return ALGORITHMS[algorithm](source, model_dir)
    except Exception as exc:
        return {
            "algorithm_id": algorithm,
            "implementation": ALGORITHMS[algorithm].__name__,
            "implementation_version": WORKER_VERSION,
            "authority": "benchmark_estimate" if algorithm not in {"metadata", "loudness"} else (
                "encoded_fact" if algorithm == "metadata" else "standardized_measurement"
            ),
            "status": "failed",
            "values": {},
            "warnings": [],
            "error": f"{type(exc).__name__}: {exc}",
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--algorithm", required=True, choices=tuple(ALGORITHMS))
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--model-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    payload = run(args.algorithm, args.source, args.model_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        handle.write("\n")
    return 0 if payload["status"] != "failed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
