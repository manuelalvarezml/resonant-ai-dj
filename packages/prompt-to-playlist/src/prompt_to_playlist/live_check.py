"""Explicit, bounded live evaluation. Never invoked by pytest or app startup.

Usage: python -m prompt_to_playlist.live_check --config playlist.toml --out FILE
This makes six real API requests with fixed test prompts, then searches locally.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys
from time import monotonic

from pydantic import RootModel

from .adapters import _safe_output_path, load_catalog, save_json
from .config import load_project_config, read_api_key
from .service import build_playlist
from .translators import OpenAITranslator
from .vocabulary import load_vocabulary

CASES = [
    ("natural_language_house_energy", "house dj set energetic",
     {"required_tags": ["genre:house"], "preferred_tags": ["energy:high"], "limit": 10}, "matched"),
    ("count_and_genre", "Find up to five tracks. Only include tracks tagged as house.",
     {"limit": 5, "required_tags": ["genre:house"]}, "matched"),
    ("spanish_genre", "Dame tres canciones. Solo incluye canciones etiquetadas como dembow.",
     {"limit": 3, "required_tags": ["genre:dembow"]}, "matched"),
    ("tempo_and_order", "Give me four tracks between 120 and 130 BPM, sorted from slower to faster.",
     {"limit": 4, "min_bpm": 120.0, "max_bpm": 130.0, "order": "bpm_ascending"}, "matched"),
    ("negative_evidence", "Find three house tracks with no vocals.",
     {"limit": 3, "excluded_tags": ["vocals:vocal"]}, "no_matches"),
    ("unsupported_mix", "Make a 45-minute continuous mix with beatmatched transitions.",
     {}, "needs_clarification"),
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        _safe_output_path(args.out)  # Refuse invalid/existing output before spending requests.
        config = load_project_config(args.config)
        if config.provider != "openai" or config.openai is None:
            raise ValueError("Live evaluation needs an OpenAI project profile.")
        catalog = load_catalog(Path(config.catalog))
        vocabulary = load_vocabulary(Path(config.vocabulary) if config.vocabulary else None)
        translator = OpenAITranslator(api_key=read_api_key(config.openai), model=config.openai.model,
                                      timeout_s=config.openai.timeout_s)
        cases = []
        for case_id, prompt, expected_query, expected_status in CASES:
            started = monotonic()
            try:
                # This historical v3 suite intentionally preserves flat-query baseline behavior.
                from types import SimpleNamespace
                run = build_playlist(prompt, catalog, vocabulary, SimpleNamespace(translate=translator.translate))
                query = run.translation.query.model_dump()
                checks = {field: query[field] == expected for field, expected in expected_query.items()}
                checks["status"] = run.status == expected_status
                checks["catalog_membership"] = run.result is None or all(
                    match.track.track_id in {track.track_id for track in catalog.tracks} for match in run.result.matches)
                record = {"id": case_id, "prompt": prompt, "passed": all(checks.values()), "checks": checks,
                          "expected_query": expected_query, "expected_status": expected_status,
                          "run": run.model_dump(mode="json", by_alias=True), "error": None}
            except (ValueError, OSError) as exc:
                record = {"id": case_id, "prompt": prompt, "passed": False, "error": str(exc)}
            record["elapsed_s"] = round(monotonic() - started, 3)
            cases.append(record)
            print(f"{case_id}: {'passed' if record['passed'] else 'FAILED'} ({record['elapsed_s']}s)", file=sys.stderr)
        report = {"schema": "prompt-playlist/live-check", "schema_version": "0.1.0",
                  "created_at": datetime.now(timezone.utc).isoformat(), "model": config.openai.model,
                  "catalog_id": catalog.catalog_id, "catalog_tracks": len(catalog.tracks),
                  "vocabulary_id": vocabulary.vocabulary_id, "requests_attempted": len(cases),
                  "passed": all(case["passed"] for case in cases), "cases": cases,
                  "note": "Bounded live smoke evaluation on this catalog. Not a general quality or injection-resistance benchmark."}
        save_json(RootModel[dict](report), args.out)
        return 0 if report["passed"] else 1
    except (ValueError, OSError) as exc:
        print(f"Live check: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
