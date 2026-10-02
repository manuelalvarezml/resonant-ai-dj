from prompt_to_playlist.feature_catalog import catalog_from_features, top_genres
from prompt_to_playlist.search import search_tracks
from prompt_to_playlist.models import PlaylistQuery

def fixture():
    scores={f'Electronic---Style {i}':.001 for i in range(519)}
    for i in range(7):scores[f'Electronic---Style {i}']=.08-i*.001
    return {'id':'track1','title':'Test','features':{'duration_s':100.,'algorithms':[
        {'algorithm_id':'genre_maest','status':'warning','values':{'scores':scores}},
        {'algorithm_id':'rhythm','status':'warning','values':{'bpm':130}},
        {'algorithm_id':'semantic','status':'warning','values':{'heads':{'mood_happy':{'scores':{'happy':.7}}}}}]}}

def test_top_six_no_threshold_no_human_overrides():
    item=fixture();item['features']['accepted_genres']=['genre:house']
    catalog,vocab=catalog_from_features([item]);assert len(catalog.tracks[0].tags)==6
    assert not any(t.tag=='genre:house' for t in catalog.tracks[0].tags)
    assert len(item['features']['algorithms'][0]['values']['scores'])==519
    assert search_tracks(catalog,PlaylistQuery(required_tags=['genre:style-5']),vocab).eligible_count==1
    assert search_tracks(catalog,PlaylistQuery(required_tags=['genre:house']),vocab).eligible_count==0

def test_scored_mood_preference_and_bpm_filter():
    catalog,vocab=catalog_from_features([fixture()])
    result=search_tracks(catalog,PlaylistQuery(preferred_tags=['mood:happy'],min_bpm=120.),vocab)
    assert result.matches[0].score==.7
    assert result.ranking_version=='maest-intent-v1'
    assert not search_tracks(catalog,PlaylistQuery(min_bpm=140.),vocab).matches
    # Score presence does not silently satisfy a hard categorical requirement.
    assert not search_tracks(catalog,PlaylistQuery(required_tags=['mood:happy']),vocab).matches

def test_failed_maest_does_not_fall_back_to_old_genre_or_review():
    item=fixture();item['features']['algorithms'][0]['status']='failed'
    item['features']['accepted_genres']=['genre:house']
    catalog,vocab=catalog_from_features([item]);assert not catalog.tracks[0].tags

def test_style_alias_cannot_become_a_vocal_tag():
    item=fixture();scores=item['features']['algorithms'][0]['values']['scores']
    scores['Electronic---Instrumental']=scores.pop('Electronic---Style 0')
    catalog,_=catalog_from_features([item]);assert any(t.tag=='genre:instrumental' for t in catalog.tracks[0].tags)
    assert not any(t.tag=='vocals:instrumental' for t in catalog.tracks[0].tags)
