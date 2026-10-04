// Real AWS persistence, injected no-op dispatch. Refuses a previously used table.
// Run explicitly with --execute. Never invoke a worker or OpenAI.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {randomBytes,randomUUID} from 'node:crypto';
import {DynamoDBClient,DescribeTableCommand} from '@aws-sdk/client-dynamodb';
import {DynamoDBDocumentClient,ScanCommand,DeleteCommand,PutCommand} from '@aws-sdk/lib-dynamodb';
import {S3Client,DeleteObjectCommand} from '@aws-sdk/client-s3';
import {createHandler,sha} from './core.mjs';
import {awsDependencies} from './aws.mjs';
if(!process.argv.includes('--execute'))throw Error('Explicit --execute required for disposable AWS fixtures.');
for(const k of ['AWS_ACCESS_KEY_ID','AWS_SECRET_ACCESS_KEY','AWS_SESSION_TOKEN','AWS_WEB_IDENTITY_TOKEN_FILE','AWS_ROLE_ARN','AWS_CONTAINER_CREDENTIALS_RELATIVE_URI','AWS_CONTAINER_CREDENTIALS_FULL_URI'])delete process.env[k];
process.env.AWS_PROFILE='manueldev';process.env.AWS_EC2_METADATA_DISABLED='true';
const root=new URL('../../../',import.meta.url),read=async file=>JSON.parse(await readFile(new URL(file,root),'utf8'));
const target=await read('output/cloud-preparation/aws-target.json');
const f=Object.fromEntries((await read('output/serverless-cloud/resonant-data/outputs.json')).Stacks[0].Outputs.map(r=>[r.OutputKey,r.OutputValue]));
const low=new DynamoDBClient({region:'us-east-2',maxAttempts:3});
const table=(await low.send(new DescribeTableCommand({TableName:f.State}))).Table;
assert.equal(table.TableArn.split(':')[4],target.account_id);
const doc=DynamoDBDocumentClient.from(low),s3=new S3Client({region:'us-east-2',maxAttempts:3});
assert.equal((await doc.send(new ScanCommand({TableName:f.State,Limit:1,ConsistentRead:true}))).Count,0,'Fixtures require an unused table.');
const member=await read('output/serverless-assets/candidate-1/api/membership.json');
const params=new Map((await read('output/serverless-private/first-release/ssm-parameters.json')).map(p=>[p.Name,p.Value]));
const values={originSecret:params.get('/resonant/first-release/origin'),passwordHash:params.get('/resonant/first-release/password-hash'),signingKey:params.get('/resonant/first-release/signing-key')};
const origin='https://fixture.invalid',deps=awsDependencies({RESONANT_STATE_TABLE:f.State,RESONANT_STATE_BUCKET:f.StateBucket});
const token=randomBytes(32).toString('base64url'),owner=sha(token),csrf=randomBytes(32).toString('base64url');let clock=Math.floor(Date.now()/1000),dispatches=0;
const handler=createHandler({...deps,secrets:async()=>values,dispatch:async()=>{dispatches++;},now:()=>clock,config:{...member,origin,keyPairId:'fixture'}});
const created=new Set(['CONFIG#ACTIVE','SESSION#'+owner]);const objects=new Set();const checks=[];
const put=async item=>doc.send(new PutCommand({TableName:f.State,Item:item}));
const event=(path,body,extra={})=>({rawPath:path,requestContext:{http:{method:body?'POST':'GET',sourceIp:'192.0.2.17'}},cookies:['__Host-resonant_session='+token],headers:{'x-resonant-origin':values.originSecret,origin,'x-resonant-csrf':csrf,'content-type':'application/json',...extra},...(body?{body:JSON.stringify(body)}:{})});
const body={releaseId:member.releaseId,idempotencyKey:randomUUID(),prompt:'Fixture only: no provider request',tracks:[member.tracks[0]]};
let result;
try{
 await put({pk:'CONFIG#ACTIVE',sk:'META',releaseId:member.releaseId,enabled:true});
 await put({pk:'SESSION#'+owner,sk:'META',csrf,expires:clock+86400,ttl:clock+86400});
 const replies=await Promise.all(Array.from({length:6},()=>handler(event('/api/playlist',body))));
 assert.ok(replies.every(r=>r.statusCode===202),JSON.stringify(replies.map(r=>r.statusCode)));
 const ids=replies.map(r=>JSON.parse(r.body).id);assert.equal(new Set(ids).size,1);
 const first=ids[0];objects.add('requests/'+first+'.json');created.add('JOB#'+first);
 const rows=(await doc.send(new ScanCommand({TableName:f.State,ConsistentRead:true}))).Items;
 for(const row of rows)created.add(row.pk);
 assert.ok(rows.filter(r=>r.pk.startsWith('DAY#')||r.pk.startsWith('MONTH#')).every(r=>r.count===1));
 checks.push('six concurrent duplicate submissions admit one job and increment counters once');
 assert.equal((await handler(event('/api/playlist',{...body,prompt:'changed'}))).statusCode,409);checks.push('conflicting idempotency payload rejected');
 assert.equal((await handler(event('/api/playlist',{...body,idempotencyKey:randomUUID(),tracks:[{id:'invalid',sha256:'0'.repeat(64)}]}))).statusCode,400);checks.push('foreign track rejected');
 assert.equal((await handler(event('/api/playlist',body,{'x-resonant-csrf':'wrong'}))).statusCode,403);checks.push('CSRF rejected');
 assert.equal((await handler(event('/api/session',null,{'x-resonant-origin':'wrong'}))).statusCode,403);checks.push('direct-origin secret rejected');
 for(let i=0;i<2;i++){
  const next=await handler(event('/api/playlist',{...body,idempotencyKey:randomUUID()}));assert.equal(next.statusCode,202);const id=JSON.parse(next.body).id;created.add('JOB#'+id);objects.add('requests/'+id+'.json');
 }
 const overflowKey=randomUUID();const denied=await handler(event('/api/playlist',{...body,idempotencyKey:overflowKey}));assert.equal(denied.statusCode,429);
 const hex=sha(owner+'\n'+overflowKey).slice(0,32),orphan=[hex.slice(0,8),hex.slice(8,12),hex.slice(12,16),hex.slice(16,20),hex.slice(20)].join('-');objects.add('requests/'+orphan+'.json');
 checks.push('three outstanding slots enforced by real transactions');
 const stored=await deps.db.get('JOB#'+first);await put({...stored,providerStarted:true,deadline:clock-1});
 const expired=await handler(event('/api/jobs/'+first));assert.equal(JSON.parse(expired.body).status,'failed');assert.equal((await deps.db.get('JOB#'+first)).status,'outcome_unknown');checks.push('expired paid attempt becomes outcome_unknown');
 const replacement=await handler(event('/api/playlist',{...body,idempotencyKey:randomUUID()}));assert.equal(replacement.statusCode,202);const replacementId=JSON.parse(replacement.body).id;created.add('JOB#'+replacementId);objects.add('requests/'+replacementId+'.json');checks.push('terminal slot reclaimed transactionally');
 const foreign=randomBytes(32).toString('base64url'),foreignOwner=sha(foreign);created.add('SESSION#'+foreignOwner);await put({pk:'SESSION#'+foreignOwner,sk:'META',csrf,expires:clock+86400,ttl:clock+86400});
 const foreignEvent=event('/api/jobs/'+replacementId);foreignEvent.cookies=['__Host-resonant_session='+foreign];assert.equal((await handler(foreignEvent)).statusCode,404);checks.push('other session cannot read job');
 result={status:'passed',checks,dispatchesIntercepted:dispatches,lambdaInvocations:0,openaiCalls:0};
}catch(error){result={status:'failed',checks,error:error.message,lambdaInvocations:0,openaiCalls:0};throw error;}
finally{
 // Capture only records from this previously empty, unpublished table. This tool
 // must never be reused after launch; the initial emptiness guard enforces that.
 for(const row of (await doc.send(new ScanCommand({TableName:f.State,ConsistentRead:true}))).Items)created.add(row.pk);
 for(const pk of created)await doc.send(new DeleteCommand({TableName:f.State,Key:{pk,sk:'META'}}));
 for(const Key of objects)await s3.send(new DeleteObjectCommand({Bucket:f.StateBucket,Key,ExpectedBucketOwner:target.account_id}));
 result.fixturesRemoved=true;await mkdir(new URL('output/serverless-cloud/acceptance/',root),{recursive:true,mode:0o700});await writeFile(new URL('output/serverless-cloud/acceptance/api-transactions.json',root),JSON.stringify(result,null,2),{mode:0o600});
}
console.log(JSON.stringify(result));
