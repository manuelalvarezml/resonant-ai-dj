import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,writeFile,mkdir,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {Readable,Writable} from 'node:stream';
import {once} from 'node:events';
import {byteRange,serveAudio,createMixService} from '../scripts/mix-service.mjs';
import {bufferedAhead} from '../src/mix-stream.js';

class Response extends Writable{
 constructor(){super();this.headers={};this.parts=[];this.statusCode=0;}
 setHeader(k,v){this.headers[k]=v;}
 writeHead(code,headers={}){this.statusCode=code;Object.assign(this.headers,headers);this.headersSent=true;}
 _write(data,encoding,callback){this.parts.push(Buffer.from(data));callback();}
 get data(){return Buffer.concat(this.parts);}
}
function req(url,method='GET',payload=null,headers={}){const r=Readable.from(payload?[Buffer.from(JSON.stringify(payload))]:[]);r.url=url;r.method=method;r.headers={host:'127.0.0.1:4192',...headers};return r;}
async function invoke(handler,request){const res=new Response();await handler(request,res,4192);if(!res.writableFinished)await once(res,'finish');return res;}

test('range semantics cover bounded, open, suffix, clamped and unsatisfiable requests',()=>{
 assert.deepEqual(byteRange('bytes=2-5',10),{start:2,end:5,partial:true});
 assert.deepEqual(byteRange('bytes=6-',10),{start:6,end:9,partial:true});
 assert.deepEqual(byteRange('bytes=-3',10),{start:7,end:9,partial:true});
 assert.equal(byteRange('bytes=20-',10),null);assert.equal(byteRange('bytes=-0',10),null);
 assert.equal(byteRange('bytes=0-1,3-5',10),null);assert.equal(byteRange('bytes=4-3',10),null);
 assert.deepEqual(byteRange('bytes=1-999',10),{start:1,end:9,partial:true});
});
test('completed media streams exact byte ranges; HEAD and 416 contain no audio',async()=>{
 const root=await mkdtemp(path.join(tmpdir(),'mix-http-'));const file=path.join(root,'audio');await writeFile(file,'0123456789');
 try{const res=new Response();await serveAudio(req('/','GET',null,{range:'bytes=2-5'}),res,file,'audio/mp4');await once(res,'finish');assert.equal(res.statusCode,206);assert.equal(res.data.toString(),'2345');assert.equal(res.headers['Content-Range'],'bytes 2-5/10');
 for(const [method,range,status] of [['HEAD','bytes=0-3',206],['GET','bytes=40-',416]]){const res=new Response();await serveAudio(req('/',method,null,{range}),res,file,'audio/mp4');assert.equal(res.statusCode,status);assert.equal(res.data.length,0);}
 }finally{await rm(root,{recursive:true,force:true});}
});
test('mix API rejects foreign origins, missing local authorization and path traversal',async()=>{
 const service=createMixService();
 for(const request of [req('/api/mixes','POST',{},{}),req('/api/mixes','POST',{}, {origin:'https://example.com','x-resonant-local':'1'}),req('/api/mixes','GET',null,{'sec-fetch-site':'cross-site'})]){assert.equal((await invoke(service,request)).statusCode,403);}
 const res=await invoke(service,req('/api/mixes','POST',{planId:'../../secret.json'},{origin:'http://127.0.0.1:4192','x-resonant-local':'1'}));assert.equal(res.statusCode,400);
});
test('completed mixes can be restored after restart without exposing internal paths',async()=>{
 const root=await mkdtemp(path.join(tmpdir(),'mix-persist-'));const key='a'.repeat(64);await mkdir(path.join(root,'output/mix-delivery',key),{recursive:true});await mkdir(path.join(root,'examples'));
 await writeFile(path.join(root,'output/mix-delivery',key,'manifest.json'),JSON.stringify({key,status:'complete',plan_id:'test',duration_s:10}));
 try{const service=createMixService({root});const res=await invoke(service,req('/api/mixes/'+key));assert.equal(res.statusCode,200);assert.equal(JSON.parse(res.data).directory,undefined);const list=await invoke(service,req('/api/mixes'));assert.equal(JSON.parse(list.data).recent[0].id,key);}finally{await rm(root,{recursive:true,force:true});}
});
test('preview buffering counts only the range containing the playhead',()=>{
 const buffered={length:2,start:i=>[0,20][i],end:i=>[10,30][i]};assert.equal(bufferedAhead({buffered,currentTime:5}),5);assert.equal(bufferedAhead({buffered,currentTime:15}),0);assert.equal(bufferedAhead({buffered,currentTime:25}),5);
});
