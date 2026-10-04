#!/usr/bin/env python3
"""Bounded first-release replay, pause and paired-alias rollback acceptance.

Requires the successful single live prompt. Makes no new AI request: the POST
reuses that terminal job's exact idempotency key. Pauses admissions before
cycling retained aliases and restoring versioned entry pointers. On failure,
restores current aliases but leaves admissions disabled for inspection.
"""
import hashlib
import http.cookiejar
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.request

import boto3
from botocore.config import Config

ROOT = Path(__file__).resolve().parents[2]


def main():
    os.umask(0o077)
    cloud = ROOT / 'output/serverless-cloud'
    folder = cloud / 'acceptance'
    receipt = folder / 'live-operations.json'
    if receipt.exists():
        raise ValueError('A receipt exists; inspect it before another execution')
    live = json.loads((folder / 'live-prompt.json').read_text())
    assert live['status'] == 'completed' and live['matches'] > 0
    active = json.loads((cloud / 'active-deployment.json').read_text())
    previous = json.loads((cloud / 'playback-deployment.json').read_text())
    assert active['releaseId'] == previous['releaseId'] == live['releaseId']
    assert set(active['pointers']) == {'index.html', 'library/current.json'}
    assert set(active['aliases']) == set(previous['aliases']) == {'api', 'worker'}

    target = json.loads((ROOT / 'output/cloud-preparation/aws-target.json').read_text())
    session = boto3.Session(profile_name='manueldev', region_name='us-east-2')
    cfg = Config(connect_timeout=5, read_timeout=30, retries={'total_max_attempts': 1})
    assert session.client('sts', config=cfg).get_caller_identity()['Account'] == target['account_id']
    stack = json.loads((cloud / 'resonant-data/outputs.json').read_text())['Stacks'][0]
    output = {row['OutputKey']: row['OutputValue'] for row in stack['Outputs']}
    table = session.resource('dynamodb', config=cfg).Table(output['State'])
    s3 = session.client('s3', config=cfg)
    functions = session.client('lambda', config=cfg)
    auth = json.loads((folder / 'login-session.json').read_text())
    jar = http.cookiejar.MozillaCookieJar(str(folder / 'listener.cookies'))
    jar.load(ignore_discard=True, ignore_expires=True)
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

    def request(path, body=None, headers=None):
        headers = {'Origin': auth['origin'], 'Content-Type': 'application/json',
                   'x-resonant-csrf': auth['csrf'], **(headers or {})}
        req = urllib.request.Request(auth['origin'] + path,
            data=None if body is None else json.dumps(body).encode(), headers=headers)
        try:
            with opener.open(req, timeout=30) as response:
                return response.status, response.read(32 * 1024 * 1024)
        except urllib.error.HTTPError as error:
            return error.code, error.read(65536)

    def item(pk):
        return table.get_item(Key={'pk': pk, 'sk': 'META'}, ConsistentRead=True).get('Item')

    def counters_and_jobs():
        rows, cursor = [], None
        while True:
            args = {'ConsistentRead': True}
            if cursor:
                args['ExclusiveStartKey'] = cursor
            result = table.scan(**args)
            rows.extend(result['Items'])
            cursor = result.get('LastEvaluatedKey')
            if not cursor:
                break
        assert not any(row['pk'].startswith('JOB#') and row.get('status') in
                       {'dispatching', 'queued', 'running'} for row in rows)
        return {row['pk']: int(row['count']) for row in rows
                if row['pk'].startswith(('DAY#', 'MONTH#'))}

    record = {'status': 'preflight', 'startedAt': time.time(), 'checks': [],
              'newProviderRequests': 0, 'releaseId': active['releaseId']}

    def save():
        receipt.write_text(json.dumps(record, indent=2))

    def aliases(versions):
        for name in ('worker', 'api'):
            function = 'resonant-runtime-' + name
            current = functions.get_alias(FunctionName=function, Name='live')
            functions.update_alias(FunctionName=function, Name='live',
                FunctionVersion=versions[name], RevisionId=current['RevisionId'])
        for name, version in versions.items():
            assert functions.get_alias(FunctionName='resonant-runtime-' + name,
                                       Name='live')['FunctionVersion'] == version

    config = item('CONFIG#ACTIVE')
    assert config['enabled'] is True and config['releaseId'] == active['releaseId']
    job_before = item('JOB#' + live['jobId'])
    assert job_before['status'] == 'succeeded'
    before = counters_and_jobs()
    for name, version in active['aliases'].items():
        assert functions.get_alias(FunctionName='resonant-runtime-' + name,
                                   Name='live')['FunctionVersion'] == version
        functions.get_function(FunctionName='resonant-runtime-' + name,
                               Qualifier=previous['aliases'][name])
    raw = s3.get_object(Bucket=output['StateBucket'],
                       Key='requests/' + live['jobId'] + '.json')['Body'].read()
    body = {**json.loads(raw), 'releaseId': live['releaseId'],
            'idempotencyKey': live['idempotencyKey']}
    save()
    code, response = request('/api/playlist', body)
    assert code == 202 and json.loads(response)['id'] == live['jobId']
    assert counters_and_jobs() == before and item('JOB#' + live['jobId']) == job_before
    record['checks'].append('terminal idempotent replay: same job, counters and durable state')
    save()
    table.update_item(Key={'pk': 'CONFIG#ACTIVE', 'sk': 'META'},
        UpdateExpression='SET enabled=:no',
        ConditionExpression='enabled=:yes AND releaseId=:release',
        ExpressionAttributeValues={':no': False, ':yes': True, ':release': live['releaseId']})
    record['status'] = 'admissions_paused'
    save()
    succeeded = False
    try:
        counters_and_jobs()
        code, response = request('/api/playlist', body)
        assert code == 503 and b'playback is still available' in response
        record['checks'].append('paused admissions return 503 without another dispatch')
        aliases(previous['aliases'])
        assert request('/api/session')[0] == 200
        hashes = {}
        versions = {}
        for key, version in active['pointers'].items():
            original = s3.get_object(Bucket=output['MediaBucket'], Key=key,
                                     VersionId=version)['Body'].read()
            hashes[key] = hashlib.sha256(original).hexdigest()
            copied = s3.copy_object(Bucket=output['MediaBucket'], Key=key,
                CopySource={'Bucket': output['MediaBucket'], 'Key': key, 'VersionId': version},
                MetadataDirective='COPY', ChecksumAlgorithm='SHA256')
            versions[key] = copied['VersionId']
            actual = s3.get_object(Bucket=output['MediaBucket'], Key=key)['Body'].read()
            code, served = request('/' if key == 'index.html' else '/' + key)
            assert code == 200 and hashlib.sha256(actual).hexdigest() == hashes[key]
            assert hashlib.sha256(served).hexdigest() == hashes[key]
        plan = json.loads((ROOT / 'output/serverless-assets/candidate-1/upload-plan.json').read_text())
        # Static playback availability: use a signed seek against a real MP3.
        entries = plan['uploads']
        mp3 = next(row for row in entries if row['key'].endswith('.mp3'))
        code, audio = request('/' + mp3['key'], headers={'Range': 'bytes=100000-132767'})
        assert code == 206 and len(audio) == 32768
        record['checks'].extend(['retained API/worker alias pair restored; session valid',
            'both entry pointers restored by saved S3 version and checksum verified',
            'actual MP3 seek works while AI is paused and aliases rolled back'])
        record['pointerVersions'] = versions
        active['pointers'] = versions
        (cloud / 'active-deployment.json').write_text(json.dumps(active, indent=2))
        succeeded = True
    finally:
        aliases(active['aliases'])
        if succeeded:
            assert request('/api/session')[0] == 200
            assert counters_and_jobs() == before
            table.update_item(Key={'pk': 'CONFIG#ACTIVE', 'sk': 'META'},
                UpdateExpression='SET enabled=:yes',
                ConditionExpression='enabled=:no AND releaseId=:release',
                ExpressionAttributeValues={':no': False, ':yes': True, ':release': live['releaseId']})
            record['checks'].append('current paired aliases and AI admissions restored')
            record['status'] = 'passed'
        else:
            record['status'] = 'review_required_admissions_paused'
        record['elapsedSeconds'] = round(time.time() - record['startedAt'], 2)
        save()
    print(json.dumps({'status': record['status'], 'checks': record['checks'],
                      'newProviderRequests': 0}))


if __name__ == '__main__':
    main()
