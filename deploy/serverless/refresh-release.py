#!/usr/bin/env python3
"""Bounded same-library refresh; preserve rollback evidence and skip existing assets."""
import argparse,base64,hashlib,json,os,subprocess,time
from pathlib import Path
import boto3
from botocore.config import Config
ROOT=Path(__file__).resolve().parents[2]
FOLDER=ROOT/'output/web-refresh/domain-release'
def load(p):return json.loads(p.read_text())
def save(p,v):p.write_text(json.dumps(v,indent=2,default=str)+'\n');p.chmod(0o600)
def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','stage','pause','publish','finish','domain-parameters']);a=p.parse_args();os.umask(0o077);FOLDER.mkdir(exist_ok=True,parents=True)
 target=load(ROOT/'output/cloud-preparation/aws-target.json');s=boto3.Session(profile_name='manueldev',region_name='us-east-2');cfg=Config(connect_timeout=5,read_timeout=60,retries={'total_max_attempts':2})
 assert s.client('sts',config=cfg).get_caller_identity()['Account']==target['account_id']
 def client(name,region='us-east-2'):return s.client(name,region_name=region,config=cfg)
 cf=client('cloudformation');stacks={name:client('cloudformation',region).describe_stacks(StackName=name)['Stacks'][0] for name,region in [('resonant-data','us-east-2'),('resonant-runtime','us-east-2'),('resonant-edge','us-east-1')]}
 def outputs(name):return {r['OutputKey']:r['OutputValue'] for r in stacks[name]['Outputs']}
 f,e=outputs('resonant-data'),outputs('resonant-edge');sub=client('pricing-plan-manager','us-east-1').get_subscription(arn=e['SubscriptionArn'])['subscription'];assert sub['status']=='ACTIVE' and sub['planTier']=='FREE'
 c=FOLDER/'candidate';s3=client('s3');lam=client('lambda');db=s.resource('dynamodb',config=cfg).Table(f['State']);active=load(ROOT/'output/serverless-cloud/active-deployment.json')
 if a.action=='prepare':
  if not c.exists():subprocess.run(['node','deploy/serverless/export-static.mjs','--release','output/cloud-releases/first-release','--output',str(c),'--state-bucket',f['StateBucket']],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
  if not (c/'api.zip').exists():subprocess.run([str(ROOT/'output/serverless-tools/bin/python'),'deploy/serverless/package-api.py','--candidate',str(c)],cwd=ROOT,check=True)
  assert load(c/'upload-plan.json')['releaseId']==active['releaseId'];print(json.dumps({'prepared':True,'audioChanged':False}));return
 if a.action=='domain-parameters':
  cert=load(FOLDER/'certificate.json');assert client('acm','us-east-1').describe_certificate(CertificateArn=cert['arn'])['Certificate']['Status']=='ISSUED'
  params=[{'ParameterKey':r['ParameterKey'],'UsePreviousValue':True} for r in stacks['resonant-edge']['Parameters'] if r['ParameterKey'] not in ['CustomDomain','CertificateArn']]
  params += [{'ParameterKey':'CustomDomain','ParameterValue':'resonant.lat'},{'ParameterKey':'CertificateArn','ParameterValue':cert['arn']}];save(FOLDER/'edge-parameters.json',params);print('Edge parameters prepared; certificate ISSUED.');return
 plan=load(c/'upload-plan.json');package=load(c/'api-package.json');assert plan['releaseId']==active['releaseId'] and plan['stateBucket']==f['StateBucket']
 if a.action=='stage':
  snapshot=FOLDER/'before.json'
  if not snapshot.exists():
   before={'active':active,'config':db.get_item(Key={'pk':'CONFIG#ACTIVE','sk':'META'},ConsistentRead=True)['Item'],'pointers':{key:s3.head_object(Bucket=f['MediaBucket'],Key=key,ExpectedBucketOwner=target['account_id'])['VersionId'] for key in ['index.html','library/current.json']},'aliases':{name:lam.get_alias(FunctionName='resonant-runtime-'+name,Name='live')['FunctionVersion'] for name in ['api','worker']},'parameters':{name:stack['Parameters'] for name,stack in stacks.items()}}
   save(snapshot,before)
  raw=(c/'api.zip').read_bytes();assert hashlib.sha256(raw).hexdigest()==package['sha256'];key='api/'+package['sha256']+'.zip'
  try:head=s3.head_object(Bucket=f['ArtifactBucket'],Key=key,ExpectedBucketOwner=target['account_id'],ChecksumMode='ENABLED')
  except s3.exceptions.ClientError as error:
   if error.response['Error']['Code'] not in ['404','NoSuchKey']:raise
   s3.put_object(Bucket=f['ArtifactBucket'],Key=key,Body=raw,ChecksumSHA256=package['codeSha256'],ContentType='application/zip',ServerSideEncryption='AES256',ExpectedBucketOwner=target['account_id'],IfNoneMatch='*');head=s3.head_object(Bucket=f['ArtifactBucket'],Key=key,ExpectedBucketOwner=target['account_id'],ChecksumMode='ENABLED')
  assert head['ChecksumSHA256']==package['codeSha256'] and head['ContentLength']==len(raw)
  params={r['ParameterKey']:r['ParameterValue'] for r in stacks['resonant-runtime']['Parameters']};params.update(CodeKey=key,CodeVersion=head['VersionId'],ApiCodeSha=package['codeSha256'],AdditionalWebOrigin='https://resonant.lat');params.pop('RuntimeRevision');params['RuntimeRevision']=hashlib.sha256(json.dumps(params,sort_keys=True).encode()).hexdigest();save(FOLDER/'runtime-parameters.json',[{'ParameterKey':k,'ParameterValue':v} for k,v in params.items()])
  foundation=[{'ParameterKey':r['ParameterKey'],'UsePreviousValue':True} for r in stacks['resonant-data']['Parameters'] if r['ParameterKey']!='AdditionalWebOrigin'];foundation.append({'ParameterKey':'AdditionalWebOrigin','ParameterValue':'https://resonant.lat'});save(FOLDER/'foundation-parameters.json',foundation)
  uploaded=[];skipped=0
  for row in plan['uploads']:
   if row['key'] in ['index.html','library/current.json']:continue
   try:
    remote=s3.head_object(Bucket=f['MediaBucket'],Key=row['key'],ExpectedBucketOwner=target['account_id'],ChecksumMode='ENABLED')
   except s3.exceptions.ClientError as error:
    if error.response['Error']['Code'] not in ['404','NoSuchKey']:raise
    remote=None
   checksum=base64.b64encode(bytes.fromhex(row['sha256'])).decode()
   if remote and remote.get('ChecksumSHA256')==checksum and remote['ContentLength']==row['bytes']:skipped+=1;continue
   if row['key'].startswith(('media/','library/')):raise ValueError('Frozen library/audio mismatch; no automatic upload')
   path=Path(row['localPath']).resolve();assert path.is_relative_to(c/'static');raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==row['sha256']
   import mimetypes
   content='text/javascript' if path.suffix=='.js' else mimetypes.guess_type(path)[0] or 'application/octet-stream'
   result=s3.put_object(Bucket=f['MediaBucket'],Key=row['key'],Body=raw,ContentType=content,CacheControl=row['cacheControl'],ServerSideEncryption='AES256',ChecksumSHA256=checksum,ExpectedBucketOwner=target['account_id'])
   verify=s3.head_object(Bucket=f['MediaBucket'],Key=row['key'],VersionId=result['VersionId'],ExpectedBucketOwner=target['account_id'],ChecksumMode='ENABLED');assert verify['ChecksumSHA256']==checksum
   uploaded.append({'key':row['key'],'versionId':result['VersionId']});save(FOLDER/'staged-assets.json',uploaded)
  print(json.dumps({'newStaticAssets':len(uploaded),'unchangedSkipped':skipped,'apiStaged':True,'audioUploaded':0}));return
 if a.action=='pause':
  before=load(FOLDER/'before.json');current=db.get_item(Key={'pk':'CONFIG#ACTIVE','sk':'META'},ConsistentRead=True)['Item'];assert current['releaseId']==plan['releaseId']
  if current['enabled']:db.update_item(Key={'pk':'CONFIG#ACTIVE','sk':'META'},UpdateExpression='SET enabled=:no',ConditionExpression='releaseId=:release AND enabled=:yes',ExpressionAttributeValues={':release':plan['releaseId'],':no':False,':yes':True})
  outstanding=[]
  for i in range(3):
   slot=db.get_item(Key={'pk':'SLOT#'+str(i),'sk':'META'},ConsistentRead=True).get('Item',{})
   if slot.get('jobId'):
    job=db.get_item(Key={'pk':'JOB#'+slot['jobId'],'sk':'META'},ConsistentRead=True).get('Item',{})
    if job.get('status') in ['dispatching','queued','running'] and job.get('deadline',0)>time.time():outstanding.append(job['id'])
  assert not outstanding,'Wait for outstanding jobs before runtime update';print('New PlaylistIQ jobs paused; no outstanding jobs. Playback remains available.');return
 if a.action in ['publish','finish']:
  params={r['ParameterKey']:r['ParameterValue'] for r in load(FOLDER/'runtime-parameters.json')};assert stacks['resonant-runtime']['StackStatus']=='UPDATE_COMPLETE'
  for name in ['api','worker']:
   function=lam.get_function(FunctionName='resonant-runtime-'+name,Qualifier='live');assert function['Configuration']['Environment']['Variables']['RESONANT_RUNTIME_REVISION']==params['RuntimeRevision']
   if name=='api':assert function['Configuration']['CodeSha256']==package['codeSha256']
   else:assert function['Code']['ResolvedImageUri']==params['ImageUri']
  if a.action=='publish':
   ssm=client('ssm');password=load(ROOT/'output/web-refresh/password-rotation/password-hash.json');old=ssm.get_parameter(Name=password['parameter'],WithDecryption=True)['Parameter'];backup=FOLDER/'previous-password.json'
   if not backup.exists():save(backup,old)
   if old['Value']!=password['value']:ssm.put_parameter(Name=password['parameter'],Value=password['value'],Type='SecureString',Overwrite=True)
   (ROOT/'output/cloud-config/first-release/listener-password.txt').write_bytes((ROOT/'output/web-refresh/password-rotation/listener-password.txt').read_bytes())
   receipt={}
   for key in ['library/current.json','index.html']:
    row=next(r for r in plan['uploads'] if r['key']==key);raw=Path(row['localPath']).read_bytes();assert hashlib.sha256(raw).hexdigest()==row['sha256'];checksum=base64.b64encode(bytes.fromhex(row['sha256'])).decode();result=s3.put_object(Bucket=f['MediaBucket'],Key=key,Body=raw,ContentType='text/html' if key.endswith('.html') else 'application/json',CacheControl=row['cacheControl'],ServerSideEncryption='AES256',ExpectedBucketOwner=target['account_id'],ChecksumSHA256=checksum);receipt[key]=result['VersionId']
   save(FOLDER/'published-pointers.json',receipt)
   invalidation=client('cloudfront','us-east-1').create_invalidation(DistributionId=e['DistributionId'],InvalidationBatch={'Paths':{'Quantity':3,'Items':['/','/index.html','/library/current.json']},'CallerReference':'resonant-refresh-'+str(time.time_ns())});save(FOLDER/'invalidation.json',{'id':invalidation['Invalidation']['Id']});print('Published new app pointers and rotated requested password.');return
  record={**active,'pointers':load(FOLDER/'published-pointers.json'),'apiCodeSha256':params['ApiCodeSha'],'runtimeRevision':params['RuntimeRevision'],'aliases':{name:lam.get_alias(FunctionName='resonant-runtime-'+name,Name='live')['FunctionVersion'] for name in ['api','worker']},'activatedAt':int(time.time()),'candidate':str(c),'appId':plan['appId']}
  save(ROOT/'output/serverless-cloud/active-deployment.json',record)
  db.update_item(Key={'pk':'CONFIG#ACTIVE','sk':'META'},UpdateExpression='SET enabled=:yes',ConditionExpression='releaseId=:release',ExpressionAttributeValues={':yes':True,':release':plan['releaseId']});print(json.dumps({'published':True,'playlistIQEnabled':True,'aliases':record['aliases'],'audioChanged':False}));return
if __name__=='__main__':main()
