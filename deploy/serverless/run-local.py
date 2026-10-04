#!/usr/bin/env python3
"""Bounded offline Linux probe with read-only artifact mounts and host RAM guard."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
import uuid

ROOT=Path(__file__).resolve().parents[2]


def run(context, output, action, image='resonant-lambda:dependencies'):
    import psutil
    context=context.resolve();output=output.resolve()
    if not re.fullmatch(r'resonant-lambda:[a-z0-9-]+',image):raise ValueError('Use a task-owned image tag')
    if not context.is_relative_to(ROOT/'output/serverless-build') or not (context/'identity.json').is_file():
        raise ValueError('Use a prepared context inside output/serverless-build')
    if not output.is_relative_to(ROOT/'output') or output.exists():
        raise ValueError('Choose a new output path inside output/')
    if psutil.virtual_memory().available < 2*1024**3 or shutil.disk_usage(ROOT).free < 4*1024**3:
        raise RuntimeError('Insufficient free host memory or disk for the bounded probe')
    output.parent.mkdir(parents=True,exist_ok=True)
    name='resonant-lambda-probe-'+uuid.uuid4().hex[:10]
    command=['docker','run','--name',name,'--platform','linux/amd64','--network','none','--read-only',
             '--tmpfs','/tmp:rw,nosuid,nodev,size=512m','--memory','4g','--memory-swap','4g','--cpus','2',
             '--pids-limit','128','--user','10001:10001','--mount',f'type=bind,src={context},dst=/opt/resonant,readonly',
             '--entrypoint','/usr/bin/timeout',image,'--signal=KILL','300','python',
             'benchmark.py' if action=='text' else ('/probe.py' if action in {'worker','ric'} else 'verify.py')]
    if action in {'worker','ric'}:
        probe='integration_probe.py' if action=='worker' else 'ric_probe.py'
        command[2:2]=['--mount',f'type=bind,src={Path(__file__).parent / probe},dst=/probe.py,readonly']
    if action=='ric':
        command[2:2]=['--mount',f'type=bind,src={ROOT / "output/serverless-build/aws-lambda-rie"},dst=/aws-lambda-rie,readonly']
    record={'action':action,'network':'none','memoryLimitGiB':4,'swapLimitGiB':0,'cpus':2,
            'timeoutSeconds':300,'hostAvailableFloorMiB':768,'awsLatencyMeasurement':False,'stopReason':None}
    started=time.monotonic();minimum=psutil.virtual_memory().available
    with output.with_suffix('.log').open('x') as log:
        process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
        try:
            while process.poll() is None:
                available=psutil.virtual_memory().available;minimum=min(minimum,available)
                if available < 768*1024**2 or time.monotonic()-started>330:
                    record['stopReason']='host_memory_floor' if available<768*1024**2 else 'wall_deadline'
                    subprocess.run(['docker','kill',name],capture_output=True,timeout=15)
                    process.wait(timeout=20)
                    break
                time.sleep(2)
            record['exitCode']=process.returncode
            observed=subprocess.run(['docker','inspect','--format','{{json .State}}',name],capture_output=True,text=True,timeout=15)
            if observed.returncode==0:
                state=json.loads(observed.stdout)
                record['oomKilled']=state.get('OOMKilled')
                record['containerExitCode']=state.get('ExitCode')
        finally:
            if process.poll() is None:
                subprocess.run(['docker','kill',name],capture_output=True,timeout=15)
                process.wait(timeout=20)
            subprocess.run(['docker','rm',name],capture_output=True,timeout=15)
    record['wallSeconds']=time.monotonic()-started
    record['minimumHostAvailableMiB']=minimum/1024**2
    output.write_text(json.dumps(record,indent=2)+'\n');output.chmod(0o600)
    print(json.dumps(record))
    return record['exitCode']


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--context',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--action',choices=['verify','text','worker','ric'],required=True)
    parser.add_argument('--image',default='resonant-lambda:dependencies')
    args=parser.parse_args()
    raise SystemExit(run(args.context,args.output,args.action,args.image))
