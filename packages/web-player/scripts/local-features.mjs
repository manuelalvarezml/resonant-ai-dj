import {isConverting} from './conversion.mjs';
import {mkdtemp,writeFile,readFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {spawn} from 'node:child_process';
import {randomUUID} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {recoveryIndex,recoveryAudio} from './recovery.mjs';
const pkg=fileURLToPath(new URL('../../prompt-to-playlist/',import.meta.url));
const project=path.resolve(pkg,'../..');
const recoverySources=[path.join(project,'test_music')];
let recoveredSources;
const jobs=new Map();let running=false;
export const isAnalysisRunning=()=>running;
const send=(res,status,data)=>{res.writeHead(status,{'Content-Type':'application/json'});res.end(JSON.stringify(data));};
async function body(req,limit){const chunks=[];let size=0;for await(const chunk of req){size+=chunk.length;if(size>limit)throw Error('Request too large');chunks.push(chunk)}return Buffer.concat(chunks)}
export function allowedLocalRequest(req,port){return [`127.0.0.1:${port}`,`localhost:${port}`].includes(req.headers.host)&&req.headers.origin===`http://${req.headers.host}`&&req.headers['x-resonant-local']==='1';}
export function validCachedFeatures(value,hash){return Boolean(value&&value.sha256===hash&&value.policy==='maest-top6-v1'&&['complete','partial'].includes(value.status)&&Array.isArray(value.algorithms)&&Array.isArray(value.genres)&&value.genres.length<=6);}
export async function localFeatures(req,res,port,{playlistTracks=null}={}){
 const url=new URL(req.url,'http://localhost');if(!url.pathname.startsWith('/api/local/'))return false;
 if(![`127.0.0.1:${port}`,`localhost:${port}`].includes(req.headers.host)){send(res,403,{error:'Invalid host'});return true;}
 if(req.method==='GET'&&url.pathname.startsWith('/api/local/recovery')){
  if(req.headers['x-resonant-local']!=='1'||(req.headers.origin&&req.headers.origin!==`http://${req.headers.host}`)){send(res,403,{error:'Use the local player to restore your analyzed files.'});return true;}
  try{
   if(url.pathname==='/api/local/recovery'){
    recoveredSources=await recoveryIndex(recoverySources,path.join(pkg,'output','web-features'),{includeUnanalyzed:true,recursive:true});
    const tracks=[];
    for(const [hash,entry] of recoveredSources){
     let hasAnalysis=false;
     try{const features=JSON.parse(await readFile(path.join(pkg,'output','web-features',hash+'.json'),'utf8'));hasAnalysis=validCachedFeatures(features,hash);}catch{}
     const {source,...publicEntry}=entry;tracks.push({...publicEntry,hasAnalysis});
    }
    send(res,200,{tracks});
   }else{
    const hash=url.pathname.match(/^\/api\/local\/recovery\/audio\/([a-f0-9]{64})$/)?.[1];
    const entry=hash&&recoveredSources?.get(hash);
    if(!entry){send(res,404,{error:'Recovered audio not found. Start recovery again.'});return true;}
    const bytes=await recoveryAudio(entry);res.writeHead(200,{'Content-Type':'application/octet-stream','Content-Length':bytes.length});res.end(bytes);
   }
  }catch{send(res,409,{error:'Could not read the original audio and saved analysis. Reload and try recovery again.'});}
  return true;
 }
 const featureHash=url.pathname.match(/^\/api\/local\/features\/([a-f0-9]{64})$/)?.[1];
 if(req.method==='GET'&&featureHash){
  if(req.headers['x-resonant-local']!=='1'){send(res,403,{error:'Use the local player to restore analysis.'});return true;}
  try{const value=JSON.parse(await readFile(path.join(pkg,'output','web-features',featureHash+'.json'),'utf8'));if(!validCachedFeatures(value,featureHash))throw Error('Invalid cache');send(res,200,{result:value});}
  catch{send(res,404,{error:'No saved analysis exists for this audio hash.'});}
  return true;
 }
 if(req.method==='GET'&&url.pathname.startsWith('/api/local/jobs/')){const j=jobs.get(url.pathname.split('/').pop());send(res,j?200:404,j??{error:'Job expired. Retry analysis.'});return true;}
 if(req.method!=='POST'||!allowedLocalRequest(req,port)){send(res,403,{error:'Use the local player to start this operation.'});return true;}
 if(!['/api/local/analyze','/api/local/playlist'].includes(url.pathname)){send(res,404,{error:'Unknown operation'});return true;}
 if(running||isConverting()){send(res,409,{error:'Another analysis or playlist request is running. Wait for it to finish.'});return true;}
 running=true;let dir;
 try{
 dir=await mkdtemp(path.join(tmpdir(),'resonant-web-'));const action=url.pathname.endsWith('/analyze')?'analyze':'prompt';
 const ext=path.extname(url.searchParams.get('filename')??'').toLowerCase();
 if(action==='analyze'&&!['.mp3','.m4a','.aac','.ogg','.oga','.opus','.wav','.flac','.aif','.aiff'].includes(ext))throw Error('Unsupported audio type');
 const input=path.join(dir,action==='analyze'?'track'+ext:'request.json'),out=path.join(dir,'result.json');
 let bytes=await body(req,action==='analyze'?512*1024*1024:1024*1024);if(!bytes.length)throw Error('Empty request');
 if(action==='prompt'){const payload=validatePlaylistRequest(JSON.parse(bytes));if(playlistTracks){const allowed=new Map(playlistTracks.map(t=>[t.id,t]));payload.tracks=payload.tracks.map(t=>{const saved=allowed.get(t.id);if(!saved||saved.fileHash!==t.sha256)throw Error('Track is outside the published library');return {id:saved.id,sha256:saved.fileHash,title:saved.title,artist:saved.artist};});bytes=Buffer.from(JSON.stringify(payload));}}
 const specialists=url.searchParams.get('specialists');
 if(specialists!==null&&(action!=='analyze'||specialists!=='1'))throw Error('Invalid specialist analysis mode');
 const supervised=url.searchParams.get('supervised');
 if(supervised!==null&&(action!=='analyze'||supervised!=='1'))throw Error('Invalid estimator analysis mode');
 await writeFile(input,bytes);const id=randomUUID(),job={id,status:'running',message:action==='analyze'?'Analyzing audio features…':'Interpreting your playlist request…'};jobs.set(id,job);
 const child=spawn(path.join(pkg,'.venv/bin/python'),['-m','prompt_to_playlist.web_bridge',action,'--input',input,'--out',out,...(supervised==='1'?['--supervised']:[]),...(specialists==='1'?['--specialists']:[])],{cwd:pkg,stdio:['ignore','pipe','pipe'],env:{...process.env,PYTHONUNBUFFERED:'1'}});
 child.stdout.on('data',b=>{job.message=b.toString().trim().slice(-700)});child.stderr.on('data',()=>{});
 let finished=false;const finish=async(error)=>{if(finished)return;finished=true;clearTimeout(timeout);try{const payload=JSON.parse(await readFile(out,'utf8'));Object.assign(job,payload,{status:payload.error?'failed':'complete'});}catch{job.status='failed';job.error=error||'Local worker stopped before completing. Check the Python analysis environment.';}finally{running=false;await rm(dir,{recursive:true,force:true});setTimeout(()=>jobs.delete(id),3600000).unref();}};
 const timeout=setTimeout(()=>{child.kill('SIGTERM');void finish('Operation timed out.');},4*3600000);timeout.unref();child.on('error',()=>void finish('Python environment is unavailable.'));child.on('close',()=>void finish());send(res,202,{id});
 }catch(error){running=false;if(dir)await rm(dir,{recursive:true,force:true});send(res,400,{error:error.message});}
 return true;
}

export function validatePlaylistRequest(value){
 const fail=()=>{throw Error('Invalid playlist request');};
 if(!value||Object.keys(value).some(k=>!['prompt','tracks','clarifications','estimator_profile'].includes(k))||typeof value.prompt!=='string'||!value.prompt.trim()||value.prompt.length>4000||!Array.isArray(value.tracks)||!value.tracks.length||value.tracks.length>5000)fail();
 if(value.tracks.some(t=>!t||typeof t.id!=='string'||!/^[-\w]{1,128}$/.test(t.id)||typeof t.sha256!=='string'||!/^[a-f0-9]{64}$/.test(t.sha256)||typeof t.title!=='string'||!t.title.trim()||t.title.length>500||typeof t.artist!=='string'||t.artist.length>500||Object.keys(t).some(k=>!['id','sha256','title','artist'].includes(k)))||new Set(value.tracks.map(t=>t.id)).size!==value.tracks.length)fail();
 if(value.estimator_profile!==undefined&&!['reference','music2emo','musicnn-dance','supervised','quality'].includes(value.estimator_profile))fail();
 const answers=value.clarifications??[];
 if(!Array.isArray(answers)||answers.length>3||answers.some(a=>!a||Object.keys(a).some(k=>!['question','answer'].includes(k))||typeof a.question!=='string'||!a.question.trim()||a.question.length>500||typeof a.answer!=='string'||!a.answer.trim()||a.answer.length>1000))fail();
 return value;
}
