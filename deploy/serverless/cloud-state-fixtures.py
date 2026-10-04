#!/usr/bin/env python3
"""Bounded real DynamoDB/S3 checks; no Lambda, OpenAI or owner audio access."""
import concurrent.futures
import importlib.util
import json
import os
from pathlib import Path
import time
import uuid
import boto3
from botocore.config import Config

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('worker_state',Path(__file__).with_name('runtime')/'state.py')
state=importlib.util.module_from_spec(spec);spec.loader.exec_module(state)

def main():
    os.umask(0o077)
    target=json.loads((ROOT/'output/cloud-preparation/aws-target.json').read_text())
    session=boto3.Session(profile_name='manueldev',region_name='us-east-2')
    config=Config(connect_timeout=5,read_timeout=25,retries={'total_max_attempts':1})
    assert session.client('sts',config=config).get_caller_identity()['Account']==target['account_id']
    stack=json.loads((ROOT/'output/serverless-cloud/resonant-data/outputs.json').read_text())['Stacks'][0]
    assert stack['StackStatus'] in ['CREATE_COMPLETE','UPDATE_COMPLETE']
    values={r['OutputKey']:r['OutputValue'] for r in stack['Outputs']}
    table=session.resource('dynamodb',config=config).Table(values['State'])
    s3=session.client('s3',config=config)
    now=int(time.time());job=str(uuid.uuid4());pk='JOB#'+job;key='results/'+job+'.json';release='0'*64
    row={'pk':pk,'sk':'META','id':job,'releaseId':release,'status':'queued','deadline':now+600,'ttl':now+3600,'fixture':True}
    receipt={'schema':'resonant/aws-state-fixtures/1','started':now,'checks':[],'openaiCalls':0,'audioInference':False}
    folder=ROOT/'output/serverless-cloud/acceptance';folder.mkdir(exist_ok=True,mode=0o700)
    file=folder/('state-'+job+'.json')
    def save():file.write_text(json.dumps(receipt,indent=2)+'\n');file.chmod(0o600)
    table.put_item(Item=row,ConditionExpression='attribute_not_exists(pk)')
    try:
        # Each thread owns its resource/client; boto3 resources are not thread-safe.
        def claim(i):
            own=boto3.Session(profile_name='manueldev',region_name='us-east-2').resource('dynamodb',config=config).Table(values['State'])
            result=state.Jobs(own).claim(job,'attempt-'+str(i),release)
            return result and result['attempt']
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            winners=[r for r in pool.map(claim,range(6)) if r]
        assert len(winners)==1
        attempt=winners[0];jobs=state.Jobs(table)
        receipt['checks'].append('six concurrent claims produce exactly one winner');save()
        jobs.provider_started(job,attempt)
        try:jobs.provider_started(job,attempt)
        except Exception as error:assert state.conditional(error)
        else:raise AssertionError('Provider start was repeated')
        receipt['checks'].append('provider-start marker is conditional and cannot repeat')
        assert not jobs.finish(job,'wrong-attempt','succeeded')
        objects=state.Objects(s3,values['StateBucket']);payload={'fixture':True,'matches':[]};digest=objects.put_json(key,payload)
        assert objects.get_json(key,65536)==payload
        assert jobs.finish(job,attempt,'succeeded',key,digest)
        assert not jobs.finish(job,attempt,'failed')
        assert jobs.claim(job,'duplicate',release) is None
        receipt['checks']+=['wrong attempt cannot finish','S3 result write/read verified','terminal completion cannot be replayed']
        table.update_item(Key={'pk':pk,'sk':'META'},UpdateExpression='SET #s=:s, deadline=:d',ExpressionAttributeNames={'#s':'status'},ExpressionAttributeValues={':s':'running',':d':now-1})
        assert not jobs.finish(job,attempt,'succeeded',key,digest)
        receipt['checks'].append('late completion cannot reactivate expired job')
        receipt['status']='passed';save()
    except Exception:
        receipt['status']='failed';save();raise
    finally:
        # Remove only the unique job/object that this run created.
        table.delete_item(Key={'pk':pk,'sk':'META'},ConditionExpression='fixture = :yes',ExpressionAttributeValues={':yes':True})
        s3.delete_object(Bucket=values['StateBucket'],Key=key,ExpectedBucketOwner=target['account_id'])
        receipt['fixturesRemoved']=True;save()
    print(json.dumps({'status':receipt['status'],'checks':len(receipt['checks']),'openaiCalls':0,'fixturesRemoved':True}))

if __name__=='__main__':main()
