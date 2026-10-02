import copy
import pytest
from pydantic import ValidationError
from prompt_to_playlist import specialists as s, web_bridge as bridge
from prompt_to_playlist.feature_catalog import catalog_from_features
from prompt_to_playlist.analysis_pipeline import _checkpoint_digest
from prompt_to_playlist.models import PlaylistQuery, Preference
from prompt_to_playlist.search import search_tracks
from test_supervised import item


def estimates(stage,score=.7):
    return s.aggregate(stage,100.,[dict(start_s=0.,end_s=30.,scores={k:score for k in s.LABELS[stage]})])

def source(id='one',score=.7):
    t=item(id)
    for stage in s.LABELS:t['features']['algorithms'].append(dict(algorithm_id=stage,status='warning',values=estimates(stage,score)))
    return t

@pytest.mark.parametrize('corrupt',['nan','mean','labels','coverage','overlap','stage'])
def test_specialist_contract_rejects_invalid_evidence(corrupt):
    v=estimates('instrument_passt')
    if corrupt=='nan':v['scores']['piano']=float('nan')
    if corrupt=='mean':v['scores']['piano']=.1
    if corrupt=='labels':v['labels'].reverse()
    if corrupt=='coverage':v['coverage_fraction']=1.
    if corrupt=='overlap':v['segments']*=2
    if corrupt=='stage':v['stage']='vocal_musicnn'
    with pytest.raises(ValidationError):s.SpecialistEstimates.model_validate(v)

def test_quality_profile_changes_selected_targets_preserves_others_and_input():
    a,b=source(),source('two',.3);before=copy.deepcopy([a,b])
    ref,_=catalog_from_features([a,b]);cat,vocab=catalog_from_features([a,b],estimator_profile='quality')
    assert [a,b]==before
    assert cat.tracks[0].tags==ref.tracks[0].tags
    for tag in ['mood:happy','danceability:danceable']:
        assert cat.tracks[0].preference_scores[tag]==ref.tracks[0].preference_scores[tag]
    assert cat.tracks[0].preference_scores['vocals:vocal'].source.startswith('vocal_musicnn-v1:')
    assert cat.tracks[0].preference_scores['mood:aggressive'].value==.7
    assert cat.tracks[0].preference_scores['openmic:banjo'].value==.7
    assert 'openmic:acousticguitar' not in cat.tracks[0].preference_scores
    result=search_tracks(cat,PlaylistQuery(preferences=[Preference(tag='openmic:banjo')]),vocab)
    assert [m.score for m in result.matches]==[.7,.3]
    assert not search_tracks(cat,PlaylistQuery(required_tags=['openmic:banjo']),vocab).matches

@pytest.mark.parametrize('failure',['missing','failed','stale','malformed'])
def test_each_axis_falls_back_for_all_candidates_independently(failure):
    a,b=source(),source('two');target=b['features']['algorithms'][-3]
    assert target['algorithm_id']=='vocal_musicnn'
    if failure=='missing':b['features']['algorithms'].remove(target)
    if failure=='failed':target['status']='failed'
    if failure=='stale':target['values']['model_id']='old'
    if failure=='malformed':target['values']['scores']={}
    ref,_=catalog_from_features([a,b]);cat,_=catalog_from_features([a,b],estimator_profile='quality')
    for i in range(2):
        assert cat.tracks[i].preference_scores.get('vocals:vocal')==ref.tracks[i].preference_scores.get('vocals:vocal')
        assert cat.tracks[i].preference_scores['mood:aggressive'].source.startswith('aggression_vggish-v1:')
    assert any('vocal_musicnn coverage is 1/2' in w for w in cat.warnings)

def test_unavailable_instruments_never_create_partial_new_evidence():
    a,b=source(),item('two')
    cat,_=catalog_from_features([a,b],estimator_profile='quality')
    assert all(not any(k.startswith('openmic:') for k in t.preference_scores) for t in cat.tracks)

def test_stage_identity_invalidates_only_optional_checkpoint(monkeypatch):
    old=_checkpoint_digest('vocal_musicnn','a'*64,4,{},{});ref=_checkpoint_digest('key','a'*64,4,{},{})
    monkeypatch.setattr(s,'identity',lambda stage:'changed')
    assert old!=_checkpoint_digest('vocal_musicnn','a'*64,4,{},{})
    assert ref==_checkpoint_digest('key','a'*64,4,{},{})

def test_assets_verified_per_stage_without_network(tmp_path,monkeypatch):
    monkeypatch.setattr(s,'model_dir',lambda:tmp_path)
    with pytest.raises(ValueError,match='Missing or changed'):s.verify_assets('instrument_passt')

def test_bridge_rejects_stale_or_wrong_stage():
    v=dict(algorithm_id='vocal_musicnn',status='warning',values=estimates('vocal_musicnn'))
    assert bridge.compatible(v)
    v['values']['model_id']='stale';assert not bridge.compatible(v)
    v['values']=estimates('aggression_vggish');assert not bridge.compatible(v)

def test_key_time_aggregation_and_camelot_do_not_invent_confidence():
    value=s.key_summary([(0.,20.,'C:major'),(20.,90.,'C:minor')],100.,'model')
    assert value['standard_key']=='C minor' and value['camelot']=='5A'
    assert 'strength' not in value
    assert s.key_summary([(0.,30.,'Db:major')],30.,'model')['camelot']=='3B'

@pytest.mark.parametrize('rows',[[(0,10,'C:minor'),(5,20,'D:major')],[(0,float('inf'),'C:minor')],[(0,10,'wrong')],[]])
def test_key_invalid_timing_or_labels_fail_closed(rows):
    with pytest.raises((ValueError,ValidationError)):s.key_summary(rows,30.,'model')

def test_serialized_key_intervals_remain_compatible_after_json_roundtrip():
    import json
    value=s.key_summary([(0.,30.,'C:minor')],30.,s.identity('key_sheetsage2'))
    a=json.loads(json.dumps(dict(algorithm_id='key_sheetsage2',status='warning',values=value)))
    assert bridge.compatible(a)
    a['values']['key_intervals'][0][1]=float('nan')
    assert not bridge.compatible(a)
