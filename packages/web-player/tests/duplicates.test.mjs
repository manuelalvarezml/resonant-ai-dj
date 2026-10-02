import test from 'node:test';
import assert from 'node:assert/strict';
import {duplicateMatch,fileHash,LocalLibrary} from '../src/adapters.js';
import {uniqueAudioTracks,validateTrack} from '../src/model.js';
test('analysis deduplication uses audio hashes and keeps the strongest analysis without changing stored tracks',()=>{
 const first={id:'a',kind:'local',title:'Same title',fileHash:'a'.repeat(64)};
 const analyzed={...first,id:'b',title:'Different tag',features:{policy:'maest-top6-v1',status:'complete'}};
 const other={...first,id:'c',fileHash:'b'.repeat(64)};
 const unknown={...first,id:'d',fileHash:null};
 const input=[first,other,analyzed,unknown,{...unknown,id:'e'}];
 assert.deepEqual(uniqueAudioTracks(input).map(t=>t.id),['b','c','d','e']);
 assert.equal(input.length,5);assert.equal(input[0],first);
 assert.equal(uniqueAudioTracks([{...first,fileHash:null,features:{sha256:first.fileHash}},analyzed]).length,1);
 assert.equal(validateTrack({...first,artist:'',duration:1,status:'ready'}).fileHash,first.fileHash);
});
test('duplicates match identical content first, then normalized filenames; unrelated files pass',async()=>{
 const file=new File(['audio'],'SONG.mp3'),hash=await fileHash(file);
 const index=[{id:'name',name:'song.mp3',hash:'different'},{id:'bytes',name:'renamed.mp3',hash}];
 assert.equal(duplicateMatch(index,file,hash).id,'bytes');
 assert.equal(duplicateMatch(index,file,'new').id,'name');
 assert.equal(duplicateMatch(index,new File(['new'],'other.mp3'),'new'),undefined);
 assert.equal(duplicateMatch([{name:'Cafe\u0301.mp3',hash:'x'}],new File(['a'],'Café.mp3'),'y').name,'Cafe\u0301.mp3');
});
test('replacement preserves identity and analysis only for identical content',async()=>{
 const originalDocument=globalThis.document;
 globalThis.document={createElement(){return {duration:30,load(){},removeAttribute(){},set src(value){queueMicrotask(()=>this.onloadedmetadata());}};}};
 try{
  const file=new File(['audio'],'song.wav'),hash=await fileHash(file),features={sha256:hash,policy:'maest-top6-v1'};
  const lib=new LocalLibrary();lib.read=async()=>({id:'existing',addedAt:1,color:2,features});
  let records;
  lib.db={transaction(){const tx={objectStore(name){return {put(value,key){records[name]=value;}}}};records={};setTimeout(()=>tx.oncomplete(),0);return tx;}};
  const same=await lib.importFile(file,{replaceId:'existing',hash});
  assert.equal(same.id,'existing');assert.equal(same.features,features);assert.equal(same.addedAt,1);assert.equal(records.audio,file);
  const changed=await lib.importFile(new File(['different'],'song.wav'),{replaceId:'existing'});
  assert.equal(changed.id,'existing');assert.equal(changed.features,undefined);assert.notEqual(changed.sourceVersion,same.sourceVersion);
  const both=await lib.importFile(file);assert.notEqual(both.id,'existing');
 }finally{globalThis.document=originalDocument;}
});
test('saved analysis is restored by audio hash without rerunning models',async()=>{
 const hash='a'.repeat(64),stored={id:'local-1',kind:'local',fileHash:hash,title:'Saved',artist:'Artist',album:'Album',duration:1,status:'ready',addedAt:1,sourceVersion:'v1',color:0,evidence:[]};
 const features={sha256:hash,policy:'maest-top6-v1',status:'complete',algorithms:[],genres:[]};let written;
 const lib=new LocalLibrary();lib.read=async(store,id)=>store==='tracks'?(id?stored:[stored]):null;
 lib.db={transaction(){const tx={objectStore(){return {put(value){written=value;}}}};setTimeout(()=>tx.oncomplete(),0);return tx;}};
 assert.equal(await lib.restoreCachedFeatures(async value=>{assert.equal(value,hash);return features;}),1);
 assert.equal(written.features,features);assert.equal(written.fileHash,hash);
 assert.equal(await lib.restoreCachedFeatures(async()=>{throw Error('should not run');}),0);
});
test('cache restoration upgrades partial analysis and rejects features for different audio',async()=>{
 const hash='a'.repeat(64),stored={id:'local-1',kind:'local',fileHash:hash,title:'Saved',artist:'',features:{sha256:hash,policy:'maest-top6-v1',status:'partial',genres:[],algorithms:[]}};
 const complete={...stored.features,status:'complete'};
 const lib=new LocalLibrary();lib.read=async(store,id)=>id?stored:[stored];
 lib.db={transaction(){const tx={objectStore(){return {put(value){Object.assign(stored,value);}}}};setTimeout(()=>tx.oncomplete(),0);return tx;}};
 assert.equal(await lib.restoreCachedFeatures(async()=>({...complete,sha256:'b'.repeat(64)})),0);
 assert.equal(await lib.restoreCachedFeatures(async()=>complete),1);
 assert.equal(stored.features.status,'complete');
});

test('completed reference analysis can gain cached optional estimates without replacing audio or IDs',async()=>{
 const hash='c'.repeat(64),baseline={algorithm_id:'semantic',status:'warning',values:{kept:true}};
 const stored={id:'stable',kind:'local',title:'Same',artist:'Artist',fileHash:hash,evidence:[],features:{sha256:hash,policy:'maest-top6-v1',status:'complete',genres:[],algorithms:[baseline]}};
 const before=structuredClone(stored.features),upgraded={...before,supervised_status:'complete',algorithms:[baseline,{algorithm_id:'emotion_music2emo',status:'warning'},{algorithm_id:'danceability_musicnn',status:'warning'}]};
 const lib=new LocalLibrary();lib.read=async(store,id)=>{assert.equal(store,'tracks');return id?stored:[stored];};
 lib.db={transaction(store){assert.equal(store,'tracks');const tx={objectStore(){return {put(value){Object.assign(stored,value);}}}};setTimeout(()=>tx.oncomplete(),0);return tx;}};
 assert.equal(await lib.restoreCachedFeatures(async()=>upgraded),1);assert.equal(stored.id,'stable');assert.deepEqual(stored.features.algorithms[0],baseline);
 assert.equal(await lib.restoreCachedFeatures(async()=>{assert.fail('already complete optional cache must not be fetched');}),0);
});
test('completed older experiments receive specialist caches without changing source identity',async()=>{
 const hash='d'.repeat(64),old={algorithm_id:'emotion_music2emo',status:'warning'};
 const stored={id:'stable',kind:'local',title:'Same',artist:'Artist',fileHash:hash,evidence:[],features:{sha256:hash,policy:'maest-top6-v1',status:'complete',supervised_status:'complete',genres:[],algorithms:[old]}};
 const newer={...structuredClone(stored.features),feature_version:'selected-estimators-v3-character120',quality_status:'complete',algorithms:[old,{algorithm_id:'instrument_passt',status:'warning'}]};
 const lib=new LocalLibrary();lib.read=async(store,id)=>{assert.equal(store,'tracks');return id?stored:[stored];};
 lib.db={transaction(store){assert.equal(store,'tracks');const tx={objectStore(){return {put(value){Object.assign(stored,value);}}}};setTimeout(()=>tx.oncomplete(),0);return tx;}};
 let calls=0;assert.equal(await lib.restoreCachedFeatures(async()=>{calls++;return newer;}),1);assert.equal(calls,1);assert.equal(stored.fileHash,hash);assert.equal(stored.id,'stable');
 assert.equal(await lib.restoreCachedFeatures(async()=>{calls++;return newer;}),0);assert.equal(calls,1);
});
