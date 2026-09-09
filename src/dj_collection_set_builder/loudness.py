"""FFmpeg EBU R128 loudness plus independent pyloudnorm validation."""

from __future__ import annotations

import json
import subprocess
from importlib.metadata import version

import numpy as np
import pyloudnorm as pyln

from dj_collection_set_builder.constants import (
    AUTHORITY_DETERMINISTIC,
    AUTHORITY_STANDARDIZED,
    FFMPEG_LOUDNORM_FILTER,
    LOUDNESS_INTEGRATED_TOLERANCE_LU,
    LOUDNESS_LRA_TOLERANCE_LU,
    STATUS_FAILED,
    STATUS_PASSED,
    STATUS_WARNING,
)
from dj_collection_set_builder.models import FeatureValue, LoudnessAnalysis, failed_feature


def _extract_last_json_object(text: str) -> dict:
    decoder = json.JSONDecoder()
    last_error: Exception | None = None
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            obj, _end = decoder.raw_decode(text[index:])
        except json.JSONDecodeError as exc:
            last_error = exc
            continue
        if isinstance(obj, dict) and "input_i" in obj:
            return obj
    if last_error:
        raise last_error
    raise ValueError("ffmpeg loudnorm JSON was not found in stderr")


def _parse_float(value: object) -> float | None:
    if value in (None, "", "nan", "-inf", "inf"):
        return None
    try:
        parsed = float(str(value))
    except (TypeError, ValueError):
        return None
    if not np.isfinite(parsed):
        return None
    return parsed


def ffmpeg_loudnorm(path, ffmpeg_version: str) -> dict[str, float | None]:
    command = [
        "ffmpeg",
        "-hide_banner",
        "-i",
        str(path),
        "-af",
        FFMPEG_LOUDNORM_FILTER,
        "-f",
        "null",
        "-",
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    combined = (completed.stderr or "") + "\n" + (completed.stdout or "")
    if completed.returncode != 0 and "input_i" not in combined:
        raise RuntimeError(completed.stderr.strip() or "ffmpeg loudnorm failed")
    payload = _extract_last_json_object(combined)
    return {
        "integrated": _parse_float(payload.get("input_i")),
        "range": _parse_float(payload.get("input_lra")),
        "true_peak": _parse_float(payload.get("input_tp")),
        "threshold": _parse_float(payload.get("input_thresh")),
        "raw": payload,  # type: ignore[dict-item]
        "ffmpeg_version": ffmpeg_version,  # type: ignore[dict-item]
    }


def pyloudnorm_check(pcm: np.ndarray, sample_rate: int) -> dict[str, float | None]:
    meter = pyln.Meter(sample_rate)
    integrated = float(meter.integrated_loudness(pcm))
    loudness_range = float(meter.loudness_range(pcm))
    return {
        "integrated": integrated if np.isfinite(integrated) else None,
        "range": loudness_range if np.isfinite(loudness_range) else None,
        "version": version("pyloudnorm"),  # type: ignore[dict-item]
    }


def _authority_for(passed: bool | None) -> str:
    if passed:
        return AUTHORITY_STANDARDIZED
    return AUTHORITY_DETERMINISTIC


def analyze_loudness(
    path,
    pcm: np.ndarray | None,
    sample_rate: int | None,
    ffmpeg_version: str,
) -> LoudnessAnalysis:
    pyloudnorm_version = version("pyloudnorm")
    primary_tool = {
        "name": "ffmpeg",
        "version": ffmpeg_version,
        "filter": FFMPEG_LOUDNORM_FILTER,
    }
    validator_block = {
        "name": "pyloudnorm",
        "version": pyloudnorm_version,
        "integrated_difference_lu": None,
        "lra_difference_lu": None,
        "passed": None,
    }

    try:
        measured = ffmpeg_loudnorm(path, ffmpeg_version)
    except Exception as exc:
        message = f"ffmpeg loudnorm failed: {exc}"
        validator_block["passed"] = False
        return LoudnessAnalysis(
            integrated=failed_feature(
                unit="LUFS",
                source_tool="ffmpeg",
                tool_version=ffmpeg_version,
                message=message,
            ),
            range=failed_feature(
                unit="LU",
                source_tool="ffmpeg",
                tool_version=ffmpeg_version,
                message=message,
            ),
            true_peak=failed_feature(
                unit="dBTP",
                source_tool="ffmpeg",
                tool_version=ffmpeg_version,
                message=message,
            ),
            primary_tool=primary_tool,
            validator=validator_block,
        )

    validator_values: dict[str, float | None] = {"integrated": None, "range": None}
    validator_error: str | None = None
    if pcm is not None and sample_rate is not None:
        try:
            validator_values = pyloudnorm_check(pcm, sample_rate)
        except Exception as exc:
            validator_error = f"pyloudnorm failed: {exc}"
    else:
        validator_error = "pyloudnorm skipped because analysis PCM was unavailable"

    integrated_diff = None
    lra_diff = None
    if measured["integrated"] is not None and validator_values.get("integrated") is not None:
        integrated_diff = abs(measured["integrated"] - validator_values["integrated"])
    if measured["range"] is not None and validator_values.get("range") is not None:
        lra_diff = abs(measured["range"] - validator_values["range"])

    integrated_pass = (
        integrated_diff is not None and integrated_diff <= LOUDNESS_INTEGRATED_TOLERANCE_LU
    )
    lra_pass = lra_diff is not None and lra_diff <= LOUDNESS_LRA_TOLERANCE_LU
    validator_passed = bool(integrated_pass and lra_pass) if validator_error is None else False
    validator_block.update(
        {
            "integrated_difference_lu": integrated_diff,
            "lra_difference_lu": lra_diff,
            "passed": validator_passed if validator_error is None else False,
            "error": validator_error,
        }
    )

    integrated_status = STATUS_PASSED if integrated_pass else STATUS_WARNING
    range_status = STATUS_PASSED if lra_pass else STATUS_WARNING
    if measured["integrated"] is None:
        integrated_status = STATUS_FAILED
    if measured["range"] is None:
        range_status = STATUS_FAILED
    if validator_error:
        integrated_status = STATUS_WARNING if measured["integrated"] is not None else STATUS_FAILED
        range_status = STATUS_WARNING if measured["range"] is not None else STATUS_FAILED

    peak_status = STATUS_PASSED if measured["true_peak"] is not None else STATUS_FAILED
    # True peak has no pyloudnorm counterpart; keep it standardized only when
    # the integrated/LRA pair passed, otherwise treat it as a deterministic reading.
    peak_authority = (
        AUTHORITY_STANDARDIZED if validator_passed and measured["true_peak"] is not None
        else AUTHORITY_DETERMINISTIC
    )

    warnings = []
    if validator_error:
        warnings.append(validator_error)
    if integrated_diff is not None and not integrated_pass:
        warnings.append(
            "Integrated loudness disagreement exceeds "
            f"{LOUDNESS_INTEGRATED_TOLERANCE_LU} LU"
        )
    if lra_diff is not None and not lra_pass:
        warnings.append(
            f"Loudness range disagreement exceeds {LOUDNESS_LRA_TOLERANCE_LU} LU"
        )

    return LoudnessAnalysis(
        integrated=FeatureValue(
            value=measured["integrated"],
            unit="LUFS",
            authority=_authority_for(integrated_pass and validator_error is None),
            status=integrated_status,
            source_tool="ffmpeg",
            tool_version=ffmpeg_version,
            parameters={"filter": FFMPEG_LOUDNORM_FILTER},
            validator={
                "tool": "pyloudnorm",
                "version": pyloudnorm_version,
                "value": validator_values.get("integrated"),
                "tolerance": LOUDNESS_INTEGRATED_TOLERANCE_LU,
                "difference": integrated_diff,
                "passed": integrated_pass,
            },
            warnings=list(warnings),
        ),
        range=FeatureValue(
            value=measured["range"],
            unit="LU",
            authority=_authority_for(lra_pass and validator_error is None),
            status=range_status,
            source_tool="ffmpeg",
            tool_version=ffmpeg_version,
            parameters={"filter": FFMPEG_LOUDNORM_FILTER},
            validator={
                "tool": "pyloudnorm",
                "version": pyloudnorm_version,
                "value": validator_values.get("range"),
                "tolerance": LOUDNESS_LRA_TOLERANCE_LU,
                "difference": lra_diff,
                "passed": lra_pass,
            },
            warnings=list(warnings),
        ),
        true_peak=FeatureValue(
            value=measured["true_peak"],
            unit="dBTP",
            authority=peak_authority,
            status=peak_status if peak_status == STATUS_FAILED else (
                STATUS_PASSED if validator_passed else STATUS_WARNING
            ),
            source_tool="ffmpeg",
            tool_version=ffmpeg_version,
            parameters={"filter": FFMPEG_LOUDNORM_FILTER, "field": "input_tp"},
            warnings=list(warnings),
        ),
        primary_tool=primary_tool,
        validator=validator_block,
    )
