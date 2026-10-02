import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,rm,symlink} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {recoveryIndex,recoveryAudio} from '../scripts/recovery.mjs';
import {recoverAnalyzedTracks} from '../src/recovery.js';
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
test('recovery scans only supplied folders, matches content to cache, deduplicates and detects changed originals',async()=>{
 const dir=await mkdtemp(path.join(tmpdir(),'resonant-recovery-test-'));
 try{
  const src=path.join(dir,'audio'),cache=path.join(dir,'cache');await mkdir(src);await mkdir(cache);
  await writeFile(path.join(src,'a.mp3'),'audio');await writeFile(path.join(src,'copy.mp3'),'audio');
  await writeFile(path.join(src,'uncached.mp3'),'other');await writeFile(path.join(src,'notes.txt'),'audio');
  await symlink(path.join(src,'uncached.mp3'),path.join(src,'link.mp3'));
  await writeFile(path.join(cache,hash('audio')+'.json'),'{}');
  const found=await recoveryIndex([src,path.join(dir,'missing')],cache);
  assert.equal(found.size,1);const entry=found.get(hash('audio'));
  assert.equal((await recoveryAudio(entry)).toString(),'audio');
  await writeFile(entry.source,'changed');await assert.rejects(recoveryAudio(entry),/changed/);
 }finally{await rm(dir,{recursive:true,force:true});}
});
test('batch restoration is idempotent, skips existing bytes, reuses features and isolates bad audio',async()=>{
 const a=hash('a'),b=hash('b'),c=hash('c'),entries=[a,b,c].map((sha256,i)=>({sha256,filename:`${i}.mp3`}));
 const features={sha256:b,policy:'maest-top6-v1',status:'complete',algorithms:[],genres:[]};
 const stored=new Set([a]);let attached=0,imports=0;
 const library={duplicateIndex:async()=>[...stored].map(hash=>({hash})),importFile:async(file,{hash})=>{stored.add(hash);imports++;return {id:hash};},saveFeatures:async(id,value)=>{assert.equal(id,b);assert.deepEqual(value,features);attached++;},restoreCachedFeatures:async()=>0};
 const request=async(url)=>{
  if(url==='/api/local/recovery')return new Response(JSON.stringify({tracks:entries}));
  if(url==='/api/local/features/'+b)return new Response(JSON.stringify({result:features}));
  if(url==='/api/local/recovery/audio/'+b)return new Response('b');
  if(url==='/api/local/recovery/audio/'+c)return new Response('wrong bytes');
  throw Error('Unexpected request: '+url);
 };
 const result=await recoverAnalyzedTracks(library,()=>{},request);
 assert.equal(result.added,1);assert.equal(result.omitted,1);assert.equal(result.errors.length,1);assert.equal(attached,1);
 assert.match(result.errors[0],/hash/);
 const rerun=await recoverAnalyzedTracks(library,()=>{},request);
 assert.equal(rerun.added,0);assert.equal(rerun.omitted,2);assert.equal(imports,1);
});
test('full recovery includes nested albums and uncached audio without following symlinks',async()=>{
 const dir=await mkdtemp(path.join(tmpdir(),'resonant-recovery-all-'));
 try{
  const src=path.join(dir,'music');await mkdir(path.join(src,'new_albums','album'),{recursive:true});
  await writeFile(path.join(src,'new_albums','album','track.m4a'),'uncached');
  await symlink(src,path.join(src,'loop'));
  const found=await recoveryIndex([src],path.join(dir,'missing-cache'),{includeUnanalyzed:true,recursive:true});
  assert.equal(found.size,1);assert.equal(found.get(hash('uncached')).filename,'track.m4a');
 }finally{await rm(dir,{recursive:true,force:true});}
});
test('uncached audio is restored as unanalyzed without requiring or inventing features',async()=>{
 const sha256=hash('new');let imports=0;
 const library={duplicateIndex:async()=>[],importFile:async()=>{imports++;return {id:'new'};},saveFeatures:()=>assert.fail('No analysis exists'),restoreCachedFeatures:async()=>0};
 const request=async url=>url==='/api/local/recovery'?new Response(JSON.stringify({tracks:[{sha256,filename:'new.mp3',hasAnalysis:false}]})):new Response('new');
 const result=await recoverAnalyzedTracks(library,()=>{},request);assert.equal(imports,1);assert.equal(result.errors.length,0);
});
