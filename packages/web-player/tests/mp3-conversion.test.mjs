import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {mkdtemp,readFile,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {convertM4a} from '../scripts/conversion.mjs';
import {prepareMp3} from '../src/mp3-import.js';
import {LocalLibrary} from '../src/adapters.js';
import {runAnalysisQueue} from '../src/analysis-queue.js';
test('real AAC converts to MP3 with duration and title preserved; invalid audio fails',async()=>{
 const dir=await mkdtemp(path.join(tmpdir(),'resonant-conversion-test-'));
 try{
  const input=path.join(dir,'fixture.m4a'),output=path.join(dir,'fixture.mp3');
  execFileSync('ffmpeg',['-v','error','-f','lavfi','-i','sine=frequency=440:duration=2','-metadata','title=Conversion test','-c:a','aac',input]);
  const bytes=await readFile(input),converted=await convertM4a(bytes);await writeFile(output,converted);
  const info=JSON.parse(execFileSync('ffprobe',['-v','error','-show_streams','-show_format','-of','json',output]));
  assert.equal(info.streams[0].codec_name,'mp3');assert.ok(Math.abs(Number(info.format.duration)-2)<.15);assert.equal(info.format.tags.title,'Conversion test');
  assert.deepEqual(await readFile(input),bytes);
  await assert.rejects(convertM4a(Buffer.from('broken')),/conversion failed/);
 }finally{await rm(dir,{recursive:true,force:true});}
});
test('new uploads pass MP3 unchanged, convert only M4A and surface failures',async()=>{
 const mp3=new File(['mp3'],'a.mp3');assert.equal(await prepareMp3(mp3,()=>assert.fail()),mp3);
 const input=new File(['aac'],'a.M4A');let calls=0;
 const converted=await prepareMp3(input,async(url,options)=>{calls++;assert.match(url,/convert-m4a/);assert.equal(options.body,input);return new Response('mp3',{status:200});});
 assert.equal(converted.name,'a.mp3');assert.equal(converted.type,'audio/mpeg');assert.equal(calls,1);
 await assert.rejects(prepareMp3(new File(['wav'],'a.wav'),()=>assert.fail()),/not supported/);
 await assert.rejects(prepareMp3(input,async()=>new Response(JSON.stringify({error:'Decoder failed'}),{status:400})),/Decoder failed/);
});
test('closed database is reopened once; persistent storage failure pauses queue',async()=>{
 const lib=new LocalLibrary();let reopened=0,calls=0;
 lib.db={close(){}};lib.init=async()=>{reopened++;lib.db={reopened:true};};
 const result=await lib.withDatabase(db=>{calls++;if(!db.reopened)throw new DOMException('connection is closing','InvalidStateError');return 42;});
 assert.equal(result,42);assert.equal(calls,2);assert.equal(reopened,1);
 let attempted=0;
 const run=await runAnalysisQueue([1,2,3],async()=>{attempted++;await lib.withDatabase(()=>{throw new DOMException('closed','InvalidStateError');});});
 assert.equal(attempted,1);assert.equal(run.paused,true);assert.equal(run.errors[0].error.code,'LIBRARY_STORAGE_UNAVAILABLE');
});
test('ordinary track failures do not stop the queue',async()=>{
 const run=await runAnalysisQueue([1,2],async n=>{if(n===1)throw Error('decode');});assert.equal(run.completed,1);assert.equal(run.paused,false);
});
function memoryDB(track,audio){
 const data={tracks:new Map([[track.id,track]]),audio:new Map([[track.id,audio]])};
 return {data,transaction(){
  const staged={tracks:new Map(data.tracks),audio:new Map(data.audio)};let aborted=false;
  const tx={abort(){aborted=true;queueMicrotask(()=>tx.onabort?.());},objectStore(name){return {
   get(id){const request={};queueMicrotask(()=>{request.result=structuredClone(staged[name].get(id));request.onsuccess?.();});return request;},
   put(value,key){staged[name].set(key??value.id,value);}
  };}};
  setTimeout(()=>{if(!aborted){data.tracks=staged.tracks;data.audio=staged.audio;tx.oncomplete?.();}},0);return tx;
 }};
}
test('conversion keeps IDs, backs up original audio/features atomically and rejects stale replacement',async()=>{
 const previous=globalThis.document;
 globalThis.document={createElement(){return {duration:2,load(){},removeAttribute(){},set src(v){queueMicrotask(()=>this.onloadedmetadata());}};}};
 try{
  const track={id:'song',title:'Song',artist:'Artist',kind:'local',status:'ready',duration:2,fileHash:'old',evidence:[],features:{sha256:'old'}};
  const original=new File(['aac'],'song.m4a');const lib=new LocalLibrary();lib.db=memoryDB(track,original);
  const result=await lib.replaceAudioWithMp3('song',new File(['mp3'],'song.mp3'),'old');
  assert.equal(result.id,'song');assert.notEqual(result.fileHash,'old');assert.ok(!result.features);
  const backup=lib.db.data.audio.get('conversion-backup:song:old');assert.equal(await backup.audio.text(),'aac');assert.equal(backup.track.features.sha256,'old');
  assert.equal(lib.db.data.audio.get('song').name,'song.mp3');
  await assert.rejects(lib.replaceAudioWithMp3('song',new File(['other'],'song.mp3'),'old'),e=>e.code==='LIBRARY_TRACK_CHANGED');
  assert.equal(await lib.db.data.audio.get('song').text(),'mp3');
  await assert.rejects(lib.saveFeatures('song',{sha256:'old'}),e=>e.code==='LIBRARY_TRACK_CHANGED');
  assert.ok(!lib.db.data.tracks.get('song').features);
 }finally{globalThis.document=previous;}
});
