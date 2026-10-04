import test from 'node:test';
import assert from 'node:assert/strict';
import {randomUUID} from 'node:crypto';
import {createProfileStore} from '../profile.mjs';
class DB{
 rows=new Map();conflicts=0;
 conditional=e=>e.name==='TransactionCanceledException';
 key=(pk,sk='META')=>pk+'|'+sk;
 async get(pk){return structuredClone(this.rows.get(this.key(pk)));}
 async profileGet(pk,sk){return structuredClone(this.rows.get(this.key(pk,sk)));}
 async profilePage(pk,prefix,cursor,asc){const rows=[...this.rows.values()].filter(r=>r.pk===pk&&r.sk.startsWith(prefix)).sort((a,b)=>asc?a.sk.localeCompare(b.sk):b.sk.localeCompare(a.sk));const start=cursor?rows.findIndex(r=>r.sk===cursor)+1:0;return{items:rows.slice(start,start+100).map(r=>r.data),cursor:start+100<rows.length?rows[start+99].sk:null};}
 async transact(ops){for(const{Put:p}of ops){const old=this.rows.get(this.key(p.Item.pk,p.Item.sk));if(p.ConditionExpression==='attribute_not_exists(pk)'?!!old:old?.revision!==p.ExpressionAttributeValues[':r']){this.conflicts++;throw Object.assign(Error('conflict'),{name:'TransactionCanceledException'});}}for(const{Put:p}of ops)this.rows.set(this.key(p.Item.pk,p.Item.sk),structuredClone(p.Item));}
}
const op=value=>({id:randomUUID(),at:Date.now(),...value});
test('shared profile merges concurrent listening transactions and retry is exactly once',async()=>{const db=new DB(),store=createProfileStore(db,new Set(['a'])),a=op({type:'listen',trackId:'a',seconds:31,qualified:1,requestId:'request'}),b=op({type:'listen',trackId:'a',seconds:35,qualified:1,requestId:'request'});await Promise.all([store.apply([a]),store.apply([b]),store.apply([a])]);const{items}=await store.list();assert.equal(items.find(r=>r.kind==='track-stats').seconds,66);assert.equal(items.find(r=>r.kind==='request-stats').qualified,2);assert.deepEqual(items.find(r=>r.kind==='request-stats').qualifiedTrackIds,['a']);assert.ok(db.conflicts>0);assert.ok([...db.rows.values()].every(r=>r.ttl===undefined));await assert.rejects(store.apply([{...a,seconds:32}]),/already used/);});
test('profile rejects nonmembers, bad cursors and oversized batches before writes',async()=>{const db=new DB(),store=createProfileStore(db,new Set(['a']));await assert.rejects(store.apply([op({type:'favorite',trackId:'foreign',value:true})]),/Unknown track/);await assert.rejects(store.list('state','prompt#other'),/Invalid history/);await assert.rejects(store.apply(Array(21).fill(op({type:'favorite',trackId:'a',value:true}))),/batch/);assert.equal(db.rows.size,0);});
test('fresh store instance and separate sessions see same owner playlist',async()=>{const db=new DB(),a=createProfileStore(db,new Set(['a']));await a.apply([op({type:'playlist',playlistId:'p',action:'create',name:'Owner picks',trackIds:['a']})]);const b=createProfileStore(db,new Set(['a']));assert.equal((await b.list()).items[0].name,'Owner picks');});
