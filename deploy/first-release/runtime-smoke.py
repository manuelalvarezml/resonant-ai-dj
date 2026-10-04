#!/usr/bin/env python3
"""Linux semantic runtime check. Only --text-smoke performs one text embedding; never audio."""
import argparse
import importlib
import importlib.metadata
import json
import os
import platform
import time
import secrets
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--imports-only', action='store_true')
    group.add_argument('--text-smoke', action='store_true')
    parser.add_argument('--model-dir', type=Path, default=Path('/models'))
    parser.add_argument('--state-dir', type=Path, default=Path('/state'))
    args = parser.parse_args()
    for module in ('numpy', 'psutil', 'torch', 'torchaudio', 'torchvision', 'muq', 'transformers', 'pydantic', 'prompt_to_playlist.cloud_bridge'):
        importlib.import_module(module)
    import torch
    if torch.version.cuda is not None:
        raise RuntimeError('This release requires CPU-only Torch')
    result = {'platform': platform.platform(), 'machine': platform.machine(), 'imports': 'passed', 'cuda': torch.version.cuda,
              'versions': {name: importlib.metadata.version(name) for name in ('torch', 'torchaudio', 'transformers', 'muq', 'numpy', 'pydantic', 'psutil')}}
    if args.text_smoke:
        if platform.system() != 'Linux':
            raise RuntimeError('Text smoke is reserved for the target Linux runtime')
        from prompt_to_playlist.cloud_text import bounded_encode
        # A unique generic description forces one genuine cache miss. There is
        # no provider/LLM call, audio decoding or library analysis in this check.
        text = 'Warm instrumental music for a quiet evening. Verification ' + secrets.token_hex(8)
        started = time.monotonic()
        first = bounded_encode([text], args.model_dir, args.state_dir)
        cold = time.monotonic() - started
        evidence = json.loads((args.state_dir / 'last-text-worker.json').read_text())
        before = (args.state_dir / 'last-text-worker.json').read_bytes()
        started = time.monotonic()
        second = bounded_encode([text], args.model_dir, args.state_dir)
        warm = time.monotonic() - started
        if first != second or before != (args.state_dir / 'last-text-worker.json').read_bytes():
            raise RuntimeError('Text cache replay changed vectors or reran the worker')
        result['textSmoke'] = {'coldSeconds': cold, 'cacheHitSeconds': warm, 'vectorsEqual': True, 'worker': evidence}
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
