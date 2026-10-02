"""Pinned public model assets with streaming, hash-verified downloads."""

from __future__ import annotations

import hashlib
import os
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from .analysis_models import ModelAssetRecord

MODEL_BASE = "https://essentia.upf.edu/models"


@dataclass(frozen=True)
class AssetSpec:
    asset_id: str
    relative_url: str
    sha256: str

    @property
    def filename(self) -> str:
        return self.relative_url.rsplit("/", 1)[-1]

    @property
    def url(self) -> str:
        if self.relative_url.startswith("https://"):
            return self.relative_url
        return f"{MODEL_BASE}/{self.relative_url}"


ASSETS = {
    item.asset_id: item
    for item in [
        AssetSpec("maest_pb", "feature-extractors/maest/discogs-maest-30s-pw-519l-2.pb", "92783feb21187443d058b4f16d7a76f47888d43fbdc7a28e8bcc8e024603bd20"),
        AssetSpec("maest_json", "feature-extractors/maest/discogs-maest-30s-pw-519l-2.json", "83240aa553ffb491b0ec5a24565eb612553e5f38da5207403c25b890c5b34acd"),
        AssetSpec("discogs_effnet_pb", "music-style-classification/discogs-effnet/discogs-effnet-bs64-1.pb", "3ed9af50d5367c0b9c795b294b00e7599e4943244f4cbd376869f3bfc87721b1"),
        AssetSpec("discogs_effnet_json", "music-style-classification/discogs-effnet/discogs-effnet-bs64-1.json", "395479c8d0e23c1185bf903079c38b9c536014787db6e1184abd68463c92b2da"),
        AssetSpec("genre_pb", "classification-heads/mtg_jamendo_genre/mtg_jamendo_genre-discogs-effnet-1.pb", "a46f94fd85b03b403d6498a820e3ee652e05a24fc2a344d84545ac36224e698e"),
        AssetSpec("genre_json", "classification-heads/mtg_jamendo_genre/mtg_jamendo_genre-discogs-effnet-1.json", "b0ae89110ddbdba5ed3ad375910b1cffc738436fbb4138ac4c2801b48fc5ec59"),
        AssetSpec("moodtheme_pb", "classification-heads/mtg_jamendo_moodtheme/mtg_jamendo_moodtheme-discogs-effnet-1.pb", "03f2b047020aee4ab39f8880da7bdae2a36d06a1508d656c6d424ad4d6de07a9"),
        AssetSpec("moodtheme_json", "classification-heads/mtg_jamendo_moodtheme/mtg_jamendo_moodtheme-discogs-effnet-1.json", "d62cd90263e4d613fa7fcce7a831e339450394794af63685f96e065c1a896ab0"),
        AssetSpec("instrument_pb", "classification-heads/mtg_jamendo_instrument/mtg_jamendo_instrument-discogs-effnet-1.pb", "2e8c3003c722e098da371b6a1f7ad0ce62fac0dcfc09c7c7997d430941196c2a"),
        AssetSpec("instrument_json", "classification-heads/mtg_jamendo_instrument/mtg_jamendo_instrument-discogs-effnet-1.json", "7d02204c6451b5615e2968ec6364bbae3b915c886e608f05f00d3a38dc5177c4"),
        AssetSpec("danceability_pb", "classification-heads/danceability/danceability-discogs-effnet-1.pb", "e1251f02cdc846445e2bc1fb3fe9963e32728c5c000e009188ae47c8963cb4c4"),
        AssetSpec("danceability_json", "classification-heads/danceability/danceability-discogs-effnet-1.json", "589e61dc05f0d7935be4b5fa7ab4341e5dc7cfecc6898f83503558564790cd75"),
        AssetSpec("voice_pb", "classification-heads/voice_instrumental/voice_instrumental-discogs-effnet-1.pb", "c8033548e17c292874265db62e82a051247768d10375a35a769e7bf695f16acf"),
        AssetSpec("voice_json", "classification-heads/voice_instrumental/voice_instrumental-discogs-effnet-1.json", "43ac2c3b055dfaed20f6232e0f10636c287f1c5a6e5bd02c5585860031964c8f"),
        AssetSpec("mood_happy_pb", "classification-heads/mood_happy/mood_happy-discogs-effnet-1.pb", "de322aee7f4da29ecbd149c86e7964bd6fabe41ca85698a0be40a39d49e88633"),
        AssetSpec("mood_happy_json", "classification-heads/mood_happy/mood_happy-discogs-effnet-1.json", "ed4601bc396b23367d29cf45aa327366cdfdbd3e2baeb7a3f7893237f1ffd9e6"),
        AssetSpec("mood_sad_pb", "classification-heads/mood_sad/mood_sad-discogs-effnet-1.pb", "4865cba49968b6ec295db3e8af6b4a7bb506b1a646628b9f07ee9910d52df82c"),
        AssetSpec("mood_sad_json", "classification-heads/mood_sad/mood_sad-discogs-effnet-1.json", "7f2c00099ad8255af33e43ab77d1ac2c86a1dd9f46d3e5ea2a9a52246f5033d9"),
        AssetSpec("mood_relaxed_pb", "classification-heads/mood_relaxed/mood_relaxed-discogs-effnet-1.pb", "2c5aa6666b58fe80429a2dc677a135e9995922889b5a399af87d1c15f0ebb71d"),
        AssetSpec("mood_relaxed_json", "classification-heads/mood_relaxed/mood_relaxed-discogs-effnet-1.json", "86c0fe1c2c6d49bf08537bc2d3a602204feaede011ed119c1fc6c36270f60e6a"),
        AssetSpec("mood_aggressive_pb", "classification-heads/mood_aggressive/mood_aggressive-discogs-effnet-1.pb", "7705284e3a67f23f04d3f2fd75e18a82c0e70db8875b7b6f7061f2432de80858"),
        AssetSpec("mood_aggressive_json", "classification-heads/mood_aggressive/mood_aggressive-discogs-effnet-1.json", "81773e95d78db1b93283d73b2d06344d1ff79685b57d9428a40d47fdfcf537b8"),
        AssetSpec("musicnn_pb", "feature-extractors/musicnn/msd-musicnn-1.pb", "cdea0722bcee7f731286843f2233e3aa69887bb5c3e2dce011eff55f38d04f3e"),
        AssetSpec("musicnn_json", "feature-extractors/musicnn/msd-musicnn-1.json", "8e6b3b509f0610c0e65dce467fd459d6777509388eaddb13ed138d8ac1341ffe"),
        AssetSpec("deam_pb", "classification-heads/deam/deam-msd-musicnn-2.pb", "beb5eeb0909266eeb78b8d6bb1323b10829cf2fe55e3c01a13fa1846fa98b371"),
        AssetSpec("deam_json", "classification-heads/deam/deam-msd-musicnn-2.json", "079df8d538d093ba35c34b7fbee01ff2773c4469be5281520f55d585295a3c58"),
        AssetSpec("beat_this_final0", "https://cloud.cp.jku.at/public.php/dav/files/7ik4RrBKTS273gp/final0.ckpt", "8c328b45f59d8dd3dff219253ff6a8d6482be57d0133a29140e2febbf8eb8331"),
    ]
}

SEMANTIC_ASSETS = tuple(
    asset_id
    for asset_id in ASSETS
    if not asset_id.startswith(("musicnn", "deam", "beat_this", "maest", "genre"))
)
ENERGY_ASSETS = ("musicnn_pb", "musicnn_json", "deam_pb", "deam_json")
RHYTHM_ASSETS = ("beat_this_final0",)
_MAX_ASSET_BYTES = 256 * 1024 * 1024


def default_model_dir() -> Path:
    root = os.environ.get("XDG_CACHE_HOME")
    if root:
        return Path(root).expanduser() / "playlistiq" / "models" / "v1"
    return Path.home() / ".cache" / "playlistiq" / "models" / "v1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def required_assets(algorithms: list[str]) -> tuple[str, ...]:
    if 'estimator_reference' in algorithms:
        algorithms = [*algorithms, 'semantic', 'energy']
    selected: list[str] = []
    if "genre_maest" in algorithms:
        selected.extend(("maest_pb", "maest_json"))
    if "semantic" in algorithms:
        selected.extend(SEMANTIC_ASSETS)
    if "energy" in algorithms:
        selected.extend(ENERGY_ASSETS)
    if "rhythm" in algorithms:
        selected.extend(RHYTHM_ASSETS)
    return tuple(dict.fromkeys(selected))


def ensure_assets(
    model_dir: Path,
    asset_ids: tuple[str, ...],
    *,
    timeout_s: float = 120.0,
) -> tuple[dict[str, Path], list[ModelAssetRecord]]:
    model_dir = model_dir.expanduser().resolve()
    model_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    records: list[ModelAssetRecord] = []
    for asset_id in asset_ids:
        spec = ASSETS[asset_id]
        max_asset_bytes = 384 * 1024 * 1024 if asset_id == "maest_pb" else _MAX_ASSET_BYTES
        destination = model_dir / spec.filename
        started = time.monotonic()
        downloaded = False
        if destination.exists():
            if not destination.is_file() or destination.is_symlink():
                raise ValueError(f"Model asset is not a regular file: {destination}")
            observed = sha256_file(destination)
            if observed != spec.sha256:
                raise ValueError(
                    f"Model asset hash mismatch for {destination.name}; remove it and retry"
                )
        else:
            temporary = model_dir / f".{spec.filename}.part-{os.getpid()}"
            request = urllib.request.Request(spec.url, headers={"User-Agent": "PlaylistIQ/0.3"})
            try:
                with urllib.request.urlopen(request, timeout=timeout_s) as response, temporary.open("xb") as handle:
                    content_length = response.headers.get("Content-Length")
                    if content_length and int(content_length) > max_asset_bytes:
                        raise ValueError(f"Model asset is larger than {max_asset_bytes} bytes")
                    written = 0
                    while chunk := response.read(1024 * 1024):
                        written += len(chunk)
                        if written > max_asset_bytes:
                            raise ValueError(f"Model asset exceeded {max_asset_bytes} bytes")
                        handle.write(chunk)
                if sha256_file(temporary) != spec.sha256:
                    raise ValueError(f"Downloaded model hash mismatch for {spec.filename}")
                temporary.replace(destination)
                downloaded = True
            finally:
                temporary.unlink(missing_ok=True)
        elapsed = time.monotonic() - started
        paths[asset_id] = destination
        records.append(
            ModelAssetRecord(
                asset_id=asset_id,
                filename=spec.filename,
                url=spec.url,
                sha256=spec.sha256,
                size_bytes=destination.stat().st_size,
                downloaded=downloaded,
                preparation_wall_time_s=elapsed,
            )
        )
    return paths, records
