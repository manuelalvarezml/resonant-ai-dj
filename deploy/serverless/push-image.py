#!/usr/bin/env python3
"""Push one verified task image to its private registry with ephemeral Docker auth."""
import argparse,base64,json,os,re,subprocess,tempfile
from pathlib import Path
import boto3
from botocore.config import Config
ROOT=Path(__file__).resolve().parents[2]
def main():
 p=argparse.ArgumentParser();p.add_argument('--build-receipt',type=Path,required=True);p.add_argument('--registry-output',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 os.umask(0o077);target=json.loads((ROOT/'output/cloud-preparation/aws-target.json').read_text());build=json.loads(a.build_receipt.read_text());outputs=json.loads(a.registry_output.read_text())['Stacks'][0]['Outputs'];uri=next(r['OutputValue'] for r in outputs if r['OutputKey']=='RepositoryUri')
 if not uri.startswith(target['account_id']+'.dkr.ecr.us-east-2.amazonaws.com/'):raise ValueError('Registry account mismatch')
 if a.output.exists():raise ValueError('Upload receipt already exists; inspect rather than repush')
 local=json.loads(subprocess.check_output(['docker','image','inspect',build['tag']],text=True))[0]
 if local['Id']!=build['imageId'] or local['Architecture']!='amd64':raise ValueError('Reviewed image changed')
 layers=sum(int(v) for v in subprocess.check_output(['docker','image','history','--human=false','--format','{{.Size}}',build['tag']],text=True).splitlines())
 if layers>=10*2**30:raise ValueError('Expanded image exceeds Lambda limit')
 s=boto3.Session(profile_name='manueldev',region_name='us-east-2');cfg=Config(connect_timeout=5,read_timeout=30,retries={'total_max_attempts':2});assert s.client('sts',config=cfg).get_caller_identity()['Account']==target['account_id'];ecr=s.client('ecr',config=cfg)
 tag='build-'+build['buildId'][:24];remote=uri+':'+tag;repo=uri.split('/',1)[1];endpoint=subprocess.check_output(['docker','context','inspect','--format','{{.Endpoints.docker.Host}}'],text=True).strip();env={**os.environ,'DOCKER_HOST':endpoint}
 with tempfile.TemporaryDirectory(prefix='resonant-ecr-') as auth:
  token=ecr.get_authorization_token(registryIds=[target['account_id']])['authorizationData'][0];user,password=base64.b64decode(token['authorizationToken']).decode().split(':',1)
  result=subprocess.run(['docker','--config',auth,'login','--username',user,'--password-stdin',token['proxyEndpoint']],input=password+'\n',text=True,capture_output=True,env=env)
  if result.returncode:raise RuntimeError('Private registry login failed')
  subprocess.run(['docker','image','tag',build['tag'],remote],check=True,capture_output=True)
  with a.output.with_suffix('.log').open('x') as log:
   result=subprocess.run(['docker','--config',auth,'push',remote],stdout=log,stderr=subprocess.STDOUT,env=env)
  if result.returncode:raise RuntimeError('Image push failed; inspect private upload log')
 image=ecr.describe_images(repositoryName=repo,imageIds=[{'imageTag':tag}])['imageDetails'][0]
 record={'repositoryUri':uri,'imageUri':uri+'@'+image['imageDigest'],'imageDigest':image['imageDigest'],'tag':tag,'buildId':build['buildId'],'expandedLayerBytes':layers,'compressedBytes':image['imageSizeInBytes'],'private':True}
 a.output.write_text(json.dumps(record,indent=2)+'\n');a.output.chmod(0o600);print(json.dumps({k:v for k,v in record.items() if k not in ['repositoryUri','imageUri']}))
if __name__=='__main__':main()
