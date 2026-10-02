// Explicit integration check: only the existing three-track manual v2 plan.
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const project=fileURLToPath(new URL('../../..',import.meta.url));
const base=process.argv[2]||'http://127.0.0.1:4192';
if(!/^http:\/\/127\.0\.0\.1:\d+$/.test(base))throw Error('Loopback test origin required');
const headers={'Content-Type':'application/json','X-Resonant-Local':'1',Origin:base};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const get=async(id)=>{const r=await fetch(base+'/api/mixes/'+id);assert.equal(r.status,200);return r.json();};
const start=async(plan)=>{const r=await fetch(base+'/api/mixes',{method:'POST',headers,body:JSON.stringify({plan})});assert.equal(r.status,202);return (await r.json()).id;};
async function until(id,predicate){const end=Date.now()+60000;while(Date.now()<end){const j=await get(id);if(predicate(j))return j;if(j.status==='failed')throw Error(j.error);await sleep(100);}throw Error('Mix wait timed out');}
const plan=JSON.parse(await readFile(project+'/examples/mvp-three-track-plan-v2.json','utf8'));
plan.plan_id='delivery-http-verification';plan.segments[0].gain_db-=0.126;
const results={date:new Date().toISOString(),scope:'known three-track v2 plan; first gain -0.126 dB for separate cache'};
const cancelled=await start(plan);await until(cancelled,j=>j.status==='rendering'||j.playable);
const cancel=await fetch(base+'/api/mixes/'+cancelled+'/cancel',{method:'POST',headers});assert.equal(cancel.status,200);await until(cancelled,j=>j.status==='cancelled');
for(let i=0;i<100;i++){const list=await (await fetch(base+'/api/mixes')).json();if(!list.active)break;await sleep(100);}
results.cancelled=true;
const began=performance.now(),id=await start(plan);await until(id,j=>j.playable);
results.http_ready_s=(performance.now()-began)/1000;
const stream=await fetch(base+'/api/mixes/'+id+'/live');assert.equal(stream.status,200);
const hash=createHash('sha256');let bytes=0;for await(const chunk of stream.body){bytes+=chunk.length;hash.update(chunk);}
const done=await until(id,j=>j.status==='complete');assert.equal(hash.digest('hex'),done.hashes['stream.m4a']);results.live_equals_final=true;results.bytes=bytes;results.job=done;
const seekBegan=performance.now();const range=await fetch(base+'/api/mixes/'+id+'/audio',{headers:{Range:'bytes=123456-124479'}});assert.equal(range.status,206);assert.equal((await range.arrayBuffer()).byteLength,1024);results.range_1024_bytes_ms=performance.now()-seekBegan;
const head=await fetch(base+'/api/mixes/'+id+'/master',{method:'HEAD'});assert.equal(head.status,200);assert.equal(head.headers.get('accept-ranges'),'bytes');
const bad=await fetch(base+'/api/mixes/'+id+'/audio',{headers:{Range:'bytes=999999999999-'}});assert.equal(bad.status,416);
const warmId=await start(plan);const warm=await until(warmId,j=>j.status==='complete');assert.equal(warm.cache_hit,true);results.warm_request_wall_s=warm.request_wall_s;
await mkdir(project+'/output/mix-delivery-benchmark',{recursive:true});await writeFile(project+'/output/mix-delivery-benchmark/http-verification.json',JSON.stringify(results,null,2)+'\n');
console.log(JSON.stringify({cancelled:results.cancelled,http_ready_s:results.http_ready_s,live_equals_final:results.live_equals_final,range_1024_bytes_ms:results.range_1024_bytes_ms,warm_request_wall_s:results.warm_request_wall_s}));
