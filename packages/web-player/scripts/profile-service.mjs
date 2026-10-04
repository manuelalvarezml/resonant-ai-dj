import {createHash} from 'node:crypto';
import {readFile,mkdir,writeFile,rename} from 'node:fs/promises';
import path from 'node:path';
import {validateProfileOperation,profileTargets,mutateProfileItem} from '../src/profile-model.js';
export function fileProfileStore(file,members){
 let chain=Promise.resolve();
 const load=async()=>{try{return JSON.parse(await readFile(file,'utf8'));}catch(e){if(e.code==='ENOENT')return {items:{},applied:{}};throw e;}};
 return {
  async list(kind='state',cursor=''){await chain;const state=await load(),all=Object.values(state.items).filter(r=>r.key.startsWith(kind+'#')).sort((a,b)=>kind==='prompt'?b.key.localeCompare(a.key):a.key.localeCompare(b.key));const offset=cursor?all.findIndex(r=>r.key===cursor)+1:0;const items=all.slice(offset,offset+100);return{items,cursor:offset+items.length<all.length?items.at(-1).key:null};},
  apply(operations){const work=chain.then(async()=>{operations.forEach(op=>validateProfileOperation(op,members));const state=await load();for(const op of operations){const digest=createHash('sha256').update(JSON.stringify(op)).digest('hex');if(state.applied[op.id]){if(state.applied[op.id]!==digest&&state.applied[op.id]!==true)throw Object.assign(Error('This save ID was already used.'),{status:409});continue;}for(const key of profileTargets(op))state.items[key]=mutateProfileItem(state.items[key],op,key);state.applied[op.id]=digest;}await mkdir(path.dirname(file),{recursive:true,mode:0o700});const temp=file+'.tmp';await writeFile(temp,JSON.stringify(state),{mode:0o600});await rename(temp,file);return{saved:operations.map(op=>op.id)};});chain=work.catch(()=>{});return work;}
 };
}
export function profileService(store){return async(req,res)=>{
 const u=new URL(req.url,'http://localhost');if(u.pathname!=='/api/profile')return false;
 const send=(status,data)=>{res.writeHead(status,{'Content-Type':'application/json','Cache-Control':'no-store'});res.end(JSON.stringify(data));};
 try{
  if(req.method==='GET'){const kind=u.searchParams.get('kind')??'state';if(!['state','prompt'].includes(kind))throw Error('Invalid history view.');send(200,await store.list(kind,u.searchParams.get('cursor')??''));return true;}
  if(req.method!=='POST'){send(405,{error:'Method not allowed.'});return true;}
  if(req.headers.origin!==`http://${req.headers.host}`){send(403,{error:'Use this app to save changes.'});return true;}
  let text='';for await(const chunk of req){text+=chunk;if(Buffer.byteLength(text)>65536)throw Error('Save request too large.');}
  const body=JSON.parse(text);if(!Array.isArray(body.operations)||!body.operations.length||body.operations.length>20)throw Error('Invalid save batch.');
  send(200,await store.apply(body.operations));
 }catch(e){send(e.status??400,{error:e.message});}return true;
};}
