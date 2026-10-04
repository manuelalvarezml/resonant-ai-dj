#!/usr/bin/env python3
"""Run target Linux checks before activation; uses one uncached text embedding, zero OpenAI calls."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', required=True)
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--models', type=Path, required=True)
    parser.add_argument('--state', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch('resonant:[A-Za-z0-9._-]+', args.image):
        parser.error('An exact local resonant:version image is required')
    if args.output.exists():
        parser.error('Evidence output already exists; retain previous evidence')
    release = load('verify-release').verify(args.release)
    load('verify-models').verify(args.models)
    image_id = subprocess.check_output(['docker', 'image', 'inspect', '--format', '{{.Id}}', args.image], text=True).strip()
    command = ['docker', 'run', '--rm', '--init', '--network', 'none', '--read-only', '--cap-drop', 'ALL',
               '--security-opt', 'no-new-privileges:true', '--memory', '7g', '--cpus', '2', '--pids-limit', '128',
               '--tmpfs', '/tmp:rw,nosuid,nodev,size=128m',
               '--mount', f'type=bind,source={args.release.resolve()},target=/release,readonly',
               '--mount', f'type=bind,source={args.models.resolve()},target=/models,readonly',
               '--mount', f'type=bind,source={args.state.resolve()},target=/state', '--entrypoint', 'python', args.image]
    result = subprocess.run(command + ['/opt/resonant/runtime-smoke.py', '--text-smoke'], text=True, capture_output=True, timeout=390, check=True)
    runtime = json.loads(result.stdout)
    subprocess.run(command + ['-m', 'prompt_to_playlist.cloud_bridge', 'verify', '--release-dir', '/release',
                               '--out', '/state/planner-verification.json'], check=True, timeout=120)
    # State belongs to the unprivileged service UID. Read via a container instead
    # of loosening its host permissions or requiring sudo for the evidence file.
    result = subprocess.check_output(command + ['-c', "from pathlib import Path; print(Path('/state/planner-verification.json').read_text())"], text=True)
    planner = json.loads(result)
    if 'error' in planner:
        raise SystemExit('Frozen planner verification failed')
    evidence = {'schema': 'resonant/linux-acceptance/1', 'imageId': image_id, 'releaseId': release['releaseId'],
                'modelManifestSHA256': hashlib.sha256((args.models / 'manifest.json').read_bytes()).hexdigest(),
                'runtime': runtime, 'planner': planner, 'network': 'disabled', 'openaiCalls': 0}
    load('activate').verify_evidence(evidence, release)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2) + '\n')
    args.output.chmod(0o600)
    print('Linux imports, uncached text/cache replay and frozen planner verification passed; evidence saved. HTTP, auth, real device and live OpenAI checks are still required.')


if __name__ == '__main__':
    main()
