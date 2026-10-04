"""Durable worker boundaries, with explicit conditional claims and fenced completion."""
import hashlib
import json
import time


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def conditional(error):
    return getattr(error, 'response', {}).get('Error', {}).get('Code') == 'ConditionalCheckFailedException'


class Objects:
    def __init__(self, client, bucket):
        self.client, self.bucket = client, bucket

    def get_json(self, key, limit):
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        body = response['Body']
        try:
            if response['ContentLength'] > limit:
                raise ValueError('Oversized stored object')
            raw = body.read(limit + 1)
            if len(raw) > limit:
                raise ValueError('Oversized stored object')
            return json.loads(raw)
        finally:
            body.close()

    def optional_json(self, key, limit):
        try:
            return self.get_json(key, limit)
        except Exception as error:
            if getattr(error, 'response', {}).get('Error', {}).get('Code') in {'NoSuchKey', '404'}:
                return None
            raise

    def put_json(self, key, value):
        raw = canonical(value)
        if len(raw) > 32 * 1024 * 1024:
            raise ValueError('Oversized result')
        self.client.put_object(Bucket=self.bucket, Key=key, Body=raw,
                               ContentType='application/json', CacheControl='private,no-store',
                               ServerSideEncryption='AES256')
        return hashlib.sha256(raw).hexdigest()


class Jobs:
    """Rows use pk=JOB#<uuid>, sk=META. Slot release is owned by the API reconciler.

    Slots have the same logical deadline as their jobs. Terminal status is enough
    for admission to atomically reclaim them; worker does not decrement a counter
    that could be decremented twice after lost acknowledgements.
    """
    def __init__(self, table, now=time.time):
        self.table, self.now = table, now

    def claim(self, job_id, attempt, release):
        try:
            result = self.table.update_item(
                Key={'pk': 'JOB#' + job_id, 'sk': 'META'},
                UpdateExpression='SET #status = :running, attempt = :attempt, started = :now',
                ConditionExpression='(#status = :queued OR #status = :dispatching) AND deadline > :now AND releaseId = :release',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':running': 'running', ':attempt': attempt, ':now': int(self.now()),
                                           ':queued': 'queued', ':dispatching': 'dispatching', ':release': release},
                ReturnValues='ALL_NEW')
            return result['Attributes']
        except Exception as error:
            if conditional(error):
                return None
            raise

    def provider_started(self, job_id, attempt):
        self.table.update_item(
            Key={'pk': 'JOB#' + job_id, 'sk': 'META'},
            UpdateExpression='SET providerStarted = :yes',
            ConditionExpression='#status = :running AND attempt = :attempt AND deadline > :now AND attribute_not_exists(providerStarted)',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':yes': True, ':running': 'running', ':attempt': attempt, ':now': int(self.now())})

    def finish(self, job_id, attempt, status, result_key=None, result_sha=None):
        values = {':status': status, ':attempt': attempt, ':running': 'running', ':now': int(self.now())}
        update = 'SET #status = :status, finished = :now'
        if result_key is not None:
            update += ', resultKey = :key, resultSha256 = :sha'
            values.update({':key': result_key, ':sha': result_sha})
        try:
            self.table.update_item(
                Key={'pk': 'JOB#' + job_id, 'sk': 'META'}, UpdateExpression=update,
                ConditionExpression='#status = :running AND attempt = :attempt AND deadline > :now',
                ExpressionAttributeNames={'#status': 'status'}, ExpressionAttributeValues=values)
            return True
        except Exception as error:
            if conditional(error):
                return False
            raise
