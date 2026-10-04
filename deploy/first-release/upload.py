#!/usr/bin/env python3
"""Upload only verified release/models/runtime and the deployment kit. Offline plan by default."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', required=True)
    parser.add_argument('--user', default='ubuntu')
    parser.add_argument('--identity', type=Path, required=True)
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--models', type=Path, required=True)
    parser.add_argument('--runtime', type=Path, required=True)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    if not re.fullmatch('[A-Za-z0-9][A-Za-z0-9.-]*', args.host) or not re.fullmatch('[a-z_][a-z0-9_-]*', args.user):
        parser.error('Invalid SSH host/user')
    if not args.identity.is_file():
        parser.error('Explicit SSH identity file is required')
    release = load('verify-release').verify(args.release)
    model_files = load('verify-models').verify(args.models)
    runtime = load('verify-runtime').verify(args.runtime)
    kit_files = sorted(p.name for p in HERE.iterdir() if p.is_file() and (p.suffix in {'.py', '.sh', '.md', '.mjs', '.lock'} or p.name in {'Dockerfile', 'compose.yaml', 'Caddyfile'} or p.name.endswith('.example')))
    plan = {'mode': 'APPLY' if args.apply else 'OFFLINE PLAN ONLY', 'ssh': args.user + '@' + args.host,
            'releaseId': release['releaseId'], 'tracks': release['trackCount'], 'runtimeSourceDigest': runtime['sourceDigest'],
            'destination': '/srv/resonant', 'models': len(model_files),
            'secretsTransferred': False, 'notes': 'Host key must already be verified in known_hosts; no automatic host-key acceptance.'}
    print(json.dumps(plan, indent=2))
    if not args.apply:
        return
    ssh = ['ssh', '-i', str(args.identity.resolve()), '-o', 'IdentitiesOnly=yes', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes']
    target = args.user + '@' + args.host
    def remote(*command):
        subprocess.run(ssh + [target, shlex.join(command)], check=True)
    release_dir = '/srv/resonant/releases/' + release['releaseId']
    runtime_dir = '/srv/resonant/runtime/' + runtime['sourceDigest']
    # Refuse overwriting a different model manifest used by an active release.
    model_digest = load('verify-release').digest(args.models / 'manifest.json')
    guard = "import hashlib,pathlib,sys;p=pathlib.Path('/srv/resonant/models/manifest.json');sys.exit(0 if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()==sys.argv[1] else 1)"
    remote('python3', '-c', guard, model_digest)
    remote('mkdir', '-p', release_dir, runtime_dir, '/srv/resonant/deploy', '/srv/resonant/models')
    def transfer(root, files, destination):
        with tempfile.NamedTemporaryFile(mode='w') as inventory:
            inventory.write('\n'.join(files) + '\n')
            inventory.flush()
            subprocess.run(['rsync', '-rt', '--partial', '--safe-links', '--chmod=D755,F644', '--files-from=' + inventory.name,
                            '--rsh=' + shlex.join(ssh), str(root.resolve()) + '/', target + ':' + destination + '/'], check=True)
    transfer(HERE, kit_files, '/srv/resonant/deploy')
    transfer(args.runtime, ['runtime-source.json'] + [i['path'] for i in runtime['files']], runtime_dir)
    transfer(args.release, ['release.json'] + [i['path'] for i in release['files']], release_dir)
    transfer(args.models, model_files, '/srv/resonant/models')
    remote('python3', '/srv/resonant/deploy/verify-runtime.py', runtime_dir)
    remote('python3', '/srv/resonant/deploy/verify-release.py', release_dir)
    remote('python3', '/srv/resonant/deploy/verify-models.py', '/srv/resonant/models')
    print('Upload and remote checks passed. No service was started. Configure secrets privately, build, run Linux acceptance, then activate.')


if __name__ == '__main__':
    main()
