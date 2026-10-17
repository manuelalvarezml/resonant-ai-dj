// Loopback companion only. Cloud upload/auth/storage wiring is deliberately absent.
import {spawn} from 'node:child_process';
import {createHash,randomUUID} from 'node:crypto';
import {mkdir,open,rename,readFile,unlink} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const project=fileURLToPath(new URL('../../..',import.meta.url));
export function createArtworkService({webEdition=false,cache=path.join(project,'output/artwork'),python=path.join(project,'tools/artwork/.venv/bin/python')}={}){
 const cli=path.join(project,'tools/artwork/cli.py');
 let worker=null,dirty=false,closed=false,receiving=false;
 const run=(args,input)=>new Promise((resolve,reject)=>{
  const child=spawn(python,[cli,'--cache',cache,...args],{stdio:['pipe','pipe','pipe']});
  let output='',error='';child.stdout.on('data',b=>{output+=b;});child.stderr.on('data',b=>{error=(error+b).slice(-1000);});
  child.on('error',reject);child.on('close',code=>{if(code!==0)reject(Error('Artwork worker unavailable. Install tools/artwork/requirements.txt. '+error));else try{resolve(JSON.parse(output));}catch{reject(Error('Artwork worker returned invalid data.'));}});
  child.stdin.on('error',()=>{});child.stdin.end(input?JSON.stringify(input):undefined);
 });
 const wake=()=>{
  if(closed)return;dirty=true;if(worker)return;
  dirty=false;worker=run(['work']).catch(error=>console.warn('Artwork:',error.message)).finally(()=>{worker=null;if(dirty)wake();});
 };
 const timer=setInterval(wake,30000);timer.unref();
 const handle=async(req,res,port)=>{
  const url=new URL(req.url,'http://localhost');if(!url.pathname.startsWith('/api/artwork/'))return false;
  const reply=(status,data)=>{res.writeHead(status,{'Content-Type':'application/json','Cache-Control':'no-store'});res.end(JSON.stringify(data));};
  const origin=`http://${req.headers.host}`,scope=webEdition?'default':`local-${port}`;
  if(![`127.0.0.1:${port}`,`localhost:${port}`].includes(req.headers.host)||req.headers['sec-fetch-site']==='cross-site'||(req.headers.origin&&req.headers.origin!==origin)){reply(403,{error:'Use this local player.'});return true;}
  try{
   if(req.method==='GET'&&url.pathname==='/api/artwork/manifest'){
    const data=await run(['manifest','--scope',scope]);reply(200,data);return true;
   }
   const image=url.pathname.match(/^\/api\/artwork\/images\/([a-f0-9]{64}\.jpg)$/)?.[1];
   if(image&&['GET','HEAD'].includes(req.method)){
    const bytes=await readFile(path.join(cache,'images',image));res.writeHead(200,{'Content-Type':'image/jpeg','Content-Length':bytes.length,'Cache-Control':'private,max-age=86400'});res.end(req.method==='HEAD'?undefined:bytes);return true;
   }
   if(req.method==='POST'&&url.pathname==='/api/artwork/stored'&&!webEdition){
    if(req.headers.origin!==origin||req.headers['x-resonant-local']!=='1'){reply(403,{error:'Use this local player.'});return true;}
    if(receiving){reply(429,{error:'Artwork intake is busy. Retry shortly.'});return true;}
    const id=url.searchParams.get('id'),version=url.searchParams.get('version');
    if(!/^[\w-]{1,128}$/.test(id??'')||! /^[\w-]{1,128}$/.test(version??''))throw Error('Invalid stored track identity.');
    receiving=true;let temp;
    try{
     await mkdir(path.join(cache,'inbox'),{recursive:true});temp=path.join(cache,'inbox',randomUUID()+'.tmp');
     const file=await open(temp,'wx');const hash=createHash('sha256');let size=0;
     try{for await(const bytes of req){size+=bytes.length;if(size>512*1024*1024)throw Error('Audio exceeds 512 MB.');hash.update(bytes);await file.write(bytes);}if(!size)throw Error('Empty source.');}finally{await file.close();}
     const sha=hash.digest('hex'),stored=path.join(cache,'inbox',sha+'.audio');await rename(temp,stored);temp=null;
     await run(['enqueue'],{scope,track_id:id,source_version:version,source_hash:sha,source_path:stored,metadata:Object.fromEntries(['artist','album','albumartist'].map(k=>[k,(url.searchParams.get(k)??'').slice(0,500)]))});
     reply(202,{queued:true});wake();return true;
    }finally{receiving=false;if(temp)await unlink(temp).catch(()=>{});}
   }
   reply(404,{error:'Artwork route unavailable.'});
  }catch(error){reply(error.code==='ENOENT'?404:503,{error:'Artwork is unavailable; playback is unaffected.'});}
  return true;
 };
 handle.close=async()=>{closed=true;clearInterval(timer);await worker;};
 return handle;
}
