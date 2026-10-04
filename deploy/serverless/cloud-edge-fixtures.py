#!/usr/bin/env python3
"""Test private CDN ranges/cookies and result CORS with generated disposable bytes."""
import base64,hashlib,json,math,os,struct,subprocess,time,uuid,wave,io
from pathlib import Path
import urllib.request,urllib.error
import boto3
from botocore.config import Config
ROOT=Path(__file__).resolve().parents[2]
def main():
 os.umask(0o077)
 target=json.loads((ROOT/'output/cloud-preparation/aws-target.json').read_text())
 session=boto3.Session(profile_name='manueldev',region_name='us-east-2')
 cfg=Config(connect_timeout=5,read_timeout=30,retries={'total_max_attempts':1})
 assert session.client('sts',config=cfg).get_caller_identity()['Account']==target['account_id']
 def outputs(name):return {r['OutputKey']:r['OutputValue'] for r in json.loads((ROOT/f'output/serverless-cloud/{name}/outputs.json').read_text())['Stacks'][0]['Outputs']}
 f,e=outputs('resonant-data'),outputs('resonant-edge');origin='https://'+e['Domain']
 subscription=session.client('pricing-plan-manager',region_name='us-east-1',config=cfg).get_subscription(arn=e['SubscriptionArn'])['subscription']
 assert subscription['status']=='ACTIVE' and subscription['planTier']=='FREE' and e['DistributionArn'] in subscription['resourceArns']
 signed=subprocess.check_output(['node','--input-type=module','-e',"import {signedCookies} from './deploy/serverless/api/core.mjs';import {readFileSync} from 'node:fs';const e=JSON.parse(readFileSync('output/serverless-cloud/resonant-edge/outputs.json')).Stacks[0].Outputs;const d=Object.fromEntries(e.map(r=>[r.OutputKey,r.OutputValue]));const k=readFileSync('output/serverless-private/first-release/cookie-private.pem');console.log(JSON.stringify({valid:signedCookies('https://'+d.Domain,d.KeyPairId,k,Math.floor(Date.now()/1000)+1200).map(c=>c.split(';')[0]).join('; '),expired:signedCookies('https://'+d.Domain,d.KeyPairId,k,1).map(c=>c.split(';')[0]).join('; ')}))"],cwd=ROOT,text=True)
 cookies=json.loads(signed);s3=session.client('s3',config=Config(signature_version='s3v4',s3={'addressing_style':'virtual'},connect_timeout=5,read_timeout=30,retries={'total_max_attempts':1}));unique=str(uuid.uuid4());key='media/acceptance-'+unique+'.wav';resultKey='results/'+unique+'.json'
 buffer=io.BytesIO()
 with wave.open(buffer,'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(22050);w.writeframes(b''.join(struct.pack('<h',int(1200*math.sin(i*2*math.pi*440/22050))) for i in range(44100)))
 raw=buffer.getvalue();checks=[];receipt={'checks':checks,'ownerAudioUploaded':False,'openaiCalls':0}
 class NoRedirect(urllib.request.HTTPRedirectHandler):
  def redirect_request(self,*args,**kwargs):return None
 opener=urllib.request.build_opener(NoRedirect)
 def request(url,method='GET',headers=None):
  try:r=opener.open(urllib.request.Request(url,method=method,headers=headers or {}),timeout=30)
  except urllib.error.HTTPError as error:r=error
  with r:return r.code,dict((k.lower(),v) for k,v in r.headers.items()),r.read(2*1024*1024)
 uploaded=s3.put_object(Bucket=f['MediaBucket'],Key=key,Body=raw,ContentType='audio/wav',CacheControl='public,max-age=31536000,immutable',ServerSideEncryption='AES256',ChecksumSHA256=base64.b64encode(hashlib.sha256(raw).digest()).decode(),ExpectedBucketOwner=target['account_id'])
 try:
  url=origin+'/'+key;good={'Cookie':cookies['valid']}
  assert request(url)[0]==403;checks.append('unsigned media denied')
  status,headers,body=request(url,'HEAD',good);assert status==200 and int(headers['content-length'])==len(raw);checks.append('signed HEAD returns exact length')
  status,headers,body=request(url,headers={**good,'Range':'bytes=1000-1999'});assert status==206 and body==raw[1000:2000] and headers['content-range']==f'bytes 1000-1999/{len(raw)}';checks.append('signed byte range 206 exact')
  status,headers,body=request(url,headers={**good,'Range':f'bytes={len(raw)+10}-'});assert status==416;checks.append('out of range rejected 416')
  assert request(url,headers=good)[2]==raw
  status,headers,body=request(url,headers=good);assert status==200 and body==raw and 'Hit' in headers.get('x-cache','');checks.append('signed cache hit verified')
  assert request(url)[0]==403 and request(url,headers={'Cookie':cookies['expired']})[0]==403;checks.append('unsigned and expired cookies denied after cache primed')
  assert request('https://'+f['MediaDomain']+'/'+key)[0]==403;checks.append('direct S3 denied')
  result=b'{"fixture":true}';s3.put_object(Bucket=f['StateBucket'],Key=resultKey,Body=result,ContentType='application/json',ServerSideEncryption='AES256')
  signedResult=s3.generate_presigned_url('get_object',Params={'Bucket':f['StateBucket'],'Key':resultKey},ExpiresIn=60)
  status,headers,body=request(signedResult,headers={'Origin':origin});receipt['resultCors']={'status':status,'allowOrigin':headers.get('access-control-allow-origin'),'bytes':len(body)};assert status==200 and body==result and headers.get('access-control-allow-origin')==origin;checks.append('presigned result CORS permits exact app origin')
  status,headers,body=request(signedResult,headers={'Origin':'https://foreign.invalid'});assert 'access-control-allow-origin' not in headers;checks.append('foreign result origin receives no CORS permission')
  receipt['status']='passed'
 except Exception:
  receipt['status']='failed';raise
 finally:
  s3.delete_object(Bucket=f['MediaBucket'],Key=key,VersionId=uploaded['VersionId'],ExpectedBucketOwner=target['account_id'])
  s3.delete_object(Bucket=f['StateBucket'],Key=resultKey,ExpectedBucketOwner=target['account_id'])
  receipt['fixturesRemoved']=True;folder=ROOT/'output/serverless-cloud/acceptance';folder.mkdir(mode=0o700,exist_ok=True);file=folder/('edge-'+unique+'.json');file.write_text(json.dumps(receipt,indent=2));file.chmod(0o600)
 print(json.dumps(receipt))
if __name__=='__main__':main()
