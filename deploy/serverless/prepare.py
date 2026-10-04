#!/usr/bin/env python3
"""Create a fresh allowlisted Lambda build context from verified local artifacts."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    with path.open('rb') as file:
        return hashlib.file_digest(file, 'sha256').hexdigest()


def safe(root, relative):
    path = root / relative
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('Invalid source path')
    return path


def prepare(release, models, destination):
    release, models, destination = map(lambda p: Path(p).resolve(), (release, models, destination))
    if destination.exists() or not destination.is_relative_to(ROOT / 'output'):
        raise ValueError('Choose a new output directory inside repository output/')
    manifest = json.loads((release / 'release.json').read_text())
    if manifest['schema'] != 'resonant/cloud-release/1':
        raise ValueError('Unsupported release')
    rows = {r['path']: r for r in manifest['files']}
    sources = {}
    for name in ['private/planner.json', 'private/planner-parity.json']:
        source = safe(release, name)
        if sha(source) != rows[name]['sha256'] or source.stat().st_size != rows[name]['bytes']:
            raise ValueError('Release checksum mismatch')
        sources['release/' + name] = source
    model_manifest = json.loads((models / 'manifest.json').read_text())
    for row in model_manifest['assets']:
        source = safe(models, row['path'])
        if sha(source) != row['sha256'] or source.stat().st_size != row['size_bytes']:
            raise ValueError('Model checksum mismatch')
        sources['models/' + row['path']] = source
    sources['models/manifest.json'] = safe(models, 'manifest.json')
    package = ROOT / 'packages/prompt-to-playlist/src/prompt_to_playlist'
    for source in package.iterdir():
        if source.suffix in {'.py', '.json'}:
            sources[source.relative_to(ROOT).as_posix()] = safe(package, source.name)
    for source in (HERE / 'runtime').glob('*.py'):
        sources['runtime/' + source.name] = source
    for name in ['Dockerfile', 'verify.py', 'benchmark.py', 'requirements-aws.lock']:
        sources[name] = safe(HERE, name)
    for name in ['requirements.lock', 'requirements-cpu.lock', 'requirements-build.lock']:
        sources[name] = safe(HERE.parent / 'first-release', name)
    sys.path.insert(0, str(package.parent))
    from prompt_to_playlist.semantic_audio import identity
    identity_doc = {'schema': 'resonant/lambda-image/1', 'releaseId': manifest['releaseId'],
                    'plannerSha256': rows['private/planner.json']['sha256'],
                    'paritySha256': rows['private/planner-parity.json']['sha256'],
                    'modelManifestSha256': sha(models / 'manifest.json'), 'encoderId': identity(models),
                    'sourceFiles': {name: sha(source) for name, source in sorted(sources.items())}}
    identity_doc['buildId'] = hashlib.sha256(json.dumps(identity_doc, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    destination.mkdir(parents=True)
    try:
        for name, source in sources.items():
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            # APFS clone avoids another physical copy of the multi-GB model.
            if sys.platform == 'darwin':
                subprocess.run(['cp', '-c', str(source), str(target)], check=True)
            else:
                shutil.copyfile(source, target)
            target.chmod(0o644)
        (destination / 'identity.json').write_text(json.dumps(identity_doc, indent=2) + '\n')
        (destination / '.dockerignore').write_text('__pycache__\n*.pyc\n')
    except Exception:
        # Retain partial context for diagnosis; never delete an arbitrary tree.
        raise
    return {'buildId': identity_doc['buildId'], 'files': len(sources), 'contextBytes': sum(x.stat().st_size for x in sources.values()), 'path': str(destination)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--models', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.release, args.models, args.output)))
