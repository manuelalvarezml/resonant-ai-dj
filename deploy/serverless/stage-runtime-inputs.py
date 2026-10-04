#!/usr/bin/env python3
"""Stage only reviewed secrets and the checksum-bound API ZIP, with private receipts."""
import base64
import hashlib
import json
import os
from pathlib import Path
import boto3
from botocore.config import Config

ROOT = Path(__file__).resolve().parents[2]

def main():
    os.umask(0o077)
    target = json.loads((ROOT/'output/cloud-preparation/aws-target.json').read_text())
    session = boto3.Session(profile_name='manueldev', region_name='us-east-2')
    config = Config(connect_timeout=5, read_timeout=60, retries={'total_max_attempts':1})
    if session.client('sts', config=config).get_caller_identity()['Account'] != target['account_id']:
        raise ValueError('Wrong personal AWS account')
    foundation = json.loads((ROOT/'output/serverless-cloud/resonant-data/outputs.json').read_text())['Stacks'][0]
    if foundation['StackStatus'] not in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']:
        raise ValueError('Foundation is not ready')
    values = {r['OutputKey']:r['OutputValue'] for r in foundation['Outputs']}
    bucket = values['ArtifactBucket']
    if bucket != f"resonant-{target['account_id']}-us-east-2-resonant-data-artifacts":
        raise ValueError('Unexpected artifact bucket')
    folder = ROOT/'output/serverless-cloud/runtime-inputs'
    folder.mkdir(mode=0o700, exist_ok=True)
    receipt = {'parameters': [], 'api': None}
    def save():
        file=folder/'receipt.json'
        file.write_text(json.dumps(receipt, indent=2)+'\n');file.chmod(0o600)
    params = json.loads((ROOT/'output/serverless-private/first-release/ssm-parameters.json').read_text())
    expected = {'/resonant/first-release/'+s for s in ['origin','password-hash','signing-key','openai']}
    if {p['Name'] for p in params} != expected or len(params)!=4 or any(not p['Value'] for p in params):
        raise ValueError('Expected the four prepared nonempty production parameters')
    ssm=session.client('ssm', config=config)
    for param in params:
        try:
            prior=ssm.get_parameter(Name=param['Name'], WithDecryption=True)['Parameter']
        except ssm.exceptions.ParameterNotFound:
            prior=None
        if prior:
            if prior['Value'] != param['Value'] or prior['Type'] != 'SecureString':
                raise ValueError('Existing remote secret differs; refusing overwrite')
            version=prior['Version']
        else:
            version=ssm.put_parameter(**param)['Version']
        receipt['parameters'].append({'name':param['Name'],'version':version,'reused':prior is not None})
        save()
    candidate=ROOT/'output/serverless-assets/candidate-1'
    package=json.loads((candidate/'api-package.json').read_text())
    raw=(candidate/'api.zip').read_bytes()
    digest=hashlib.sha256(raw).hexdigest()
    checksum=base64.b64encode(hashlib.sha256(raw).digest()).decode()
    if digest != package['sha256'] or checksum != package['codeSha256']:
        raise ValueError('API package checksum changed')
    s3=session.client('s3',config=config)
    key='api/'+digest+'.zip'
    try:
        head=s3.head_object(Bucket=bucket,Key=key,ExpectedBucketOwner=target['account_id'],ChecksumMode='ENABLED')
    except s3.exceptions.ClientError as error:
        if error.response['Error']['Code'] not in ['404','NoSuchKey']:raise
        result=s3.put_object(Bucket=bucket,Key=key,Body=raw,ContentType='application/zip',ChecksumSHA256=checksum,
                             ExpectedBucketOwner=target['account_id'],ServerSideEncryption='AES256',IfNoneMatch='*')
        head=s3.head_object(Bucket=bucket,Key=key,VersionId=result['VersionId'],ExpectedBucketOwner=target['account_id'],ChecksumMode='ENABLED')
    if head.get('ChecksumSHA256') != checksum or head['ContentLength'] != len(raw):
        raise ValueError('Remote code verification failed')
    receipt['api']={'bucket':bucket,'key':key,'versionId':head['VersionId'],'sha256':digest,'codeSha256':checksum}
    save()
    print(json.dumps({'secureParameters':len(receipt['parameters']),'apiBytes':len(raw),'apiVerified':True,'openaiCalls':0}))

if __name__=='__main__':
    main()
