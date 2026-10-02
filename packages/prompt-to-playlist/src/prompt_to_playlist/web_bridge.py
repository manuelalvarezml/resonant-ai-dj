"""Local player bridge; launched by the loopback Node service, never a public API."""
import argparse
import json
import re
import tempfile
from pathlib import Path
from .feature_catalog import POLICY, top_genres, catalog_from_features
from .model_assets import sha256_file, default_model_dir, ASSETS, required_assets

ROOT=Path(__file__).resolve().parents[2]
CACHE=ROOT/'output/web-features'
STAGES=['metadata','loudness','rhythm','semantic','genre_maest','semantic_audio','emotion_music2emo','vocal_musicnn','aggression_vggish','instrument_passt','key_sheetsage2']
RETIRED_STAGES=['key','energy']
FEATURE_VERSION='selected-estimators-v3-character120'
EXPERIMENTAL_STAGES=['emotion_music2emo','danceability_musicnn']
from .specialists import STAGES as SPECIALIST_STAGES
OPTIONAL_STAGES=[*EXPERIMENTAL_STAGES,*SPECIALIST_STAGES]

def compatible(a):
    if a.get('status') not in ('passed','warning'):return False
    if a['algorithm_id']=='semantic':
        return a.get('implementation') in ('essentia-discogs-effnet-expanded-v3','essentia-discogs-effnet-selected-v4') and len(a.get('values',{}).get('heads',{}).get('mood_theme',{}).get('scores',{}))==56 and len(a.get('values',{}).get('heads',{}).get('instruments',{}).get('scores',{}))==40
    if a['algorithm_id']=='semantic_audio':
        from .semantic_audio import matching_compatible
        return matching_compatible(a.get('values',{}))
    if a['algorithm_id'] in SPECIALIST_STAGES:
        from .specialists import identity, SpecialistEstimates, KeyEstimates
        try:
            v=a['values']
            if a['algorithm_id'] != 'key_sheetsage2':
                parsed=SpecialistEstimates.model_validate(v)
                if parsed.stage != a['algorithm_id']:return False
            else:KeyEstimates.model_validate_json(json.dumps(v,allow_nan=False))
            return v['model_id']==identity(a['algorithm_id'])
        except (KeyError,ValueError):return False
    if a['algorithm_id'] in EXPERIMENTAL_STAGES:
        from .supervised import identity, SampledEstimates
        try:
            value=SampledEstimates.model_validate(a['values'])
            kind='music2emo' if a['algorithm_id']=='emotion_music2emo' else 'musicnn-dance'
            return value.model_id==identity() and value.kind==kind
        except (KeyError,ValueError):return False
    return True


def cache_path(digest):
    if not re.fullmatch('[a-f0-9]{64}',digest):raise ValueError('Invalid source hash')
    return CACHE/(digest+'.json')


def analyze(source, *, supervised=False, specialists=False, reuse_existing=True):
    from .analysis_pipeline import analyze_folder, _atomic_json
    digest=sha256_file(source); saved={}; cached=cache_path(digest); old={}
    if reuse_existing and cached.exists():
        old=json.loads(cached.read_text())
        if old.get('policy')==POLICY:
            saved={a['algorithm_id']:a for a in old['algorithms'] if a['status']!='failed' or a['algorithm_id'] in OPTIONAL_STAGES}
    # Explicit trusted local completed runs only. No audio read during reuse.
    for name in (['playlistiq-diverse-37','playlistiq-house-10-full','maest-discogs519-diverse-37'] if reuse_existing else []):
        path=ROOT/'output'/name/'descriptor-run.json'
        if not path.exists():continue
        run=json.loads(path.read_text())
        if not run.get('source_hashes_unchanged') or not run.get('source_inventory_unchanged'):continue
        asset_hashes={a['asset_id']:a['sha256'] for a in run.get('model_assets',[])}
        for t in run['tracks']:
            if t['source']['sha256_before']==digest and t['source']['sha256_after']==digest:
                for a in t['algorithms']:
                    needed=required_assets([a['algorithm_id']])
                    if a['status']!='failed' and all(asset_hashes.get(k)==ASSETS[k].sha256 for k in needed):saved.setdefault(a['algorithm_id'],a)
    reused=[k for k,a in saved.items() if compatible(a)]
    requested=list(dict.fromkeys(STAGES+(EXPERIMENTAL_STAGES if supervised else [])))
    missing=[a for a in requested if a not in reused]
    upgrade_failures=list(old.get('upgrade_failures',[]))
    rematched=[]
    if missing:
        # One guarded subprocess per stage; a failed estimator cannot stop later stages.
        for group in [[a] for a in missing]:
            if not group:continue
            if group==['semantic_audio']:
                try:
                    from .semantic_audio import identity, rematch_cached_audio
                    identity()
                    result=rematch_cached_audio(digest,saved.get('semantic_audio',{}).get('values'))
                    if result is not None:
                        saved['semantic_audio']=result
                        rematched.append('semantic_audio')
                        upgrade_failures=[f for f in upgrade_failures if f['algorithm_id']!='semantic_audio']
                        print('  semantic_audio: refreshed 120 description scores; reused audio embeddings; no model inference',flush=True)
                        continue
                except (ValueError,OSError) as exc:
                    from .analysis_models import AlgorithmResult
                    failure=AlgorithmResult(algorithm_id='semantic_audio',implementation='muq-3x10s-v1',implementation_version='1.0.0',authority='benchmark_estimate',status='failed',error=str(exc)).model_dump(mode='json')
                    if 'semantic_audio' in saved:upgrade_failures.append({'algorithm_id':'semantic_audio','error':str(exc),'attempt':failure})
                    else:saved['semantic_audio']=failure
                    continue
            if group[0] in EXPERIMENTAL_STAGES:
                try:
                    from .supervised import verify_assets
                    verify_assets()
                except ValueError as exc:
                    from .analysis_models import AlgorithmResult
                    failure=AlgorithmResult(algorithm_id=group[0],implementation=group[0],implementation_version='1.0.0',authority='benchmark_estimate',status='failed',error=str(exc)).model_dump(mode='json')
                    if group[0] in saved:upgrade_failures.append({'algorithm_id':group[0],'error':str(exc),'attempt':failure})
                    else:saved[group[0]]=failure
                    continue
            if group[0] in SPECIALIST_STAGES:
                from .specialists import verify_assets as verify_specialists
                try:verify_specialists(group[0])
                except ValueError as exc:
                    from .analysis_models import AlgorithmResult
                    failure=AlgorithmResult(algorithm_id=group[0],implementation=group[0],implementation_version='1.0.0',authority='benchmark_estimate',status='failed',error=str(exc)).model_dump(mode='json')
                    if group[0] in saved:upgrade_failures.append({'algorithm_id':group[0],'error':str(exc),'attempt':failure})
                    else:saved[group[0]]=failure
                    continue
            out=CACHE/'checkpoints'/digest/(group[0] if group[0] in OPTIONAL_STAGES else 'maest' if group==['genre_maest'] else 'semantic-audio' if group==['semantic_audio'] else group[0])
            out.mkdir(parents=True,exist_ok=True)
            try:
                run,_=analyze_folder(folder=source.parent,source_name=source.name,output_dir=out/'run',max_tracks=1,resume=reuse_existing,
                     algorithms=group,model_dir=ROOT/'output/maest-models' if group==['genre_maest'] else ROOT/'output/estimator-models',
                     max_worker_rss_mb=8000 if group==['key_sheetsage2'] else 6000 if group==['semantic_audio'] else 4096,
                     worker_timeout_s=1800 if group==['key_sheetsage2'] else 600,
                     progress=lambda text:print(text,flush=True))
            except (ValueError,OSError) as exc:
                from .analysis_models import AlgorithmResult
                failure=AlgorithmResult(algorithm_id=group[0],implementation=group[0],implementation_version='1.0.0',authority='benchmark_estimate',status='failed',error=str(exc)).model_dump(mode='json')
                if group[0] in saved:upgrade_failures.append({'algorithm_id':group[0],'error':str(exc),'attempt':failure})
                else:saved[group[0]]=failure
                continue
            if not run.source_hashes_unchanged or not run.source_inventory_unchanged:raise ValueError('Source preservation failed')
            for a in run.tracks[0].algorithms:
                if a.status=='failed' and a.algorithm_id in saved:
                    upgrade_failures.append({'algorithm_id':a.algorithm_id,'error':a.error,'attempt':a.model_dump(mode='json')})
                else:
                    saved[a.algorithm_id]=a.model_dump(mode='json')
                    if a.status!='failed':upgrade_failures=[f for f in upgrade_failures if f['algorithm_id']!=a.algorithm_id]
    # Derive transparent tempo diagnostics from an already saved beat grid; no rerun.
    if saved.get('rhythm',{}).get('status') in ('passed','warning'):
        from .analysis_worker import rhythm_diagnostics
        values=saved['rhythm']['values']
        values.update(rhythm_diagnostics(values.get('beats_s',[]), values.get('bpm')))
    # Drop legacy genre results even when reusing the old semantic stage.
    if 'semantic' in saved:saved['semantic']['values'].get('heads',{}).pop('genre',None)
    for a in saved.values():
        if a['status']=='failed' and not a.get('error'):
            a['error']='No reliable beat grid was detected.' if a['algorithm_id']=='rhythm' else 'This feature could not be estimated.'
    maest=saved.get('genre_maest',{});genres=top_genres(maest['values']['scores']) if maest.get('status') in ('passed','warning') else []
    result={'feature_version':FEATURE_VERSION,'supervised_status':'complete' if all(a in saved and compatible(saved[a]) for a in EXPERIMENTAL_STAGES) else 'partial' if any(a in saved for a in EXPERIMENTAL_STAGES) else 'not_run','upgrade_failures':upgrade_failures,'reused_algorithms':reused,'executed_algorithms':[a for a in missing if a not in rematched],'rematched_algorithms':rematched,'policy':POLICY,'sha256':digest,'genres':genres,'algorithms':[saved[a] for a in dict.fromkeys(STAGES+OPTIONAL_STAGES+RETIRED_STAGES) if a in saved],
            'duration_s':saved.get('metadata',{}).get('values',{}).get('duration_s'),
            'status':'complete' if all(a in saved and compatible(saved[a]) for a in STAGES) else 'partial'}
    result['quality_status']='complete' if all(a in saved and compatible(saved[a]) for a in ['emotion_music2emo',*SPECIALIST_STAGES]) else 'partial' if any(a in saved for a in SPECIALIST_STAGES) else 'not_run'
    if sha256_file(source)!=digest:raise ValueError('Source changed')
    CACHE.mkdir(parents=True,exist_ok=True)
    if cached.exists() and missing:
        import time
        history=CACHE/'history'/digest;history.mkdir(parents=True,exist_ok=True)
        _atomic_json(history/(str(time.time_ns())+'.json'),json.loads(cached.read_text()))
    _atomic_json(cached,result)
    return result


def prompt(request):
    from .service import build_playlist
    from .config import load_project_config, read_api_key
    from .translators import OpenAITranslator
    from .models import ClarificationAnswer
    answers=[ClarificationAnswer.model_validate(a) for a in request.get("clarifications", [])]
    if len(answers)>3:raise ValueError("At most three clarification answers are supported")
    items=[]
    for t in request['tracks']:
        feature=json.loads(cache_path(t['sha256']).read_text())
        if feature['policy']!=POLICY or not feature['genres']:continue
        items.append(dict(t,features=feature))
    if not items:raise ValueError('Analyze tracks before creating a playlist.')
    catalog,vocabulary=catalog_from_features(items, estimator_profile=request.get('estimator_profile','reference'))
    cfg=load_project_config(ROOT/'playlist.toml')
    if cfg.provider!='openai' or not cfg.openai:raise ValueError('Configure OpenAI for PlaylistIQ.')
    from .semantic_audio import encode_query
    run=build_playlist(request['prompt'],catalog,vocabulary,OpenAITranslator(api_key=read_api_key(cfg.openai),model=cfg.openai.model,timeout_s=cfg.openai.timeout_s,intent_reasoning_effort=cfg.openai.intent_reasoning_effort),clarifications=answers,query_encoder=encode_query)
    result=run.model_dump(mode='json',by_alias=True)
    CACHE.mkdir(parents=True,exist_ok=True)
    from .analysis_pipeline import _atomic_json
    import uuid
    audit_id=str(uuid.uuid4())
    _atomic_json(CACHE/('playlist-'+audit_id+'.json'),result)
    _atomic_json(CACHE/('playlist-'+audit_id+'-inputs.json'),{'request':request,'catalog':catalog.model_dump(mode='json',by_alias=True),'vocabulary':vocabulary.model_dump(mode='json',by_alias=True)})
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['analyze','prompt']);p.add_argument('--input',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--supervised',action='store_true');p.add_argument('--specialists',action='store_true');a=p.parse_args()
    try:
        result=analyze(a.input,supervised=a.supervised,specialists=a.specialists) if a.action=='analyze' else prompt(json.loads(a.input.read_text()))
        a.out.write_text(json.dumps({'result':result},allow_nan=False));return 0
    except Exception as exc:
        import traceback
        CACHE.mkdir(parents=True,exist_ok=True)
        if a.action=='analyze':
            (CACHE/'last-analysis-error.log').write_text(traceback.format_exc())
        # Never forward provider/config contents or credentials to the browser.
        message=('macOS denied analysis runtime access. Restart the player using Open Resonant Player.command in Terminal.' if isinstance(exc,OSError) and not str(exc) else str(exc)) if isinstance(exc,(ValueError,OSError)) else 'Local analysis or PlaylistIQ failed. Check the local runtime and project configuration.'
        a.out.write_text(json.dumps({'error':message[:1200]}));return 1
if __name__=='__main__':raise SystemExit(main())
