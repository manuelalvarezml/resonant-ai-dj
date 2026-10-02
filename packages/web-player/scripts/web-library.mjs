import {mkdir,readFile,writeFile,readdir,rename} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {fullyAnalyzed} from '../src/release-policy.js';
import {recoveryIndex} from './recovery.mjs';
export const project=fileURLToPath(new URL('../../..',import.meta.url));
export const releaseDir=path.join(project,'output/web-release');
export const cacheDir=path.join(project,'packages/prompt-to-playlist/output/web-features');
export const hashBytes=bytes=>createHash('sha256').update(bytes).digest('hex');
export async function prepareWebAudio(req,res,port){
 if(!req.url.startsWith('/api/local/web-library'))return false;
 const reply=(code,data)=>{res.writeHead(code,{'Content-Type':'application/json'});res.end(JSON.stringify(data));};
 if(req.method==='GET'&&req.headers.host===`127.0.0.1:${port}`&&req.headers['x-resonant-local']==='1'&&(!req.headers.origin||req.headers.origin===`http://127.0.0.1:${port}`)){const data=await buildWebLibrary();reply(200,{availableHashes:data.manifest.tracks.map(t=>t.fileHash)});return true;}
 if(req.method!=='POST'||req.headers.host!==`127.0.0.1:${port}`||req.headers.origin!==`http://127.0.0.1:${port}`||req.headers['x-resonant-local']!=='1'){reply(403,{error:'Use the owner’s local app.'});return true;}
 try{
  const hash=new URL(req.url,'http://localhost').searchParams.get('hash');if(!/^[a-f0-9]{64}$/.test(hash??''))throw Error('Invalid hash');
  const features=JSON.parse(await readFile(path.join(cacheDir,hash+'.json'),'utf8'));if(!fullyAnalyzed(features))throw Error('Only fully analyzed MP3 audio can enter this edition.');
  let size=0;const parts=[];for await(const b of req){size+=b.length;if(size>512*1024*1024)throw Error('Audio too large');parts.push(b);}
  const bytes=Buffer.concat(parts);if(hashBytes(bytes)!==hash)throw Error('Audio hash mismatch');
  await mkdir(path.join(releaseDir,'audio'),{recursive:true});const dest=path.join(releaseDir,'audio',hash+'.mp3');await writeFile(dest+'.tmp',bytes);await rename(dest+'.tmp',dest);reply(200,{saved:true});
 }catch(e){reply(400,{error:e.message});}return true;
}
// Public values exclude process metrics, file paths, and stored embedding arrays.
export function publicFeatures(f){return JSON.parse(JSON.stringify(f,(key,value)=>['metrics','embedding','embeddings','implementation','implementation_version'].includes(key)?undefined:typeof value==='string'&&(/\/Users\/|\/private\/|\/var\/folders\//.test(value))?undefined:value));}
export async function buildWebLibrary(){
 await mkdir(path.join(releaseDir,'audio'),{recursive:true});
 const index=await recoveryIndex([path.join(project,'test_music'),path.join(releaseDir,'audio')],cacheDir,{recursive:true});
 const tracks=[],sources={},excluded={incomplete:0,notMp3:0};
 for(const [hash,entry] of index){
  const f=JSON.parse(await readFile(path.join(cacheDir,hash+'.json'),'utf8'));
  if(!fullyAnalyzed(f)){excluded.incomplete++;continue;}
  if(!/\.mp3$/i.test(entry.filename)){excluded.notMp3++;continue;}
  const tags=f.algorithms.find(a=>a.algorithm_id==='metadata').values.encoded_tags??{};
  const get=k=>Object.entries(tags).find(([key])=>key.toLowerCase()===k)?.[1]??'';
  tracks.push({id:hash,fileHash:hash,sourceVersion:hash,title:get('title')||entry.filename.replace(/\.mp3$/i,''),artist:get('artist'),album:get('album'),duration:f.duration_s,status:'ready',kind:'cloud',addedAt:0,color:tracks.length%6,evidence:[],features:publicFeatures(f)});sources[hash]=entry.source;
 }
 tracks.sort((a,b)=>a.title.localeCompare(b.title));
 const revision=hashBytes(Buffer.from(JSON.stringify(tracks)));
 const manifest={revision,tracks};await writeFile(path.join(releaseDir,'catalog.json'),JSON.stringify(manifest));await writeFile(path.join(releaseDir,'sources.json'),JSON.stringify(sources));
 return {manifest,sources,excluded};
}
