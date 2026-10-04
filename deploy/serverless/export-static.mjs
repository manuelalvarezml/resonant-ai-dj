#!/usr/bin/env node
// Derive immutable CDN assets/API membership without changing or copying source audio.
import {readFile,writeFile,mkdir,readdir,lstat,copyFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {verifyRelease} from '../../packages/web-player/scripts/export-release.mjs';
const root=fileURLToPath(new URL('../..',import.meta.url));
const sha=b=>createHash('sha256').update(b).digest('hex');
async function files(dir,prefix=''){const found=[];for(const row of await readdir(path.join(dir,prefix),{withFileTypes:true})){const name=path.join(prefix,row.name);if(row.isSymbolicLink())throw Error('Symlink in static source');if(row.isDirectory())found.push(...await files(dir,name));else if(row.isFile())found.push(name);else throw Error('Unexpected source type');}return found.sort();}
export async function exportStatic({release,output,stateBucket}){
 release=path.resolve(release);output=path.resolve(output);
 if(!output.startsWith(path.join(root,'output')+path.sep)||!/^resonant-[a-z0-9-]{3,50}$/.test(stateBucket))throw Error('Use a new output subdirectory and an explicit Resonant state bucket.');
 try{await lstat(output);throw Error('Output already exists; choose a new candidate name.');}catch(e){if(e.code!=='ENOENT')throw e;}
 const manifest=await verifyRelease(release,{requirePlanner:true});
 const catalog=JSON.parse(await readFile(path.join(release,'public/catalog.json'),'utf8'));
 const source=new Map(),web=path.join(root,'packages/web-player');
 for(const base of ['public','src'])for(const file of await files(path.join(web,base))){
  if(base==='public'&&['config.json','prepare-web.html','app-status.json','app-status.md'].includes(file))continue;
  source.set(base==='src'?'src/'+file:file,await readFile(path.join(web,base,file)));
 }
 source.set('config.json',Buffer.from(JSON.stringify({contract_version:'resonant-player/config/1',mode:'http',edition:'web',apiBase:'/api/',mediaOrigins:[],serverless:true})));
 const appId=sha(JSON.stringify([...source].map(([k,v])=>[k,sha(v)]).sort())),prefix='app/releases/'+appId;
 await mkdir(output,{recursive:true,mode:0o700});const uploads=[];
 async function put(key,bytes,cache='public,max-age=31536000,immutable'){
  const target=path.join(output,'static',key);await mkdir(path.dirname(target),{recursive:true});await writeFile(target,bytes,{flag:'wx'});
  uploads.push({key,localPath:target,bytes:Buffer.byteLength(bytes),sha256:sha(bytes),cacheControl:cache});
 }
 for(const [key,bytes]of source)await put(prefix+'/'+key,bytes);
 const html=source.get('index.html').toString().replaceAll('href="./','href="/'+prefix+'/').replaceAll('src="./','src="/'+prefix+'/');
 await put('index.html',html,'no-cache,max-age=0,must-revalidate');
 for(const file of await files(path.join(root,'deploy/serverless/login')))await put('login/'+file,await readFile(path.join(root,'deploy/serverless/login',file)),'public,max-age=300');
 const pages=[];
 for(let i=0;i<catalog.tracks.length;i+=25){const key='library/releases/'+manifest.releaseId+'/page-'+Math.floor(i/25)+'.json';pages.push('/'+key);await put(key,JSON.stringify({releaseId:manifest.releaseId,tracks:catalog.tracks.slice(i,i+25)}));}
 const mix=JSON.parse(await readFile(path.join(release,manifest.mixPath),'utf8')),mixFile=manifest.files.find(f=>f.path===manifest.mixAudioPath),mixKey='media/mix-'+mixFile.sha256+'.m4a';mix.url='/'+mixKey;
 await put('library/releases/'+manifest.releaseId+'/mix.json',JSON.stringify(mix));
 await put('library/current.json',JSON.stringify({contract_version:'resonant-player/static-library/1',releaseId:manifest.releaseId,appId,trackCount:manifest.trackCount,pages,resultOrigin:'https://'+stateBucket+'.s3.us-east-2.amazonaws.com'}),'no-cache,max-age=0,must-revalidate');
 for(const file of manifest.files.filter(f=>f.path.startsWith('media/')))uploads.push({key:file.path===manifest.mixAudioPath?mixKey:file.path,localPath:path.join(release,file.path),bytes:file.bytes,sha256:file.sha256,cacheControl:'public,max-age=31536000,immutable'});
 await mkdir(path.join(output,'api'));for(const file of ['aws.mjs','core.mjs','profile.mjs','package.json','package-lock.json'])await copyFile(path.join(root,'deploy/serverless/api',file),path.join(output,'api',file));
 await copyFile(path.join(web,'src/profile-model.js'),path.join(output,'api/profile-model.js'));
 const profileSource=await readFile(path.join(output,'api/profile.mjs'),'utf8');await writeFile(path.join(output,'api/profile.mjs'),profileSource.replace('../../../packages/web-player/src/profile-model.js','./profile-model.js'));
 await writeFile(path.join(output,'api/membership.json'),JSON.stringify({releaseId:manifest.releaseId,tracks:catalog.tracks.map(t=>({id:t.id,sha256:t.fileHash}))}));
 const plan={schema:'resonant-serverless-assets/1',releaseId:manifest.releaseId,appId,stateBucket,trackCount:manifest.trackCount,uploads};
 await writeFile(path.join(output,'upload-plan.json'),JSON.stringify(plan,null,2),{mode:0o600});
 return{releaseId:manifest.releaseId,appId,trackCount:manifest.trackCount,pages:pages.length,files:uploads.length,output};
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
 const args=process.argv.slice(2);const get=k=>args[args.indexOf(k)+1];
 if(!['--release','--output','--state-bucket'].every(k=>args.includes(k)))throw Error('Required: --release PATH --output NEW-PATH --state-bucket NAME');
 console.log(JSON.stringify(await exportStatic({release:get('--release'),output:get('--output'),stateBucket:get('--state-bucket')})));
}
