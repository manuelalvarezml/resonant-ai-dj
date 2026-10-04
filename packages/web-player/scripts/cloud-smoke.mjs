// Local HTTP acceptance against the exact frozen release. No provider or model call.
import assert from 'node:assert/strict';
import http from 'node:http';
import {mkdtemp,writeFile,rm,mkdir} from 'node:fs/promises';
import {randomBytes} from 'node:crypto';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {cloudConfig,createCloudServer} from './cloud-server.mjs';

const value=flag=>{const i=process.argv.indexOf(flag);return i<0?null:process.argv[i+1];};
const root=value('--release');if(!root)throw Error('Usage: node cloud-smoke.mjs --release ROOT [--out REPORT]');
const state=await mkdtemp(path.join(tmpdir(),'resonant-release-smoke-'));
let app;
try{
  const config=cloudConfig({RESONANT_PUBLIC_ORIGIN:'https://release.invalid',RESONANT_RELEASE_ROOT:path.resolve(root),RESONANT_STATE_ROOT:state,RESONANT_MODEL_ROOT:state,RESONANT_PYTHON:'/unused/python',RESONANT_PROXY_TOKEN:randomBytes(32).toString('hex'),RESONANT_SESSION_SECRET:randomBytes(32).toString('hex')});
  app=await createCloudServer(config,{runner:()=>{throw Error('Smoke checks must never invoke a model.');}});
  await new Promise(resolve=>app.server.listen(0,'127.0.0.1',resolve));
  const port=app.server.address().port;
  const request=(url,{method='GET',headers={},body}={})=>new Promise((resolve,reject)=>{
    const data=body===undefined?undefined:JSON.stringify(body);
    const req=http.request({host:'127.0.0.1',port,path:url,method,headers:{Host:config.host,'X-Resonant-Proxy-Token':config.proxyToken,...(data?{'Content-Type':'application/json','Content-Length':Buffer.byteLength(data)}:{}),...headers}},res=>{const chunks=[];res.on('data',b=>chunks.push(b));res.on('end',()=>resolve({status:res.statusCode,headers:res.headers,data:Buffer.concat(chunks)}));});req.on('error',reject);req.end(data);
  });
  const results=[];
  const page=await request('/');assert.equal(page.status,200);assert.match(page.headers['content-type'],/text\/html/);results.push('static HTML');
  const cookie=page.headers['set-cookie'][0].split(';')[0];
  assert.equal((await request('/',{headers:{'X-Resonant-Proxy-Token':''}})).status,403);results.push('proxy authentication boundary');
  const configResponse=await request('/config.json');assert.equal(JSON.parse(configResponse.data).edition,'web');results.push('web edition config');
  const tracks=[];let cursor=null;
  do{const response=await request('/api/v1/tracks'+(cursor?'?cursor='+cursor:''));assert.equal(response.status,200);const body=JSON.parse(response.data);tracks.push(...body.tracks);cursor=body.next_cursor;}while(cursor);
  assert.equal(tracks.length,app.release.manifest.trackCount);assert.equal(new Set(tracks.map(t=>t.id)).size,tracks.length);results.push('complete paginated catalog');
  for(const track of [tracks[0],tracks[Math.floor(tracks.length/2)],tracks.at(-1)]){
    const playback=await request('/api/v1/playback-sessions',{method:'POST',headers:{Cookie:cookie,Origin:config.origin},body:{track_id:track.id,source_version:track.sourceVersion}});assert.equal(playback.status,200);
    const audio=new URL(JSON.parse(playback.data).url);assert.equal(audio.origin,config.origin);
    for(const range of ['bytes=0-31','bytes=-32']){const response=await request(audio.pathname,{headers:{Range:range}});assert.equal(response.status,206);assert.equal(response.data.length,32);}
    const head=await request(audio.pathname,{method:'HEAD'});assert.equal(head.status,200);assert.equal(head.headers['accept-ranges'],'bytes');
    const size=Number(head.headers['content-length']);assert.equal((await request(audio.pathname,{headers:{Range:`bytes=${size}-`}})).status,416);
  }
  results.push('three real MP3s: HEAD, prefix/suffix ranges, invalid ranges');
  const mix=JSON.parse((await request('/api/web/mix')).data);assert.equal(mix.transitions.length,2);assert.equal((await request('/api/web/mix/audio',{headers:{Range:'bytes=0-31'}})).status,206);results.push('single mix and two transition intervals');
  for(const route of ['/private/planner.json','/release.json','/api/local/analyze','/api/local/recovery','/api/local/convert','/api/mixes','/app-status.json','/prepare-web.html'])assert.equal((await request(route)).status,404,route);
  results.push('private files and owner-only routes blocked');
  const report={schema:'resonant/cloud-local-smoke/1',releaseId:app.release.manifest.releaseId,tracks:tracks.length,checks:results,status:'passed',limits:['Loopback HTTP transport only; HTTPS origin behavior simulated with canonical Host/Origin headers.','No Caddy login/TLS issuance, Linux container, paid OpenAI request, audio analysis or model inference.']};
  const output=value('--out');if(output){await mkdir(path.dirname(path.resolve(output)),{recursive:true});await writeFile(output,JSON.stringify(report,null,2)+'\n');}
  console.log(JSON.stringify(report));
}finally{if(app)await app.close();await rm(state,{recursive:true,force:true});}
