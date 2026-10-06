import test from 'node:test';
import assert from 'node:assert/strict';
import {createAccounts,hashPassword,verifyPassword,identityKey} from '../accounts.mjs';
import {createProfileStore} from '../profile.mjs';
import {recordEvents,adminAnalytics} from '../analytics.mjs';
import {randomUUID} from 'node:crypto';
export class DB{
 rows=new Map();key=(pk,sk='META')=>pk+'|'+sk;
 conditional=e=>e.name==='TransactionCanceledException';
 fail(){throw Object.assign(Error('condition'),{name:'TransactionCanceledException'});}
 async get(pk){return structuredClone(this.rows.get(this.key(pk)));}
 async profileGet(pk,sk){return structuredClone(this.rows.get(this.key(pk,sk)));}
 async profilePage(pk,prefix,cursor,asc){const rows=[...this.rows.values()].filter(r=>r.pk===pk&&r.sk.startsWith(prefix)).sort((a,b)=>asc?a.sk.localeCompare(b.sk):b.sk.localeCompare(a.sk));const start=cursor?rows.findIndex(r=>r.sk===cursor)+1:0;return{items:rows.slice(start,start+100).map(r=>r.data),cursor:start+100<rows.length?rows[start+99].sk:null};}
 async update(Key,UpdateExpression,ConditionExpression,ExpressionAttributeNames,ExpressionAttributeValues){return this.transact([{Update:{Key,UpdateExpression,ConditionExpression,ExpressionAttributeNames,ExpressionAttributeValues}}]);}
 async transact(ops){
  const next=new Map(this.rows);
  for(const op of ops){const p=op.Put,u=op.Update;if(p){const k=this.key(p.Item.pk,p.Item.sk),old=next.get(k);if(p.ConditionExpression==='attribute_not_exists(pk)'?!!old:old?.revision!==p.ExpressionAttributeValues[':r'])this.fail();next.set(k,structuredClone(p.Item));}else{const k=this.key(u.Key.pk,u.Key.sk),r=next.get(k)??u.Key,v=u.ExpressionAttributeValues;if((r.count??0)>=v[':limit'])this.fail();next.set(k,{...r,count:(r.count??0)+1,ttl:v[':ttl']});}}
  this.rows=next;
 }
}
const value={email:'test@example.com',username:'tester',password:'twelve-or-more-characters'};
test('passwords have unique salts and case insensitive identities have unique reservations',async()=>{const db=new DB(),a=createAccounts(db,()=>100);const u=await a.register(value);assert.notEqual(u.passwordHash,value.password);assert.ok(await verifyPassword(value.password,u.passwordHash));assert.equal(await verifyPassword('wrong',u.passwordHash),false);assert.equal((await a.login('TEST@EXAMPLE.COM',value.password)).id,u.id);assert.equal((await a.login('TESTER',value.password)).id,u.id);assert.notEqual(await hashPassword(value.password),u.passwordHash);await assert.rejects(a.register({...value,username:'different'}),/Registration/);await assert.rejects(a.register({...value,email:'different@example.com'}),/Registration/);assert.equal((await db.get('ACCOUNTS#COUNT')).count,1);await assert.rejects(a.login('absent','wrong'),/not recognized/);});
test('simultaneous unique registration is atomic and account cap holds',async()=>{const db=new DB(),a=createAccounts(db,()=>100);const result=await Promise.allSettled([a.register(value),a.register(value)]);assert.equal(result.filter(r=>r.status==='fulfilled').length,1);db.rows.set(db.key('ACCOUNTS#COUNT'),{count:10});await assert.rejects(a.register({...value,email:'next@example.com',username:'next'}),/group is full/);assert.equal(await db.get(identityKey('username','next')),undefined);});
test('same IDs and operation UUIDs are independent between users; cursors cannot cross users',async()=>{const db=new DB(),a=createProfileStore(db,new Set(['one']),'PROFILE#a'),b=createProfileStore(db,new Set(['one']),'PROFILE#b');const op={id:randomUUID(),at:1,type:'playlist',playlistId:'same',action:'create',name:'Private A',trackIds:['one']};await a.apply([op]);assert.deepEqual((await b.list()).items,[]);await b.apply([{...op,name:'Private B'}]);assert.equal((await a.list()).items[0].name,'Private A');assert.equal((await b.list()).items[0].name,'Private B');await assert.rejects(b.list('state','PROFILE#a'),/Invalid/);});
test('events discard arbitrary fields, deduplicate retries and retain only bounded usage evidence',async()=>{const db=new DB(),now=2000000000;const e={id:randomUUID(),at:now*1000,type:'click',view:'library',action:'play-track',password:'must-not-store',email:'private',prompt:'private'};await recordEvents(db,'a','session-a',{events:[e]},now);await recordEvents(db,'a','session-a',{events:[e]},now);const rows=await db.profilePage('EVENTS#a','event#','',true);assert.equal(rows.items.length,1);assert.deepEqual(Object.keys(rows.items[0]).sort(),['id','at','type','view','action','session'].sort());assert.equal((await db.profilePage('EVENTS#b','event#','',true)).items.length,0);assert.equal([...db.rows.values()].find(r=>r.pk==='EVENTS#a').ttl,now+90*86400);await assert.rejects(recordEvents(db,'a','s',{events:[{...e,view:'https://foreign.invalid'}]},now),/Invalid/);});

test('Google tokens enforce signature, issuer, audience, expiry, verified email and nonce',async()=>{
 const {generateKeyPair,exportJWK,SignJWT,createLocalJWKSet}=await import('jose');const {verifyGoogle}=await import('../accounts.mjs');const {privateKey,publicKey}=await generateKeyPair('RS256'),jwk=await exportJWK(publicKey);jwk.kid='fixture';const keys=createLocalJWKSet({keys:[jwk]});
 const sign=(patch={})=>new SignJWT({email:'test@example.com',email_verified:true,nonce:'nonce',sub:'google-subject',...patch}).setProtectedHeader({alg:'RS256',kid:'fixture'}).setIssuer('https://accounts.google.com').setAudience('client').setIssuedAt().setExpirationTime('5m').sign(privateKey);
 const token=await sign();assert.equal((await verifyGoogle(token,'client','nonce',keys)).sub,'google-subject');
 await assert.rejects(verifyGoogle(token,'wrong','nonce',keys),/verified/);await assert.rejects(verifyGoogle(token,'client','wrong',keys),/verified/);await assert.rejects(verifyGoogle(await sign({email_verified:false}),'client','nonce',keys),/verified/);await assert.rejects(verifyGoogle(token.slice(0,-8)+'invalid','client','nonce',keys),/verified/);
});
