"""Fresh default web pipeline on exactly two hash-authorized sources; then cache retries."""
import json
import time
from pathlib import Path
from prompt_to_playlist import web_bridge as bridge
from prompt_to_playlist.model_assets import sha256_file
from smoke_specialists import SOURCES

root=Path(__file__).resolve().parents[1]
bridge.CACHE=root/'output/default-pipeline-smoke-2026-10-01'
records=[]
for filename,slug,digest in SOURCES:
    source=root.parents[1]/'test_music/test_folder_37_tracks_diff_genres'/filename
    assert sha256_file(source)==digest
    start=time.monotonic()
    result=bridge.analyze(source,reuse_existing=False)
    elapsed=time.monotonic()-start
    (bridge.CACHE/(slug+'-fresh.json')).write_text(json.dumps(result,indent=2))
    assert result['status']=='complete',result.get('upgrade_failures')
    assert len(result['executed_algorithms'])==11
    retry=bridge.analyze(source)
    assert retry['executed_algorithms']==[] and retry['status']=='complete'
    assert sha256_file(source)==digest
    records.append({'source':slug,'elapsed_s':elapsed,'stages':result['algorithms'],'retry_executed':retry['executed_algorithms']})
    (bridge.CACHE/'measurements.json').write_text(json.dumps(records,indent=2))
    print(json.dumps({'source':slug,'elapsed_s':elapsed,'status':result['status'],'retry_executed':[]}),flush=True)
