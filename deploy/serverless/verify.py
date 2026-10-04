"""Offline image acceptance: no model inference, provider calls or AWS clients."""
import hashlib
import json
from pathlib import Path


def verify(root):
    from prompt_to_playlist.cloud_catalog import FrozenPlanner, verify_parity
    from prompt_to_playlist.semantic_audio import model_manifest, identity
    doc = json.loads((root / 'identity.json').read_text())
    for relative, expected in doc['sourceFiles'].items():
        with (root / relative).open('rb') as file:
            if hashlib.file_digest(file, 'sha256').hexdigest() != expected:
                raise ValueError('Image source checksum mismatch: ' + relative)
    frozen = FrozenPlanner.load(root / 'release/private/planner.json')
    cases = verify_parity(frozen, json.loads((root / 'release/private/planner-parity.json').read_text()))
    model_manifest(root / 'models', verify=True)
    if identity(root / 'models') != doc['encoderId']:
        raise ValueError('Encoder identity mismatch')
    import awslambdaric
    import boto3
    import torch
    import torchaudio
    import torchvision
    import transformers
    from runtime.worker import handler
    return {'schema': 'resonant/lambda-verification/1', 'buildId': doc['buildId'], 'releaseId': doc['releaseId'],
            'tracks': len(frozen.items), 'profiles': list(frozen.presets), 'parityCases': cases,
            'torchVersion': torch.__version__, 'pythonHandlerCallable': callable(handler), 'inference': False}


if __name__ == '__main__':
    print(json.dumps(verify(Path(__file__).resolve().parent)))
