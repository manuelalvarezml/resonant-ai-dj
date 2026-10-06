#!/usr/bin/env python3
"""Authorized one-time reset of pre-account live history. Preserve library, models and cost quotas."""
import json,os,time
from pathlib import Path
import boto3
from boto3.dynamodb.conditions import Attr
ROOT=Path(__file__).resolve().parents[2]
os.umask(0o077)
s=boto3.Session(profile_name='manueldev',region_name='us-east-2')
assert s.client('sts').get_caller_identity()['Account']==json.loads((ROOT/'output/cloud-preparation/aws-target.json').read_text())['account_id']
stack=s.client('cloudformation').describe_stacks(StackName='resonant-data')['Stacks'][0]
out={r['OutputKey']:r['OutputValue'] for r in stack['Outputs']}
table=s.resource('dynamodb').Table(out['State']);s3=s.client('s3');folder=ROOT/'output/accounts/legacy-reset';folder.mkdir(parents=True,exist_ok=True)
# Never sweep newly created per-user namespaces or cost/queue controls.
rows=[];cursor=None
while True:
 page=table.scan(**({'ExclusiveStartKey':cursor} if cursor else {}));rows+=page['Items'];cursor=page.get('LastEvaluatedKey')
 if not cursor:break
legacy=[r for r in rows if r['pk']=='PROFILE#OWNER' or (r['pk'].startswith('PROFILEOP#') and ('PROFILE#' not in r['pk'] or 'PROFILE#OWNER#' in r['pk'])) or (r['pk'].startswith('SESSION#') and not r.get('userId')) or (r['pk'].startswith('JOB#') and len(r.get('owner',''))==64)]
backup=folder/'rows.json'
if not backup.exists():backup.write_text(json.dumps(legacy,default=str,indent=2)+'\n')
for r in legacy:table.delete_item(Key={'pk':r['pk'],'sk':r['sk']})
# Historic job records can already have expired from DynamoDB. All pre-migration
# request/result/audit objects are archived before hiding them from the live bucket.
objects=[]
for prefix in ['requests/','results/','audits/']:
 for page in s3.get_paginator('list_objects_v2').paginate(Bucket=out['StateBucket'],Prefix=prefix):
  for row in page.get('Contents',[]):
   if row['LastModified'].timestamp()>folder.stat().st_ctime:continue
   key=row['Key'];dest=folder/key;dest.parent.mkdir(parents=True,exist_ok=True)
   obj=s3.get_object(Bucket=out['StateBucket'],Key=key)
   if not dest.exists():dest.write_bytes(obj['Body'].read())
   deleted=s3.delete_object(Bucket=out['StateBucket'],Key=key)
   objects.append({'key':key,'previousVersion':obj.get('VersionId'),'deleteMarkerVersion':deleted.get('VersionId')})
(folder/'objects.json').write_text(json.dumps(objects,indent=2)+'\n')
print(json.dumps({'legacyRowsRemoved':len(legacy),'legacyJobObjectsArchived':len(objects),'libraryChanged':False,'costQuotaCountersPreserved':True}))
