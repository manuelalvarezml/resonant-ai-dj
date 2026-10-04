#!/usr/bin/env python3
"""Verify and activate one immutable release. Offline validation by default; --apply starts services."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

HERE = Path(__file__).resolve().parent


def read_env(file):
    if file.is_symlink() or not file.is_file() or file.stat().st_mode & 0o077:
        raise ValueError(f'{file.name} must exist with mode 600')
    values = {}
    for line in file.read_text().splitlines():
        if not line or line.startswith('#'):
            continue
        key, value = line.split('=', 1)
        if not re.fullmatch('[A-Z][A-Z0-9_]*', key) or key in values:
            raise ValueError('Invalid/duplicate env key')
        values[key] = value
    return values


def verify_config(directory):
    config = read_env(directory / '.env')
    app = read_env(directory / 'app.env')
    caddy = read_env(directory / 'caddy.env')
    hostname = config.get('RESONANT_HOSTNAME', '')
    if not re.fullmatch(r'[a-zA-Z0-9](?:[a-zA-Z0-9.-]*[a-zA-Z0-9])?\.[a-zA-Z]{2,63}', hostname) or hostname.endswith(('.invalid', '.example', '.localhost')):
        raise ValueError('Set the actual public DNS hostname')
    if not app.get('AUTODJ_OPENAI_API_DEV_KEY') or len(app.get('RESONANT_PROXY_TOKEN', '')) < 32 or len(app.get('RESONANT_SESSION_SECRET', '')) < 32:
        raise ValueError('Missing key/proxy/session secret')
    if app['RESONANT_PROXY_TOKEN'] == app['RESONANT_SESSION_SECRET'] or caddy.get('RESONANT_PROXY_TOKEN') != app['RESONANT_PROXY_TOKEN']:
        raise ValueError('Proxy/session secret separation or proxy agreement failed')
    if not re.fullmatch('[a-zA-Z0-9_.-]+', caddy.get('RESONANT_ACCESS_USER', '')) or not re.fullmatch(r'\$2[aby]\$\d\d\$[./A-Za-z0-9]{53}', caddy.get('RESONANT_ACCESS_PASSWORD_HASH', '')):
        raise ValueError('Set a valid listener username/bcrypt hash')
    if config.get('RESONANT_DATA_ROOT') != '/srv/resonant':
        raise ValueError('This first-release kit uses /srv/resonant')
    return config


def verify_evidence(evidence, release):
    runtime = evidence.get('runtime', {})
    planner = evidence.get('planner', {}).get('result', {})
    if (evidence.get('schema') != 'resonant/linux-acceptance/1'
            or evidence.get('releaseId') != release['releaseId']
            or not re.fullmatch(r'sha256:[a-f0-9]{64}', evidence.get('imageId', ''))
            or not re.fullmatch(r'[a-f0-9]{64}', evidence.get('modelManifestSHA256', ''))
            or evidence.get('network') != 'disabled' or evidence.get('openaiCalls') != 0
            or runtime.get('imports') != 'passed' or runtime.get('machine') != 'x86_64'
            or not runtime.get('platform', '').startswith('Linux-') or runtime.get('cuda') is not None
            or runtime.get('textSmoke', {}).get('vectorsEqual') is not True
            or planner.get('tracks') != release['trackCount'] or planner.get('parity_cases_passed') != 60
            or set(planner.get('profiles', [])) != {'reference', 'music2emo', 'musicnn-dance', 'supervised', 'quality'}):
        raise ValueError('Matching complete Linux acceptance evidence is required')


def has_previous_activation(config, root=Path('/srv/resonant')):
    """A populated preparation .env is not proof of an earlier good deployment."""
    current = root / 'current'
    previous = Path(config.get('RESONANT_RELEASE_DIR', ''))
    return (bool(config.get('RESONANT_IMAGE')) and current.is_symlink()
            and current.exists() and previous.is_dir()
            and current.resolve() == previous.resolve()
            and previous.resolve().parent == root / 'releases'
            and re.fullmatch('[a-f0-9]{64}', previous.name) is not None)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--image', required=True)
    parser.add_argument('--linux-evidence', type=Path, required=True)
    parser.add_argument('--config-dir', type=Path, default=HERE)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    if not re.fullmatch('resonant:[A-Za-z0-9._-]+', args.image):
        parser.error('Use an exact built resonant:version image')
    spec = importlib.util.spec_from_file_location('verify_release', HERE / 'verify-release.py')
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    release = verifier.verify(args.release)
    config = verify_config(args.config_dir)
    evidence = json.loads(args.linux_evidence.read_text())
    verify_evidence(evidence, release)
    if not args.apply:
        print(json.dumps({'verified': True, 'mode': 'OFFLINE PLAN ONLY', 'releaseId': release['releaseId'], 'image': args.image, 'hostname': config['RESONANT_HOSTNAME']}))
        return
    if args.release.resolve() != Path('/srv/resonant/releases') / release['releaseId']:
        raise SystemExit('Activation requires the verified immutable /srv/resonant/releases/<releaseId> path')
    image_id = subprocess.check_output(['docker', 'image', 'inspect', '--format', '{{.Id}}', args.image], text=True).strip()
    if image_id != evidence['imageId']:
        raise SystemExit('The tested image and selected image differ')
    model_manifest = Path('/srv/resonant/models/manifest.json')
    if hashlib.sha256(model_manifest.read_bytes()).hexdigest() != evidence['modelManifestSHA256']:
        raise SystemExit('The tested semantic model and deployed model differ')
    config_file = args.config_dir / '.env'
    previous = config_file.read_text()
    previous_activated = has_previous_activation(config)
    config.update(RESONANT_RELEASE_DIR=str(args.release.resolve()), RESONANT_IMAGE=args.image)
    candidate = args.config_dir / '.env.next'
    candidate.write_text(''.join(f'{key}={value}\n' for key, value in config.items()))
    candidate.chmod(0o600)
    env = os.environ.copy()
    for key in config:
        env.pop(key, None)
    command = ['docker', 'compose', '--project-directory', str(args.config_dir), '--env-file', str(candidate), '-f', str(args.config_dir / 'compose.yaml')]
    subprocess.run(command + ['config', '--quiet'], env=env, check=True)
    # Validate the actual pinned Linux Caddy image with its exact mounted
    # configuration before changing serving containers. No ports are published
    # by this one-off run, and logs are captured so expanded secrets stay private.
    caddy_check = subprocess.run(command + ['run', '--rm', '--no-deps', 'caddy', 'caddy', 'validate',
                                          '--config', '/etc/caddy/Caddyfile', '--adapter', 'caddyfile'],
                                 env=env, capture_output=True, text=True)
    if caddy_check.returncode:
        candidate.unlink(missing_ok=True)
        raise SystemExit('Pinned Caddy configuration validation failed; serving containers were not changed. Validation output withheld to protect configuration secrets.')
    history = args.config_dir / 'evidence'
    history.mkdir(mode=0o700, exist_ok=True)
    backup = history / ('previous-' + str(time.time_ns()) + '.env')
    backup.write_text(previous)
    backup.chmod(0o600)
    try:
        subprocess.run(command + ['up', '-d', '--wait', '--wait-timeout', '150'], env=env, check=True)
    except Exception:
        candidate.write_text(previous)
        if previous_activated:
            subprocess.run(command + ['up', '-d', '--wait', '--wait-timeout', '150'], env=env, check=False)
        else:
            subprocess.run(command + ['stop'], env=env, check=False)
        candidate.unlink(missing_ok=True)
        raise SystemExit('Activation failed; previous activated configuration retained/restarted where available, otherwise services stopped. Inspect service status before retrying.')
    candidate.replace(config_file)
    root = Path('/srv/resonant')
    pointer = root / 'current.next'
    pointer.unlink(missing_ok=True)
    pointer.symlink_to(args.release.resolve())
    pointer.replace(root / 'current')
    print(json.dumps({'activated': True, 'releaseId': release['releaseId'], 'imageId': image_id, 'previousConfig': str(backup), 'next': 'Run verify-https.py and actual browser checks before sharing.'}))


if __name__ == '__main__':
    main()
