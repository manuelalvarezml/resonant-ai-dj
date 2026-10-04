#!/usr/bin/env python3
"""Check published Linux wheels and exact dependency closure using only small upstream metadata."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from email.parser import Parser
import json
from pathlib import Path
import urllib.request
from packaging.markers import default_environment
from packaging.requirements import Requirement
from packaging.tags import cpython_tags, compatible_tags
from packaging.utils import parse_wheel_filename
from packaging.version import Version

HERE = Path(__file__).resolve().parent


def fetch(url):
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read()


def check():
    pins = {}
    for file in ('requirements.lock', 'requirements-cpu.lock', 'requirements-build.lock'):
        for line in (HERE / file).read_text().splitlines():
            if line and not line.startswith(('#', '--')):
                requirement = Requirement(line)
                pins[requirement.name.lower().replace('_', '-')] = next(iter(requirement.specifier)).version
    platforms = ['manylinux_2_' + str(v) + '_x86_64' for v in range(36, 16, -1)] + ['manylinux2014_x86_64', 'manylinux2010_x86_64', 'manylinux1_x86_64', 'linux_x86_64']
    tags = set(cpython_tags((3, 12), abis=['cp312'], platforms=platforms)) | set(compatible_tags((3, 12), interpreter='cp312', platforms=platforms))
    def package(item):
        name, version = item
        if name in {'torch', 'torchaudio', 'torchvision'}:
            filename = f'{name}-{version}-cp312-cp312-manylinux_2_28_x86_64.whl'
            url = 'https://download.pytorch.org/whl/cpu/' + filename.replace('+', '%2B')
            metadata = Parser().parsestr(fetch(url + '.metadata').decode())
            return {'name': name, 'version': version, 'wheel': filename, 'url': url, 'metadataURL': url + '.metadata', 'requires': metadata.get_all('Requires-Dist', [])}
        data = json.loads(fetch(f'https://pypi.org/pypi/{name}/{version}/json'))
        wheels = []
        for artifact in data['urls']:
            if artifact['packagetype'] == 'bdist_wheel' and not artifact.get('yanked') and parse_wheel_filename(artifact['filename'])[3] & tags:
                wheels.append(artifact)
        if not wheels and name == 'muq':
            wheels = [a for a in data['urls'] if a['packagetype'] == 'sdist' and not a.get('yanked')]
        if not wheels:
            raise ValueError(f'No compatible Linux CPython 3.12 wheel: {name}=={version}')
        artifact = sorted(wheels, key=lambda x: x['filename'])[0]
        return {'name': name, 'version': version, 'artifactType': artifact['packagetype'], 'wheel': artifact['filename'], 'url': artifact['url'], 'sha256': artifact['digests']['sha256'],
                'metadataURL': f'https://pypi.org/pypi/{name}/{version}/json', 'requires': data['info'].get('requires_dist') or []}
    with ThreadPoolExecutor(max_workers=6) as executor:
        records = sorted(executor.map(package, pins.items()), key=lambda x: x['name'])
    env = default_environment()
    env.update(sys_platform='linux', platform_system='Linux', platform_machine='x86_64', python_version='3.12', python_full_version='3.12.12', extra='')
    errors = []
    for package in records:
        for value in package['requires']:
            req = Requirement(value)
            if req.marker and not req.marker.evaluate(env):
                continue
            dependency = req.name.lower().replace('_', '-')
            if dependency not in pins:
                errors.append(package['name'] + ' missing dependency ' + str(req))
            elif Version(pins[dependency]) not in req.specifier:
                errors.append(package['name'] + ' incompatible dependency ' + str(req) + '; pinned ' + pins[dependency])
    return {'schema': 'resonant/linux-dependency-metadata/1', 'target': 'CPython 3.12.12 Linux x86_64 glibc 2.36 CPU',
            'passed': not errors, 'errors': errors, 'packages': records, 'limits': 'Metadata/wheel compatibility only; no install/import or inference performed. Docker pip check and Linux acceptance remain required.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = check()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'passed': result['passed'], 'packages': len(result['packages']), 'errors': result['errors']}))
    raise SystemExit(0 if result['passed'] else 1)
