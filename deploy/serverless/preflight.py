#!/usr/bin/env python3
"""Read-only AWS preflight. Exact selected account/profile; no implicit default."""
import argparse
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def aws(*args):
    result = subprocess.run(['aws','--profile','manueldev','--region','us-east-2',*args,'--output','json'],
                            capture_output=True, text=True, timeout=45)
    if result.returncode:
        raise RuntimeError('Selected-profile AWS read failed; inspect permissions privately')
    return json.loads(result.stdout)


def main():
    # File is private and must never be echoed. Schema is checked explicitly.
    target = json.loads((ROOT/'output/cloud-preparation/aws-target.json').read_text())
    identity = aws('sts','get-caller-identity')
    account = target.get('account_id')
    if not account or identity['Account'] != account:
        raise ValueError('Selected AWS account does not match the recorded target')
    settings = aws('lambda','get-account-settings')
    quota = settings['AccountLimit']['ConcurrentExecutions']
    return {'profile':'manueldev','accountSuffix':account[-4:],'region':'us-east-2',
            'concurrency':quota,'reservedCapacityReady':quota>=106,
            'requiredQuotaRequest':1001 if quota<106 else None,'mutations':0,
            'cloudfrontFreeEligibility':'unverified','memoryEligibility':'unverified'}


if __name__=='__main__':
    print(json.dumps(main()))
