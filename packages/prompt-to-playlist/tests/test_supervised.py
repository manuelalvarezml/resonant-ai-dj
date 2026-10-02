import copy
import json
import pytest
from pydantic import ValidationError
from prompt_to_playlist import supervised as s
from prompt_to_playlist.feature_catalog import catalog_from_features
from prompt_to_playlist.models import PlaylistQuery, Preference
from prompt_to_playlist.search import search_tracks
from prompt_to_playlist.analysis_pipeline import _checkpoint_digest, _load_checkpoint
from prompt_to_playlist import web_bridge as bridge
from test_feature_catalog import fixture


def estimate(kind='music2emo',score=.4,valence=7.,arousal=5.):
    labels=s.MOOD_LABELS if kind=='music2emo' else ['danceable','not_danceable']
    seg={'start_s':0.,'end_s':30.,'scores':{l:score for l in labels}}
    if kind=='music2emo':seg.update(valence=valence,arousal=arousal)
    return s.aggregate(kind,100.,[seg])


def item(id='one',kind='music2emo',**kw):
    t=fixture();t['id']=id
    t['features']['algorithms'].append({'algorithm_id':'emotion_music2emo' if kind=='music2emo' else 'danceability_musicnn','status':'warning','values':estimate(kind,**kw)})
    t['features']['algorithms'].append({'algorithm_id':'energy','status':'warning','values':{'valence_mean':3.,'arousal_mean':4.}})
    t['features']['algorithms'][2]['values']['heads']['mood_theme']={'scores':{'happy':.2}}
    t['features']['algorithms'][2]['values']['heads']['danceability']={'scores':{'danceable':.1}}
    return t


@pytest.mark.parametrize('duration',[1.,5.,29.,30.,31.,59.,60.,89.,90.,300.,10000.])
def test_sampling_bounded_nonoverlapping_and_covered(duration):
    w=s.windows(duration)
    assert 1<=len(w)<=3
    assert sum(b-a for a,b in w)<=min(duration,90.)
    assert all(0<=a<b<=duration and b-a<=30.000001 for a,b in w)
    assert all(w[i][1]<=w[i+1][0] for i in range(len(w)-1))


@pytest.mark.parametrize('duration',[0.,.99,float('nan'),float('inf'),-1.])
def test_invalid_audio_duration_rejected(duration):
    with pytest.raises(ValueError):s.windows(duration)


@pytest.mark.parametrize('corruption',['nan','inf','label-order','missing-label','coverage','overlap','mean','units'])
def test_bad_estimates_rejected(corruption):
    v=estimate()
    if corruption=='nan':v['segments'][0]['valence']=float('nan')
    if corruption=='inf':v['scores']['happy']=float('inf')
    if corruption=='label-order':v['labels']=list(reversed(v['labels']))
    if corruption=='missing-label':v['segments'][0]['scores'].pop('happy')
    if corruption=='coverage':v['coverage_fraction']=1.
    if corruption=='overlap':v['segments']*=2
    if corruption=='mean':v['valence_mean']=2.
    if corruption=='units':v['regression_units']='probability'
    with pytest.raises(ValidationError):s.SampledEstimates.model_validate(v)


def test_regressions_not_clipped_and_invalid_scale_falls_back_for_everyone():
    a,b=item(),item('two',valence=10.)
    assert s.SampledEstimates.model_validate(b['features']['algorithms'][-2]['values']).valence_mean==10.
    ref,_=catalog_from_features([a,b]);cat,_=catalog_from_features([a,b],estimator_profile='music2emo')
    assert [t.preference_scores['valence:positive'] for t in cat.tracks]==[t.preference_scores['valence:positive'] for t in ref.tracks]
    assert all(t.preference_scores['energy:high'].value==.5 for t in cat.tracks)
    assert any('outside 1–9' in w for w in cat.warnings)


def test_uniform_selection_preserves_reference_genres_binary_moods_and_hard_constraints():
    a,b=item(score=.9),item('two',score=.3);before=copy.deepcopy([a,b])
    ref,_=catalog_from_features([a,b]);cat,vocab=catalog_from_features([a,b],estimator_profile='music2emo')
    assert [a,b]==before
    assert cat.tracks[0].tags==ref.tracks[0].tags
    assert cat.tracks[0].preference_scores['mood:happy']==ref.tracks[0].preference_scores['mood:happy']
    q=PlaylistQuery(preferences=[Preference(tag='theme:happy')])
    result=search_tracks(cat,q,vocab)
    assert [m.score for m in result.matches]==[.9,.3]
    assert result==search_tracks(cat,q,vocab)
    assert all(sum(c.contribution for c in m.score_contributions)==pytest.approx(m.score) for m in result.matches)
    assert not search_tracks(cat,q.model_copy(update={'min_bpm':140.}),vocab).matches
    assert not search_tracks(cat,q.model_copy(update={'required_tags':['theme:happy']}),vocab).matches
    assert [m.track.track_id for m in search_tracks(cat,q.model_copy(update={'excluded_track_ids':['one']}),vocab).matches]==['two']


@pytest.mark.parametrize('failure',['missing','failed','wrong-model','wrong-kind','malformed'])
def test_partial_challenger_coverage_never_rewards_upgraded_subset(failure):
    a,b=item(),item('two');e=b['features']['algorithms'][-2]
    if failure=='missing':b['features']['algorithms'].remove(e)
    if failure=='failed':e['status']='failed'
    if failure=='wrong-model':e['values']['model_id']='different'
    if failure=='wrong-kind':e['values']=estimate('musicnn-dance')
    if failure=='malformed':e['values']['scores']={}
    ref,_=catalog_from_features([a,b]);cat,_=catalog_from_features([a,b],estimator_profile='music2emo')
    assert [t.preference_scores for t in cat.tracks]==[t.preference_scores for t in ref.tracks]
    assert any('reference retained for everyone' in w for w in cat.warnings)


def test_default_reference_and_independent_dance_selection():
    a=item(kind='musicnn-dance',score=.8)
    base,_=catalog_from_features([a]);dance,_=catalog_from_features([a],estimator_profile='musicnn-dance')
    assert base.tracks[0].preference_scores['danceability:danceable'].value==.1
    assert dance.tracks[0].preference_scores['danceability:danceable'].value==.8
    with pytest.raises(ValueError):catalog_from_features([a],estimator_profile='unknown')


def test_cache_identity_changes_only_experimental_stages(monkeypatch):
    def digest(stage):return _checkpoint_digest(stage,'a'*64,4,{'torch':'test'},{})
    old=[digest(x) for x in ('metadata','semantic','emotion_music2emo')]
    monkeypatch.setattr(s,'identity',lambda:'different')
    new=[digest(x) for x in ('metadata','semantic','emotion_music2emo')]
    assert old[:2]==new[:2] and old[2]!=new[2]


def test_asset_corruption_is_detected_without_download(tmp_path,monkeypatch):
    monkeypatch.setattr(s,'model_dir',lambda:tmp_path)
    monkeypatch.setattr(s,'manifest',lambda:{'assets':[{'path':'test','size_bytes':1,'sha256':'a'*64}]})
    (tmp_path/'test').write_bytes(b'x')
    with pytest.raises(ValueError,match='missing or changed'):s.verify_assets()


def fake_cache(tmp_path,monkeypatch,extra):
    monkeypatch.setattr(bridge,'ROOT',tmp_path);monkeypatch.setattr(bridge,'CACHE',tmp_path/'cache')
    monkeypatch.setattr(bridge,'sha256_file',lambda _: 'a'*64)
    monkeypatch.setattr(bridge,'STAGES',['metadata'])
    path=bridge.cache_path('a'*64);path.parent.mkdir()
    old={'policy':bridge.POLICY,'algorithms':[{'algorithm_id':'metadata','status':'passed','values':{}}]+extra,'upgrade_failures':[]}
    path.write_text(json.dumps(old));return old


def test_base_retry_preserves_failed_optional_stage(tmp_path,monkeypatch):
    failure={'algorithm_id':'emotion_music2emo','status':'failed','values':{},'error':'Setup missing'}
    fake_cache(tmp_path,monkeypatch,[failure])
    result=bridge.analyze(tmp_path/'source')
    assert result['algorithms'][-1]==failure
    assert result['status']=='complete' and result['supervised_status']=='partial'
    assert result['executed_algorithms']==[]


def test_missing_assets_preserves_old_success_and_records_stage_failure(tmp_path,monkeypatch):
    old={'algorithm_id':'emotion_music2emo','status':'warning','values':estimate()}
    old['values']['model_id']='older-version'
    fake_cache(tmp_path,monkeypatch,[old])
    monkeypatch.setattr(s,'verify_assets',lambda:(_ for _ in ()).throw(ValueError('Missing assets')))
    result=bridge.analyze(tmp_path/'source',supervised=True)
    assert next(a for a in result['algorithms'] if a['algorithm_id']=='emotion_music2emo')==old
    assert result['upgrade_failures'][0]['error']=='Missing assets'
    again=bridge.analyze(tmp_path/'source')
    assert again['upgrade_failures']==result['upgrade_failures']


def test_successful_optional_retry_is_a_noop(tmp_path,monkeypatch):
    extras=[{'algorithm_id':stage,'status':'warning','values':estimate(kind)} for stage,kind in [('emotion_music2emo','music2emo'),('danceability_musicnn','musicnn-dance')]]
    fake_cache(tmp_path,monkeypatch,extras)
    result=bridge.analyze(tmp_path/'source',supervised=True)
    assert result['executed_algorithms']==[] and result['supervised_status']=='complete'
    assert result['algorithms'][1:]==extras


def test_weighted_aggregation_and_capabilities_use_the_selected_evidence():
    from prompt_to_playlist.intent import capabilities, plan_schema
    from prompt_to_playlist.models import Vocabulary
    low={'start_s':0.,'end_s':10.,'scores':{l:0. for l in s.MOOD_LABELS},'valence':1.,'arousal':3.}
    high={'start_s':20.,'end_s':40.,'scores':{l:.9 for l in s.MOOD_LABELS},'valence':7.,'arousal':6.}
    value=s.aggregate('music2emo',100.,[low,high])
    assert value['scores']['happy']==pytest.approx(.6) and value['valence_mean']==5. and value['arousal_mean']==5.
    a=item();a['features']['algorithms'][-2]['values']=value
    cat,vocab=catalog_from_features([a],estimator_profile='music2emo')
    counts=capabilities(cat)['descriptor_track_counts']
    assert counts['theme:romantic']==1 and counts['valence:positive']==1
    assert 'lyrics:romantic' not in counts and not cat.tracks[0].complete_tag_axes


def test_failed_or_changed_checkpoint_never_reuses(tmp_path):
    path=tmp_path/'checkpoint.json'
    result={'algorithm_id':'emotion_music2emo','implementation':'test','implementation_version':'1','authority':'benchmark_estimate','status':'failed','error':'failed'}
    path.write_text(json.dumps({'checkpoint_digest':'expected','result':result}))
    assert _load_checkpoint(path,'expected') is None
    result['status']='warning';result['error']=None
    path.write_text(json.dumps({'checkpoint_digest':'expected','result':result}))
    assert _load_checkpoint(path,'changed') is None
    assert _load_checkpoint(path,'expected') is not None
