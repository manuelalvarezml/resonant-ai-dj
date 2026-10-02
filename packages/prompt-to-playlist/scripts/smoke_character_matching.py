"""Upgrade exactly the two existing acceptance records; forbid model/audio inference."""
import copy
import json
import time
from prompt_to_playlist import web_bridge as bridge, semantic_audio as sa, analysis_pipeline as pipeline
from prompt_to_playlist.model_assets import sha256_file
from smoke_specialists import SOURCES

def forbidden(*args,**kwargs):raise AssertionError('Matching unexpectedly requested audio or model inference')
sa.load_model=forbidden
pipeline.analyze_folder=forbidden
sa.subprocess.check_output=forbidden
records=[]
for filename,slug,digest in SOURCES:
 source=bridge.ROOT.parents[1]/'test_music/test_folder_37_tracks_diff_genres'/filename
 assert sha256_file(source)==digest
 before=json.loads(bridge.cache_path(digest).read_text())
 prior={a['algorithm_id']:a for a in before['algorithms']}
 assert before['status']=='complete'
 original=copy.deepcopy(prior['semantic_audio']['values']['segments'])
 start=time.perf_counter();result=bridge.analyze(source);elapsed=time.perf_counter()-start
 current={a['algorithm_id']:a for a in result['algorithms']}
 assert current['semantic_audio']['values']['segments']==original
 assert len(current['semantic_audio']['values']['descriptors'])==120
 assert sa.matching_compatible(current['semantic_audio']['values'])
 for stage,value in prior.items():
  if stage!='semantic_audio':assert current[stage]==value,stage
 assert result['executed_algorithms']==[] and result['status']=='complete'
 again=bridge.analyze(source)
 assert again['executed_algorithms']==again['rematched_algorithms']==[]
 records.append({'source':slug,'matching_s':current['semantic_audio']['values']['description_matching_wall_time_s'],
                 'bridge_wall_s':elapsed,'rematched':result['rematched_algorithms'],'audio_vectors_unchanged':True,
                 'other_stages_unchanged':True,'retry_executed':[],'retry_rematched':[]})
 print(json.dumps(records[-1]),flush=True)
path=bridge.ROOT/'output/semantic-description-banks/matching-acceptance.json'
path.write_text(json.dumps(records,indent=2)+'\n')
