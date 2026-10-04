#!/usr/bin/env python3
"""Guarded change-set lifecycle. Planning and execution are separate commands."""
import argparse,hashlib,json,os,time,uuid,re
from pathlib import Path
import boto3
from botocore.config import Config
ROOT=Path(__file__).resolve().parents[2]
STACKS={'resonant-registry':('us-east-2','registry'),'resonant-text-probe':('us-east-2','benchmark'),'resonant-data':('us-east-2','foundation'),'resonant-edge':('us-east-1','edge'),'resonant-runtime':('us-east-2','runtime')}
def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['plan','review','execute','status']);p.add_argument('--stack',required=True,choices=STACKS);p.add_argument('--parameters',type=Path);a=p.parse_args()
 os.umask(0o077);target=json.loads((ROOT/'output/cloud-preparation/aws-target.json').read_text());region,kind=STACKS[a.stack];config=Config(connect_timeout=5,read_timeout=25,retries={'total_max_attempts':1});s=boto3.Session(profile_name='manueldev',region_name=region)
 if s.client('sts',config=config).get_caller_identity()['Account']!=target['account_id']:raise ValueError('Selected personal account mismatch')
 c=s.client('cloudformation',config=config);folder=ROOT/'output/serverless-cloud'/a.stack;folder.mkdir(parents=True,exist_ok=True,mode=0o700);receipt=folder/'change-set.json';template=ROOT/'deploy/serverless'/(kind+'-template.json')
 def save(file,data):file.write_text(json.dumps(data,indent=2,default=str)+'\n');file.chmod(0o600)
 def clean(message):return re.sub(r'[0-9]{12}','[account]',message)
 if a.action=='plan':
  try:stack=c.describe_stacks(StackName=a.stack)['Stacks'][0];change_type='CREATE' if stack['StackStatus']=='REVIEW_IN_PROGRESS' else 'UPDATE'
  except c.exceptions.ClientError as e:
   if e.response['Error']['Code']!='ValidationError' or 'does not exist' not in e.response['Error']['Message']:raise
   change_type='CREATE'
  if receipt.exists():
   previous=json.loads(receipt.read_text());old=c.describe_change_set(ChangeSetName=previous['changeSetId'])
   if old['ExecutionStatus']=='AVAILABLE':raise ValueError('An unexecuted change set exists; review it first')
  params=json.loads(a.parameters.read_text()) if a.parameters else []
  body=template.read_text();review_name='review-'+time.strftime('%Y%m%d%H%M%S')+'-'+uuid.uuid4().hex[:6]
  record={'stack':a.stack,'region':region,'changeType':change_type,'templatePath':str(template),'templateSha256':hashlib.sha256(body.encode()).hexdigest(),'changeSetName':review_name,'status':'creating'};save(folder/(review_name+'.json'),record)
  created=c.create_change_set(StackName=a.stack,ChangeSetName=review_name,ChangeSetType=change_type,TemplateBody=body,Parameters=params,Capabilities=['CAPABILITY_IAM'],Tags=[{'Key':'Project','Value':'resonant'}],ClientToken=review_name)
  record.update(changeSetId=created['Id'],stackId=created['StackId']);save(receipt,record);print(json.dumps({'stack':a.stack,'changeType':change_type,'status':'change_set_requested'}));return
 if a.action in ['review','execute']:
  record=json.loads(receipt.read_text());d=c.describe_change_set(ChangeSetName=record['changeSetId']);changes=[{k:row['ResourceChange'].get(k) for k in ['Action','LogicalResourceId','ResourceType','Replacement']} for row in d.get('Changes',[])];save(folder/'review.json',{'status':d['Status'],'executionStatus':d['ExecutionStatus'],'changes':changes,'reason':clean(d.get('StatusReason',''))})
  if a.action=='review':print(json.dumps({'stack':a.stack,'status':d['Status'],'executionStatus':d['ExecutionStatus'],'changes':changes,'reason':clean(d.get('StatusReason',''))}));return
  if d['Status']!='CREATE_COMPLETE' or d['ExecutionStatus']!='AVAILABLE':raise ValueError('Change set is not executable')
  if hashlib.sha256(template.read_bytes()).hexdigest()!=record['templateSha256']:raise ValueError('Template changed after planning')
  if any(row['Action']=='Remove' for row in changes):raise ValueError('Resource deletion requires separate review')
  if any(row['Replacement']=='True' and row['ResourceType']!='AWS::Lambda::Version' for row in changes):raise ValueError('Persistent resource replacement requires separate review')
  c.execute_change_set(ChangeSetName=record['changeSetId'],ClientRequestToken=record['changeSetName']+'-execute');record['status']='execution_requested';save(receipt,record);print(json.dumps({'stack':a.stack,'status':'execution_requested','resources':len(changes)}));return
 d=c.describe_stacks(StackName=a.stack);save(folder/'outputs.json',d);stack=d['Stacks'][0];events=c.describe_stack_events(StackName=a.stack)['StackEvents'];save(folder/'events.json',events)
 failures=[{'resource':e['LogicalResourceId'],'status':e['ResourceStatus'],'reason':clean(e.get('ResourceStatusReason',''))} for e in events if 'FAILED' in e['ResourceStatus']][:4]
 print(json.dumps({'stack':a.stack,'status':stack['StackStatus'],'failedEvents':failures}))
if __name__=='__main__':main()
