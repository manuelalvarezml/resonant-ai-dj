"""Frozen real-cache comparisons; no audio inference or provider requests."""
import json
from pathlib import Path
from prompt_to_playlist.feature_catalog import catalog_from_features
from prompt_to_playlist.models import PlaylistQuery,Preference
from prompt_to_playlist.search import search_tracks
from prompt_to_playlist.intent import capabilities,plan_schema
from prompt_to_playlist.web_bridge import cache_path
from smoke_specialists import SOURCES,ROOT
from compare_supervised import SCENES

def main():
    items=[dict(id=slug,title=name,artist='',features=json.loads(cache_path(digest).read_text())) for name,slug,digest in SOURCES]
    cases=[*SCENES,('vocal',[('vocals:vocal','increase')]),('aggression',[('mood:aggressive','increase')]),('piano',[('instrument:piano','increase')])]
    out=[];frozen={}
    for profile in ['reference','quality']:
        cat,vocab=catalog_from_features(items,estimator_profile=profile)
        frozen[profile]=dict(catalog=cat.model_dump(mode='json'),vocabulary=vocab.model_dump(mode='json'),capabilities=capabilities(cat))
        queries=[(name,PlaylistQuery(preferences=[Preference(tag=tag,direction=d) for tag,d in tags])) for name,tags in cases]
        if profile=='quality':
            queries.extend((label,PlaylistQuery(preferences=[Preference(tag='openmic:'+label)])) for label in ['banjo','cymbals','mallet-percussion','mandolin','ukulele','piano'])
            schema=plan_schema(vocab,capabilities(cat));assert 'openmic:banjo' in schema['$defs']['AvailablePreferenceTag']['enum']
            assert not any('coverage is' in w for w in cat.warnings)
        for name,query in queries:
            result=search_tracks(cat,query,vocab);assert result==search_tracks(cat,query,vocab)
            assert all(abs(sum(c.contribution for c in m.score_contributions)-m.score)<1e-5 for m in result.matches)
            out.append(dict(profile=profile,case=name,result=result.model_dump(mode='json'),exact_replay=True))
    target=ROOT/'output/top-estimators/comparison';target.mkdir(parents=True,exist_ok=True)
    (target/'frozen-inputs.json').write_text(json.dumps(frozen,indent=2)+'\n')
    (target/'results.json').write_text(json.dumps(out,indent=2)+'\n')
    (target/'manifest.json').write_text(json.dumps(dict(exact_replays=len(out),provider_calls=0,audio_inference=False,listener_judgments=0),indent=2)+'\n')
    print('Exact fixed-query replays:',len(out))
if __name__=='__main__':main()
