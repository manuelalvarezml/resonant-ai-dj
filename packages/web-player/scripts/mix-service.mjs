import {createReadStream} from 'node:fs';
import {readFile,writeFile,mkdir,readdir,open,stat,rm} from 'node:fs/promises';
import {spawn} from 'node:child_process';
import {randomUUID} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {setTimeout as delay} from 'node:timers/promises';

const project=fileURLToPath(new URL('../../..',import.meta.url));
const json=(res,status,value)=>{res.writeHead(status,{'Content-Type':'application/json','Cache-Control':'no-store'});res.end(JSON.stringify(value));};
export function byteRange(header,size){
  if(!header)return {start:0,end:size-1,partial:false};
  const m=/^bytes=(\d*)-(\d*)$/.exec(header);if(!m||(!m[1]&&!m[2]))return null;
  let start=m[1]?Number(m[1]):Math.max(0,size-Number(m[2])),end=m[1]?(m[2]?Number(m[2]):size-1):size-1;
  if(!Number.isSafeInteger(start)||!Number.isSafeInteger(end)||start<0||start>=size||end<start)return null;
  return {start,end:Math.min(end,size-1),partial:true};
}
export async function serveAudio(req,res,file,type){
  const size=(await stat(file)).size,range=byteRange(req.headers.range,size);
  res.setHeader('Accept-Ranges','bytes');
  if(!range){res.writeHead(416,{'Content-Range':`bytes */${size}`});res.end();return;}
  const {start,end,partial}=range;
  res.writeHead(partial?206:200,{'Content-Type':type,'Content-Length':end-start+1,'Cache-Control':'private, max-age=3600',...(partial?{'Content-Range':`bytes ${start}-${end}/${size}`}:{})});
  if(req.method==='HEAD'){res.end();return;}
  const stream=createReadStream(file,{start,end});res.on('close',()=>stream.destroy());stream.on('error',()=>res.destroy());stream.pipe(res);
}
const publicJob=job=>Object.fromEntries(Object.entries(job).filter(([key])=>!['child','directory','timeout','buffer','log','input'].includes(key)));

export function createMixService({root=project,analysis=path.join(root,'output/step1-collection.json'),cache=path.join(root,'output/mix-delivery'),python=path.join(root,'.venv/bin/python')}={}){
 const jobs=new Map();let active=null;
 async function getJob(id){
  if(jobs.has(id))return jobs.get(id);
  if(!/^[a-f0-9]{64}$/.test(id))return null;
  try{const result=JSON.parse(await readFile(path.join(cache,id,'manifest.json'),'utf8'));if(result.key!==id||result.status!=='complete')return null;return {...result,id,directory:path.join(cache,id)};}catch{return null;}
 }
 async function handler(req,res,port){
  const url=new URL(req.url,'http://localhost');if(!url.pathname.startsWith('/api/mixes'))return false;
  const origin=`http://${req.headers.host}`;
  if(![`127.0.0.1:${port}`,`localhost:${port}`].includes(req.headers.host)||(req.headers.origin&&req.headers.origin!==origin)||['cross-site','same-site'].includes(req.headers['sec-fetch-site'])){json(res,403,{error:'Use the local Resonant app.'});return true;}
  try{
   if(req.method==='GET'&&url.pathname==='/api/mixes'){
    const names=await readdir(path.join(root,'examples'));
    const plans=[];
    for(const name of names.filter(n=>/^[a-zA-Z0-9_-]*plan[a-zA-Z0-9_-]*\.json$/.test(n))){try{const p=JSON.parse(await readFile(path.join(root,'examples',name),'utf8'));plans.push({id:name,title:p.plan_id,description:p.explanation||'',duration_s:p.requested_duration_s});}catch{}}
    let recent=[];try{for(const name of (await readdir(cache)).filter(n=>/^[a-f0-9]{64}$/.test(n))){const job=await getJob(name);if(job)recent.push(publicJob(job));}}catch{}
    json(res,200,{plans,recent:recent.slice(-20),active:active?publicJob(active):null});return true;
   }
   if(req.method==='POST'&&url.pathname==='/api/mixes'){
    if(req.headers.origin!==origin||req.headers['x-resonant-local']!=='1'){json(res,403,{error:'Start a mix from the local app.'});return true;}
    if(active){json(res,409,{error:'Another mix is rendering. Wait or cancel it.'});return true;}
    // Reserve before reading: overlapping requests cannot both start a worker.
    active={id:randomUUID(),status:'preparing',message:'Checking the mix plan and source audio…'};
    const job=active;let bytes=0;const parts=[];
    try{
     for await(const part of req){bytes+=part.length;if(bytes>1024*1024)throw Error('Mix plan is too large');parts.push(part);}
     const payload=JSON.parse(Buffer.concat(parts).toString());
     if(!payload||Object.keys(payload).some(k=>!['planId','plan'].includes(k))||Boolean(payload.planId)===Boolean(payload.plan))throw Error('Choose one saved plan or provide one manual MixPlan');
     await mkdir(path.join(cache,'jobs'),{recursive:true});
     let plan;
     if(payload.planId){if(!/^[a-zA-Z0-9_-]*plan[a-zA-Z0-9_-]*\.json$/.test(payload.planId))throw Error('Unknown saved plan');plan=JSON.parse(await readFile(path.join(root,'examples',payload.planId),'utf8'));}
     else plan=payload.plan;
     job.input=path.join(cache,'jobs',job.id+'.json');await writeFile(job.input,JSON.stringify(plan));
     jobs.set(job.id,job);
     const child=spawn(python,['-m','dj_collection_set_builder.mix_worker','--analysis',analysis,'--plan',job.input,'--cache',cache],{cwd:root,stdio:['ignore','pipe','pipe'],env:{...process.env,PYTHONUNBUFFERED:'1'}});job.child=child;job.buffer='';job.log='';
     child.stdout.on('data',chunk=>{
      job.buffer+=chunk.toString();const lines=job.buffer.split('\n');job.buffer=lines.pop();
      for(const line of lines){try{
       const event=JSON.parse(line);
       if(job.status==='cancelled')continue;
       if(event.event==='started'){job.status='rendering';job.directory=event.directory;job.key=event.key;job.duration_s=event.duration_s;job.message='Rendering your mix…';}
       if(event.event==='playable'){job.playable=true;job.first_fragment_s=event.first_fragment_s;job.message='Ready to preview. Rendering continues…';}
       if(event.event==='verifying'){job.status='verifying';job.render_wall_s=event.render_wall_s;job.message='Audio rendered. Checking duration, source integrity and audio peaks…';}
       if(event.event==='complete'){Object.assign(job,event,{id:job.id,status:'complete',playable:true,message:event.cache_hit?'Reused the verified mix.':'Mix and listening copy are ready.'});delete job.event;if(active===job)active=null;}
       if(event.event==='failed'){job.status='failed';job.error=event.error;job.playable=false;}
      }catch{}}
     });
     child.stderr.on('data',b=>{job.log=(job.log+b.toString()).slice(-2000);});
     const finish=()=>{clearTimeout(job.timeout);if(active===job)active=null;if(!['complete','failed','cancelled'].includes(job.status)){job.status='failed';job.error='The mix worker stopped before completion.';job.playable=false;}void rm(job.input,{force:true});delete job.child;delete job.buffer;delete job.log;};
     child.on('error',()=>{job.status='failed';job.error='The local DJ Python environment is unavailable.';});child.on('close',finish);
     job.timeout=setTimeout(()=>{job.status='failed';job.error='Mix job timed out.';child.kill('SIGTERM');},35*60*1000);job.timeout.unref();
     json(res,202,{id:job.id});return true;
    }catch(error){active=null;if(job.input)await rm(job.input,{force:true});jobs.delete(job.id);throw error;}
   }
   const match=/^\/api\/mixes\/([a-f0-9-]{32,64})(?:\/(live|audio|master|cancel))?$/.exec(url.pathname);
   if(!match){json(res,404,{error:'Unknown mix endpoint'});return true;}
   const job=await getJob(match[1]),action=match[2];
   if(!job){json(res,404,{error:'Mix not found. Completed mixes are available in Recent mixes.'});return true;}
   if(req.method==='POST'&&action==='cancel'){
    if(req.headers.origin!==origin||req.headers['x-resonant-local']!=='1'){json(res,403,{error:'Cancel from the local app.'});return true;}
    if(job.child){job.status='cancelled';job.playable=false;job.child.kill('SIGTERM');}json(res,200,publicJob(job));return true;
   }
   if(!['GET','HEAD'].includes(req.method)){json(res,405,{error:'Method not allowed'});return true;}
   if(!action){json(res,200,publicJob(job));return true;}
   if(action==='audio'||action==='master'){
    if(job.status!=='complete'){json(res,409,{error:'The completed mix is not ready yet.'});return true;}
    if(action==='master')res.setHeader('Content-Disposition','attachment; filename="resonant-mix.wav"');
    await serveAudio(req,res,path.join(job.directory,action==='master'?'master.wav':'stream.m4a'),action==='master'?'audio/wav':'audio/mp4');return true;
   }
   if(action==='live'){
    if(!job.directory||!job.playable||['failed','cancelled'].includes(job.status)){json(res,409,{error:'Preview is not ready.'});return true;}
    if(req.method==='HEAD'){res.writeHead(200,{'Content-Type':'audio/mp4'});res.end();return true;}
    // Tail the same continuous encode that becomes the final listening file.
    let handle;try{handle=await open(path.join(job.directory,'stream.partial.m4a'),'r');}catch{handle=await open(path.join(job.directory,'stream.m4a'),'r');}
    res.writeHead(200,{'Content-Type':'audio/mp4','Cache-Control':'no-store','Accept-Ranges':'none'});
    let offset=0;const buffer=Buffer.alloc(64*1024);
    try{while(!res.destroyed){
      if(['failed','cancelled'].includes(job.status)){res.destroy();break;}
      const {bytesRead}=await handle.read(buffer,0,buffer.length,offset);
      if(bytesRead){offset+=bytesRead;await new Promise(resolve=>{const done=()=>{res.off('close',done);resolve();};res.once('close',done);res.write(buffer.subarray(0,bytesRead),done);});}
      else if(job.status==='complete'){res.end();break;}else await delay(40);
    }}finally{await handle.close();}
    return true;
   }
   json(res,404,{error:'Unknown mix action'});return true;
  }catch(error){if(!res.headersSent)json(res,400,{error:error.message});else res.destroy();return true;}
 }
 handler.close=()=>{active?.child?.kill('SIGTERM');};
 return handler;
}
export const mixService=createMixService();
