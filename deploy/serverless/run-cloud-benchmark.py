#!/usr/bin/env python3
"""Explicit paid probe runner; default prints a plan and never invokes AWS."""
import argparse
import base64
import json
import os
from pathlib import Path
import re
import time
import uuid

ROOT = Path(__file__).resolve().parents[2]
RATE = .0000166667


def report_metrics(encoded):
    log = base64.b64decode(encoded).decode('utf-8', errors='replace')
    fields = {}
    for field, key in [('Billed Duration', 'billedMilliseconds'), ('Max Memory Used', 'maxMemoryMB'), ('Init Duration', 'initMilliseconds')]:
        match = re.search(re.escape(field) + r':\s*([0-9.]+)', log)
        if match:
            fields[key] = float(match[1])
    if 'billedMilliseconds' not in fields:
        raise ValueError('Missing Lambda billing report')
    return fields


def plan():
    return {'profile':'manueldev','region':'us-east-2','memoryMB':[8192,6144,4096],
            'coldTrialsPerMemory':5,'invocationsPerTrial':3,'maximumInvocations':45,
            'timeoutSeconds':360,'providerCalls':0,'audioInference':False,
            'workerComputeAtAll45Times360SecondsAnd8GiB':45*360*8*RATE,
            'note':'Additional initialization, ECR and logs billed separately. Plan only unless --execute.'}


def run(args):
    import boto3
    from botocore.config import Config
    target = json.loads((ROOT/'output/cloud-preparation/aws-target.json').read_text())
    if target['profile'] != 'manueldev' or target['region'] != 'us-east-2':
        raise ValueError('Recorded target configuration changed')
    session = boto3.Session(profile_name='manueldev', region_name='us-east-2')
    if session.client('sts').get_caller_identity()['Account'] != target['account_id']:
        raise ValueError('Wrong AWS account')
    client = session.client('lambda', config=Config(connect_timeout=5,read_timeout=400,retries={'total_max_attempts':1}))
    account = client.get_account_settings()['AccountLimit']['ConcurrentExecutions']
    if account < 106:
        raise ValueError('Concurrency quota prerequisite is not met')
    fn = client.get_function(FunctionName=args.function)
    cfg = fn['Configuration']
    if (cfg['PackageType'] != 'Image' or cfg['Architectures'] != ['x86_64']
        or cfg['Timeout'] != 360 or cfg.get('EphemeralStorage',{}).get('Size') != 512
        or cfg.get('ImageConfigResponse',{}).get('ImageConfig',{}).get('Command') != ['runtime.benchmark_handler.handler']
        or fn.get('Tags',{}).get('Purpose') != 'bounded-text-benchmark'
        or fn.get('Concurrency',{}).get('ReservedConcurrentExecutions') != 1
        or not fn['Code'].get('ResolvedImageUri','').endswith('@sha256:'+args.image_digest)):
        raise ValueError('Function is not the reviewed isolated benchmark')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Refuse overwrite/resume; ambiguous responses are never retried automatically.
    with args.output.open('x') as file:
        file.write('{}\n')
    args.output.chmod(0o600)
    record = {'plan':plan(),'function':args.function,'imageDigest':args.image_digest,'attempts':[],'status':'running'}
    record['requestedTrial']={'memoryMB':args.memory,'coldTrialsPerMemory':args.trials,'maximumInvocations':len(args.memory)*args.trials*3,'computeLimitUSD':args.compute_limit}
    def save():
        temporary = args.output.with_suffix('.tmp')
        temporary.write_text(json.dumps(record,indent=2)+'\n')
        temporary.chmod(0o600)
        temporary.replace(args.output)
    charged_compute = 0
    try:
        baseline = None
        for memory in args.memory:
            for trial in range(args.trials):
                environment = dict(cfg.get('Environment',{}).get('Variables',{}))
                environment['RESONANT_PROBE_EPOCH'] = str(uuid.uuid4())
                client.update_function_configuration(FunctionName=args.function,MemorySize=memory,Environment={'Variables':environment})
                client.get_waiter('function_updated_v2').wait(FunctionName=args.function,WaiterConfig={'Delay':5,'MaxAttempts':60})
                version = client.publish_version(FunctionName=args.function,Description='Bounded generic text probe')['Version']
                for sample in range(3):
                    if len(record['attempts']) >= 45 or charged_compute + (memory/1024)*400*RATE > args.compute_limit:
                        raise RuntimeError('Configured invocation or compute stop threshold reached')
                    row = {'memoryMB':memory,'trial':trial,'sample':sample,'version':version,'outcome':'dispatching'}
                    record['attempts'].append(row);save()
                    response = client.invoke(FunctionName=args.function,Qualifier=version,InvocationType='RequestResponse',
                                             LogType='Tail',Payload=b'{"probe":"muq-text-v1"}')
                    body = response['Payload']
                    try:result=json.loads(body.read(65537))
                    finally:body.close()
                    if response.get('FunctionError'):
                        row.update(outcome='function_error', errorType=result.get('errorType'), errorMessage=result.get('errorMessage','')[:1000])
                        try:
                            metrics=report_metrics(response.get('LogResult',''))
                            cost=metrics['billedMilliseconds']/1000*(memory/1024)*RATE
                            charged_compute+=cost
                            row.update(metrics=metrics,computeUSD=cost)
                        except ValueError:pass
                        save()
                        raise RuntimeError('Benchmark function failed; stop before smaller memory tests')
                    metrics = report_metrics(response.get('LogResult',''))
                    if result.get('probe') != 'muq-text-v1' or result.get('modelLoads') != 1:
                        raise ValueError('Unexpected probe result')
                    if bool(result['coldModel']) != (sample == 0):
                        raise ValueError('Cold/warm environment did not match the trial; do not relabel it')
                    if baseline is None:baseline=result['vectorSha256']
                    if result['vectorSha256'] != baseline:
                        raise ValueError('Embedding hash changed across the benchmark')
                    cost = metrics['billedMilliseconds']/1000*(memory/1024)*RATE
                    charged_compute += cost
                    row.update(outcome='completed',result=result,metrics=metrics,computeUSD=cost)
                    save();print(json.dumps({'completed':len(record['attempts']),'memoryMB':memory,'cold':result['coldModel'],'computeUSD':charged_compute}),flush=True)
        record['status']='completed'
    except Exception:
        record['status']='stopped_review_required'
        save()
        raise RuntimeError('Probe stopped; review the saved sanitized run before any retry') from None
    finally:
        record['computeUSDObserved']=charged_compute
        save()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute',action='store_true')
    parser.add_argument('--function',default='resonant-text-probe-probe')
    parser.add_argument('--image-digest')
    parser.add_argument('--output',type=Path,default=ROOT/'output/serverless-benchmark/aws-run.json')
    parser.add_argument('--compute-limit',type=float,default=3.0)
    parser.add_argument('--memory',type=int,nargs='+',choices=[3008,4096,6144,8192],default=[8192,6144,4096])
    parser.add_argument('--trials',type=int,choices=range(1,6),default=5)
    args=parser.parse_args()
    if not args.execute:
        print(json.dumps(plan(),indent=2))
    else:
        if not re.fullmatch(r'resonant-text-probe[-a-z0-9]*',args.function):parser.error('Only a named Resonant probe function is allowed')
        if not args.image_digest or not re.fullmatch('[a-f0-9]{64}',args.image_digest):parser.error('Exact reviewed ECR image digest required')
        if not 0 < args.compute_limit <= 3:parser.error('Compute stop threshold must be in (0,3] USD')
        run(args)
