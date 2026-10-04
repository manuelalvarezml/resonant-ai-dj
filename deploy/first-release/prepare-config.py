#!/usr/bin/env python3
"""Generate private runtime configuration without printing or reading existing account secrets."""
import argparse
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--hostname', default='')
    parser.add_argument('--image', default='')
    parser.add_argument('--release-dir', default='')
    parser.add_argument('--openai-key-file', type=Path)
    parser.add_argument('--listener-password-file', type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Output already exists; configuration is never overwritten')
    for value in (args.hostname, args.image, args.release_dir):
        if any(c in value for c in '\r\n\x00'):
            parser.error('Configuration must be single-line')
    password = args.listener_password_file.read_text().strip() if args.listener_password_file else secrets.token_urlsafe(24)
    if len(password) < 20 or any(c in password for c in '\r\n\x00'):
        parser.error('Listener password needs at least 20 single-line characters')
    if shutil.which('htpasswd') is None:
        parser.error('htpasswd is required; on the approved Linux host install apache2-utils, or prepare this on the Mac')
    hashed = subprocess.run(['htpasswd', '-niBC', '12', 'listener'], input=password + '\n' + password + '\n',
                            text=True, capture_output=True, check=True).stdout.strip().split(':', 1)[1]
    api_key = args.openai_key_file.read_text().strip() if args.openai_key_file else ''
    if any(c.isspace() for c in api_key):
        parser.error('OpenAI key must be a single token')
    proxy = secrets.token_urlsafe(48)
    session = secrets.token_urlsafe(48)
    os.umask(0o077)
    args.output.mkdir(parents=True, mode=0o700)
    files = {
        '.env': f'RESONANT_IMAGE={args.image}\nRESONANT_HOSTNAME={args.hostname}\nRESONANT_RELEASE_DIR={args.release_dir}\nRESONANT_DATA_ROOT=/srv/resonant\nRESONANT_DAILY_PROMPT_LIMIT=30\nRESONANT_JOB_TIMEOUT_SECONDS=360\n',
        'app.env': f'AUTODJ_OPENAI_API_DEV_KEY={api_key}\nRESONANT_PROXY_TOKEN={proxy}\nRESONANT_SESSION_SECRET={session}\n',
        'caddy.env': f'RESONANT_ACCESS_USER=listener\nRESONANT_ACCESS_PASSWORD_HASH={hashed}\nRESONANT_PROXY_TOKEN={proxy}\n',
        'listener-password.txt': password + '\n',
    }
    for name, data in files.items():
        (args.output / name).write_text(data)
        (args.output / name).chmod(0o600)
    print('Private configuration generated (mode 600); no secret values displayed. Fill any empty hostname/image/release/OpenAI fields before activation. Keep listener-password.txt local; never upload it with the runtime.')


if __name__ == '__main__':
    main()
