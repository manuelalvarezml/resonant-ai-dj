import test from 'node:test';
import assert from 'node:assert/strict';
import {DynamoDBDocumentClient} from '@aws-sdk/lib-dynamodb';
import {awsDependencies} from '../aws.mjs';
test('whole-partition user queries omit the empty sort-key value DynamoDB rejects',async t=>{
 const calls=[];t.mock.method(DynamoDBDocumentClient.prototype,'send',async command=>{calls.push(command.input);for(const v of Object.values(command.input.ExpressionAttributeValues))assert.notEqual(v,'','DynamoDB rejects empty key attributes');return{Items:[]};});
 const {db}=awsDependencies({RESONANT_STATE_TABLE:'fixture',RESONANT_STATE_BUCKET:'fixture'});
 await db.profilePage('USERS','','',false);assert.deepEqual(calls[0].ExpressionAttributeValues,{':pk':'USERS'});assert.equal(calls[0].KeyConditionExpression,'pk = :pk');
 await db.profilePage('PROFILE#listener','state#','state#playlist#same',true);assert.equal(calls[1].ExpressionAttributeValues[':pk'],'PROFILE#listener');assert.deepEqual(calls[1].ExclusiveStartKey,{pk:'PROFILE#listener',sk:'state#playlist#same'});
});
