#!/usr/bin/env python3
"""Fresh-visitor login navigation and protected media acceptance; no AI calls."""
import argparse
import socket
import hashlib
import http.cookiejar
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[2]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, newurl):
        return None


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--origin")
    parser.add_argument("--candidate",type=Path,default=ROOT/"output/serverless-assets/candidate-1")
    parser.add_argument("--receipt",type=Path,default=ROOT/"output/serverless-cloud/acceptance/entry-smoke.json")
    parser.add_argument("--connect-via-cloudfront",action="store_true",help="Check custom-host TLS while local DNS is propagating")
    args=parser.parse_args()
    if args.connect_via_cloudfront:
        assert args.origin=="https://resonant.lat"
        resolve=socket.getaddrinfo
        socket.getaddrinfo=lambda host,*a,**kw:resolve("dl3pumk9rpbun.cloudfront.net" if host=="resonant.lat" else host,*a,**kw)
    os.umask(0o077)
    cloud = ROOT / 'output/serverless-cloud'
    outputs = json.loads((cloud / 'resonant-edge/outputs.json').read_text())['Stacks'][0]['Outputs']
    origin = 'https://' + next(row['OutputValue'] for row in outputs if row['OutputKey'] == 'Domain')
    if args.origin:
        assert args.origin in [origin, 'https://resonant.lat']
        origin=args.origin
    anonymous = urllib.request.build_opener(NoRedirect())
    cookies = http.cookiejar.CookieJar()
    signed = urllib.request.build_opener(NoRedirect(), urllib.request.HTTPCookieProcessor(cookies))
    checks = []

    def request(opener, path, body=None, headers=None):
        headers = {'Origin': origin, 'Content-Type': 'application/json', **(headers or {})}
        req = urllib.request.Request(origin + path, headers=headers,
            data=None if body is None else json.dumps(body).encode())
        try:
            with opener.open(req, timeout=30) as response:
                return response.status, response.headers, response.read(32 * 1024 * 1024)
        except urllib.error.HTTPError as error:
            return error.code, error.headers, error.read(65536)

    for path in ['/', '/index.html']:
        code, headers, _ = request(anonymous, path)
        assert code == 302 and headers['Location'] == '/login/index.html', (path, code)
    checks.append('fresh root and index redirect to login without signed cookies')
    for path, marker in [('/login/index.html', b'Library password'),
                         ('/login/login.js', b'/api/session/login'),
                         ('/login/style.css', b'')]:
        code, _, body = request(anonymous, path)
        assert code == 200 and marker in body, (path, code)
    checks.append('public login HTML, script and stylesheet load')
    plan = json.loads((args.candidate / 'upload-plan.json').read_text())
    mp3 = next(row for row in plan['uploads'] if row['key'].endswith('.mp3'))
    spectra = [row for row in plan['uploads'] if row['key'].startswith('library/spectra/v1/')]
    sampled_spectra = ([spectra[0], next(row for row in spectra if row['key'].endswith('/mix-house-example.json'))] if spectra else [])
    for row in sampled_spectra:
        assert request(anonymous, '/' + row['key'])[0] == 403
    for path in ['/library/current.json', '/' + mp3['key']]:
        assert request(anonymous, path)[0] == 403
        assert request(anonymous, path, headers={'Cookie': 'CloudFront-Key-Pair-Id=invalid; CloudFront-Policy=invalid; CloudFront-Signature=invalid'})[0] == 403
    checks.append('unsigned and invalid-cookie catalog/audio requests denied')
    password = (ROOT / 'output/cloud-config/first-release/listener-password.txt').read_text().strip()
    code, _, body = request(signed, '/api/session/login', {'password': password})
    assert code == 200, code
    csrf = json.loads(body)['csrf']
    try:
        for path, key in [('/', 'index.html'), ('/index.html', 'index.html'),
                          ('/library/current.json', 'library/current.json')]:
            code, _, body = request(signed, path)
            expected = next(row['sha256'] for row in plan['uploads'] if row['key'] == key)
            assert code == 200 and hashlib.sha256(body).hexdigest() == expected, (path, code)
        checks.append('fresh login opens exact app shell and protected catalog')
        code, _, body = request(signed, '/' + mp3['key'], headers={'Range': 'bytes=100000-132767'})
        with Path(mp3['localPath']).open('rb') as source:
            source.seek(100000)
            expected = source.read(32768)
        assert code == 206 and body == expected
        checks.append('authenticated MP3 seek matches original source bytes')
        for row in sampled_spectra:
            code, _, body = request(signed, '/' + row['key'])
            assert code == 200 and hashlib.sha256(body).hexdigest() == row['sha256']
            assert json.loads(body)['schema'] == 'resonant-spectrum/1'
        if sampled_spectra:
            checks.append('track and mix spectra protected; signed bytes match local measurements')
        assert request(signed, '/api/session')[0] == 200
    finally:
        code, _, _ = request(signed, '/api/session/logout', {}, {'x-resonant-csrf': csrf})
        assert code == 200
    assert request(signed, '/')[0] == 302
    checks.append('logout returns visitor to login')
    receipt = {'status': 'passed', 'origin':origin, 'transport':'CloudFront DNS override; custom-host TLS verified' if args.connect_via_cloudfront else 'public DNS', 'at': time.time(), 'checks': checks, 'openaiCalls': 0}
    args.receipt.write_text(json.dumps(receipt, indent=2))
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
