import {readdir,readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import path from 'node:path';

// Only the project's established source folders are inspected. No request supplies a path.
export async function recoveryIndex(sourceDirs,cacheDir,{includeUnanalyzed=false,recursive=false}={}){
 const cached=new Set((await readdir(cacheDir).catch(error=>{if(error.code==='ENOENT')return [];throw error;})).filter(n=>/^[a-f0-9]{64}\.json$/.test(n)).map(n=>n.slice(0,-5)));
 const entries=new Map();
 const pending=[...sourceDirs];
 for(let i=0;i<pending.length;i++){
  const directory=pending[i];
  let files;try{files=await readdir(directory,{withFileTypes:true});}catch(error){if(error.code==='ENOENT')continue;throw error;}
  for(const file of files.sort((a,b)=>a.name.localeCompare(b.name))){
   if(recursive&&file.isDirectory()){pending.push(path.join(directory,file.name));continue;}
   if(!file.isFile()||! /\.(mp3|m4a|aac|ogg|oga|opus|wav|flac|aif|aiff)$/i.test(file.name))continue;
   const source=path.join(directory,file.name),bytes=await readFile(source);
   const sha256=createHash('sha256').update(bytes).digest('hex');
   if((includeUnanalyzed||cached.has(sha256))&&!entries.has(sha256))entries.set(sha256,{sha256,filename:file.name,size:bytes.length,source});
  }
 }
 return entries;
}
export async function recoveryAudio(entry){
 const bytes=await readFile(entry.source);
 if(createHash('sha256').update(bytes).digest('hex')!==entry.sha256)throw Error('The original audio changed. Reload recovery before importing it.');
 return bytes;
}
