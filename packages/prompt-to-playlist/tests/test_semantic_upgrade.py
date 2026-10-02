import copy
import math
import pytest
from pydantic import ValidationError
from prompt_to_playlist.models import (Catalog, CatalogTrack, Descriptor, NumericEvidence, Preference, PlaylistQuery, SemanticAudio, SemanticQuery, Vocabulary)
from prompt_to_playlist.search import search_tracks
from prompt_to_playlist.semantic_audio import segment_starts, normalized, covered_seconds
from prompt_to_playlist.feature_catalog import catalog_from_features
from prompt_to_playlist.web_bridge import compatible


def vector(a=1.,b=0.):return [a,b]+[0.]*510

def audio(v=None,encoder='test'):
    return SemanticAudio(encoder_id=encoder,sampling_policy='muq-3x10s-v1',segments=[{'start_s':0.,'end_s':10.,'embedding':v or vector()}])

def track(name,v=None,score=.5,bpm=120.):
    return CatalogTrack(track_id=name,title=name,semantic_audio=audio(v),preference_scores={'mood:happy':NumericEvidence(value=score,authority='benchmark_estimate',source='test')},bpm=NumericEvidence(value=bpm,authority='benchmark_estimate',source='test'))

def query(**kw):
    return PlaylistQuery(semantic=SemanticQuery(description='Airy relaxed music',encoder_id='test',embeddings=[vector()]),preferences=[Preference(tag='mood:happy')],**kw)

V=Vocabulary(vocabulary_id='test',descriptors=[Descriptor(id='mood:happy',description='Happy')])

def search(tracks,q=None):return search_tracks(Catalog(catalog_id='test',tracks=tracks),q or query(),V)


def test_hybrid_arithmetic_and_replay_are_exact_and_inputs_unchanged():
    tracks=[track('a'),track('b',vector(0.,1.))];before=copy.deepcopy(tracks)
    result=search(tracks)
    assert result.ranking_version=='hybrid-semantic-v1'
    assert [m.score for m in result.matches]==[.575,.425]
    assert tracks==before
    assert result==search(tracks)
    for match in result.matches:assert sum(c.contribution for c in match.score_contributions)==pytest.approx(match.score)
    assert result.matches[0].score_contributions[-1].score_kind=='relative_similarity'


def test_complete_eligible_coverage_is_required_not_just_top_k():
    tracks=[track('a'),track('b',vector(0.,1.)),track('c')];tracks[-1].semantic_audio=None
    result=search(tracks,query(limit=1))
    assert result.ranking_version=='maest-intent-v1'
    assert result.matches[0].score==.5
    assert any('coverage' in w for w in result.warnings)


def test_ineligible_missing_embedding_does_not_disable_semantics():
    tracks=[track('a'),track('b',vector(0.,1.)),track('c',bpm=70.)];tracks[-1].semantic_audio=None
    result=search(tracks,query(min_bpm=100.))
    assert result.ranking_version=='hybrid-semantic-v1'
    assert result.eligible_count==2


def test_semantics_cannot_override_bpm_or_exclusion():
    result=search([track('a',bpm=80.),track('b'),track('c')],query(min_bpm=100.,excluded_track_ids=['b']))
    assert [m.track.track_id for m in result.matches]==['c']
    assert result.ranking_version=='maest-intent-v1' # No comparative evidence.


def test_ties_and_candidate_count_do_not_manufacture_perfect_scores():
    result=search([track('b'),track('a')])
    assert [m.track.track_id for m in result.matches]==['a','b']
    assert all(m.score==.5 for m in result.matches)
    assert search([track('a')]).matches[0].score==.5


def test_wrong_encoder_and_failed_query_fall_back():
    a,b=track('a'),track('b');b.semantic_audio.encoder_id='different'
    assert search([a,b]).ranking_version=='maest-intent-v1'
    q=query();q.semantic=SemanticQuery(description='Airy music')
    assert search([a,track('c')],q).ranking_version=='maest-intent-v1'


def test_negative_description_is_a_contrast_not_complement_probability():
    q=query();q.semantic=SemanticQuery(description='Music',avoid=['Harsh music'],encoder_id='test',embeddings=[vector(),vector(0.,1.)])
    result=search([track('a',vector(.6,.8)),track('b',vector(.6,-.8))],q)
    assert result.matches[0].track.track_id=='b'
    assert result.matches[0].score_contributions[-1].evidence_value==pytest.approx(.8)
    assert result.eligible_count==2


def test_bpm_sort_still_precedes_hybrid_score():
    result=search([track('a',bpm=140.),track('b',vector(0.,1.),bpm=110.)],query(order='bpm_ascending'))
    assert [m.track.track_id for m in result.matches]==['b','a']


def test_semantic_only_queries_take_modern_path():
    q=query();q.preferences=[]
    result=search([track('a'),track('b',vector(0.,1.))],q)
    assert [m.score for m in result.matches]==[.75,.25]


@pytest.mark.parametrize('v',[[],[0.]*512,[float('nan')]+[0.]*511,[2.]+[0.]*511])
def test_corrupt_embeddings_cannot_enter_catalog(v):
    with pytest.raises(ValidationError):audio(v if v else [0.])


def test_segment_sampling_is_bounded_and_disclosed():
    assert segment_starts(5)==[0]
    assert len(segment_starts(600))==3
    assert all(0<=x<=590 for x in segment_starts(600))
    with pytest.raises(ValueError):segment_starts(float('nan'))
    with pytest.raises(ValueError):normalized([0.]*512)
    assert covered_seconds([{'start_s':s,'end_s':s+10} for s in segment_starts(20)])==20


def test_full_extended_vectors_are_soft_and_failed_outputs_stay_missing():
    feature={'algorithms':[{'algorithm_id':'semantic','status':'warning','values':{'heads':{'mood_theme':{'scores':{'romantic':.2,'christmas':.8}},'instruments':{'scores':{'piano':.6}}}}},{'algorithm_id':'semantic_audio','status':'failed','values':{}},{'algorithm_id':'energy','status':'warning','values':{'valence_mean_deferred':7.}}]}
    catalog,vocab=catalog_from_features([{'id':'one','title':'One','features':feature}])
    t=catalog.tracks[0]
    assert t.preference_scores['theme:romantic'].value==.2
    assert t.preference_scores['theme:christmas'].value==.8
    assert t.preference_scores['instrument:piano'].value==.6
    assert t.preference_scores['valence:positive'].value==.75
    assert t.semantic_audio is None and not t.tags and not t.complete_tag_axes
    assert search_tracks(catalog,PlaylistQuery(required_tags=['theme:romantic']),vocab).matches==[]


def test_legacy_complete_stage_needs_upgrade():
    assert not compatible({'algorithm_id':'semantic','status':'warning','implementation':'essentia-discogs-effnet-non-genre-v2','values':{'heads':{}}})
    assert compatible({'algorithm_id':'metadata','status':'passed'})


def test_new_head_cannot_favor_only_the_upgraded_subset():
    a,b=track('a'),track('b');a.preference_scores['theme:romantic']=NumericEvidence(value=.9,authority='benchmark_estimate',source='new-head')
    vocab=V.model_copy(deep=True);vocab.descriptors.append(Descriptor(id='theme:romantic',description='Romantic'))
    q=PlaylistQuery(preferences=[Preference(tag='theme:romantic'),Preference(tag='mood:happy')])
    result=search_tracks(Catalog(catalog_id='test',tracks=[a,b]),q,vocab)
    assert [m.score for m in result.matches]==[.5,.5]
    assert all(len(m.score_contributions)==1 for m in result.matches)
    assert any('incomplete eligible coverage' in w for w in result.warnings)
    assert all('theme:romantic' not in m.matched_tags for m in result.matches)


def test_legacy_replay_cannot_silently_discard_semantic_query():
    with pytest.raises(ValueError):search_tracks(Catalog(catalog_id='test',tracks=[track('a')]),query(),V,ranking_version='legacy')
