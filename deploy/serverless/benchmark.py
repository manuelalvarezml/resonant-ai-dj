"""Generic text-only cold/warm probe. No AWS client, source audio or OpenAI call."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import tempfile
import time

TEXTS = ['Warm intimate acoustic music', 'Bright energetic dance music']


def benchmark(model_dir, repeat):
    from runtime.encoder import WarmEncoder
    started = time.monotonic()
    encoder = WarmEncoder(model_dir)
    rows = []
    vectors = []
    for index in range(repeat):
        # Fresh cache forces inference; the same model instance must stay warm.
        with tempfile.TemporaryDirectory(prefix='resonant-benchmark-') as temp:
            begin = time.monotonic()
            result = encoder.embeddings(TEXTS, Path(temp))
            vectors.append(result['embeddings'])
            rows.append({'index': index, 'coldModel': index == 0, 'wallSeconds': time.monotonic() - begin,
                         'vectorSha256': hashlib.sha256(json.dumps(result['embeddings']).encode()).hexdigest()})
    if any(row != vectors[0] for row in vectors[1:]) or encoder.loads != 1:
        raise ValueError('Warm inference changed vectors or reloaded the model')
    return {'schema': 'resonant/lambda-local-text-benchmark/1', 'rows': rows, 'modelLoads': encoder.loads,
            'wallSeconds': time.monotonic() - started, 'peakRssKiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'encoderId': encoder.encoder_id, 'awsLatencyMeasurement': False, 'openaiCalls': 0, 'audioInference': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--models', type=Path, default=Path('/opt/resonant/models'))
    parser.add_argument('--repeat', type=int, default=2, choices=range(2, 11))
    args = parser.parse_args()
    print(json.dumps(benchmark(args.models, args.repeat)))
