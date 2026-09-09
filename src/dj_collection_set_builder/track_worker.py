"""Short-lived stage workers so MLX/PyTorch memory is released after each step."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze one stage of one source MP3.")
    parser.add_argument("--stage", required=True, choices=("ingest", "allin1", "beatthis"))
    parser.add_argument("--path", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--folder")
    parser.add_argument("--work-dir")
    parser.add_argument("--ffmpeg-version")
    parser.add_argument("--ffprobe-version")
    args = parser.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    path = Path(args.path)

    if args.stage == "ingest":
        if not args.folder or not args.work_dir or not args.ffmpeg_version or not args.ffprobe_version:
            raise SystemExit("ingest stage requires --folder, --work-dir, and ffmpeg/ffprobe versions")
        from dj_collection_set_builder.analyze import ingest_track

        payload = ingest_track(
            path,
            Path(args.folder),
            work_dir=Path(args.work_dir),
            ffmpeg_version=args.ffmpeg_version,
            ffprobe_version=args.ffprobe_version,
        )
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return

    if args.stage == "allin1":
        if not args.work_dir:
            raise SystemExit("allin1 stage requires --work-dir")
        from dj_collection_set_builder.engines import run_allin1

        result = run_allin1(path, Path(args.work_dir))
        out.write_text(json.dumps(result.as_dict(), indent=2), encoding="utf-8")
        return

    from dj_collection_set_builder.engines import BeatThisRunner

    runner = BeatThisRunner(device="cpu")
    result = runner.analyze(path)
    payload = result.as_dict()
    payload["fallback_reason"] = runner.fallback_reason
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
