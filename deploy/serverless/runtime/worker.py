"""Private Event-invoked Lambda. No audio access, analysis, or public HTTP surface."""
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import time

from .state import Jobs, Objects, canonical
from .encoder import WarmEncoder

UUID = re.compile(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}')
_RUNTIME = None


class ClaimedTranslator:
    def __init__(self, translator, before):
        self.translator, self.before = translator, before
        self.started = False

    def translate_intent(self, *args):
        if self.started:
            raise RuntimeError('Only one provider attempt is permitted')
        self.before()
        self.started = True
        return self.translator.translate_intent(*args)


def browser_result(value):
    """Preserve scores/explanations, keep raw vectors and source paths private."""
    if isinstance(value, list):
        return [browser_result(item) for item in value]
    if isinstance(value, dict):
        return {key: browser_result(item) for key, item in value.items()
                if key not in {'embedding', 'embeddings', 'audio_embedding',
                               'audio_embeddings', 'source_path', 'absolute_path'}}
    return value


class Worker:
    def __init__(self, release_id, snapshot, encoder, jobs, objects, translator_factory,
                 scratch='/tmp', now=time.time):
        self.release_id, self.snapshot, self.encoder = release_id, snapshot, encoder
        self.jobs, self.objects, self.translator_factory = jobs, objects, translator_factory
        self.scratch, self.now = scratch, now

    def handle(self, event, context):
        if not isinstance(event, dict) or set(event) != {'jobId', 'releaseId'}:
            raise ValueError('Invalid worker event')
        job_id = event['jobId']
        if not isinstance(job_id, str) or not UUID.fullmatch(job_id) or event['releaseId'] != self.release_id:
            raise ValueError('Invalid worker identity')
        attempt = context.aws_request_id
        job = self.jobs.claim(job_id, attempt, self.release_id)
        if job is None:
            return {'jobId': job_id, 'status': 'not_claimed'}
        provider = None
        try:
            if context.get_remaining_time_in_millis() < 45000:
                raise TimeoutError('Insufficient remaining time')
            request = self.objects.get_json('requests/' + job_id + '.json', 65536)
            if hashlib.sha256(canonical(request)).hexdigest() != job['requestSha256']:
                raise ValueError('Stored request changed')
            if not isinstance(request, dict) or set(request) - {'prompt', 'tracks', 'clarifications', 'estimator_profile'}:
                raise ValueError('Invalid request shape')
            prompt = request.get('prompt')
            if not isinstance(prompt, str) or not 1 <= len(prompt.strip()) <= 4000:
                raise ValueError('Invalid prompt')
            from prompt_to_playlist.models import ClarificationAnswer
            from prompt_to_playlist.service import build_playlist
            answers = [ClarificationAnswer.model_validate(a) for a in request.get('clarifications', [])]
            if len(answers) > 3:
                raise ValueError('Too many clarification answers')
            catalog, vocabulary = self.snapshot.select(request.get('tracks'), request.get('estimator_profile', 'reference'))

            def before():
                if context.get_remaining_time_in_millis() < 45000 or int(self.now()) >= int(job['deadline']):
                    raise TimeoutError('Insufficient provider budget')
                self.jobs.provider_started(job_id, attempt)

            provider = ClaimedTranslator(self.translator_factory(self.snapshot.planner_settings), before)
            with tempfile.TemporaryDirectory(prefix='resonant-', dir=self.scratch) as scratch:
                run = build_playlist(prompt, catalog, vocabulary, provider, clarifications=answers,
                    query_encoder=self.encoder.query_encoder(Path(scratch) / 'text-cache', self.objects))
                result = run.model_dump(mode='json', by_alias=True)
                # Keep exact evidence and request inputs separate from browser results.
                self.objects.put_json('audits/' + job_id + '.json', {
                    'request': request, 'result': result,
                    'planner_snapshot_sha256': self.snapshot.snapshot_sha256,
                    'catalog': catalog.model_dump(mode='json', by_alias=True),
                    'vocabulary': vocabulary.model_dump(mode='json', by_alias=True)})
                result_key = 'results/' + job_id + '.json'
                sha = self.objects.put_json(result_key, browser_result(result))
                status = 'needs_clarification' if run.status == 'needs_clarification' else 'succeeded'
                completed = self.jobs.finish(job_id, attempt, status, result_key, sha)
                return {'jobId': job_id, 'status': status if completed else 'expired'}
        except Exception:
            status = 'outcome_unknown' if provider is not None and provider.started else 'failed'
            # If this write fails, leave durable claim/provider marker intact. An
            # async retry cannot claim running; API deadline reconciliation expires it.
            self.jobs.finish(job_id, attempt, status)
            raise RuntimeError('Playlist worker failed; inspect durable job status') from None


def create_runtime():
    import boto3
    from botocore.config import Config
    from prompt_to_playlist.cloud_catalog import FrozenPlanner
    from prompt_to_playlist.translators import OpenAITranslator
    release = json.loads(Path(os.environ.get('RESONANT_IDENTITY', '/opt/resonant/identity.json')).read_text())
    expected = os.environ['RESONANT_RELEASE_ID']
    if release['releaseId'] != expected:
        raise ValueError('Release configuration mismatch')
    root = Path(os.environ.get('RESONANT_RELEASE_ROOT', '/opt/resonant/release'))
    planner_file = root / 'private/planner.json'
    if hashlib.sha256(planner_file.read_bytes()).hexdigest() != release['plannerSha256']:
        raise ValueError('Planner checksum mismatch')
    snapshot = FrozenPlanner.load(planner_file)
    encoder = WarmEncoder(os.environ.get('RESONANT_MODEL_ROOT', '/opt/resonant/models'))
    if encoder.encoder_id != release['encoderId']:
        raise ValueError('Model configuration mismatch')
    sdk = Config(connect_timeout=3, read_timeout=10, retries={'mode': 'standard', 'total_max_attempts': 3})
    objects = Objects(boto3.client('s3', config=sdk), os.environ['RESONANT_STATE_BUCKET'])
    table = boto3.resource('dynamodb', config=sdk).Table(os.environ['RESONANT_STATE_TABLE'])
    ssm = boto3.client('ssm', config=sdk)
    secret = {'until': 0, 'value': None}

    def translator(settings):
        if time.time() >= secret['until']:
            secret['value'] = ssm.get_parameter(Name=os.environ['RESONANT_OPENAI_PARAMETER'], WithDecryption=True)['Parameter']['Value']
            secret['until'] = time.time() + 300
        return OpenAITranslator(api_key=secret['value'], model=settings.model, timeout_s=settings.timeout_s,
                                intent_reasoning_effort=settings.intent_reasoning_effort)
    return Worker(expected, snapshot, encoder, Jobs(table), objects, translator)


def handler(event, context):
    global _RUNTIME
    if _RUNTIME is None:
        _RUNTIME = create_runtime()
    return _RUNTIME.handle(event, context)
