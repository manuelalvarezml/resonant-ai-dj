"""Private isolated benchmark entrypoint; no S3, DynamoDB, SSM or OpenAI calls."""
import hashlib
import json
import os
from pathlib import Path
import time
import tempfile

_ENCODER = None


def handler(event, context):
    global _ENCODER
    if event != {'probe': 'muq-text-v1'}:
        raise ValueError('Only the fixed generic text probe is allowed')
    started = time.monotonic()
    cold = _ENCODER is None
    if cold:
        from .encoder import WarmEncoder
        _ENCODER = WarmEncoder(Path(os.environ['RESONANT_MODEL_ROOT']))
    from benchmark import TEXTS
    with tempfile.TemporaryDirectory(prefix='resonant-probe-') as scratch:
        result = _ENCODER.embeddings(TEXTS, Path(scratch))
    return {'probe': 'muq-text-v1', 'coldModel': cold, 'wallSeconds': time.monotonic() - started,
            'vectorSha256': hashlib.sha256(json.dumps(result['embeddings']).encode()).hexdigest(),
            'modelLoads': _ENCODER.loads, 'memoryMB': int(os.environ['AWS_LAMBDA_FUNCTION_MEMORY_SIZE']),
            'openaiCalls': 0, 'audioInference': False}
