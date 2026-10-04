"""Offline boundary regressions; never creates resources or invokes model/provider APIs."""
import contextlib
import base64
import copy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DeploymentTests(unittest.TestCase):
    def test_aws_environment_drops_other_accounts_and_endpoints(self):
        provision = load('provision-lightsail')
        with patch.dict(os.environ, {'AWS_PROFILE': 'job', 'AWS_ACCESS_KEY_ID': 'job-key', 'AWS_CONFIG_FILE': '/job/config',
                                     'AWS_ENDPOINT_URL_STS': 'http://untrusted', 'AWS_SHARED_CREDENTIALS_FILE': '/job/keys'}):
            env = provision.aws_environment()
        self.assertEqual({k: v for k, v in env.items() if k.startswith('AWS_')},
                         {'AWS_EC2_METADATA_DISABLED': 'true', 'AWS_PAGER': ''})

    def provision_args(self, blueprint='ubuntu_24_04'):
        return ['--profile', 'manueldev', '--account-id', '123456789012', '--region', 'us-east-2', '--zone', 'us-east-2a',
                '--instance', 'resonant-test', '--keypair', 'test', '--blueprint', blueprint, '--bundle', 'large_3_0',
                '--admin-cidr', '8.8.8.8/32', '--accepted-monthly-usd', '44']

    def test_provision_default_is_entirely_offline(self):
        with patch('subprocess.run') as run, contextlib.redirect_stdout(io.StringIO()):
            load('provision-lightsail').main(self.provision_args())
        run.assert_not_called()

    def test_public_key_import_accepts_rsa_and_rejects_other_key_types(self):
        provision = load('provision-lightsail')
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / 'test.pub'
            parts = [b'ssh-rsa', bytes.fromhex('010001'), b'\x00\x80' + b'\x01' * 511]
            blob = b''.join(len(part).to_bytes(4, 'big') + part for part in parts)
            file.write_text('ssh-rsa ' + base64.b64encode(blob).decode() + ' test\n')
            provision.parse_args(self.provision_args() + ['--public-key-file', str(file)])
            file.write_text('ssh-ed25519 AAAA test\n')
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                provision.parse_args(self.provision_args() + ['--public-key-file', str(file)])

    def test_account_mismatch_stops_before_lightsail(self):
        commands = []
        def run(command, **kwargs):
            commands.append(command)
            return subprocess.CompletedProcess(command, 0, json.dumps({'Account': '999999999999'}), '')
        with patch('subprocess.run', side_effect=run), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(SystemExit, 'account mismatch'):
                load('provision-lightsail').main(self.provision_args() + ['--apply'])
        self.assertEqual(len(commands), 1)
        self.assertIn('get-caller-identity', commands[0])

    def test_unsupported_os_stops_before_paid_creation(self):
        for blueprint in ('ubuntu_22_04', 'ubuntu_24_04_arm64'):
            commands = []
            def run(command, **kwargs):
                commands.append(command)
                if 'get-caller-identity' in command:
                    data = {'Account': '123456789012'}
                elif 'get-bundles' in command:
                    data = {'bundles': [{'bundleId': 'large_3_0', 'isActive': True, 'ramSizeInGb': 8,
                                         'diskSizeInGb': 160, 'price': 44, 'publicIpv4AddressCount': 1}]}
                elif 'get-blueprints' in command:
                    data = {'blueprints': [{'blueprintId': blueprint, 'isActive': True}]}
                else:
                    self.fail('Unexpected command before OS validation: ' + str(command))
                return subprocess.CompletedProcess(command, 0, json.dumps(data), '')
            with self.subTest(blueprint=blueprint), patch('subprocess.run', side_effect=run), contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(SystemExit, 'ubuntu_24_04 x86_64'):
                    load('provision-lightsail').main(self.provision_args(blueprint) + ['--apply'])
            self.assertEqual(len(commands), 3)

    def test_runtime_inventory_rejects_extra_secret_and_changed_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            (root / 'server.js').write_text('original')
            manifest = {'schema': 'resonant/runtime-source/1', 'files': [{'path': 'server.js', 'bytes': 8,
                        'sha256': hashlib.sha256(b'original').hexdigest()}]}
            manifest['sourceDigest'] = hashlib.sha256(json.dumps(manifest, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
            (root / 'runtime-source.json').write_text(json.dumps(manifest))
            verify = load('verify-runtime').verify
            verify(root)
            (root / 'secret.env').write_text('credential')
            with self.assertRaisesRegex(ValueError, 'Unmanifested'):
                verify(root)
            (root / 'secret.env').unlink()
            (root / 'server.js').write_text('tampered')
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                verify(root)

    def test_model_inventory_rejects_extra_files_and_symlinks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            (root / 'asset').write_bytes(b'x')
            manifest = {'model_id': 'OpenMuQ/MuQ-MuLan-large', 'revision': '2e01c796b71dca71b45251384c04cd7b237c9020',
                        'assets': [{'path': 'asset', 'size_bytes': 1, 'sha256': hashlib.sha256(b'x').hexdigest()}]}
            (root / 'manifest.json').write_text(json.dumps(manifest))
            verify = load('verify-models').verify
            verify(root)
            (root / 'extra').write_bytes(b'secret')
            with self.assertRaisesRegex(ValueError, 'Unmanifested'):
                verify(root)
            (root / 'extra').unlink()
            (root / 'alias').symlink_to(root / 'asset')
            with self.assertRaisesRegex(ValueError, 'symlink'):
                verify(root)

    def test_activation_requires_full_matching_linux_evidence(self):
        release = {'releaseId': 'a' * 64, 'trackCount': 187}
        evidence = {'schema': 'resonant/linux-acceptance/1', 'releaseId': 'a' * 64, 'imageId': 'sha256:' + 'b' * 64,
                    'modelManifestSHA256': 'c' * 64, 'network': 'disabled', 'openaiCalls': 0,
                    'runtime': {'imports': 'passed', 'machine': 'x86_64', 'platform': 'Linux-6.8', 'cuda': None,
                                'textSmoke': {'vectorsEqual': True}},
                    'planner': {'result': {'tracks': 187, 'parity_cases_passed': 60,
                                          'profiles': ['reference', 'music2emo', 'musicnn-dance', 'supervised', 'quality']}}}
        verify = load('activate').verify_evidence
        verify(evidence, release)
        for section, key, value in (('runtime', 'machine', 'arm64'), ('runtime', 'imports', 'failed'),
                                    ('planner', 'result', {}), (None, 'releaseId', 'd' * 64), (None, 'network', 'enabled')):
            broken = copy.deepcopy(evidence)
            (broken[section] if section else broken)[key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'complete Linux acceptance'):
                verify(broken, release)

    def test_config_refuses_world_readable_or_symlink_secrets(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            file = root / 'app.env'
            file.write_text('KEY=value\n')
            file.chmod(0o644)
            with self.assertRaisesRegex(ValueError, 'mode 600'):
                load('activate').read_env(file)
            file.chmod(0o600)
            self.assertEqual(load('activate').read_env(file), {'KEY': 'value'})
            (root / 'alias').symlink_to(file)
            with self.assertRaisesRegex(ValueError, 'mode 600'):
                load('activate').read_env(root / 'alias')

    def test_prepared_config_is_not_a_successful_previous_activation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            previous = root / 'releases' / ('a' * 64)
            previous.mkdir(parents=True)
            config = {'RESONANT_IMAGE': 'resonant:prepared', 'RESONANT_RELEASE_DIR': str(previous)}
            check = load('activate').has_previous_activation
            self.assertFalse(check(config, root))
            (root / 'current').symlink_to(previous)
            self.assertTrue(check(config, root))
            other = root / 'releases' / ('b' * 64)
            other.mkdir()
            config['RESONANT_RELEASE_DIR'] = str(other)
            self.assertFalse(check(config, root))

    def test_https_verifier_never_sends_password_to_http_or_url_credentials(self):
        verify = load('verify-https').verify
        for origin in ('http://example.com', 'https://other:password@example.com', 'https://example.com/path', 'https://example.com:8443'):
            with self.subTest(origin=origin), patch('http.client.HTTPSConnection') as connection:
                with self.assertRaisesRegex(ValueError, 'exact HTTPS origin'):
                    verify(origin, 'listener', 'password', 'a' * 64)
                connection.assert_not_called()

    def test_https_verifier_consumes_production_contract_without_model_calls(self):
        calls = []
        track = {'id': 'a' * 64, 'sourceVersion': 'a' * 64}
        class Response:
            def __init__(self, status, body, headers=None):
                self.status, self.body, self.headers = status, body, headers or {}
            def read(self, _):
                return self.body if isinstance(self.body, bytes) else json.dumps(self.body).encode()
            def getheaders(self):
                return list(self.headers.items())
        class Connection:
            def __init__(self, host, **kwargs):
                self.host = host
            def request(self, method, path, body=None, headers=None):
                calls.append((method, path))
                if 'Authorization' not in headers:
                    self.response = Response(401, {}, {'WWW-Authenticate': 'Basic realm="private"'})
                elif path == '/':
                    self.response = Response(200, b'<html>', {'Content-Type': 'text/html', 'Strict-Transport-Security': 'max-age=31536000',
                                             'Set-Cookie': '__Host-resonant_session=value; Secure; HttpOnly; SameSite=Strict'})
                elif path == '/healthz':
                    self.response = Response(200, {'release': 'b' * 64, 'tracks': 1})
                elif path == '/config.json':
                    self.response = Response(200, {'edition': 'web'})
                elif path == '/api/v1/tracks':
                    self.response = Response(200, {'tracks': [track], 'next_cursor': None})
                elif path == '/api/v1/playback-sessions':
                    self.response = Response(403, {}) if headers['Origin'] != 'https://music.example.com' else Response(200, {'url': 'https://music.example.com/api/web/audio/' + track['id']})
                elif path.startswith('/api/web/audio/') or path == '/api/web/mix/audio':
                    if method == 'HEAD':
                        self.response = Response(200, b'', {'Content-Length': '100', 'Accept-Ranges': 'bytes'})
                    elif headers.get('Range') == 'bytes=100-':
                        self.response = Response(416, {})
                    else:
                        self.response = Response(206, b'x' * 32, {'Content-Range': 'bytes 0-31/100'})
                elif path == '/api/web/mix':
                    self.response = Response(200, {'transitions': [{}, {}]})
                else:
                    self.response = Response(404, {})
            def getresponse(self):
                return self.response
            def close(self):
                pass
        with patch('http.client.HTTPSConnection', Connection):
            result = load('verify-https').verify('https://music.example.com', 'listener', 'private-password', 'b' * 64)
        self.assertEqual(result['status'], 'passed')
        self.assertEqual(result['tracks'], 1)
        self.assertEqual(result['openaiCalls'], 0)
        self.assertFalse(any(path == '/api/local/playlist' for _, path in calls))
        self.assertNotIn('private-password', json.dumps(result))


if __name__ == '__main__':
    unittest.main()
