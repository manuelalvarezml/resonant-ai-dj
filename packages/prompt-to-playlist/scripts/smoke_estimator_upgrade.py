"""Bounded local smoke on exactly two established, hash-verified source tracks."""
from pathlib import Path
import json
from prompt_to_playlist.analysis_pipeline import analyze_folder
from prompt_to_playlist.model_assets import sha256_file
from prompt_to_playlist.web_bridge import analyze, CACHE

ROOT=Path(__file__).resolve().parents[1]
SOURCES=[('04 Listen Over the Ocean.mp3','ocean','b23cf7fc573254db349ab179fdcc406c5da159186b04b1fe914ff913d83e4ae2'),('01 My Paradise - Edit.mp3','paradise','c4fa9722112e74661c9a4da26fa386d9a65564da8a3cef25048df25168f31bae')]

def main():
    records=[]
    for name,slug,digest in SOURCES:
        source=ROOT.parents[1]/'test_music'/'test_folder_37_tracks_diff_genres'/name
        if sha256_file(source)!=digest:raise ValueError('Source does not match authorized inventory')
        for algorithm,folder,prior in [('semantic','expanded-features','expanded'),('semantic_audio','semantic-audio','muq')]:
            existing=ROOT/'output/estimator-upgrade'/slug/prior
            reuse=[existing] if (existing/'descriptor-run.json').exists() else []
            run,_=analyze_folder(folder=source.parent,source_name=name,output_dir=CACHE/'checkpoints'/digest/folder/'run',max_tracks=1,algorithms=[algorithm],model_dir=ROOT/'output/estimator-models',resume=True,reuse_from=reuse,max_worker_rss_mb=6000 if algorithm=='semantic_audio' else 4096,worker_timeout_s=600)
            if run.failure_count or not run.source_hashes_unchanged or not run.source_inventory_unchanged:
                raise RuntimeError('Bounded smoke failed; inspect descriptor run before continuing')
        result=analyze(source)
        if result['status']!='complete':raise RuntimeError('Integrated feature upgrade is incomplete')
        again=analyze(source)
        if again['executed_algorithms']:raise RuntimeError('Compatible feature cache unexpectedly reran inference')
        records.append({'source':name,'sha256':digest,'status':result['status'],'heads':{k:len(v['scores']) for k,v in next(a for a in result['algorithms'] if a['algorithm_id']=='semantic')['values']['heads'].items()},'retry_executed':again['executed_algorithms'],'source_unchanged':sha256_file(source)==digest})
    out=ROOT/'output/estimator-upgrade/integration-smoke.json';out.write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(records,indent=2),flush=True)

if __name__=='__main__':main()
