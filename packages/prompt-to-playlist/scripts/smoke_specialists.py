"""Explicit two-source experiment. Never discovers an additional analysis corpus."""
import argparse
import json
from pathlib import Path
from prompt_to_playlist.analysis_pipeline import analyze_folder
from prompt_to_playlist.model_assets import sha256_file
from prompt_to_playlist.specialists import STAGES

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    ('04 Listen Over the Ocean.mp3', 'ocean', 'b23cf7fc573254db349ab179fdcc406c5da159186b04b1fe914ff913d83e4ae2'),
    ('01 My Paradise - Edit.mp3', 'paradise', 'c4fa9722112e74661c9a4da26fa386d9a65564da8a3cef25048df25168f31bae'),
]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--track', choices=['ocean', 'paradise'])
    p.add_argument('--stage', choices=STAGES)
    p.add_argument('--run-name', default='specialists-v1')
    args = p.parse_args()
    if not args.run_name.replace('-', '').isalnum():
        raise ValueError('Use a simple run name')
    records = []
    for filename, slug, digest in SOURCES:
        if args.track and args.track != slug:
            continue
        source = ROOT.parents[1] / 'test_music' / 'test_folder_37_tracks_diff_genres' / filename
        if sha256_file(source) != digest:
            raise ValueError('Authorized source identity mismatch')
        for stage in [args.stage] if args.stage else STAGES:
            out = ROOT / 'output/top-estimators/runs' / args.run_name / slug / stage
            run, _ = analyze_folder(folder=source.parent, source_name=filename, output_dir=out,
                algorithms=[stage], model_dir=ROOT/'output/estimator-models',
                max_tracks=1, resume=True, cpu_threads=4, max_worker_rss_mb=8000 if stage=="key_sheetsage2" else 4096,
                worker_timeout_s=1800 if stage=="key_sheetsage2" else 600)
            records.append({'source':slug, 'stage':stage, 'failures':run.failure_count,
                            'hashes_unchanged':run.source_hashes_unchanged, 'inventory_unchanged':run.source_inventory_unchanged})
            print(json.dumps(records[-1]), flush=True)
            if run.failure_count or not run.source_hashes_unchanged or not run.source_inventory_unchanged:
                raise RuntimeError('Smoke failed; inspect the preserved descriptor-run before continuing')
    print(json.dumps(records, indent=2))


if __name__ == '__main__':
    main()
