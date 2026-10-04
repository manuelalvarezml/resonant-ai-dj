import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,readFile,rm,symlink} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {createHash} from 'node:crypto';
import http from 'node:http';
import {cloudConfig,createCloudServer,loadCloudRelease,byteRange,canonicalPlaylist} from '../scripts/cloud-server.mjs';
import {createJobs} from '../scripts/cloud-jobs.mjs';
import {RELEASE_STAGES} from '../src/release-policy.js';

const hash=data=>createHash('sha256').update(data).digest('hex');
async function fixture(t){
  const root=await mkdtemp(path.join(tmpdir(),'resonant-cloud-test-'));t.after(()=>rm(root,{recursive:true,force:true}));
  const releaseRoot=path.join(root,'release'),stateRoot=path.join(root,'state');
  const audio=Buffer.from('0123456789'),id=hash(audio),track={id,fileHash:id,sourceVersion:id,title:'Fixture song',artist:'Fixture',status:'ready'};
  const features={sha256:id,feature_version:'selected-estimators-v3-character120',status:'complete',policy:'maest-top6-v1',algorithms:RELEASE_STAGES.map(algorithm_id=>({algorithm_id,status:'passed',values:algorithm_id==='metadata'?{codec:'mp3'}:{}}))};
  const contents={'public/index.html':'<!doctype html>Fixture','public/src/app.js':'console.log("fixture")','public/catalog.json':JSON.stringify({revision:hash(JSON.stringify([track])),tracks:[track]}),'public/mix.json':JSON.stringify({duration_s:10,transitions:[{start_s:2,end_s:3},{start_s:6,end_s:7}]}),'private/planner.json':'{}',[`private/features/${id}.json`]:JSON.stringify(features),'media/mix.m4a':audio,[`media/${id}.mp3`]:audio};
  const files=[];
  for(const [relative,content]of Object.entries(contents)){const file=path.join(releaseRoot,relative);await mkdir(path.dirname(file),{recursive:true});await writeFile(file,content);files.push({path:relative,sha256:hash(content),bytes:Buffer.byteLength(content)});}
  const manifest={schema:'resonant/cloud-release/1',trackCount:1,audioBytes:audio.length,files,catalogPath:'public/catalog.json',mixPath:'public/mix.json',mixAudioPath:'media/mix.m4a',featureDirectory:'private/features',plannerPath:'private/planner.json'};manifest.releaseId=hash(JSON.stringify(manifest));await writeFile(path.join(releaseRoot,'release.json'),JSON.stringify(manifest));
  const env={RESONANT_PUBLIC_ORIGIN:'https://music.example',RESONANT_RELEASE_ROOT:releaseRoot,RESONANT_STATE_ROOT:stateRoot,RESONANT_MODEL_ROOT:path.join(root,'models'),RESONANT_PYTHON:'/usr/bin/python3',RESONANT_PROXY_TOKEN:'p'.repeat(32),RESONANT_SESSION_SECRET:'s'.repeat(32)};
  return {root,releaseRoot,stateRoot,env,config:cloudConfig(env),id,track};
}
async function listening(t,config,runner,release){const app=await createCloudServer(config,{runner,release});await new Promise(r=>app.server.listen(0,'127.0.0.1',r));t.after(()=>app.close());return {app,port:app.server.address().port};}
function request(port,config,url,options={}){
  return new Promise((resolve,reject)=>{
    const headers={Host:config.host,'X-Resonant-Proxy-Token':config.proxyToken,...options.headers};
    const body=options.body===undefined?undefined:JSON.stringify(options.body);if(body){headers['Content-Type']='application/json';headers['Content-Length']=Buffer.byteLength(body);}
    const req=http.request({hostname:'127.0.0.1',port,path:url,method:options.method??'GET',headers},res=>{const chunks=[];res.on('data',b=>chunks.push(b));res.on('end',()=>{const bytes=Buffer.concat(chunks);resolve({status:res.statusCode,headers:res.headers,body:bytes.toString(),json:()=>JSON.parse(bytes)});});});req.on('error',reject);req.end(body);
  });
}
const cookie=res=>res.headers['set-cookie'][0].split(';')[0];
const delay=ms=>new Promise(r=>setTimeout(r,ms));

test('production config fails closed for plaintext remote origin, weak/equal secrets and state inside release',async t=>{
  const f=await fixture(t);
  assert.throws(()=>cloudConfig({...f.env,RESONANT_PUBLIC_ORIGIN:'http://music.example'}));
  assert.throws(()=>cloudConfig({...f.env,RESONANT_PROXY_TOKEN:'weak'}));
  assert.throws(()=>cloudConfig({...f.env,RESONANT_SESSION_SECRET:'p'.repeat(32)}));
  assert.throws(()=>cloudConfig({...f.env,RESONANT_STATE_ROOT:f.releaseRoot+'/state'}));
  assert.throws(()=>cloudConfig({...f.env,RESONANT_PUBLIC_ORIGIN:'https://music.example/a'}));
});
test('manifest validation detects tampering and symlink escape',async t=>{
  const f=await fixture(t);await loadCloudRelease(f.releaseRoot);
  await writeFile(path.join(f.releaseRoot,'public/index.html'),'changed');await assert.rejects(loadCloudRelease(f.releaseRoot),/checksum/);
  const second=await fixture(t);await rm(path.join(second.releaseRoot,'public/index.html'));await symlink('/etc/hosts',path.join(second.releaseRoot,'public/index.html'));await assert.rejects(loadCloudRelease(second.releaseRoot),/symlink/);
});
test('range parsing handles suffix, open-ended, out-of-range and multipart',()=>{
  assert.deepEqual(byteRange('bytes=-3',10),{start:7,end:9,partial:true});assert.deepEqual(byteRange('bytes=4-',10),{start:4,end:9,partial:true});
  for(const v of ['bytes=10-','bytes=-0','bytes=5-2','bytes=1-3,4-5','bytes=-','bytes=99999999999999999999-'])assert.equal(byteRange(v,10),null);
});
test('HTTPS origin, proxy boundary, protected media, routes and ranges integrate',async t=>{
  const f=await fixture(t),{port}=await listening(t,f.config);
  assert.equal((await request(port,f.config,'/',{headers:{'X-Resonant-Proxy-Token':''}})).status,403);
  assert.equal((await request(port,f.config,'/',{headers:{Host:'evil.example'}})).status,403);
  const page=await request(port,f.config,'/');assert.equal(page.status,200);assert.match(page.headers['set-cookie'][0],/Secure/);const session=cookie(page);
  for(const url of ['/private/planner.json','/release.json','/api/local/analyze','/api/local/recovery','/prepare-web.html','/app-status.json','/media/'+f.id+'.mp3'])assert.equal((await request(port,f.config,url)).status,404,url);
  const catalog=await request(port,f.config,'/api/v1/tracks');assert.equal(catalog.json().tracks[0].id,f.id);
  const payload={track_id:f.id,source_version:f.id};
  assert.equal((await request(port,f.config,'/api/v1/playback-sessions',{method:'POST',body:payload,headers:{Cookie:session,Origin:'https://evil.example'}})).status,403);
  const sessionResponse=await request(port,f.config,'/api/v1/playback-sessions',{method:'POST',body:payload,headers:{Cookie:session,Origin:f.config.origin}});
  assert.equal(sessionResponse.status,200);assert.match(sessionResponse.json().url,/^https:\/\/music\.example\//);
  const audio='/api/web/audio/'+f.id;
  const partial=await request(port,f.config,audio,{headers:{Range:'bytes=3-5'}});assert.equal(partial.status,206);assert.equal(partial.body,'345');assert.equal(partial.headers['content-range'],'bytes 3-5/10');
  const head=await request(port,f.config,audio,{method:'HEAD'});assert.equal(head.status,200);assert.equal(head.headers['content-length'],'10');assert.equal(head.body,'');
  assert.equal((await request(port,f.config,audio,{headers:{Range:'bytes=10-'}})).status,416);
});
test('playlist canonicalization ignores forged metadata and rejects unpublished or duplicate songs',async t=>{
  const f=await fixture(t),tracks=new Map([[f.id,f.track]]),value={prompt:'house',tracks:[{id:f.id,sha256:f.id,title:'FORGED'}]};
  assert.equal(canonicalPlaylist(value,tracks).tracks[0].title,'Fixture song');
  assert.throws(()=>canonicalPlaylist({...value,tracks:[...value.tracks,...value.tracks]},tracks));
  assert.throws(()=>canonicalPlaylist({...value,tracks:[{id:'a'.repeat(64),sha256:'a'.repeat(64)}]},tracks));
});
test('catalog pagination bounds large feature payloads and visits every track once',async t=>{
  const f=await fixture(t),release=await loadCloudRelease(f.releaseRoot);
  release.catalog.tracks=Array.from({length:61},(_,index)=>({...f.track,id:hash(String(index)),title:'Fixture '+index}));
  release.tracks=new Map(release.catalog.tracks.map(track=>[track.id,track]));
  const {port}=await listening(t,f.config,undefined,release),seen=[],sizes=[];
  let cursor=null;
  do{
    const response=await request(port,f.config,'/api/v1/tracks'+(cursor?'?cursor='+cursor:''));
    assert.equal(response.status,200);
    const page=response.json();sizes.push(page.tracks.length);seen.push(...page.tracks.map(track=>track.id));cursor=page.next_cursor;
    assert.ok(sizes.length<=3,'pagination must terminate');
  }while(cursor);
  assert.deepEqual(sizes,[25,25,11]);
  assert.deepEqual(seen,release.catalog.tracks.map(track=>track.id));
});
test('shutdown bounds an unfinished media response from a paused client', {timeout:5000},async t=>{
  const f=await fixture(t),release=await loadCloudRelease(f.releaseRoot),file=path.join(f.root,'slow-media.mp3');
  await writeFile(file,Buffer.alloc(16*1024*1024));
  release.files.set(`media/${f.id}.mp3`,{file,bytes:16*1024*1024});
  const {port,app}=await listening(t,f.config,undefined,release);
  let client;
  const response=await new Promise((resolve,reject)=>{
    client=http.get({hostname:'127.0.0.1',port,path:'/api/web/audio/'+f.id,headers:{Host:f.config.host,'X-Resonant-Proxy-Token':f.config.proxyToken}},resolve);
    client.on('error',reject);
  });
  response.pause();response.on('error',()=>{});
  assert.equal(response.complete,false);
  const closing=app.close();let deadline;
  try{
    await Promise.race([closing,new Promise((_,reject)=>{deadline=setTimeout(()=>reject(Error('Shutdown waited for the slow client')),2500);})]);
    assert.equal(app.server.listening,false);
  }finally{clearTimeout(deadline);response.destroy();client.destroy();await closing;}
});
test('one active prompt, session-scoped polling and persisted daily quota',async t=>{
  const f=await fixture(t);let complete;
  const runner=(_config,_input,out)=>({done:new Promise(resolve=>{complete=async()=>{await writeFile(out,JSON.stringify({result:{tracks:[f.id]}}));resolve();};}),cancel(){void complete();}});
  const config={...f.config,dailyLimit:1}, {port,app}=await listening(t,config,runner);
  const a=cookie(await request(port,config,'/')),b=cookie(await request(port,config,'/'));
  const payload={prompt:'house',tracks:[{id:f.id,sha256:f.id}]};
  const start=()=>request(port,config,'/api/local/playlist',{method:'POST',body:payload,headers:{Cookie:a,Origin:config.origin}});
  const accepted=await start();assert.equal(accepted.status,202);const id=accepted.json().id;
  assert.equal((await start()).status,409);
  assert.equal((await request(port,config,'/api/local/jobs/'+id,{headers:{Cookie:b}})).status,404);
  await complete();let job;
  for(let i=0;i<30;i++){job=await request(port,config,'/api/local/jobs/'+id,{headers:{Cookie:a}});if(job.json().status==='complete')break;await delay(5);}
  assert.equal(job.json().status,'complete');assert.equal((await start()).status,429);
  const persisted=JSON.parse(await readFile(path.join(f.stateRoot,'prompt-quota.json')));assert.equal(persisted.count,1);
  await app.close();const restarted=await createJobs(config,{runner});t.after(()=>restarted.close());await assert.rejects(restarted.start(payload,'owner'),e=>e.status===429);
});
test('timeout retains the concurrency slot until worker termination completes',async t=>{
  const f=await fixture(t);let rejectWorker,cancelled=false;
  const jobs=await createJobs({...f.config,jobTimeoutMs:10},{runner:()=>({done:new Promise((_r,reject)=>{rejectWorker=reject;}),cancel(){cancelled=true;}})});t.after(()=>jobs.close());
  const {id}=await jobs.start({prompt:'fixture'},'owner');await delay(25);assert.equal(cancelled,true);
  await assert.rejects(jobs.start({prompt:'another'},'owner'),e=>e.status===409);
  rejectWorker(Error('terminated'));await delay(10);assert.equal(jobs.get(id,'owner').status,'failed');
});
