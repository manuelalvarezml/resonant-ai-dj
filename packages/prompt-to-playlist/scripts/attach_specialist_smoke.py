"""Attach verified two-source smoke evidence to the existing local web caches."""
import argparse
import json
import time
from pathlib import Path
from prompt_to_playlist import web_bridge as bridge
from prompt_to_playlist.analysis_pipeline import _atomic_json
from prompt_to_playlist.model_assets import sha256_file
from prompt_to_playlist.specialists import STAGES
from smoke_specialists import SOURCES, ROOT

def main():
    p=argparse.ArgumentParser();p.add_argument('--run-name',required=True);args=p.parse_args()
    if not args.run_name.replace('-','').isalnum():raise ValueError('Invalid run name')
    for filename,slug,digest in SOURCES:
        source=ROOT.parents[1]/'test_music'/'test_folder_37_tracks_diff_genres'/filename
        if sha256_file(source)!=digest:raise ValueError('Source identity changed')
        path=bridge.cache_path(digest);old=json.loads(path.read_text());new=json.loads(path.read_text())
        saved={a['algorithm_id']:a for a in old['algorithms']}
        for stage in STAGES:
            run=json.loads((ROOT/'output/top-estimators/runs'/args.run_name/slug/stage/'descriptor-run.json').read_text())
            if not run['source_hashes_unchanged'] or not run['source_inventory_unchanged'] or run['failure_count']:raise ValueError('Smoke evidence failed')
            if len(run['tracks'])!=1:raise ValueError('Unexpected smoke scope')
            track=run['tracks'][0]
            if track['source']['sha256_before']!=digest or track['source']['sha256_after']!=digest:raise ValueError('Wrong smoke source')
            a=track['algorithms'][0]
            if a['algorithm_id']!=stage or not bridge.compatible(a):raise ValueError('Stale or invalid smoke output')
            saved[stage]=a
        new['algorithms']=list(saved.values())
        new['quality_status']='complete' if all(k in saved and bridge.compatible(saved[k]) for k in ['emotion_music2emo',*STAGES]) else 'partial'
        if new['quality_status']!='complete':raise ValueError('Music2Emo coverage incomplete')
        new['upgrade_failures']=[f for f in new.get('upgrade_failures',[]) if f['algorithm_id'] not in STAGES]
        history=bridge.CACHE/'history'/digest;history.mkdir(parents=True,exist_ok=True)
        _atomic_json(history/(str(time.time_ns())+'.json'),old);_atomic_json(path,new)
        print(slug,new['quality_status'],len(new['algorithms']))
if __name__=='__main__':main()
