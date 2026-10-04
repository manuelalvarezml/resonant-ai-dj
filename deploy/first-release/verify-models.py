#!/usr/bin/env python3
"""Verify only pinned semantic assets; emit a transfer allowlist with --files."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath


def verify(root):
    root = Path(os.path.abspath(root))
    if any(parent.is_symlink() for parent in [root, *root.parents]):
        raise ValueError('Model root/parents cannot be symlinks; use their real path')
    root = root.resolve(strict=True)
    manifest = root / 'manifest.json'
    if manifest.is_symlink():
        raise ValueError('Model manifest cannot be a symlink')
    data = json.loads(manifest.read_text())
    if data.get('model_id') != 'OpenMuQ/MuQ-MuLan-large' or data.get('revision') != '2e01c796b71dca71b45251384c04cd7b237c9020':
        raise ValueError('Unexpected semantic model revision')
    paths = ['manifest.json']
    for item in data['assets']:
        name = item['path']
        parts = PurePosixPath(name).parts
        if not parts or name.startswith('/') or '\\' in name or any(p.startswith('.') or not p for p in name.split('/')) or name in paths:
            raise ValueError('Unsafe/duplicate model path')
        file = root / name
        cursor = root
        for part in parts:
            cursor = cursor / part
            if cursor.is_symlink():
                raise ValueError('Model symlinks are forbidden')
        if not file.is_file() or file.stat().st_size != item['size_bytes']:
            raise ValueError('Model size mismatch')
        with file.open('rb') as source:
            if hashlib.file_digest(source, 'sha256').hexdigest() != item['sha256']:
                raise ValueError('Model hash mismatch')
        paths.append(name)
    for file in root.rglob('*'):
        if file.is_symlink() or (file.is_file() and file.relative_to(root).as_posix() not in paths):
            raise ValueError('Unmanifested file/symlink in model bundle')
    return paths


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('model_dir', type=Path)
    parser.add_argument('--files', action='store_true')
    args = parser.parse_args()
    files = verify(args.model_dir)
    print('\n'.join(files) if args.files else json.dumps({'verified': True, 'files': len(files)}))
