#!/usr/bin/env python3
"""Verify deployed TLS, shared login, catalog and byte ranges. Never calls a planner/model."""
import argparse
import base64
import datetime
import http.client
import json
from pathlib import Path
import re
import ssl
from urllib.parse import urlsplit, quote


def verify(origin, username, password, expected_release):
    parsed = urlsplit(origin)
    if (parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password
            or parsed.path not in ('', '/') or parsed.query or parsed.fragment or parsed.port not in (None, 443)):
        raise ValueError('Use the exact HTTPS origin on port 443')
    origin = 'https://' + parsed.hostname
    authorization = 'Basic ' + base64.b64encode((username + ':' + password).encode()).decode()

    def request(path, method='GET', headers=None, body=None, authenticated=True):
        if not path.startswith('/') or path.startswith('//'):
            raise ValueError('Requests must stay at the configured origin')
        connection = http.client.HTTPSConnection(parsed.hostname, context=ssl.create_default_context(), timeout=30)
        values = {'Authorization': authorization} if authenticated else {}
        values.update(headers or {})
        data = None if body is None else json.dumps(body).encode()
        if data is not None:
            values['Content-Type'] = 'application/json'
        try:
            connection.request(method, path, body=data, headers=values)
            response = connection.getresponse()
            payload = response.read(20 * 1024 * 1024 + 1)
            if len(payload) > 20 * 1024 * 1024:
                raise ValueError('Unexpectedly large verification response')
            # Redirects are deliberately not followed, so credentials cannot
            # leak to another host and a redirect cannot mask a route failure.
            return response.status, dict((k.lower(), v) for k, v in response.getheaders()), payload
        finally:
            connection.close()

    def expect(path, status=200, **kwargs):
        result = request(path, **kwargs)
        if result[0] != status:
            raise ValueError(f'Expected HTTP {status} at {path}; received {result[0]}')
        return result

    checks = []
    for path in ('/', '/healthz', '/config.json', '/api/v1/tracks', '/api/web/mix', '/api/web/mix/audio'):
        _, headers, _ = expect(path, 401, authenticated=False)
        if 'basic ' not in headers.get('www-authenticate', '').lower():
            raise ValueError('Shared login challenge is missing')
    checks.append('TLS certificate verification and unauthenticated route denial')
    _, headers, _ = expect('/')
    if 'text/html' not in headers.get('content-type', '') or 'max-age=' not in headers.get('strict-transport-security', ''):
        raise ValueError('Missing HTML/HSTS response')
    cookie = headers.get('set-cookie', '')
    if not all(word in cookie.lower() for word in ('__host-resonant_session=', 'secure', 'httponly', 'samesite=strict')):
        raise ValueError('Secure session cookie is missing')
    session_headers = {'Cookie': cookie.split(';', 1)[0], 'Origin': origin}
    health = json.loads(expect('/healthz')[2])
    if health.get('release') != expected_release:
        raise ValueError('Serving a different release than expected')
    if json.loads(expect('/config.json')[2]).get('edition') != 'web':
        raise ValueError('Serving the wrong app edition')
    tracks, cursor = [], None
    for _ in range(100):
        page = json.loads(expect('/api/v1/tracks' + ('?cursor=' + quote(str(cursor), safe='') if cursor else ''))[2])
        tracks.extend(page['tracks'])
        cursor = page.get('next_cursor')
        if not cursor:
            break
    else:
        raise ValueError('Catalog pagination did not finish')
    if not tracks or len({t['id'] for t in tracks}) != len(tracks) or len(tracks) != health.get('tracks'):
        raise ValueError('Empty/duplicate catalog')
    checks.append('Authenticated web edition, exact release and full paginated catalog')
    for track in (tracks[0], tracks[len(tracks) // 2], tracks[-1]):
        body = {'track_id': track['id'], 'source_version': track['sourceVersion']}
        playback = json.loads(expect('/api/v1/playback-sessions', method='POST', headers=session_headers, body=body)[2])
        url = urlsplit(playback['url'])
        if 'https://' + url.netloc != origin or url.query or url.fragment:
            raise ValueError('Playback origin is not canonical')
        path = url.path
        expect(path, 401, authenticated=False, headers={'Range': 'bytes=0-31'})
        _, media_headers, _ = expect(path, method='HEAD')
        size = int(media_headers['content-length'])
        if media_headers.get('accept-ranges') != 'bytes':
            raise ValueError('Seeking header is missing')
        for interval in ('bytes=0-31', 'bytes=-32'):
            _, range_headers, payload = expect(path, 206, headers={'Range': interval})
            if len(payload) != 32 or not range_headers.get('content-range', '').endswith('/' + str(size)):
                raise ValueError('Incorrect audio byte range')
        expect(path, 416, headers={'Range': 'bytes=' + str(size) + '-'})
    checks.append('Three MP3s: authentication, HEAD, prefix/suffix and invalid ranges')
    expect('/api/v1/playback-sessions', 403, method='POST', headers={'Cookie': session_headers['Cookie'], 'Origin': 'https://untrusted.invalid'}, body=body)
    for path in ('/private/planner.json', '/release.json', '/app-status.json', '/prepare-web.html'):
        expect(path, 404)
    for path in ('/api/local/analyze', '/api/local/recovery', '/api/local/convert', '/api/mixes'):
        expect(path, 404, method='POST', headers=session_headers, body={})
    mix = json.loads(expect('/api/web/mix')[2])
    if len(mix['transitions']) != 2:
        raise ValueError('Expected one mix with two transition descriptions')
    if len(expect('/api/web/mix/audio', 206, headers={'Range': 'bytes=0-31'})[2]) != 32:
        raise ValueError('Mix byte range failed')
    checks.append('CSRF rejection, private/owner route denial and single two-transition mix')
    return {'schema': 'resonant/https-acceptance/1', 'verifiedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'origin': origin, 'releaseId': expected_release, 'tracks': len(tracks), 'status': 'passed', 'checks': checks,
            'openaiCalls': 0, 'limits': ['Does not test a live PlaylistIQ request, human listening, or mobile/browser behavior.']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--origin', required=True)
    parser.add_argument('--username', default='listener')
    parser.add_argument('--password-file', type=Path, required=True)
    parser.add_argument('--release-id', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.password_file.is_symlink() or not args.password_file.is_file() or args.password_file.stat().st_mode & 0o077:
        parser.error('Use a private mode-600 password file; never put the password in a command argument')
    if not re.fullmatch('[a-f0-9]{64}', args.release_id) or args.output.exists():
        parser.error('Use a valid release ID and a new evidence output path')
    result = verify(args.origin, args.username, args.password_file.read_text().strip(), args.release_id)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    args.output.chmod(0o600)
    print(json.dumps({'status': result['status'], 'tracks': result['tracks'], 'releaseId': result['releaseId']}))
