import {DynamoDBClient} from '@aws-sdk/client-dynamodb';
import {DynamoDBDocumentClient,GetCommand,QueryCommand,PutCommand,UpdateCommand,DeleteCommand,TransactWriteCommand} from '@aws-sdk/lib-dynamodb';
import {S3Client,GetObjectCommand,PutObjectCommand} from '@aws-sdk/client-s3';
import {getSignedUrl} from '@aws-sdk/s3-request-presigner';
import {LambdaClient,InvokeCommand} from '@aws-sdk/client-lambda';
import {SSMClient,GetParametersCommand} from '@aws-sdk/client-ssm';
import {canonical,sha,createHandler} from './core.mjs';
import {readFile} from 'node:fs/promises';

export function awsDependencies(env){
 const options={region:'us-east-2',maxAttempts:3};
 const database=DynamoDBDocumentClient.from(new DynamoDBClient(options),{marshallOptions:{removeUndefinedValues:false}});
 const s3=new S3Client(options),ssm=new SSMClient(options),lambda=new LambdaClient({...options,maxAttempts:1});
 const table=env.RESONANT_STATE_TABLE,bucket=env.RESONANT_STATE_BUCKET;
 const conditional=e=>['ConditionalCheckFailedException','TransactionCanceledException'].includes(e?.name);
 const db={conditional,
  async get(pk){return(await database.send(new GetCommand({TableName:table,Key:{pk,sk:'META'},ConsistentRead:true}))).Item;},
  async put(Item){await database.send(new PutCommand({TableName:table,Item,ConditionExpression:'attribute_not_exists(pk)'}));},
  async delete(pk){await database.send(new DeleteCommand({TableName:table,Key:{pk,sk:'META'}}));},
  async update(Key,UpdateExpression,ConditionExpression,ExpressionAttributeNames,ExpressionAttributeValues){return database.send(new UpdateCommand({TableName:table,Key,UpdateExpression,ConditionExpression,...(Object.keys(ExpressionAttributeNames??{}).length?{ExpressionAttributeNames}:{}),ExpressionAttributeValues}));},
  async transact(operations){return database.send(new TransactWriteCommand({TransactItems:operations.map(op=>{const [type,value]=Object.entries(op)[0];return{[type]:{TableName:table,...value}};})}));}
 };
 db.profileGet=async(pk,sk)=>(await database.send(new GetCommand({TableName:table,Key:{pk,sk},ConsistentRead:true}))).Item;
 db.profilePage=async(pk,prefix,cursor,ascending)=>{const page=await database.send(new QueryCommand({TableName:table,KeyConditionExpression:prefix?'pk = :pk AND begins_with(sk,:prefix)':'pk = :pk',ExpressionAttributeValues:{':pk':pk,...(prefix?{':prefix':prefix}:{})},ConsistentRead:true,Limit:100,ScanIndexForward:ascending,...(cursor?{ExclusiveStartKey:{pk,sk:cursor}}:{})}));return{items:(page.Items??[]).map(r=>r.data),cursor:page.LastEvaluatedKey?.sk??null};};
 const objects={
  async immutableRequest(Key,request,digest){
   try{await s3.send(new PutObjectCommand({Bucket:bucket,Key,Body:canonical(request),ContentType:'application/json',CacheControl:'private,no-store',ServerSideEncryption:'AES256',IfNoneMatch:'*'}));}
   catch(e){if(e.$metadata?.httpStatusCode!==412)throw e;const existing=await s3.send(new GetObjectCommand({Bucket:bucket,Key}));if(existing.ContentLength>65536){existing.Body.destroy();throw Error('Invalid stored request');}const raw=await existing.Body.transformToByteArray();if(raw.length>65536||sha(raw)!==digest)throw Object.assign(Error('This request key was already used for different inputs.'),{status:409});}
  },
  async resultUrl(Key){if(!/^results\/[a-f0-9-]{36}\.json$/.test(Key??''))throw Error('Invalid result key');return getSignedUrl(s3,new GetObjectCommand({Bucket:bucket,Key}),{expiresIn:60});}
 };
 let cached,until=0;
 const names={originSecret:env.RESONANT_SECRET_PREFIX+'/origin',passwordHash:env.RESONANT_SECRET_PREFIX+'/password-hash',signingKey:env.RESONANT_SECRET_PREFIX+'/signing-key'};
 async function secrets(){if(Date.now()<until)return cached;const result=await ssm.send(new GetParametersCommand({Names:Object.values(names),WithDecryption:true}));if(result.InvalidParameters?.length)throw Error('Missing secret');const values=new Map(result.Parameters.map(p=>[p.Name,p.Value]));cached=Object.fromEntries(Object.entries(names).map(([key,name])=>[key,values.get(name)]));if(Object.values(cached).some(v=>typeof v!=='string'||!v))throw Error('Missing secret');until=Date.now()+60000;return cached;}
 return{db,objects,secrets,async dispatch(event){const result=await lambda.send(new InvokeCommand({FunctionName:env.RESONANT_WORKER_ALIAS,InvocationType:'Event',Payload:Buffer.from(JSON.stringify(event))}));if(result.StatusCode!==202)throw Error('Dispatch not accepted');}};
}
let handler;
export async function main(event){
 try{if(!handler){const release=JSON.parse(await readFile(new URL('./membership.json',import.meta.url),'utf8'));if(release.releaseId!==process.env.RESONANT_RELEASE_ID)throw Error('Release mismatch');handler=createHandler({...awsDependencies(process.env),config:{...release,origin:process.env.RESONANT_ORIGIN,additionalOrigins:(process.env.RESONANT_ADDITIONAL_ORIGINS??'').split(',').filter(Boolean),keyPairId:process.env.RESONANT_KEY_PAIR_ID}});}return await handler(event);}
 catch{return{statusCode:503,headers:{'content-type':'application/json','cache-control':'private,no-store'},body:'{"error":"The service is temporarily unavailable."}'};}
}
