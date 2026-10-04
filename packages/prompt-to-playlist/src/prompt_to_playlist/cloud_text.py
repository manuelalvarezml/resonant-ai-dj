"""Cloud text-only MuQ retrieval with persistent cache and bounded subprocesses."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

from .cloud_catalog import atomic_json
from .models import SemanticQuery
from .semantic_audio import POLICY, identity, text_embeddings


def encode_texts(texts, model_dir, cache_dir, *, cached_only=False):
    if not isinstance(texts, list) or not 1 <= len(texts) <= 4:
        raise ValueError("Expected one positive and at most three negative descriptions")
    return {"encoder_id": identity(model_dir),
            "embeddings": text_embeddings(texts, cached_only=cached_only,
                                          model_dir=model_dir, cache_dir=cache_dir)}


def _stop(process):
    import psutil
    try:
        children = psutil.Process(process.pid).children(recursive=True)
    except psutil.Error:
        children = []
    for child in reversed(children):
        try:
            child.kill()
        except psutil.Error:
            pass
    if process.poll() is None:
        process.kill()
    process.wait(timeout=10)


def bounded_encode(texts, model_dir, state_dir, *, timeout_s=300,
                   max_rss_mb=6000, min_available_ram_mb=1024):
    """Only misses start a model process; process-group ownership stays with Node."""
    model_dir, state_dir = Path(model_dir), Path(state_dir)
    cache_dir = state_dir / "text-cache"
    # Cache hits have the same normalization as the local encoder and no model IO.
    try:
        return encode_texts(texts, model_dir, cache_dir, cached_only=True)
    except ValueError as exc:
        if str(exc) != "Description text cache is missing. Run scripts/prepare_character_bank.py.":
            raise
    import psutil
    directory = state_dir / "text-jobs"
    directory.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=directory) as temporary:
        job = Path(temporary)
        atomic_json(job / "input.json", {"texts": texts})
        threads = int(os.environ.get("PLAYLISTIQ_CPU_THREADS", "2"))
        if not 1 <= threads <= 8:
            raise ValueError("Invalid text worker thread limit")
        environment = os.environ.copy()
        for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                     "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS", "PLAYLISTIQ_CPU_THREADS"):
            environment[name] = str(threads)
        environment.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", TOKENIZERS_PARALLELISM="false")
        command = [sys.executable, "-m", "prompt_to_playlist.cloud_text", "--input", str(job / "input.json"),
                   "--out", str(job / "output.json"), "--model-dir", str(model_dir),
                   "--cache-dir", str(cache_dir)]
        started = time.monotonic()
        peak_rss = 0
        # No separate process group: the HTTP job supervisor can kill this whole
        # tree on cancellation/timeout without leaving a model child running.
        with tempfile.TemporaryFile() as log:
            process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=log, stderr=log, env=environment)
            try:
                while process.poll() is None:
                    try:
                        parent = psutil.Process(process.pid)
                        members = [parent, *parent.children(recursive=True)]
                        rss = 0
                        for member in members:
                            try:
                                rss += member.memory_info().rss
                            except psutil.Error:
                                pass
                        peak_rss = max(peak_rss, rss)
                    except psutil.Error:
                        pass
                    if (time.monotonic() - started > timeout_s
                            or peak_rss / 1024**2 > max_rss_mb
                            or psutil.virtual_memory().available / 1024**2 < min_available_ram_mb):
                        raise ValueError("Text encoder exceeded its configured time or memory limit")
                    time.sleep(.2)
                if process.returncode != 0 or not (job / "output.json").is_file():
                    raise ValueError("Text encoder worker failed")
                result = json.loads((job / "output.json").read_text())
                # Validate the untrusted process result before using any vectors.
                SemanticQuery(description=texts[0], avoid=texts[1:], **result)
                atomic_json(state_dir / "last-text-worker.json", {
                    "wall_time_s": time.monotonic() - started, "peak_rss_mb": peak_rss / 1024**2,
                    "encoder_id": result["encoder_id"], "count": len(texts), "exit_code": process.returncode})
                return result
            finally:
                if process.poll() is None:
                    _stop(process)


def query_encoder(model_dir, state_dir):
    from .search import search_tracks

    def encode(query, catalog, vocabulary):
        candidates = set(search_tracks(catalog, query.model_copy(update={"semantic": None}),
                                      vocabulary, ranking_version="maest-intent-v1").eligible_track_ids)
        tracks = [track for track in catalog.tracks if track.track_id in candidates]
        if len(tracks) < 2:
            return query, []
        try:
            encoder = identity(Path(model_dir))
            if any(track.semantic_audio is None or track.semantic_audio.encoder_id != encoder
                   or track.semantic_audio.sampling_policy != POLICY for track in tracks):
                return query, ["Upgrade analysis for all eligible tracks to enable semantic ranking."]
            texts = [query.semantic.description, *query.semantic.avoid]
            result = bounded_encode(texts, model_dir, state_dir)
            if result["encoder_id"] != encoder:
                raise ValueError("Text encoder identity changed")
            semantic = SemanticQuery(description=texts[0], avoid=texts[1:], **result)
            return query.model_copy(update={"semantic": semantic}), []
        except (ValueError, OSError):
            return query, ["Semantic text encoding unavailable; structured ranking retained."]
    return encode


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Offline text-only MuQ worker")
    for name in ("input", "out", "model-dir", "cache-dir"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    result = encode_texts(json.loads(args.input.read_text())["texts"], args.model_dir, args.cache_dir)
    atomic_json(args.out, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
