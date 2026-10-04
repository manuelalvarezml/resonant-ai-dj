#!/usr/bin/env python3
"""Prepare a small Docker context using explicit source allowlists, never Git/credentials/audio."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def prepare(destination: Path) -> dict:
    if destination.exists():
        raise ValueError('Output must not exist; choose a new context directory')
    # Source inclusion is deliberately independent of Git status and ignore rules.
    sources = {HERE / name: Path(name) for name in
               ('Dockerfile', 'requirements.lock', 'requirements-cpu.lock', 'requirements-build.lock', 'healthcheck.mjs', 'runtime-smoke.py')}
    package = ROOT / 'packages/prompt-to-playlist'
    for source in (package / 'src').rglob('*'):
        if source.is_symlink():
            raise ValueError('Symlinks are forbidden in runtime source')
        if source.is_file() and '__pycache__' not in source.parts and (source.suffix in {'.py', '.json'} or source.name.startswith('LICENSE')):
            sources[source] = source.relative_to(ROOT)
    for name in ('playlist.toml', 'pool-vocabulary.json'):
        sources[package / name] = (package / name).relative_to(ROOT)
    for name in ('serve-cloud.mjs', 'cloud-server.mjs', 'cloud-jobs.mjs'):
        source = ROOT / 'packages/web-player/scripts' / name
        if source.exists():
            sources[source] = source.relative_to(ROOT)
    for name in ('package.json', 'src/release-policy.js'):
        source = ROOT / 'packages/web-player' / name
        sources[source] = source.relative_to(ROOT)
    if not all(any(source.name == name for source in sources) for name in ('serve-cloud.mjs', 'cloud-server.mjs', 'cloud-jobs.mjs')):
        raise ValueError('Production Node entrypoint or dependency is missing')
    for source in sources:
        if not source.is_file() or source.is_symlink():
            raise ValueError(f'Required regular source is missing: {source.relative_to(ROOT)}')
    destination.mkdir(parents=True)
    files = []
    for source, relative in sorted(sources.items(), key=lambda item: str(item[1])):
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        target.chmod(0o644)
        files.append({'path': relative.as_posix(), 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'bytes': target.stat().st_size})
    manifest = {'schema': 'resonant/runtime-source/1', 'files': files}
    manifest['sourceDigest'] = hashlib.sha256(json.dumps(manifest, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    (destination / 'runtime-source.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--archive', type=Path)
    args = parser.parse_args()
    if args.archive and args.archive.exists():
        parser.error('Archive already exists; choose a new path')
    manifest = prepare(args.output.resolve())
    if args.archive:
        args.archive.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(args.archive, 'w:gz') as archive:
            for file in sorted(args.output.rglob('*')):
                archive.add(file, arcname=file.relative_to(args.output), recursive=False)
        args.archive.chmod(0o600)
    print(json.dumps({'sourceDigest': manifest['sourceDigest'], 'fileCount': len(manifest['files'])}))


if __name__ == '__main__':
    main()
