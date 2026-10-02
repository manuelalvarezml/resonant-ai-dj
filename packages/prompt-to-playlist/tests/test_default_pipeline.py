from types import SimpleNamespace
from prompt_to_playlist import web_bridge as bridge, analysis_pipeline as pipeline
from prompt_to_playlist.analysis_models import AlgorithmResult


def test_stage_failure_is_partial_and_retry_only_executes_missing(tmp_path,monkeypatch):
    monkeypatch.setattr(bridge,'ROOT',tmp_path)
    monkeypatch.setattr(bridge,'CACHE',tmp_path/'cache')
    monkeypatch.setattr(bridge,'STAGES',['metadata','loudness'])
    monkeypatch.setattr(bridge,'sha256_file',lambda _: 'a'*64)
    calls=[]
    def run(**kwargs):
        stage=kwargs['algorithms'][0];calls.append(stage)
        if stage=='metadata' and calls.count(stage)==1:raise OSError('Decoder unavailable')
        result=AlgorithmResult(algorithm_id=stage,implementation='test',implementation_version='1',authority='benchmark_estimate',status='passed',values={})
        return SimpleNamespace(source_hashes_unchanged=True,source_inventory_unchanged=True,tracks=[SimpleNamespace(algorithms=[result])]),None
    monkeypatch.setattr(pipeline,'analyze_folder',run)
    first=bridge.analyze(tmp_path/'test.mp3')
    assert first['status']=='partial' and calls==['metadata','loudness']
    second=bridge.analyze(tmp_path/'test.mp3')
    assert second['status']=='complete' and calls==['metadata','loudness','metadata']
    third=bridge.analyze(tmp_path/'test.mp3')
    assert third['executed_algorithms']==[]


def test_default_lineup_preserves_both_moods_and_replaces_retired_stages():
    assert {'emotion_music2emo','semantic','vocal_musicnn','aggression_vggish','instrument_passt','key_sheetsage2'}<=set(bridge.STAGES)
    assert not {'key','energy','danceability_musicnn'} & set(bridge.STAGES)
    assert len(bridge.STAGES)==len(set(bridge.STAGES))==11
