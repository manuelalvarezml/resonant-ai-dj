"""Explicit, bounded live planner evaluation against saved feature JSON; no audio IO.

python -m prompt_to_playlist.evaluate_intent --live --limit 4 --out output/intent-eval.json
The maintained web listening lab is the source of the exported benchmark prompts.
"""
import argparse
import json
import time
from pathlib import Path
from .feature_catalog import catalog_from_features, POLICY
from .config import load_project_config, read_api_key
from .translators import OpenAITranslator
from .service import build_playlist
from .search import search_tracks
from .models import PlaylistQuery
from .benchmark import check_case
from .intent import INSTRUCTIONS, PROMPT_VERSION, COMPILER_VERSION

ROOT = Path(__file__).resolve().parents[2]


def saved_catalog(cache):
    items=[]
    for path in sorted(cache.glob('*.json')):
        if len(path.stem)!=64:
            continue
        feature=json.loads(path.read_text())
        if feature.get('policy')==POLICY and feature.get('genres'):
            items.append({'id':path.stem,'title':'Cached track '+path.stem[:12], 'sha256':path.stem,'features':feature})
    if not items:
        raise ValueError('No completed saved genre features')
    return catalog_from_features(items), [i['sha256'] for i in items]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live',action='store_true',help='Explicitly allow one model request per selected case')
    parser.add_argument('--limit',type=int,default=4)
    parser.add_argument('--ids',nargs='*')
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    if not args.live:parser.error('Live evaluation requires --live')
    if not 1<=args.limit<=20:parser.error('Use a limit from 1 to 20')
    suite=json.loads((ROOT/'docs/evaluations/iteration1-prompts.json').read_text())
    cases=[c for c in suite['cases'] if not args.ids or c['id'] in args.ids][:args.limit]
    (catalog,vocabulary),hashes=saved_catalog(ROOT/'output/web-features')
    cfg=load_project_config(ROOT/'playlist.toml')
    class AuditedTranslator(OpenAITranslator):
        proposal = None
        def _request(self, payload):
            from .translators import _extract_proposal
            from .models import IntentPlan
            response = super()._request(payload)
            self.proposal = _extract_proposal(response, IntentPlan)
            return response
    translator=AuditedTranslator(api_key=read_api_key(cfg.openai),model=cfg.openai.model,timeout_s=cfg.openai.timeout_s,intent_reasoning_effort=cfg.openai.intent_reasoning_effort)
    report={'version':suite['version'],'model':cfg.openai.model,'reasoning_effort':cfg.openai.intent_reasoning_effort,'prompt_version':PROMPT_VERSION,'compiler_version':COMPILER_VERSION,'instructions':INSTRUCTIONS,'catalog':catalog.model_dump(mode='json',by_alias=True),
            'vocabulary':vocabulary.model_dump(mode='json',by_alias=True),'source_hashes':hashes,
            'listening_acceptance':'pending human review','attempts':[],'genre_ablation':[]}
    for case in cases:
        translator.proposal=None
        start=time.monotonic();entry={'case':case,'listening_verdict':None}
        try:
            run=build_playlist(case['prompt'],catalog,vocabulary,translator)
            entry['run']=run.model_dump(mode='json',by_alias=True)
            entry['checks']=check_case(case['id'],run)
            print(case['id'],run.status,len(run.result.matches) if run.result else 0,flush=True)
        except (ValueError,OSError) as exc:
            entry['error']=str(exc)
            if translator.proposal:
                entry['rejected_plan']=translator.proposal.model_dump(mode='json')
                from .intent import compile_plan
                try:compile_plan(case['prompt'],translator.proposal,vocabulary,model=translator.model)
                except ValueError as diagnostic:entry['validation_diagnostic']=str(diagnostic)
            print(case['id'],'ERROR',str(exc),flush=True)
        entry['elapsed_s']=round(time.monotonic()-start,3);report['attempts'].append(entry)
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(report,indent=2,ensure_ascii=False))
    # Same catalog/query/eligibility; isolate probability ordering from interpretation.
    for genre in sorted({e.tag for t in catalog.tracks for e in t.tags}):
        q=PlaylistQuery(required_tags=[genre],limit=10)
        old=search_tracks(catalog,q,vocabulary,ranking_version='legacy')
        new=search_tracks(catalog,q,vocabulary,ranking_version='maest-intent-v1')
        if old.eligible_count>=2:
            report['genre_ablation'].append({'genre':genre,'eligible_count':new.eligible_count,
                'legacy':[m.track.track_id for m in old.matches],
                'probability':[{'id':m.track.track_id,'score':m.score} for m in new.matches]})
    args.out.write_text(json.dumps(report,indent=2,ensure_ascii=False))
    return int(any('error' in a or not a.get('checks',{}).get('passed') for a in report['attempts']))

if __name__=='__main__':raise SystemExit(main())
