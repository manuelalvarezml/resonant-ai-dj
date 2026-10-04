#!/usr/bin/env python3
"""Verify portable release inventory and every file before transfer/activation."""
import argparse
import hashlib
import json
import re
import os
from pathlib import Path, PurePosixPath


def digest(file):
    with file.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify(root):
    root = Path(os.path.abspath(root))
    for parent in [root, *root.parents]:
        if parent.is_symlink():
            raise ValueError('Release root/parents cannot be symlinks; use their real path')
    root = root.resolve(strict=True)
    manifest_path = root / 'release.json'
    if manifest_path.is_symlink():
        raise ValueError('Manifest must be a regular file')
    manifest = json.loads(manifest_path.read_text())
    if manifest.get('schema') != 'resonant/cloud-release/1' or not re.fullmatch('[a-f0-9]{64}', manifest.get('releaseId', '')):
        raise ValueError('Invalid release identity/schema')
    identity = {key: value for key, value in manifest.items() if key != 'releaseId'}
    calculated = hashlib.sha256(json.dumps(identity, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
    if calculated != manifest['releaseId']:
        raise ValueError('Release identity does not match its manifest')
    if not isinstance(manifest.get('trackCount'), int) or manifest['trackCount'] < 1:
        raise ValueError('Empty or invalid release')
    expected = {'release.json'}
    for item in manifest['files']:
        name = item['path']
        parts = PurePosixPath(name).parts
        if '\\' in name or not parts or parts[0] not in {'public', 'private', 'media'} or any(p in {'..', '.'} or p.startswith('.') for p in parts):
            raise ValueError('Unsafe release path')
        if name in expected or PurePosixPath(name).as_posix() != name:
            raise ValueError('Duplicate/noncanonical path')
        expected.add(name)
        if not isinstance(item['bytes'], int) or isinstance(item['bytes'], bool) or item['bytes'] < 0 or not re.fullmatch('[a-f0-9]{64}', item['sha256']):
            raise ValueError('Invalid file inventory size/digest')
        file = root / name
        if any(path.is_symlink() for path in [file, *file.parents] if path != root.parent):
            raise ValueError('Symlinks are forbidden')
        if not file.is_file() or file.stat().st_size != item['bytes'] or digest(file) != item['sha256']:
            raise ValueError(f'Integrity mismatch: {name}')
    for file in root.rglob('*'):
        if file.is_symlink():
            raise ValueError('Symlinks are forbidden')
        if file.is_file() and file.relative_to(root).as_posix() not in expected:
            raise ValueError('Unmanifested file in release')
    for name in ('public/catalog.json', 'public/mix.json', 'private/planner.json', 'private/planner-parity.json', 'media/mix.m4a', 'public/index.html', 'public/config.json'):
        if name not in expected:
            raise ValueError(f'Required cloud artifact missing: {name}')
    catalog = json.loads((root / 'public/catalog.json').read_text())
    if len(catalog['tracks']) != manifest['trackCount']:
        raise ValueError('Catalog track count mismatch')
    files = {item['path']: item for item in manifest['files']}
    ids = set()
    for track in catalog['tracks']:
        identity = track['id']
        if not re.fullmatch('[a-f0-9]{64}', identity) or identity in ids or track.get('fileHash') != identity or track.get('sourceVersion') != identity:
            raise ValueError('Invalid published track identity')
        ids.add(identity)
        media = files.get('media/' + identity + '.mp3')
        if not media or media['sha256'] != identity or 'private/features/' + identity + '.json' not in expected:
            raise ValueError('Track/audio/feature hash binding mismatch')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('release', type=Path)
    args = parser.parse_args()
    result = verify(args.release)
    print(json.dumps({'verified': True, 'releaseId': result['releaseId'], 'trackCount': result['trackCount'], 'audioBytes': result['audioBytes']}))
