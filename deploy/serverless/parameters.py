#!/usr/bin/env python3
"""Assemble private CloudFormation parameter files from captured outputs; local only."""
import argparse,hashlib,json,os,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def outputs(file):
 data=json.loads(Path(file).read_text());rows=data['Stacks'][0]['Outputs'] if isinstance(data,dict) and 'Stacks' in data else data
 return {r['OutputKey']:r['OutputValue'] for r in rows}
def main():
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['edge','foundation-final','runtime']);p.add_argument('--foundation-output',required=True,type=Path);p.add_argument('--edge-output',type=Path);p.add_argument('--secret-dir',type=Path);p.add_argument('--candidate',type=Path);p.add_argument('--image');p.add_argument('--code-version');p.add_argument('--alert-email');p.add_argument('--memory',type=int,choices=[3008,4096,6144,8192],default=8192);p.add_argument('--worker-concurrency',type=int,choices=[0,1],default=0);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 dest=a.output.resolve()
 if not dest.is_relative_to(ROOT/'output') or dest.exists():raise ValueError('Choose a new private output file')
 f=outputs(a.foundation_output);target=json.loads((ROOT/'output/cloud-preparation/aws-target.json').read_text());account=target['account_id']
 if any(not f[k].startswith('resonant-'+account+'-us-east-2-resonant-data-') for k in ['MediaBucket','StateBucket','ArtifactBucket']):raise ValueError('Foundation does not match selected personal deployment')
 if a.stage=='edge':
  if not a.secret_dir:raise ValueError('Supply private secret directory')
  values={'MediaDomain':f['MediaDomain'],'HttpApiId':f['HttpApi'],'OriginSecret':(a.secret_dir/'origin.txt').read_text(),'CookiePublicKey':(a.secret_dir/'cookie-public.pem').read_text()}
 else:
  if not a.edge_output:raise ValueError('Supply captured edge outputs')
  e=outputs(a.edge_output)
  if not e['DistributionArn'].startswith('arn:aws:cloudfront::'+account+':distribution/') or e['SubscriptionStatus']!='ACTIVE':raise ValueError('Free subscription must be active in selected account')
  values={'WebOrigin':'https://'+e['Domain'],'DistributionArn':e['DistributionArn']}
  if a.stage=='runtime':
   if not a.candidate or not a.alert_email or not a.code_version or not re.fullmatch(re.escape(account)+r'\.dkr\.ecr\.us-east-2\.amazonaws\.com/[a-z0-9/_-]+@sha256:[a-f0-9]{64}',a.image or ''):raise ValueError('Supply candidate, personal ECR digest, immutable S3 code version and alert email')
   plan=json.loads((a.candidate/'upload-plan.json').read_text());api=json.loads((a.candidate/'api-package.json').read_text())
   if plan['stateBucket']!=f['StateBucket'] or hashlib.sha256((a.candidate/'api.zip').read_bytes()).hexdigest()!=api['sha256']:raise ValueError('Candidate/package mismatch')
   values={'StateTable':f['State'],'StateBucket':f['StateBucket'],'HttpApiId':f['HttpApi'],'CodeBucket':f['ArtifactBucket'],'CodeKey':'api/'+api['sha256']+'.zip','CodeVersion':a.code_version,'ApiCodeSha':api['codeSha256'],'ImageUri':a.image,'ReleaseId':plan['releaseId'],'WebOrigin':'https://'+e['Domain'],'KeyPairId':e['KeyPairId'],'SecretPrefix':'/resonant/first-release','MemoryMB':str(a.memory),'WorkerConcurrency':str(a.worker_concurrency),'AlertEmail':a.alert_email}
   values['RuntimeRevision']=hashlib.sha256(json.dumps(values,sort_keys=True).encode()).hexdigest()
 os.umask(0o077);dest.parent.mkdir(parents=True,exist_ok=True,mode=0o700);dest.write_text(json.dumps([{'ParameterKey':k,'ParameterValue':v} for k,v in values.items()],indent=2));dest.chmod(0o600)
 print(json.dumps({'stage':a.stage,'parameters':len(values),'awsWrites':0}))
if __name__=='__main__':main()
