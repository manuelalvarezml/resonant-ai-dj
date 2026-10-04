#!/usr/bin/env python3
"""One isolated 120-second generic-text invocation with timed stack diagnostics."""
import base64,json,os,time,uuid
from pathlib import Path
import boto3
from botocore.config import Config
ROOT=Path(__file__).resolve().parents[2]
def main():
 os.umask(0o077)
 target=json.loads((ROOT/'output/cloud-preparation/aws-target.json').read_text())
 s=boto3.Session(profile_name='manueldev',region_name='us-east-2')
 assert s.client('sts').get_caller_identity()['Account']==target['account_id']
 c=s.client('lambda',config=Config(connect_timeout=5,read_timeout=180,retries={'total_max_attempts':1}))
 name='resonant-text-probe-probe';fn=c.get_function(FunctionName=name)
 assert fn['Tags']['Purpose']=='bounded-text-benchmark' and fn['Concurrency']['ReservedConcurrentExecutions']==1
 assert fn['Configuration']['MemorySize']==3008 and fn['Configuration']['PackageType']=='Image'
 image=json.loads((ROOT/'output/serverless-cloud/resonant-registry/image-20261003.json').read_text())
 assert fn['Code']['ResolvedImageUri']==image['imageUri']
 file=ROOT/'output/serverless-benchmark/aws-startup-diagnostic.json'
 with file.open('x') as f:f.write('{}')
 wrapper="import sys,faulthandler; faulthandler.enable(); faulthandler.dump_traceback_later(30,repeat=True); from awslambdaric.__main__ import main; main(['awslambdaric',sys.argv[1]])"
 c.update_function_configuration(FunctionName=name,Timeout=120,ImageConfig={'EntryPoint':['python','-c',wrapper],'Command':['runtime.benchmark_handler.handler']})
 c.get_waiter('function_updated_v2').wait(FunctionName=name,WaiterConfig={'Delay':5,'MaxAttempts':60})
 version=c.publish_version(FunctionName=name,Description='One 120-second startup diagnostic; no provider access')['Version']
 record={'function':name,'version':version,'timeoutSeconds':120,'memoryMB':3008,'maximumInvocations':1,'maximumComputeUSD':180*3008/1024*0.0000166667,'openaiCalls':0,'status':'dispatching'}
 file.write_text(json.dumps(record,indent=2));file.chmod(0o600)
 try:
  r=c.invoke(FunctionName=name,Qualifier=version,InvocationType='RequestResponse',LogType='Tail',Payload=b'{"probe":"muq-text-v1"}')
  stream=r['Payload']
  try:result=json.loads(stream.read(65537))
  finally:stream.close()
  log=base64.b64decode(r.get('LogResult','')).decode(errors='replace');file.with_suffix('.log').write_text(log);file.with_suffix('.log').chmod(0o600)
  record.update(status='function_error' if r.get('FunctionError') else 'completed',result=result)
 except Exception as error:
  record.update(status='transport_unconfirmed_no_retry',errorType=type(error).__name__)
 finally:file.write_text(json.dumps(record,indent=2))
 print(json.dumps(record))
if __name__=='__main__':main()
