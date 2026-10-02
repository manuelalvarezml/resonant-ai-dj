"""Explicit three-request live planner smoke over two upgraded local cache records."""
import argparse,json,time
from pathlib import Path
from prompt_to_playlist.web_bridge import prompt,cache_path
from prompt_to_playlist.feature_catalog import catalog_from_features
from prompt_to_playlist.models import PlaylistRun
from prompt_to_playlist.search import search_tracks

SOURCES=[('smoke-ocean','Listen Over the Ocean','b23cf7fc573254db349ab179fdcc406c5da159186b04b1fe914ff913d83e4ae2'),('smoke-paradise','My Paradise - Edit','c4fa9722112e74661c9a4da26fa386d9a65564da8a3cef25048df25168f31bae')]
PROMPTS=['Un día en la playa, tranquilo y con una sensación de aire libre.','Música para una noche íntima y romántica en el sofá después de una cita.','Playlist for my birthday party at night to make the room dance.']

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--live',action='store_true',required=True);parser.add_argument('--output-name',default='planner-v1.6');parser.add_argument('--case',type=int,choices=range(1,len(PROMPTS)+1));args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]/'output/estimator-upgrade'/args.output_name;root.mkdir(parents=True,exist_ok=False);records=[]
    tracks=[{'id':id,'title':title,'artist':'','sha256':sha} for id,title,sha in SOURCES]
    items=[dict(t,features=json.loads(cache_path(t['sha256']).read_text())) for t in tracks]
    catalog,vocab=catalog_from_features(items)
    for index,text in enumerate(PROMPTS):
        if args.case is not None and index+1!=args.case:continue
        start=time.monotonic()
        try:
            run=PlaylistRun.model_validate(prompt({'prompt':text,'tracks':tracks}))
            (root/f'live-{index+1}.json').write_text(run.model_dump_json(by_alias=True,indent=2)+'\n')
            if run.result is None:raise RuntimeError('Planner did not produce a usable result: '+run.status)
            replay=search_tracks(catalog,run.result.query,vocab)
            exact=replay==run.result
            record={'prompt':text,'status':run.status,'wall_s':round(time.monotonic()-start,2),'ranking':run.result.ranking_version,'semantic_description':run.result.query.semantic.description if run.result.query.semantic else None,'exact_replay':exact,'matches':[{'id':m.track.track_id,'score':m.score,'semantic_contribution':next((c.model_dump() for c in m.score_contributions if c.group=='semantic'),None)} for m in run.result.matches]}
            records.append(record);print(json.dumps(record,ensure_ascii=False),flush=True)
            if not exact or run.result.ranking_version!='hybrid-semantic-v1':raise RuntimeError('Hybrid pipeline/replay check failed')
        except Exception as exc:
            records.append({'prompt':text,'failure_type':type(exc).__name__,'wall_s':round(time.monotonic()-start,2)})
            (root/'live-smoke-summary.json').write_text(json.dumps(records,indent=2,ensure_ascii=False)+'\n')
            raise
    (root/'live-smoke-summary.json').write_text(json.dumps(records,indent=2,ensure_ascii=False)+'\n')

if __name__=='__main__':main()
