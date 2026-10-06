// Operator-only provisioning/configuration. Credentials are written to ignored output, never stdout.
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {randomBytes} from 'node:crypto';
import {DynamoDBClient} from '@aws-sdk/client-dynamodb';
import {DynamoDBDocumentClient,GetCommand,TransactWriteCommand,PutCommand} from '@aws-sdk/lib-dynamodb';
import {createAccounts} from './accounts.mjs';
const root=resolve(import.meta.dirname,'../../..'),action=process.argv[2],input=process.argv[3];
if(!['create','google'].includes(action)||!input)throw Error('Usage: AWS_PROFILE=manueldev node deploy/serverless/api/manage-accounts.mjs create|google <private-config-file>');
const spec=JSON.parse(await readFile(resolve(input),'utf8'));
const {execFile}=await import('node:child_process');const {promisify}=await import('node:util');if(process.env.AWS_PROFILE!=='manueldev')throw Error('Expected manueldev profile');const target=JSON.parse(await readFile(resolve(root,'output/cloud-preparation/aws-target.json'),'utf8'));const caller=JSON.parse((await promisify(execFile)('aws',['sts','get-caller-identity','--profile','manueldev','--output','json'])).stdout);if(caller.Account!==target.account_id)throw Error('AWS account mismatch');
const table=process.env.RESONANT_STATE_TABLE;if(!table)throw Error('State table required after AWS account guard.');
const client=DynamoDBDocumentClient.from(new DynamoDBClient({region:'us-east-2'}));
const db={get:async pk=>(await client.send(new GetCommand({TableName:table,Key:{pk,sk:'META'},ConsistentRead:true}))).Item,conditional:e=>e.name==='TransactionCanceledException',transact:async ops=>client.send(new TransactWriteCommand({TransactItems:ops.map(o=>{const [type,v]=Object.entries(o)[0];return{[type]:{TableName:table,...v}};})}))};
if(action==='google'){if(!/^[a-zA-Z0-9_-]+\.apps\.googleusercontent\.com$/.test(spec.googleClientId))throw Error('Invalid Google web client ID');await client.send(new PutCommand({TableName:table,Item:{pk:'AUTH#CONFIG',sk:'META',googleClientId:spec.googleClientId}}));console.log('Google client configured.');}
else{
 const accounts=createAccounts(db,()=>Math.floor(Date.now()/1000));if(await accounts.lookup('username',spec.username))throw Error('Account already exists; no reset performed.');
 const password=randomBytes(18).toString('base64url');const user=await accounts.register({username:spec.username,email:spec.email,password,role:spec.owner?'owner':'listener'});
 const dir=resolve(root,'output/accounts');await mkdir(dir,{recursive:true,mode:0o700});const path=resolve(dir,user.username+'.json');await writeFile(path,JSON.stringify({id:user.id,email:user.email,username:user.username,password,role:user.role},null,2)+'\n',{mode:0o600,flag:'wx'});console.log(JSON.stringify({created:true,role:user.role,credentials:path}));
}
