import test from 'node:test';
import assert from 'node:assert/strict';
import {reviewPrompts,recordReviewAttempt} from '../src/playlist-review.js';
test('review preserves repeated runs, failure evidence and exact candidate identities',()=>{
 const store=new Map();globalThis.localStorage={getItem:k=>store.get(k)??null,setItem:(k,v)=>store.set(k,v)};
 const candidates=[{id:'a',title:'Song',artist:'Artist',features:{sha256:'abc'}}];
 const first=recordReviewAttempt({prompt:reviewPrompts[0].prompt,run:{result:{matches:[]}},candidates,elapsedMs:50});
 const second=recordReviewAttempt({prompt:reviewPrompts[0].prompt,error:'Unavailable',candidates,elapsedMs:10});
 const saved=JSON.parse([...store.values()][0]);
 assert.equal(saved.attempts.length,2);assert.notEqual(first.entry.id,second.entry.id);
 assert.equal(saved.attempts[0].testId,'P01');assert.equal(saved.attempts[1].error,'Unavailable');assert.equal(saved.attempts[0].catalog[0].sha256,'abc');
 globalThis.localStorage.setItem=()=>{throw Error('full');};
 assert.equal(recordReviewAttempt({prompt:'custom',candidates,elapsedMs:1}).saved,false);
 delete globalThis.localStorage;
});
