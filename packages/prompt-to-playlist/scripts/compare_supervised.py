"""Read-only comparisons and blinded rating sheets; no inference/provider calls."""
import hashlib
import json
import random
from pathlib import Path
from prompt_to_playlist.feature_catalog import catalog_from_features
from prompt_to_playlist.models import PlaylistRun, PlaylistQuery, Preference
from prompt_to_playlist.search import search_tracks
from prompt_to_playlist.supervised import PROFILES
from prompt_to_playlist.web_bridge import cache_path
from smoke_playlist_semantics import SOURCES

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/supervised-estimators/comparison-v1'
# Fixed structured probes are diagnostic hypotheses, not newly generated plans or truth.
SCENES=[
 ('calm-beach',[('theme:calm','increase'),('energy:high','decrease')]),
 ('energetic-beach',[('theme:summer','increase'),('energy:high','increase'),('danceability:danceable','increase')]),
 ('intimate-evening',[('theme:romantic','increase'),('theme:soft','increase'),('energy:high','decrease')]),
 ('picnic',[('theme:relaxing','increase'),('valence:positive','increase')]),
 ('heartbreak',[('theme:sad','increase'),('valence:positive','decrease')]),
 ('celebration',[('theme:happy','increase'),('theme:party','increase')]),
 ('dance-party',[('danceability:danceable','increase'),('energy:high','increase')]),
]


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    items=[{'id':id,'title':title,'artist':'','features':json.loads(cache_path(sha).read_text())} for id,title,sha in SOURCES]
    comparisons=[];catalogs={}
    for profile in PROFILES:
        cat,vocab=catalog_from_features(items,estimator_profile=profile)
        catalogs[profile]={'catalog':cat.model_dump(mode='json',by_alias=True),'vocabulary':vocab.model_dump(mode='json',by_alias=True)}
        queries=[(name,PlaylistQuery(preferences=[Preference(tag=tag,direction=direction) for tag,direction in prefs]),'fixed structured diagnostic') for name,prefs in SCENES]
        for i in range(1,4):
            path=ROOT/'output/estimator-upgrade'/('planner-v1.6/live-2.json' if i==2 else f'planner-v1.5/live-{i}.json')
            run=PlaylistRun.model_validate_json(path.read_text())
            queries.append((f'recorded-plan-{i}',run.result.query,str(path.relative_to(ROOT))))
        for name,query,origin in queries:
            result=search_tracks(cat,query,vocab)
            replay=search_tracks(cat,query,vocab)
            assert result==replay
            assert all(abs(sum(c.contribution for c in m.score_contributions)-m.score)<1e-5 for m in result.matches)
            comparisons.append({'profile':profile,'case':name,'query_origin':origin,'exact_replay':True,'result':result.model_dump(mode='json',by_alias=True)})
    (OUT/'frozen-inputs.json').write_text(json.dumps(catalogs,indent=2)+'\n')
    (OUT/'results.json').write_text(json.dumps(comparisons,indent=2)+'\n')
    key=[]
    for reviewer in ('Manuel','Grecia'):
        rng=random.Random('supervised-development-v1-'+reviewer)
        rows=[]
        for scene,_ in SCENES:
            candidates=[r for r in comparisons if r['case']==scene];rng.shuffle(candidates)
            for n,r in enumerate(candidates):
                code=f'{scene}-{n+1}'
                key.append({'reviewer':reviewer,'code':code,'profile':r['profile']})
                rows.append({'code':code,'scene':scene,'ranked_track_ids':[m['track']['track_id'] for m in r['result']['matches']], 'scene_fit_1_to_5':None,'preferred_over_codes':[],'notes':'','track_ratings':[{'track_id':m['track']['track_id'],'perceived_valence_1_to_9':None,'perceived_arousal_1_to_9':None,'movement_1_to_5':None,'personal_induced_emotion':'','scene_fit_1_to_5':None} for m in r['result']['matches']]})
        (OUT/f'blind-development-{reviewer}.json').write_text(json.dumps({'reviewer':reviewer,'split':'development-only; two smoke tracks, no superiority claim','judgments':rows},indent=2)+'\n')
    for reviewer in ('Manuel','Grecia'):
        sheet=json.loads((OUT/f'blind-development-{reviewer}.json').read_text())
        names={'smoke-ocean':'Listen Over the Ocean','smoke-paradise':'My Paradise - Edit'}
        lines=[f'# {reviewer}: blinded development listening sheet', '', 'Two known development tracks only. Do not read the organizer key or estimator scores before rating. Scene fit: 1 poor to 5 excellent; ties and unsure are valid. No ratings have been entered.', '', '| Scene / code | Listen in this order | Scene fit 1–5 | Prefer over / tie | Notes |', '|---|---|---|---|---|']
        for row in sheet['judgments']:
            order=' → '.join(names[i] for i in row['ranked_track_ids'])
            lines.append(f"| {row['code']} | {order} | | | |")
        lines += ['', '## Separate track judgments', '', '| Track | Perceived valence 1–9 | Perceived arousal 1–9 | Movement 1–5 | Personal induced feeling / uncertainty |', '|---|---|---|---|---|', '| Listen Over the Ocean | | | | |', '| My Paradise - Edit | | | | |', '', 'Keep each scene judgment separate; low arousal alone does not prove intimate or beach suitability. Save completed ratings to a new file before regenerating templates.']
        (OUT/f'blind-development-{reviewer}.md').write_text('\n'.join(lines)+'\n')
    (OUT/'organizer-key.json').write_text(json.dumps(key,indent=2)+'\n')
    measurements=[]
    for slug in ('ocean','paradise'):
        record={'source':slug,'stages':{}}
        for stage in ('emotion_music2emo','danceability_musicnn','estimator_reference'):
            d=json.loads((ROOT/f'output/supervised-estimators/matched-v2/{slug}/{stage}/descriptor-run.json').read_text());a=d['tracks'][0]['algorithms'][0]
            record['stages'][stage]={'status':a['status'],'wall_s':a['metrics']['wall_time_s'],'peak_process_tree_rss_mib':a['metrics']['peak_rss_mb'],'source_hashes_unchanged':d['source_hashes_unchanged'],'source_inventory_unchanged':d['source_inventory_unchanged'],'values':a['values']}
        record['historical_full_track_reference']={a['algorithm_id']:a['values'] for a in items[0 if slug=='ocean' else 1]['features']['algorithms'] if a['algorithm_id'] in ('semantic','energy')}
        measurements.append(record)
    (OUT/'measurements.json').write_text(json.dumps(measurements,indent=2)+'\n')
    files=[p for p in OUT.iterdir() if p.name!='manifest.json']
    (OUT/'manifest.json').write_text(json.dumps({'version':'supervised-comparison-v1','audio_inference':False,'provider_calls':0,'cases_per_profile':10,'profiles':list(PROFILES),'exact_replays':len(comparisons),'judgments_entered':0,'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}},indent=2)+'\n')
    print(json.dumps({'comparisons':len(comparisons),'exact_replays':len(comparisons),'judgments':0,'output':str(OUT)}))

if __name__=='__main__':main()
