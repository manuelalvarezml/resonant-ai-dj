#!/usr/bin/env python3
"""Enable a measured, digest-matched runtime and submit exactly one hosted prompt."""
import hashlib,http.cookiejar,json,os,time,urllib.error,urllib.request,uuid
from pathlib import Path
import boto3
from botocore.config import Config
ROOT=Path(__file__).resolve().parents[2]
def main():
 os.umask(0o077)
 folder=ROOT/'output/serverless-cloud/acceptance';file=folder/'live-prompt.json'
 if file.exists():raise ValueError('A live prompt receipt exists; inspect it, never automatically resubmit')
 evidence=json.loads((ROOT/'output/serverless-benchmark/aws-text-only-final.json').read_text())
 expected=json.loads((ROOT/'output/serverless-cloud/resonant-registry/text-only-image-20261003.json').read_text())
 assert evidence['status']=='completed' and len(evidence['attempts'])==15 and evidence['imageDigest']==expected['imageDigest'].split(':')[1]
 rows=evidence['attempts'];assert sum(r['result']['coldModel'] for r in rows)==5 and max(r['metrics']['maxMemoryMB'] for r in rows)<2600
 assert max(r['result']['wallSeconds'] for r in rows)<240
 assert all(r['result']['vectorSha256']=='89f18c6ef0314ec9dcbd04d8c5d10121c4ba7d4546c98cd445b9309058399d87' for r in rows)
 target=json.loads((ROOT/'output/cloud-preparation/aws-target.json').read_text());s=boto3.Session(profile_name='manueldev',region_name='us-east-2')
 cfg=Config(connect_timeout=5,read_timeout=30,retries={'total_max_attempts':1})
 assert s.client('sts',config=cfg).get_caller_identity()['Account']==target['account_id']
 def outputs(name):return {r['OutputKey']:r['OutputValue'] for r in json.loads((ROOT/f'output/serverless-cloud/{name}/outputs.json').read_text())['Stacks'][0]['Outputs']}
 f,e,r=outputs('resonant-data'),outputs('resonant-edge'),outputs('resonant-runtime')
 c=s.client('lambda',config=cfg);worker=c.get_function(FunctionName=r['WorkerAlias']);api=c.get_function(FunctionName=r['ApiAlias']);params={p['ParameterKey']:p['ParameterValue'] for p in json.loads((ROOT/'output/serverless-cloud/resonant-runtime/parameters-text-only.json').read_text())}
 concurrency=c.get_function_concurrency(FunctionName='resonant-runtime-worker')
 assert worker['Code']['ResolvedImageUri']==expected['imageUri'] and concurrency['ReservedConcurrentExecutions']==1
 for function in [worker,api]:assert function['Configuration']['Environment']['Variables']['RESONANT_RUNTIME_REVISION']==params['RuntimeRevision']
 assert api['Configuration']['CodeSha256']==params['ApiCodeSha']
 sub=s.client('pricing-plan-manager',region_name='us-east-1',config=cfg).get_subscription(arn=e['SubscriptionArn'])['subscription'];assert sub['status']=='ACTIVE' and sub['planTier']=='FREE'
 member=json.loads((ROOT/'output/serverless-assets/candidate-1/api/membership.json').read_text());release=member['releaseId'];db=s.resource('dynamodb',config=cfg).Table(f['State'])
 prior=db.get_item(Key={'pk':'CONFIG#ACTIVE','sk':'META'},ConsistentRead=True)['Item'];assert prior['enabled'] is False and prior['releaseId']==release
 s3=s.client('s3',config=cfg);pointers={key:s3.head_object(Bucket=f['MediaBucket'],Key=key)['VersionId'] for key in ['index.html','library/current.json']}
 tuple_record={'releaseId':release,'pointers':pointers,'imageDigest':expected['imageDigest'],'apiCodeSha256':params['ApiCodeSha'],'aliases':{name:c.get_alias(FunctionName='resonant-runtime-'+name,Name='live')['FunctionVersion'] for name in ['api','worker']},'previousConfig':prior,'runtimeRevision':params['RuntimeRevision'],'activatedAt':int(time.time())}
 tuple_file=ROOT/'output/serverless-cloud/active-deployment.json';tuple_file.write_text(json.dumps(tuple_record,indent=2));tuple_file.chmod(0o600)
 db.update_item(Key={'pk':'CONFIG#ACTIVE','sk':'META'},UpdateExpression='SET enabled=:yes',ConditionExpression='enabled=:no AND releaseId=:release',ExpressionAttributeValues={':yes':True,':no':False,':release':release})
 jar=http.cookiejar.MozillaCookieJar(str(folder/'listener.cookies'));jar.load(ignore_discard=True,ignore_expires=True);opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar));auth=json.loads((folder/'login-session.json').read_text());origin=auth['origin']
 body={'releaseId':release,'idempotencyKey':str(uuid.uuid4()),'prompt':'Create a playlist of 10 upbeat, cheerful songs from the entire library for a daytime party. Any genre is fine. Prioritize energy and danceability with soft preferences.','tracks':member['tracks'],'estimator_profile':'quality'}
 record={'status':'prepared','idempotencyKey':body['idempotencyKey'],'releaseId':release,'maxSubmissions':1,'startedAt':time.time(),'openaiBudget':'one normal planner request; no automatic replay'}
 def save():file.write_text(json.dumps(record,indent=2));file.chmod(0o600)
 def request(path,body=None):
  headers={'Origin':origin,'Content-Type':'application/json','x-resonant-csrf':auth['csrf']}
  with opener.open(urllib.request.Request(origin+path,data=None if body is None else json.dumps(body).encode(),headers=headers),timeout=30) as response:return json.load(response)
 save()
 try:
  record['status']='dispatching';save()
  # Exactly one POST; an ambiguous transport result is retained for reconciliation.
  job=request('/api/playlist',body);record.update(status='submitted',jobId=job['id']);save();print(json.dumps({'status':'submitted'}),flush=True)
  for _ in range(180):
   result=request('/api/jobs/'+job['id'])
   if result['status']=='complete':
    with urllib.request.urlopen(urllib.request.Request(result['resultUrl'],headers={'Origin':origin}),timeout=30) as response:raw=response.read(32*1024*1024+1)
    assert len(raw)<=32*1024*1024 and hashlib.sha256(raw).hexdigest()==result['resultSha256']
    payload=json.loads(raw);path=folder/'live-result.json';path.write_bytes(raw);path.chmod(0o600)
    matches=(payload.get('result') or {}).get('matches',[])
    record.update(status='completed',resultStatus=payload.get('status'),matches=len(matches),resultSha256=result['resultSha256'],elapsedSeconds=round(time.time()-record['startedAt'],2));save();break
   if result['status']=='failed':record.update(status='failed',message=result.get('error'));save();break
   time.sleep(5)
  else:record['status']='poll_deadline';save()
 except Exception as error:
  record.update(status='review_required_no_replay',errorType=type(error).__name__);save();raise
 finally:
  if record['status']!='completed' or not record.get('matches'):
   db.update_item(Key={'pk':'CONFIG#ACTIVE','sk':'META'},UpdateExpression='SET enabled=:no',ConditionExpression='releaseId=:release',ExpressionAttributeValues={':no':False,':release':release})
   record['admissionsPaused']=True;save()
 print(json.dumps(record))
if __name__=='__main__':main()
