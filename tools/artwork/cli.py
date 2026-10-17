"""Resumable artwork-only CLI; all outputs are sidecars outside source directories."""
import argparse
import json
from pathlib import Path
import sys
from artwork import Store

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--cache", type=Path, default=Path(__file__).resolve().parents[2] / "output/artwork")
commands = parser.add_subparsers(dest="command", required=True)
commands.add_parser("enqueue", help="Read one trusted stored-track event from stdin")
commands.add_parser("retry-unavailable", help="Explicitly reset exhausted provider retries")
backfill = commands.add_parser("backfill", help="Enqueue an existing catalog and its local source map")
backfill.add_argument("--catalog", type=Path, required=True)
backfill.add_argument("--sources", type=Path, required=True)
backfill.add_argument("--scope", default="default")
backfill.add_argument("--limit", type=int, default=0)
work = commands.add_parser("work")
work.add_argument("--offline", action="store_true")
work.add_argument("--limit", type=int, default=0, help="Maximum uncached album resolutions; 0 means all")
export = commands.add_parser("manifest")
export.add_argument("--scope", default="default")

def main():
    args = parser.parse_args()
    store = Store(args.cache)
    if args.command == "enqueue":
        store.enqueue_stored(**json.load(sys.stdin))
        result = {"queued": True}
    elif args.command == "backfill":
        catalog = json.loads(args.catalog.read_text())
        sources = json.loads(args.sources.read_text())
        tracks = catalog["tracks"][:args.limit or None]
        for track in tracks:
            store.enqueue_stored(scope=args.scope, track_id=track["id"], source_version=track.get("sourceVersion", track["id"]), source_hash=track["fileHash"], source_path=sources[track["id"]], metadata={k: track.get(k) for k in ("artist", "albumartist", "album")})
        result = {"queued": len(tracks)}
    elif args.command == "work":
        result = store.work(offline=args.offline, limit=args.limit)
    elif args.command == "retry-unavailable":
        store.retry_unavailable()
        result = {"reset": True}
    else:
        result = store.manifest(args.scope)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
