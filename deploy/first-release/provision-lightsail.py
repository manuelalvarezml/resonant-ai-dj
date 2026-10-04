#!/usr/bin/env python3
"""Explicit-account Lightsail preparation. Default is an offline plan; --apply spends money."""
import argparse
import base64
import ipaddress
import json
import os
import re
import subprocess
import time
from pathlib import Path

TAG = {'key': 'managedBy', 'value': 'resonant-first-release'}


def aws_environment():
    env = os.environ.copy()
    # Do not accidentally use job/session/static credentials from the shell.
    for key in list(env):
        if not key.startswith('AWS_'):
            continue
        env.pop(key, None)
    env['AWS_EC2_METADATA_DISABLED'] = 'true'
    env['AWS_PAGER'] = ''
    return env


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', required=True)
    parser.add_argument('--account-id', required=True)
    parser.add_argument('--region', required=True)
    parser.add_argument('--zone', required=True)
    parser.add_argument('--instance', required=True)
    parser.add_argument('--keypair', required=True)
    parser.add_argument('--public-key-file', type=Path, help='Optional new RSA public key to import, never a private key')
    parser.add_argument('--blueprint', required=True)
    parser.add_argument('--bundle', required=True)
    parser.add_argument('--admin-cidr', required=True)
    parser.add_argument('--accepted-monthly-usd', type=float, required=True)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args(argv)
    if args.profile == 'default' or not re.fullmatch('[A-Za-z0-9_.@-]+', args.profile):
        parser.error('Name the new personal profile explicitly; default is prohibited')
    if not re.fullmatch('[0-9]{12}', args.account_id):
        parser.error('Use the exact full 12-digit personal AWS account ID')
    if not re.fullmatch('[a-z]{2}-[a-z]+-[0-9]', args.region) or args.zone not in [args.region + letter for letter in 'abcdef']:
        parser.error('Region and availability zone must agree')
    for value in (args.instance, args.keypair, args.blueprint, args.bundle):
        if not re.fullmatch('[A-Za-z0-9_.-]+', value):
            parser.error('Invalid AWS resource identifier')
    network = ipaddress.ip_network(args.admin_cidr, strict=True)
    if network.version != 4 or network.prefixlen != 32 or network.is_private or network.is_loopback:
        parser.error('SSH requires the owner current public IPv4 /32')
    if not 0 < args.accepted_monthly_usd < 1000:
        parser.error('Provide the explicitly accepted monthly instance budget')
    if args.public_key_file:
        if args.public_key_file.is_symlink() or not args.public_key_file.is_file():
            parser.error('RSA public key must be a regular file')
        try:
            fields = args.public_key_file.read_text().strip().split()
            raw = base64.b64decode(fields[1], validate=True)
            position, parts = 0, []
            for _ in range(3):
                size = int.from_bytes(raw[position:position + 4], 'big')
                position += 4
                parts.append(raw[position:position + size])
                position += size
            if (fields[0] != 'ssh-rsa' or parts[0] != b'ssh-rsa' or position != len(raw)
                    or int.from_bytes(parts[2], 'big').bit_length() < 3072):
                raise ValueError('Invalid/short RSA public key')
        except (ValueError, IndexError, UnicodeError):
            parser.error('Lightsail import requires an ssh-rsa public key with at least 3072 bits')
    return args


def main(argv=None):
    args = parse_args(argv)
    plan = {'mode': 'APPLY' if args.apply else 'OFFLINE PLAN ONLY', 'profile': args.profile, 'accountSuffix': args.account_id[-4:],
            'region': args.region, 'zone': args.zone, 'instance': args.instance, 'bundle': args.bundle,
            'blueprint': args.blueprint, 'keypair': args.keypair, 'importPublicKey': bool(args.public_key_file), 'sshSource': args.admin_cidr,
            'acceptedMonthlyInstanceUSD': args.accepted_monthly_usd,
            'resources': ['one instance', 'one attached static IPv4'],
            'notIncludedInBudget': ['tax', 'usage overages', 'OpenAI', 'optional backup/snapshot'],
            'ports': ['22 only owner IPv4 /32', '80 and 443 public TCP; 443 public UDP'],
            'accountGuard': 'STS exact-account match before any mutation; no default/static credential fallback'}
    print(json.dumps(plan, indent=2))
    if not args.apply:
        return
    prefix = ['aws', '--profile', args.profile, '--region', args.region, '--output', 'json', '--no-cli-pager']
    def call(*command):
        completed = subprocess.run(prefix + list(command), env=aws_environment(), text=True, capture_output=True, check=True)
        return json.loads(completed.stdout or '{}')
    if call('sts', 'get-caller-identity')['Account'] != args.account_id:
        raise SystemExit('AWS account mismatch. No resources changed.')
    bundles = call('lightsail', 'get-bundles', '--include-inactive')['bundles']
    chosen = next((b for b in bundles if b['bundleId'] == args.bundle), None)
    if not chosen or not chosen['isActive'] or chosen['ramSizeInGb'] < 8 or chosen['diskSizeInGb'] < 30 or chosen['price'] > args.accepted_monthly_usd:
        raise SystemExit('Bundle availability, RAM/disk or accepted budget check failed. No resources changed.')
    if chosen.get('supportedPlatforms') and 'LINUX_UNIX' not in chosen['supportedPlatforms']:
        raise SystemExit('Choose a Linux bundle. No resources changed.')
    if chosen.get('publicIpv4AddressCount', 0) < 1:
        raise SystemExit('Choose a bundle including public IPv4; IPv6-only bundles are not supported. No resources changed.')
    blueprints = call('lightsail', 'get-blueprints')['blueprints']
    blueprint = next((b for b in blueprints if b['blueprintId'] == args.blueprint), None)
    # bootstrap-host.sh deliberately supports exactly this OS/architecture.
    # Do not buy a host that the next step would immediately reject.
    if (not blueprint or not blueprint['isActive'] or blueprint['blueprintId'] != 'ubuntu_24_04'
            or blueprint.get('platform', 'LINUX_UNIX') != 'LINUX_UNIX'
            or (blueprint.get('version') and not blueprint['version'].startswith('24.04'))):
        raise SystemExit('Choose the active ubuntu_24_04 x86_64 blueprint. No resources changed.')
    instances = call('lightsail', 'get-instances')['instances']
    instance = next((i for i in instances if i['name'] == args.instance), None)
    if instance and TAG not in instance.get('tags', []):
        raise SystemExit('Existing instance is not tagged as owned by this deployment. No resources changed.')
    if instance and (instance.get('bundleId') != args.bundle or instance.get('blueprintId') != args.blueprint):
        raise SystemExit('Existing instance differs from requested bundle/blueprint. No resources changed.')
    if instance and instance.get('sshKeyName') != args.keypair:
        raise SystemExit('Existing instance uses a different SSH key. No resources changed.')
    address_name = args.instance + '-ip'
    addresses = call('lightsail', 'get-static-ips')['staticIps']
    address = next((ip for ip in addresses if ip['name'] == address_name), None)
    if address and address.get('attachedTo') not in (None, '', args.instance):
        raise SystemExit('Named static IP belongs to another instance. No resources changed.')
    pairs = call('lightsail', 'get-key-pairs')['keyPairs']
    keypair = next((key for key in pairs if key['name'] == args.keypair), None)
    if keypair and args.public_key_file and TAG not in keypair.get('tags', []):
        raise SystemExit('Existing key name is not owned by this deployment; choose a new scoped name. No resources changed.')
    if not keypair:
        if not args.public_key_file:
            raise SystemExit('Named key pair does not exist; supply the prepared RSA public key. No resources changed.')
        public_key = base64.b64encode(args.public_key_file.read_bytes()).decode('ascii')
        call('lightsail', 'import-key-pair', '--key-pair-name', args.keypair, '--public-key-base64', public_key,
             '--tags', json.dumps([TAG]))
    if not instance:
        call('lightsail', 'create-instances', '--instance-names', args.instance, '--availability-zone', args.zone,
             '--blueprint-id', args.blueprint, '--bundle-id', args.bundle, '--key-pair-name', args.keypair,
             '--tags', json.dumps([TAG]))
    for _ in range(60):
        instance = call('lightsail', 'get-instance', '--instance-name', args.instance)['instance']
        if instance['state']['name'] == 'running':
            break
        time.sleep(5)
    else:
        raise SystemExit('Instance did not reach running in 5 minutes. Inspect named instance; do not create another.')
    ports = [{'fromPort': 22, 'toPort': 22, 'protocol': 'tcp', 'cidrs': [args.admin_cidr], 'ipv6Cidrs': []},
             {'fromPort': 80, 'toPort': 80, 'protocol': 'tcp', 'cidrs': ['0.0.0.0/0'], 'ipv6Cidrs': []},
             {'fromPort': 443, 'toPort': 443, 'protocol': 'tcp', 'cidrs': ['0.0.0.0/0'], 'ipv6Cidrs': []},
             {'fromPort': 443, 'toPort': 443, 'protocol': 'udp', 'cidrs': ['0.0.0.0/0'], 'ipv6Cidrs': []}]
    call('lightsail', 'put-instance-public-ports', '--instance-name', args.instance, '--port-infos', json.dumps(ports))
    if not address:
        call('lightsail', 'allocate-static-ip', '--static-ip-name', address_name)
    if not address or address.get('attachedTo') != args.instance:
        call('lightsail', 'attach-static-ip', '--static-ip-name', address_name, '--instance-name', args.instance)
    address = call('lightsail', 'get-static-ip', '--static-ip-name', address_name)['staticIp']
    print(json.dumps({'provisioned': True, 'instance': args.instance, 'staticIpName': address_name, 'publicIPv4': address['ipAddress'],
                      'monthlyBundleUSD': chosen['price'], 'next': 'Verify SSH host key, then run bootstrap-host.sh --apply on this host.'}, indent=2))


if __name__ == '__main__':
    main()
