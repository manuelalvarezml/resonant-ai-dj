import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import uuid

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from runtime.worker import Worker, ClaimedTranslator
from runtime.state import canonical, Objects, Jobs
from runtime.encoder import WarmEncoder


class MemoryJobs:
    def __init__(self, request, deadline=2000):
        self.row = {'status': 'queued', 'deadline': deadline, 'requestSha256': hashlib.sha256(canonical(request)).hexdigest()}
        self.started = 0
        self.finished = []
    def claim(self, job_id, attempt, release):
        if self.row['status'] not in {'queued', 'dispatching'}:
            return None
        self.row.update(status='running', attempt=attempt)
        return self.row.copy()
    def provider_started(self, job, attempt):
        assert self.row['status'] == 'running' and self.row['attempt'] == attempt
        assert not self.started
        self.started += 1
    def finish(self, job, attempt, status, key=None, sha=None):
        if self.row['status'] != 'running' or self.row['attempt'] != attempt:
            return False
        self.row['status'] = status
        self.finished.append((status, key, sha))
        return True


class MemoryObjects:
    def __init__(self, request):
        self.request = request
        self.writes = []
    def get_json(self, key, limit):
        return self.request
    def put_json(self, key, value):
        self.writes.append((key, value))
        return hashlib.sha256(canonical(value)).hexdigest()


@pytest.fixture
def harness(monkeypatch, tmp_path):
    request = {'prompt': 'warm house', 'tracks': [{'id': 'one', 'sha256': 'a' * 64}]}
    jobs, objects = MemoryJobs(request), MemoryObjects(request)
    catalog = SimpleNamespace(model_dump=lambda **_: {'tracks': []})
    snap = SimpleNamespace(select=lambda *_: (catalog, catalog), planner_settings=None, snapshot_sha256='b' * 64)
    calls = []
    translator = SimpleNamespace(translate_intent=lambda *args: calls.append(args))
    encoder = SimpleNamespace(query_encoder=lambda *_: None)
    run = SimpleNamespace(status='matched', model_dump=lambda **_: {'status': 'matched'})
    def build(prompt, cat, voc, provider, **kwargs):
        provider.translate_intent(prompt, voc, {}, [])
        return run
    monkeypatch.setattr('prompt_to_playlist.service.build_playlist', build)
    worker = Worker('release', snap, encoder, jobs, objects, lambda _: translator, scratch=tmp_path, now=lambda: 1000)
    event = {'jobId': str(uuid.uuid4()), 'releaseId': 'release'}
    context = SimpleNamespace(aws_request_id='attempt-one', get_remaining_time_in_millis=lambda: 300000)
    return worker, event, context, jobs, objects, calls


def test_duplicate_delivery_does_not_repeat_provider_or_write_result(harness):
    worker, event, context, jobs, objects, calls = harness
    assert worker.handle(event, context)['status'] == 'succeeded'
    assert worker.handle(event, context)['status'] == 'not_claimed'
    assert len(calls) == jobs.started == 1
    assert [k.split('/')[0] for k, _ in objects.writes] == ['audits', 'results']
    assert jobs.finished[0][1].startswith('results/')


def test_tampered_stored_request_fails_before_paid_work(harness):
    worker, event, context, jobs, objects, calls = harness
    objects.request = {'prompt': 'changed'}
    with pytest.raises(RuntimeError): worker.handle(event, context)
    assert jobs.row['status'] == 'failed'
    assert not calls and not objects.writes


def test_timeout_after_provider_is_unknown_and_never_retried(harness, monkeypatch):
    worker, event, context, jobs, objects, calls = harness
    def build(prompt, cat, voc, provider, **_):
        provider.translate_intent(prompt, voc, {}, [])
        raise TimeoutError('possible paid call')
    monkeypatch.setattr('prompt_to_playlist.service.build_playlist', build)
    with pytest.raises(RuntimeError): worker.handle(event, context)
    assert jobs.row['status'] == 'outcome_unknown'
    assert worker.handle(event, context)['status'] == 'not_claimed'
    assert len(calls) == 1


def test_low_time_budget_rejects_before_provider(harness):
    worker, event, context, jobs, objects, calls = harness
    context.get_remaining_time_in_millis = lambda: 10000
    with pytest.raises(RuntimeError): worker.handle(event, context)
    assert not calls and jobs.row['status'] == 'failed'


def test_result_write_failure_never_marks_success(harness):
    worker, event, context, jobs, objects, calls = harness
    objects.put_json = lambda *_: (_ for _ in ()).throw(OSError('S3 failure'))
    with pytest.raises(RuntimeError): worker.handle(event, context)
    assert jobs.row['status'] == 'outcome_unknown'
    assert jobs.finished[0][1] is None


def test_late_completion_cannot_reactivate_expired_job(harness):
    worker, event, context, jobs, objects, calls = harness
    original = objects.put_json
    def put(key, value):
        jobs.row['status'] = 'expired'
        return original(key, value)
    objects.put_json = put
    assert worker.handle(event, context)['status'] == 'expired'
    assert not jobs.finished


@pytest.mark.parametrize('event', [{}, {'jobId': '../x', 'releaseId': 'release'}, {'jobId': str(uuid.uuid4()), 'releaseId': 'wrong'}, {'jobId': str(uuid.uuid4()), 'releaseId': 'release', 'prompt': 'extra'}])
def test_untrusted_event_rejected(harness, event):
    worker, _, context, jobs, objects, calls = harness
    with pytest.raises(ValueError): worker.handle(event, context)
    assert not calls and jobs.row['status'] == 'queued'


def test_provider_wrapper_allows_exactly_one_logical_attempt():
    calls=[]
    provider=ClaimedTranslator(SimpleNamespace(translate_intent=lambda *_: calls.append('call')), lambda: calls.append('claim'))
    provider.translate_intent('text')
    with pytest.raises(RuntimeError): provider.translate_intent('text')
    assert calls == ['claim', 'call']


def test_warm_encoder_loads_once_and_preserves_original_vectors(monkeypatch, tmp_path):
    from prompt_to_playlist import semantic_audio
    monkeypatch.setattr(semantic_audio, 'identity', lambda *_: 'encoder')
    loads=[]
    # Fake tensors only; original text_embeddings, normalization and disk cache execute.
    tensor=SimpleNamespace(tolist=lambda: [float(i+1) for i in range(512)])
    model=lambda **_: [tensor]
    encoder=WarmEncoder(tmp_path, loader=lambda _: loads.append(1) or model)
    first=encoder.embeddings(['text'],tmp_path/'first')
    second=encoder.embeddings(['text'],tmp_path/'second')
    assert first == second
    assert len(loads) == encoder.loads == 1
    assert first['embeddings'] == semantic_audio.text_embeddings(['text'],model=model,model_dir=tmp_path,cache_dir=tmp_path/'baseline')


def test_durable_cache_avoids_loading_model(monkeypatch, tmp_path):
    from prompt_to_playlist import semantic_audio
    monkeypatch.setattr(semantic_audio, 'identity', lambda *_: 'encoder')
    cache={'text':'text','encoder':'encoder','embedding':[1.] * 512}
    objects=SimpleNamespace(optional_json=lambda *_:cache,put_json=lambda *_:None)
    encoder=WarmEncoder(tmp_path, loader=lambda _:pytest.fail('cache hit loaded model'))
    assert len(encoder.embeddings(['text'],tmp_path/'cache',objects)['embeddings'][0]) == 512
    assert encoder.loads == 0


def test_foreign_cache_rejected(monkeypatch,tmp_path):
    from prompt_to_playlist import semantic_audio
    monkeypatch.setattr(semantic_audio,'identity',lambda *_:'encoder')
    objects=SimpleNamespace(optional_json=lambda *_:{'text':'text','encoder':'foreign','embedding':[1.] * 512})
    with pytest.raises(ValueError):WarmEncoder(tmp_path).embeddings(['text'],tmp_path/'cache',objects)


def test_object_download_closes_stream_and_rejects_oversize():
    closed=[]
    body=SimpleNamespace(read=lambda n:b'{}',close=lambda:closed.append(True))
    client=SimpleNamespace(get_object=lambda **_:{'ContentLength':100,'Body':body})
    with pytest.raises(ValueError):Objects(client,'state').get_json('request',10)
    assert closed == [True]


def test_job_claim_and_completion_require_unexpired_matching_attempt():
    calls=[]
    table=SimpleNamespace(update_item=lambda **kw: calls.append(kw) or {'Attributes':{'status':'running'}})
    jobs=Jobs(table,now=lambda:1234)
    assert jobs.claim('id','attempt','release')['status']=='running'
    jobs.provider_started('id','attempt')
    assert jobs.finish('id','attempt','succeeded','results/id.json','a'*64)
    assert all('deadline > :now' in call['ConditionExpression'] for call in calls)
    assert all(call['ExpressionAttributeValues'][':now']==1234 for call in calls)
    assert 'releaseId = :release' in calls[0]['ConditionExpression']
    assert 'attribute_not_exists(providerStarted)' in calls[1]['ConditionExpression']
    assert 'attempt = :attempt' in calls[2]['ConditionExpression']


def test_lost_claim_is_benign_but_infrastructure_error_is_not():
    class Conditional(Exception):
        response={'Error':{'Code':'ConditionalCheckFailedException'}}
    table=SimpleNamespace(update_item=lambda **_:(_ for _ in ()).throw(Conditional()))
    jobs=Jobs(table)
    assert jobs.claim('id','attempt','release') is None
    assert not jobs.finish('id','attempt','succeeded')
    table.update_item=lambda **_:(_ for _ in ()).throw(OSError('database unavailable'))
    with pytest.raises(OSError):jobs.claim('id','attempt','release')


def test_browser_result_retains_evidence_without_exposing_vectors():
    from runtime.worker import browser_result
    full = {'query': {'embedding': [1, 2], 'description': 'warm'},
            'matches': [{'score': 0.7, 'source_path': '/private/source.mp3'}]}
    assert browser_result(full) == {'query': {'description': 'warm'}, 'matches': [{'score': 0.7}]}
    assert full['query']['embedding'] == [1, 2]
