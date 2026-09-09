"""Wrappers for All-In-One MLX and Beat This. Heavy imports stay lazy."""

from __future__ import annotations

from dataclasses import dataclass
from importlib.metadata import version
from pathlib import Path

import numpy as np


@dataclass
class EngineResult:
    beats_s: list[float]
    downbeats_s: list[float]
    bpm: float | None = None
    segments: list | None = None
    extra: dict | None = None
    error: str | None = None
    device: str | None = None
    return_order: str | None = None
    tool_version: str | None = None

    def as_dict(self) -> dict:
        segments = []
        for segment in self.segments or []:
            if isinstance(segment, dict):
                segments.append(
                    {
                        "start": float(segment["start"]),
                        "end": float(segment["end"]),
                        "label": str(segment.get("label") or ""),
                    }
                )
            else:
                segments.append(
                    {
                        "start": float(segment.start),
                        "end": float(segment.end),
                        "label": str(getattr(segment, "label", "") or ""),
                    }
                )
        return {
            "beats_s": list(self.beats_s),
            "downbeats_s": list(self.downbeats_s),
            "bpm": self.bpm,
            "segments": segments,
            "extra": self.extra or {},
            "error": self.error,
            "device": self.device,
            "return_order": self.return_order,
            "tool_version": self.tool_version,
        }

    @classmethod
    def from_dict(cls, payload: dict | None) -> EngineResult:
        data = payload or {}
        return cls(
            beats_s=[float(x) for x in data.get("beats_s") or []],
            downbeats_s=[float(x) for x in data.get("downbeats_s") or []],
            bpm=data.get("bpm"),
            segments=list(data.get("segments") or []),
            extra=data.get("extra") or {},
            error=data.get("error"),
            device=data.get("device"),
            return_order=data.get("return_order"),
            tool_version=data.get("tool_version"),
        )


def _as_floats(values) -> list[float]:
    if values is None:
        return []
    array = np.asarray(values).reshape(-1)
    return [float(item) for item in array.tolist()]


def allin1_version() -> str:
    return version("all-in-one-mlx")


def beat_this_version() -> str:
    return version("beat-this")


def run_allin1(path: Path, work_dir: Path) -> EngineResult:
    import allin1_mlx

    allin1_mlx.configure()
    out_dir = work_dir / "allin1-out"
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        result = allin1_mlx.analyze(
            path,
            out_dir=out_dir,
            model="harmonix-all",
            device="mlx",
            include_activations=False,
            include_embeddings=False,
            keep_byproducts=False,
            multiprocess=False,
            mlx_in_memory=False,
            mlx_compile=False,
            ensemble_parallel=False,
            demix_seed=1234,
        )
    except Exception as exc:
        return EngineResult(
            beats_s=[],
            downbeats_s=[],
            error=f"{type(exc).__name__}: {exc}",
            device="mlx",
        )

    bpm = float(result.bpm) if getattr(result, "bpm", None) is not None else None
    return EngineResult(
        beats_s=_as_floats(result.beats),
        downbeats_s=_as_floats(result.downbeats),
        bpm=bpm,
        segments=list(result.segments or []),
        extra={
            "beat_positions": _as_floats(getattr(result, "beat_positions", [])),
            "model": "harmonix-all",
        },
        device="mlx",
        tool_version=allin1_version(),
    )


class BeatThisRunner:
    """Load Beat This once per collection.

    Default device is CPU. MPS plus All-In-One MLX in the same process was
    observed to stall during the first combined smoke run (E011).
    """

    def __init__(self, device: str | None = None) -> None:
        import torch
        from beat_this.inference import File2Beats

        self.version = beat_this_version()
        self.fallback_reason: str | None = None
        requested = device or "cpu"
        self.device = requested
        self._estimator = None
        if requested == "mps" and not torch.backends.mps.is_available():
            self.fallback_reason = "Beat This requested MPS but it is unavailable; using CPU"
            requested = "cpu"
        try:
            self._estimator = File2Beats(
                checkpoint_path="final0",
                device=requested,
                dbn=False,
            )
            self.device = requested
        except Exception as exc:
            if requested != "cpu":
                self.fallback_reason = f"Beat This {requested} init failed, using CPU: {exc}"
                self._estimator = File2Beats(
                    checkpoint_path="final0",
                    device="cpu",
                    dbn=False,
                )
                self.device = "cpu"
            else:
                raise


    def analyze(self, path: Path) -> EngineResult:
        try:
            first, second = self._estimator(str(path))
        except Exception as exc:
            if self.device == "mps":
                self.fallback_reason = f"Beat This MPS inference failed, retrying CPU: {exc}"
                from beat_this.inference import File2Beats

                self._estimator = File2Beats(
                    checkpoint_path="final0",
                    device="cpu",
                    dbn=False,
                )
                self.device = "cpu"
                try:
                    first, second = self._estimator(str(path))
                except Exception as retry_exc:
                    return EngineResult(
                        beats_s=[],
                        downbeats_s=[],
                        error=str(retry_exc),
                        device=self.device,
                    )
            else:
                return EngineResult(
                    beats_s=[],
                    downbeats_s=[],
                    error=str(exc),
                    device=self.device,
                )

        first_list = _as_floats(first)
        second_list = _as_floats(second)
        # Postprocessor returns (beats, downbeats). File2File unpacks the opposite
        # names. Prefer the longer sequence as beats; log the convention used.
        if first_list and second_list and len(first_list) < len(second_list) * 0.6:
            downbeats, beats = first_list, second_list
            order = "file2file-heuristic-swapped"
        else:
            beats, downbeats = first_list, second_list
            order = "postprocessor-beats-then-downbeats"
        return EngineResult(
            beats_s=beats,
            downbeats_s=downbeats,
            bpm=None,
            extra={"checkpoint": "final0", "dbn": False},
            device=self.device,
            return_order=order,
            tool_version=self.version,
        )
