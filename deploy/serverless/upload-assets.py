#!/usr/bin/env python3
"""Explicit checksum allowlist uploader. Plan by default; no recursive folder sync."""
import argparse,base64,hashlib,json,mimetypes
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main():
 p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--bucket',required=True);p.add_argument('--phase',choices=['immutable','pointers'],default='immutable');p.add_argument('--execute',action='store_true');p.add_argument('--free-subscription-arn');a=p.parse_args()
 target=json.loads((ROOT/'output/cloud-preparation/aws-target.json').read_text());account=target['account_id'];expected=f'resonant-{account}-us-east-2-resonant-data-media'
 if a.bucket!=expected:raise ValueError('Unexpected destination bucket')
 plan=json.loads((a.candidate/'upload-plan.json').read_text());rows=[r for r in plan['uploads'] if (r['key'] in {'index.html','library/current.json'})==(a.phase=='pointers')]
 if a.phase=='pointers':rows.sort(key=lambda r:r['key']=='index.html')
 for row in rows:
  file=Path(row['localPath']);resolved=file.resolve()
  if file.is_symlink() or not (resolved.is_relative_to(a.candidate.resolve()/'static') or resolved.is_relative_to(ROOT/'output/cloud-releases/first-release/media')):raise ValueError('Unexpected upload source')
  if file.stat().st_size!=row['bytes'] or hashlib.sha256(file.read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Candidate changed; do not upload')
 print(json.dumps({'phase':a.phase,'objects':len(rows),'bytes':sum(r['bytes'] for r in rows),'execute':a.execute}))
 if not a.execute:return
 import boto3
 from botocore.config import Config
 s=boto3.Session(profile_name='manueldev',region_name='us-east-2')
 if s.client('sts').get_caller_identity()['Account']!=account:raise ValueError('Wrong personal AWS account')
 if not a.free_subscription_arn:raise ValueError('Require the actual Free subscription ARN')
 sub=s.client('pricing-plan-manager',region_name='us-east-1').get_subscription(arn=a.free_subscription_arn)['subscription']
 if sub.get('status')!='ACTIVE' or sub.get('planTier')!='FREE':raise ValueError('Free subscription is not active')
 client=s.client('s3',config=Config(connect_timeout=5,read_timeout=60,retries={'total_max_attempts':3}))
 client.head_bucket(Bucket=a.bucket,ExpectedBucketOwner=account)
 bucket_policy=json.loads(client.get_bucket_policy(Bucket=a.bucket,ExpectedBucketOwner=account)['Policy'])
 origins=[r.get('Condition',{}).get('StringEquals',{}).get('AWS:SourceArn') for r in bucket_policy.get('Statement',[]) if r.get('Effect')=='Allow' and r.get('Principal',{}).get('Service')=='cloudfront.amazonaws.com']
 if len(origins)!=1 or origins[0] not in sub.get('resourceArns',[]):raise ValueError('Free subscription does not cover this bucket distribution')
 receipts=[]
 for row in rows:
  raw=Path(row['localPath']).read_bytes();checksum=base64.b64encode(hashlib.sha256(raw).digest()).decode()
  # Immutable names are overwrite-safe only for exactly matching bytes. Pointers
  # intentionally create a new version; record the previous versions before launch.
  content={'.js':'text/javascript','.m4a':'audio/mp4'}.get(Path(row['key']).suffix) or mimetypes.guess_type(row['key'])[0] or 'application/octet-stream'
  result=client.put_object(Bucket=a.bucket,Key=row['key'],Body=raw,ExpectedBucketOwner=account,ServerSideEncryption='AES256',ChecksumSHA256=checksum,ContentType=content,CacheControl=row['cacheControl'])
  head=client.head_object(Bucket=a.bucket,Key=row['key'],VersionId=result['VersionId'],ExpectedBucketOwner=account,ChecksumMode='ENABLED')
  if head.get('ChecksumSHA256')!=checksum or head['ContentLength']!=row['bytes']:raise ValueError('Remote verification failed; stop publication')
  receipts.append({'key':row['key'],'versionId':result['VersionId'],'sha256':row['sha256']})
  (a.candidate/('uploaded-'+a.phase+'.json')).write_text(json.dumps(receipts,indent=2))
 print(json.dumps({'verifiedObjects':len(receipts)}))
if __name__=='__main__':main()
