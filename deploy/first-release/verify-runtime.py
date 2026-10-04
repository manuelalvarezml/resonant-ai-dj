#!/usr/bin/env python3
"""Verify an allowlisted runtime context, its source identity and exact inventory."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re


def verify(root):
    root = Path(os.path.abspath(root))
    if any(parent.is_symlink() for parent in [root, *root.parents]):
        raise ValueError('Runtime root/parents cannot be symlinks; use their real path')
    root = root.resolve(strict=True)
    file = root / 'runtime-source.json'
    if file.is_symlink():
        raise ValueError('Runtime manifest cannot be a symlink')
    data = json.loads(file.read_text())
    if data.get('schema') != 'resonant/runtime-source/1':
        raise ValueError('Unexpected runtime schema')
    original = {k: v for k, v in data.items() if k != 'sourceDigest'}
    calculated = hashlib.sha256(json.dumps(original, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    if data.get('sourceDigest') != calculated:
        raise ValueError('Runtime source identity mismatch')
    expected = {'runtime-source.json'}
    for item in data['files']:
        name = item['path']
        if not isinstance(name, str) or not name or '\\' in name or name.startswith('/') or any(p.startswith('.') or not p for p in name.split('/')) or name in expected:
            raise ValueError('Unsafe or duplicate runtime path')
        if not re.fullmatch('[a-f0-9]{64}', item['sha256']) or not isinstance(item['bytes'], int) or item['bytes'] < 0:
            raise ValueError('Invalid runtime file metadata')
        cursor = root
        for part in PurePosixPath(name).parts:
            cursor = cursor / part
            if cursor.is_symlink():
                raise ValueError('Runtime symlinks are forbidden')
        if not cursor.is_file() or cursor.stat().st_size != item['bytes']:
            raise ValueError('Runtime source size mismatch')
        with cursor.open('rb') as source:
            if hashlib.file_digest(source, 'sha256').hexdigest() != item['sha256']:
                raise ValueError('Runtime source hash mismatch')
        expected.add(name)
    for file in root.rglob('*'):
        if file.is_symlink() or (file.is_file() and file.relative_to(root).as_posix() not in expected):
            raise ValueError('Unmanifested file/symlink in runtime context')
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('runtime', type=Path)
    args = parser.parse_args()
    result = verify(args.runtime)
    print(json.dumps({'verified': True, 'sourceDigest': result['sourceDigest'], 'files': len(result['files'])}))
