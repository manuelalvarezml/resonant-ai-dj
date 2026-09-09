"""Essentia KeyExtractor wrapper. Output is always a benchmark estimate."""

from __future__ import annotations

from importlib.metadata import version

import numpy as np

from dj_collection_set_builder.constants import (
    AUTHORITY_ESTIMATE,
    KEY_HPCP_SIZE,
    KEY_PROFILE,
    KEY_SAMPLE_RATE,
    STATUS_FAILED,
    STATUS_WARNING,
    WEAK_KEY_STRENGTH,
)
from dj_collection_set_builder.keys import notation_bundle
from dj_collection_set_builder.models import KeyAnalysis


def estimate_key(pcm: np.ndarray | None, sample_rate: int | None) -> KeyAnalysis:
    parameters = {
        "profileType": KEY_PROFILE,
        "hpcpSize": KEY_HPCP_SIZE,
        "sampleRate": KEY_SAMPLE_RATE,
        "averageDetuningCorrection": True,
    }
    tool_version = version("essentia")
    warnings = ["Global key is an estimate and may hide modulation."]
    if pcm is None or sample_rate is None:
        return KeyAnalysis(
            authority=AUTHORITY_ESTIMATE,
            status=STATUS_FAILED,
            tool_version=tool_version,
            model_profile=KEY_PROFILE,
            warnings=warnings + ["Key skipped because analysis PCM was unavailable"],
            parameters=parameters,
        )
    if sample_rate != KEY_SAMPLE_RATE:
        warnings.append(
            f"Analysis PCM sample rate was {sample_rate} Hz; KeyExtractor expects {KEY_SAMPLE_RATE}."
        )

    try:
        import essentia.standard as es
    except Exception as exc:
        return KeyAnalysis(
            authority=AUTHORITY_ESTIMATE,
            status=STATUS_FAILED,
            tool_version=tool_version,
            model_profile=KEY_PROFILE,
            warnings=warnings + [f"Essentia import failed: {exc}"],
            parameters=parameters,
        )

    mono = np.asarray(pcm, dtype=np.float32)
    if mono.ndim == 2:
        mono = mono.mean(axis=1)
    mono = np.ascontiguousarray(mono, dtype=np.float32)

    try:
        extractor = es.KeyExtractor(
            profileType=KEY_PROFILE,
            hpcpSize=KEY_HPCP_SIZE,
            sampleRate=int(sample_rate),
        )
        tonic, mode, strength = extractor(mono)
    except Exception as exc:
        return KeyAnalysis(
            authority=AUTHORITY_ESTIMATE,
            status=STATUS_FAILED,
            tool_version=tool_version,
            model_profile=KEY_PROFILE,
            warnings=warnings + [f"KeyExtractor failed: {exc}"],
            parameters=parameters,
        )

    display, standard_name, camelot, open_key = notation_bundle(str(tonic), str(mode))
    strength_value = float(strength) if strength is not None else None
    if strength_value is not None and strength_value < WEAK_KEY_STRENGTH:
        warnings.append(
            f"Key strength {strength_value:.3f} is below {WEAK_KEY_STRENGTH}; treat as weak."
        )
    if camelot is None:
        warnings.append(f"Could not derive Camelot/Open Key from tonic={tonic!r} mode={mode!r}")

    return KeyAnalysis(
        authority=AUTHORITY_ESTIMATE,
        status=STATUS_WARNING,
        source_tool="essentia-key-extractor",
        tool_version=tool_version,
        model_profile=KEY_PROFILE,
        tonic=display,
        mode=str(mode).lower() if mode else None,
        standard_name=standard_name,
        camelot=camelot,
        open_key=open_key,
        strength=strength_value,
        warnings=warnings,
        parameters=parameters,
    )
