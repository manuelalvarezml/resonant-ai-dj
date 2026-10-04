"""Published-library planner CLI. No audio analysis, local source scan or key file."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import stat
import time
import uuid

from .cloud_catalog import FrozenPlanner, atomic_json, export_release, verify_parity
from .config import read_api_key
from .models import ClarificationAnswer

AUDIT_NAME = re.compile(r"playlist-([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})(?:-inputs)?\.json")


def prune_audits(state_dir, *, now=None, max_pairs=200, max_age_days=7):
    """Bound exact private replays; ignore symlinks and all unrelated files."""
    root = Path(state_dir).resolve()
    directory = root / "audits"
    if directory.is_symlink() or not directory.is_dir():
        return
    groups = {}
    for path in directory.iterdir():
        matched = AUDIT_NAME.fullmatch(path.name)
        if not matched:
            continue
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode):
            continue
        groups.setdefault(matched[1], []).append((path, info.st_mtime))
    newest = sorted(groups.values(), key=lambda rows: max(row[1] for row in rows), reverse=True)
    cutoff = (time.time() if now is None else now) - max_age_days * 86400
    for index, rows in enumerate(newest):
        if index >= max_pairs or max(row[1] for row in rows) < cutoff:
            for path, _ in rows:
                path.unlink(missing_ok=True)


def prompt(request, *, release_dir, state_dir, model_dir, translator=None, encoder=None):
    from .cloud_text import query_encoder
    from .service import build_playlist
    from .translators import OpenAITranslator
    if not isinstance(request, dict) or set(request) - {"prompt", "tracks", "clarifications", "estimator_profile"}:
        raise ValueError("Invalid playlist request")
    if not isinstance(request.get("prompt"), str) or not 1 <= len(request["prompt"].strip()) <= 4000:
        raise ValueError("Invalid playlist prompt")
    answers = [ClarificationAnswer.model_validate(row) for row in request.get("clarifications", [])]
    if len(answers) > 3:
        raise ValueError("At most three clarification answers are supported")
    snapshot = FrozenPlanner.load(Path(release_dir) / "private/planner.json")
    profile = request.get("estimator_profile", "reference")
    catalog, vocabulary = snapshot.select(request.get("tracks"), profile)
    if translator is None:
        # Frozen selected model/reasoning from playlist.toml. No shell-file fallback
        # or implicit OPENAI_API_KEY; only the explicitly injected project key.
        settings = snapshot.planner_settings
        translator = OpenAITranslator(api_key=read_api_key(settings), model=settings.model,
                                      timeout_s=settings.timeout_s,
                                      intent_reasoning_effort=settings.intent_reasoning_effort)
    run = build_playlist(request["prompt"], catalog, vocabulary, translator,
                         clarifications=answers, query_encoder=encoder or query_encoder(model_dir, state_dir))
    result = run.model_dump(mode="json", by_alias=True)
    audit_id = str(uuid.uuid4())
    audit = Path(state_dir) / "audits"
    if audit.is_symlink():
        raise ValueError("Audit directory must be inside the application state directory")
    atomic_json(audit / ("playlist-" + audit_id + ".json"), result)
    atomic_json(audit / ("playlist-" + audit_id + "-inputs.json"), {
        "request": {"prompt": request["prompt"], "clarifications": [a.model_dump(mode="json") for a in answers],
                    "estimator_profile": profile,
                    "tracks": [{"id": row["id"], "sha256": row["sha256"]} for row in request["tracks"]]},
        "planner_snapshot_sha256": snapshot.snapshot_sha256,
        "catalog": catalog.model_dump(mode="json", by_alias=True),
        "vocabulary": vocabulary.model_dump(mode="json", by_alias=True)})
    prune_audits(state_dir)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["export", "verify", "prompt"])
    parser.add_argument("--release-dir", type=Path, required=True)
    parser.add_argument("--state-dir", type=Path)
    parser.add_argument("--model-dir", type=Path)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    os.umask(0o077)
    try:
        if args.action == "export":
            result = export_release(args.release_dir, args.out)
            print(json.dumps(result))
            return 0
        if args.action == "verify":
            frozen = FrozenPlanner.load(args.release_dir / "private/planner.json")
            parity = json.loads((args.release_dir / "private/planner-parity.json").read_text())
            result = {"tracks": len(frozen.items), "profiles": list(frozen.presets),
                      "snapshot_sha256": frozen.snapshot_sha256,
                      "parity_cases_passed": verify_parity(frozen, parity)}
        else:
            if args.input is None or args.state_dir is None or args.model_dir is None:
                raise ValueError("Prompt requires input, state and model directories")
            if args.input.stat().st_size > 2 * 1024 * 1024:
                raise ValueError("Playlist request is too large")
            result = prompt(json.loads(args.input.read_text()), release_dir=args.release_dir,
                            state_dir=args.state_dir, model_dir=args.model_dir)
        atomic_json(args.out, {"result": result})
        return 0
    except Exception:
        # Provider/config errors can contain URLs, request data or secrets.
        # Only the deployment operator sees exit status; browsers get no paths.
        if args.action != "export":
            atomic_json(args.out, {"error": "PlaylistIQ could not complete this request. Check the published release and server configuration."})
        else:
            print("Planner export failed: verify current complete local analysis and source records.", file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
