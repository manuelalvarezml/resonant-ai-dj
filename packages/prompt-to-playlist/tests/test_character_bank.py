import copy
import json
from collections import Counter
import pytest
from prompt_to_playlist import semantic_audio as sa, web_bridge as bridge
from prompt_to_playlist import analysis_pipeline as pipeline


def audio():
    return {'encoder_id':'test-encoder','sampling_policy':sa.POLICY,'duration_s':30.,'sampled_seconds':30.,
            'segments':[{'start_s':x,'end_s':x+10,'embedding':[1.]+[0.]*511} for x in (0.,10.,20.)]}


@pytest.fixture
def configured(tmp_path,monkeypatch):
    monkeypatch.setattr(sa,'ROOT',tmp_path)
    monkeypatch.setattr(sa,'identity',lambda:'test-encoder')
    monkeypatch.setattr(sa,'load_model',lambda *a,**k:pytest.fail('Model loading forbidden during cached matching'))
    monkeypatch.setattr(sa.subprocess,'check_output',lambda *a,**k:pytest.fail('Audio decoding forbidden during cached matching'))
    def probes(texts,model=None,*,cached_only=False):
        assert cached_only
        return [[1.]+[0.]*511 for _ in texts]
    monkeypatch.setattr(sa,'text_embeddings',probes)
    return tmp_path


def test_bank_has_120_unique_concepts_and_expected_dimensions():
    assert len(sa.BANK)==len(sa.CONCEPTS)==120
    assert Counter(c['dimension'] for c in sa.CONCEPTS)==dict(emotion=30,groove=25,texture=25,intensity=20,space_arrangement=20)
    assert len(set(sa.BANK.values()))==120
    assert all(1<=len(text)<=500 for text in sa.BANK.values())


def test_matching_reuses_vectors_exactly_and_bank_change_only_invalidates_scores(configured,monkeypatch):
    original=audio();before=copy.deepcopy(original)
    result=sa.rematch_cached_audio('a'*64,original)
    assert original==before and result['values']['segments']==original['segments']
    assert result['values']['audio_embeddings_reused'] is True
    assert len(result['values']['descriptors'])==120
    assert all(v['mean']==v['min']==v['max']==1 for v in result['values']['descriptors'].values())
    assert sa.matching_compatible(result['values'])
    fingerprint=sa.audio_fingerprint(original)
    monkeypatch.setattr(sa,'BANK_DIGEST','new-wording')
    assert sa.audio_compatible(result['values']) and not sa.matching_compatible(result['values'])
    assert sa.audio_fingerprint(original)==fingerprint
    again=sa.rematch_cached_audio('a'*64)
    assert again['values']['segments']==original['segments'] and again['values']['descriptor_bank_digest']=='new-wording'


def test_worker_reuses_existing_audio_without_model_or_decoder(configured):
    source=configured/'song.mp3';source.write_bytes(b'no need to decode')
    from prompt_to_playlist.model_assets import sha256_file
    sa.save_audio_cache(sha256_file(source),audio())
    result=sa.analyze_semantic_audio(source)
    assert len(result['values']['descriptors'])==120 and result['values']['audio_embeddings_reused']


@pytest.mark.parametrize('change',['encoder','sampling','nan','length','interval','duration'])
def test_invalid_audio_cannot_be_reused(configured,change):
    value=audio()
    if change=='encoder':value['encoder_id']='old'
    if change=='sampling':value['sampling_policy']='old'
    if change=='nan':value['segments'][0]['embedding'][0]=float('nan')
    if change=='length':value['segments'][0]['embedding']=[]
    if change=='interval':value['segments'][0]['end_s']=12.
    if change=='duration':value['duration_s']=-1.
    assert not sa.audio_compatible(value)
    with pytest.raises(ValueError):sa.save_audio_cache('b'*64,value)


def test_bank_upgrade_in_bridge_is_similarity_only_then_noop(configured,monkeypatch):
    monkeypatch.setattr(bridge,'ROOT',configured);monkeypatch.setattr(bridge,'CACHE',configured/'features')
    monkeypatch.setattr(bridge,'STAGES',['semantic_audio'])
    monkeypatch.setattr(bridge,'sha256_file',lambda _: 'a'*64)
    monkeypatch.setattr(pipeline,'analyze_folder',lambda **k:pytest.fail('No analyzer should execute'))
    path=bridge.cache_path('a'*64);path.parent.mkdir()
    old={'policy':bridge.POLICY,'sha256':'a'*64,'algorithms':[{'algorithm_id':'semantic_audio','status':'warning',
        'values':{**audio(),'descriptor_bank_version':'musical-character-v1','descriptors':{'old':{'mean':.2}}}}]}
    path.write_text(json.dumps(old))
    first=bridge.analyze(configured/'song.mp3')
    assert first['status']=='complete' and first['executed_algorithms']==[] and first['rematched_algorithms']==['semantic_audio']
    assert len(first['algorithms'][0]['values']['descriptors'])==120
    assert first['algorithms'][0]['values']['segments']==old['algorithms'][0]['values']['segments']
    assert list((path.parent/'history'/('a'*64)).glob('*.json'))
    again=bridge.analyze(configured/'song.mp3')
    assert again['executed_algorithms']==again['rematched_algorithms']==[]


def test_missing_text_cache_fails_without_loading_model(tmp_path,monkeypatch):
    monkeypatch.setattr(sa,'ROOT',tmp_path);monkeypatch.setattr(sa,'identity',lambda:'test')
    monkeypatch.setattr(sa,'load_model',lambda:pytest.fail('Unexpected inference'))
    with pytest.raises(ValueError,match='text cache is missing'):sa.text_embeddings(['new description'],cached_only=True)
