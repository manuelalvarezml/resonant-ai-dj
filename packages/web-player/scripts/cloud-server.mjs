import http from 'node:http';
import {createReadStream} from 'node:fs';
import {readFile,realpath,lstat,mkdir} from 'node:fs/promises';
import {createHash,createHmac,randomBytes,timingSafeEqual} from 'node:crypto';
import {pipeline} from 'node:stream/promises';
import path from 'node:path';
import {createJobs} from './cloud-jobs.mjs';
import {fullyAnalyzed} from '../src/release-policy.js';

const HASH=/^[a-f0-9]{64}$/;
const CATALOG_PAGE_SIZE=25;
const MIME={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8','.svg':'image/svg+xml','.ttf':'font/ttf','.txt':'text/plain; charset=utf-8','.png':'image/png','.ico':'image/x-icon'};
const CSP="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' blob: data:; media-src 'self' blob:; connect-src 'self'; font-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'";
const same=(a,b)=>{const aa=Buffer.from(a??''),bb=Buffer.from(b??'');return aa.length===bb.length&&timingSafeEqual(aa,bb);};
const bounded=(value,fallback,min,max)=>{const n=value===undefined?fallback:Number(value);if(!Number.isSafeInteger(n)||n<min||n>max)throw Error('Invalid numeric runtime setting.');return n;};

export function cloudConfig(env=process.env){
  const origin=new URL(env.RESONANT_PUBLIC_ORIGIN??'');
  const local=env.RESONANT_ALLOW_HTTP_LOCAL==='1'&&['127.0.0.1','localhost'].includes(origin.hostname)&&origin.protocol==='http:';
  if((origin.protocol!=='https:'&&!local)||origin.pathname!=='/'||origin.search||origin.hash||origin.username||origin.password)throw Error('Set a canonical HTTPS RESONANT_PUBLIC_ORIGIN.');
  const required=name=>{const value=env[name];if(!value)throw Error(`Missing ${name}.`);return value;};
  const absolute=name=>{const value=required(name);if(!path.isAbsolute(value))throw Error(`${name} must be absolute.`);return path.resolve(value);};
  const config={origin:origin.origin,host:origin.host,secure:!local,releaseRoot:absolute('RESONANT_RELEASE_ROOT'),stateRoot:absolute('RESONANT_STATE_ROOT'),modelRoot:absolute('RESONANT_MODEL_ROOT'),python:required('RESONANT_PYTHON'),proxyToken:required('RESONANT_PROXY_TOKEN'),sessionSecret:required('RESONANT_SESSION_SECRET'),listenHost:env.RESONANT_HOST??'127.0.0.1',port:bounded(env.RESONANT_PORT,4175,1,65535),dailyLimit:bounded(env.RESONANT_DAILY_PROMPT_LIMIT,30,1,1000),jobTimeoutMs:bounded(env.RESONANT_JOB_TIMEOUT_SECONDS,360,1,900)*1000};
  if(config.proxyToken.length<32||config.sessionSecret.length<32||same(config.proxyToken,config.sessionSecret))throw Error('Use independent proxy/session secrets of at least 32 characters.');
  if(config.stateRoot===config.releaseRoot||config.stateRoot.startsWith(config.releaseRoot+path.sep))throw Error('Writable state must be outside the immutable release.');
  if(!path.isAbsolute(config.python))throw Error('RESONANT_PYTHON must be an absolute executable path.');
  return config;
}

export async function containedFile(root,relative){
  if(typeof relative!=='string'||relative.includes('\\')||relative.startsWith('/')||relative.split('/').some(x=>!x||x==='.'||x==='..'||x.startsWith('.')))throw Error('Invalid release path.');
  const base=await realpath(root),filename=path.join(base,relative);
  let current=base;
  for(const part of relative.split('/')){current=path.join(current,part);if((await lstat(current)).isSymbolicLink())throw Error('Release symlinks are not allowed.');}
  const resolved=await realpath(filename);if(!resolved.startsWith(base+path.sep)||!(await lstat(resolved)).isFile())throw Error('Invalid release file.');
  return resolved;
}
async function sha256(file){const digest=createHash('sha256');for await(const chunk of createReadStream(file))digest.update(chunk);return digest.digest('hex');}

export async function loadCloudRelease(root){
  const manifest=JSON.parse(await readFile(await containedFile(root,'release.json'),'utf8'));
  if(manifest.schema!=='resonant/cloud-release/1')throw Error('Unsupported release manifest.');
  const {releaseId,...manifestBody}=manifest;
  if(!HASH.test(releaseId??'')||createHash('sha256').update(JSON.stringify(manifestBody)).digest('hex')!==releaseId)throw Error('Release manifest digest mismatch.');
  if(!Array.isArray(manifest.files)||manifest.files.length>20000)throw Error('Invalid release inventory.');
  if(manifest.catalogPath!=='public/catalog.json'||manifest.mixPath!=='public/mix.json'||manifest.mixAudioPath!=='media/mix.m4a'||manifest.featureDirectory!=='private/features'||manifest.plannerPath!=='private/planner.json')throw Error('Unsupported release locations.');
  const files=new Map();
  for(const item of manifest.files){
    if(files.has(item.path)||! /^(public|private|media)\//.test(item.path)||!HASH.test(item.sha256)||!Number.isSafeInteger(item.bytes)||item.bytes<0)throw Error('Invalid release inventory entry.');
    const file=await containedFile(root,item.path),info=await lstat(file);
    if(info.size!==item.bytes||await sha256(file)!==item.sha256)throw Error('Release checksum mismatch.');
    files.set(item.path,{...item,file});
  }
  const json=async relative=>{if(!files.has(relative))throw Error('Required artifact missing from inventory.');return JSON.parse(await readFile(files.get(relative).file,'utf8'));};
  const catalog=await json(manifest.catalogPath??'public/catalog.json'),mix=await json(manifest.mixPath??'public/mix.json');
  if(!Array.isArray(catalog.tracks)||!catalog.tracks.length||catalog.tracks.length!==manifest.trackCount)throw Error('Catalog count mismatch.');
  if(createHash('sha256').update(JSON.stringify(catalog.tracks)).digest('hex')!==catalog.revision)throw Error('Catalog revision mismatch.');
  const tracks=new Map();
  let audioBytes=0;
  for(const t of catalog.tracks){
    const audio=files.get(`media/${t.id}.mp3`);
    if(!HASH.test(t.id)||t.id!==t.fileHash||t.id!==t.sourceVersion||tracks.has(t.id)||audio?.sha256!==t.id)throw Error('Invalid published track.');
    const features=await json(`private/features/${t.id}.json`);
    if(!fullyAnalyzed(features)||features.sha256!==t.id)throw Error('Ineligible published analysis.');
    audioBytes+=audio.bytes;tracks.set(t.id,t);
  }
  if(audioBytes!==manifest.audioBytes)throw Error('Audio byte count mismatch.');
  if(!files.has('private/planner.json')||!files.has(manifest.mixAudioPath??'media/mix.m4a')||!files.has('public/index.html'))throw Error('Release is not ready: planner, media or static assets missing.');
  return {manifest,files,catalog,mix,tracks};
}

export function byteRange(header,size){
  if(header===undefined)return {start:0,end:size-1,partial:false};
  if(typeof header!=='string'||!/^bytes=\d*-\d*$/.test(header))return null;
  const [a,b]=header.slice(6).split('-');if(!a&&!b)return null;
  const start=a?Number(a):Math.max(0,size-Number(b)),end=a?(b?Math.min(Number(b),size-1):size-1):size-1;
  if(!Number.isSafeInteger(start)||!Number.isSafeInteger(end)||start<0||start>=size||end<start||(!a&&Number(b)===0))return null;
  return {start,end,partial:true};
}
async function media(req,res,item,type){
  const range=byteRange(req.headers.range,item.bytes);res.setHeader('Accept-Ranges','bytes');res.setHeader('Content-Type',type);
  if(!range){res.writeHead(416,{'Content-Range':`bytes */${item.bytes}`});res.end();return;}
  const {start,end,partial}=range;
  res.writeHead(partial?206:200,{'Content-Length':end-start+1,...(partial?{'Content-Range':`bytes ${start}-${end}/${item.bytes}`}:{})});
  if(req.method==='HEAD'){res.end();return;}
  try{await pipeline(createReadStream(item.file,{start,end}),res);}catch{res.destroy();}
}
async function jsonBody(req,max=1024*1024){
  if(!String(req.headers['content-type']??'').toLowerCase().startsWith('application/json'))throw Object.assign(Error('JSON required.'),{status:415});
  const chunks=[];let size=0;for await(const chunk of req){size+=chunk.length;if(size>max)throw Object.assign(Error('Request too large.'),{status:413});chunks.push(chunk);}
  try{return JSON.parse(Buffer.concat(chunks).toString('utf8'));}catch{throw Object.assign(Error('Invalid JSON.'),{status:400});}
}
export function canonicalPlaylist(value,tracks){
  const invalid=()=>{throw Object.assign(Error('Invalid playlist request.'),{status:400});};
  if(!value||typeof value!=='object'||Array.isArray(value)||Object.keys(value).some(k=>!['prompt','tracks','clarifications','estimator_profile'].includes(k))||typeof value.prompt!=='string'||!value.prompt.trim()||value.prompt.length>4000||!Array.isArray(value.tracks)||!value.tracks.length||value.tracks.length>tracks.size)invalid();
  const seen=new Set();
  const selected=value.tracks.map(t=>{const saved=tracks.get(t?.id);if(!saved||seen.has(t.id)||t.sha256!==saved.fileHash)invalid();seen.add(t.id);return {id:saved.id,sha256:saved.fileHash,title:saved.title,artist:saved.artist??''};});
  const profile=value.estimator_profile??'reference';if(!['reference','music2emo','musicnn-dance','supervised','quality'].includes(profile))invalid();
  const answers=value.clarifications??[];
  if(!Array.isArray(answers)||answers.length>3||answers.some(a=>!a||typeof a.question!=='string'||!a.question.trim()||a.question.length>500||typeof a.answer!=='string'||!a.answer.trim()||a.answer.length>1000||Object.keys(a).some(k=>!['question','answer'].includes(k))))invalid();
  return {prompt:value.prompt,tracks:selected,estimator_profile:profile,clarifications:answers};
}
function session(req,res,config){
  const name=config.secure?'__Host-resonant_session':'resonant_session';
  const raw=String(req.headers.cookie??'').split(';').map(x=>x.trim()).find(x=>x.startsWith(name+'='))?.slice(name.length+1)??'';
  const parts=raw.split('.'),sign=value=>createHmac('sha256',config.sessionSecret).update(value).digest('base64url');
  if(parts.length===3&&/^[\w-]{43}$/.test(parts[0])&&/^\d{13}$/.test(parts[1])){
    const age=Date.now()-Number(parts[1]);if(age>=0&&age<86400000&&same(parts[2],sign(parts[0]+'.'+parts[1])))return {id:parts[0],existing:true};
  }
  const id=randomBytes(32).toString('base64url'),body=id+'.'+Date.now();
  res.setHeader('Set-Cookie',`${name}=${body}.${sign(body)}; Path=/; HttpOnly; SameSite=Strict; Max-Age=86400${config.secure?'; Secure':''}`);
  return {id,existing:false};
}

export async function createCloudServer(config,{runner,release}={}){
  release??=await loadCloudRelease(config.releaseRoot);await mkdir(config.stateRoot,{recursive:true,mode:0o700});
  const jobs=await createJobs(config,{runner});
  const server=http.createServer(async(req,res)=>{
    const send=(code,value)=>{res.writeHead(code,{'Content-Type':'application/json; charset=utf-8'});res.end(JSON.stringify(value));};
    res.setHeader('Cache-Control','private, no-store');res.setHeader('X-Content-Type-Options','nosniff');res.setHeader('Referrer-Policy','no-referrer');res.setHeader('Content-Security-Policy',CSP);res.setHeader('Permissions-Policy','camera=(), microphone=(), geolocation=()');
    if(req.headers.host!==config.host||!same(req.headers['x-resonant-proxy-token'],config.proxyToken)){send(403,{error:'Access denied.'});return;}
    try{
      const url=new URL(req.url,config.origin),pathname=decodeURIComponent(url.pathname);
      if(url.origin!==config.origin||pathname.includes('\\')||pathname.split('/').some(p=>p==='..'||p==='.'||p.startsWith('.'))){send(404,{error:'Not found.'});return;}
      if(!['GET','HEAD','POST'].includes(req.method)){res.setHeader('Allow','GET, HEAD, POST');send(405,{error:'Method not allowed.'});return;}
      if(pathname==='/healthz'&&req.method==='GET'){send(200,{status:'ready',release:release.manifest.releaseId,tracks:release.tracks.size});return;}
      const browser=session(req,res,config);
      if(req.method==='POST'&&(req.headers.origin!==config.origin||!browser.existing)){send(403,{error:'Open this app before making a request.'});return;}
      if(req.method==='GET'&&pathname==='/config.json'){send(200,{contract_version:'resonant-player/config/1',mode:'http',edition:'web',apiBase:'/api/',mediaOrigins:[]});return;}
      if(req.method==='GET'&&pathname==='/api/v1/tracks'){
        const cursor=Number(url.searchParams.get('cursor')??'0');if(!Number.isSafeInteger(cursor)||cursor<0||cursor>release.tracks.size)throw Object.assign(Error('Invalid cursor.'),{status:400});
        send(200,{contract_version:'resonant-player/library/1',revision:release.catalog.revision,tracks:release.catalog.tracks.slice(cursor,cursor+CATALOG_PAGE_SIZE),next_cursor:cursor+CATALOG_PAGE_SIZE<release.tracks.size?String(cursor+CATALOG_PAGE_SIZE):null});return;
      }
      if(req.method==='POST'&&pathname==='/api/v1/playback-sessions'){
        const input=await jsonBody(req,10000),track=release.tracks.get(input?.track_id);
        if(!track||track.sourceVersion!==input.source_version)throw Object.assign(Error('Track unavailable.'),{status:404});
        send(200,{contract_version:'resonant-player/playback-session/1',track_id:track.id,source_version:track.sourceVersion,url:`${config.origin}/api/web/audio/${track.id}`,expires_at:new Date(Date.now()+3600000).toISOString()});return;
      }
      const hash=pathname.match(/^\/api\/web\/audio\/([a-f0-9]{64})$/)?.[1];
      if(['GET','HEAD'].includes(req.method)&&hash&&release.tracks.has(hash)){await media(req,res,release.files.get(`media/${hash}.mp3`),'audio/mpeg');return;}
      if(req.method==='GET'&&pathname==='/api/web/mix'){send(200,{...release.mix,url:'/api/web/mix/audio'});return;}
      if(['GET','HEAD'].includes(req.method)&&pathname==='/api/web/mix/audio'){await media(req,res,release.files.get(release.manifest.mixAudioPath??'media/mix.m4a'),'audio/mp4');return;}
      if(req.method==='POST'&&pathname==='/api/local/playlist'){
        const payload=canonicalPlaylist(await jsonBody(req),release.tracks);send(202,await jobs.start(payload,browser.id));return;
      }
      const jobId=pathname.match(/^\/api\/local\/jobs\/([\w-]+)$/)?.[1];
      if(req.method==='GET'&&jobId){const job=jobs.get(jobId,browser.id);send(job?200:404,job??{error:'Playlist request expired. Please retry.'});return;}
      if(pathname.startsWith('/api/')||['/app-status.json','/prepare-web.html'].includes(pathname)||req.method==='POST'){send(404,{error:'Not available in this edition.'});return;}
      const relative='public/'+(pathname==='/'?'index.html':pathname.slice(1)),item=release.files.get(relative);
      if(!item||!relative.startsWith('public/')||relative==='public/catalog.json'||relative==='public/mix.json'){send(404,{error:'Not found.'});return;}
      res.writeHead(200,{'Content-Type':MIME[path.extname(relative)]??'application/octet-stream','Content-Length':item.bytes});
      if(req.method==='HEAD'){res.end();return;}try{await pipeline(createReadStream(item.file),res);}catch{res.destroy();}
    }catch(error){if(res.headersSent)res.destroy();else send(error.status??400,{error:error.status?error.message:'Request could not be completed.'});}
  });
  server.requestTimeout=30000;server.headersTimeout=15000;server.keepAliveTimeout=5000;
  let closing;
  return {server,release,close(){
    closing??=(async()=>{
      await jobs.close();
      const stopped=new Promise(resolve=>server.close(resolve));
      // Slow media clients must not keep a deployment shutdown open indefinitely.
      const deadline=setTimeout(()=>server.closeAllConnections(),1000);deadline.unref();
      try{await stopped;}finally{clearTimeout(deadline);server.closeAllConnections();}
    })();
    return closing;
  }};
}
