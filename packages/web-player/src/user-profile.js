import {profileTargets,mutateProfileItem,preferencesFromItems} from './profile-model.js';
import {serverlessTransport} from './serverless.js';
const opPrefix='resonant:owner:pending:',cacheKey='resonant:owner:cache',migrationKey='resonant:owner:imported-v1';
const clone=x=>JSON.parse(JSON.stringify(x));
export class UserProfile{
 constructor({storage=globalThis.localStorage,request=globalThis.fetch.bind(globalThis),onChange=()=>{},onError=()=>{},preferences={favorites:[],playlists:[]},importLegacy=true}={}){
  Object.assign(this,{storage,request,onChange,onError,importLegacy});this.previous=clone(preferences);this.items=[];this.syncing=null;this.timer=null;try{this.items=JSON.parse(storage.getItem(cacheKey)??'[]');this.lastAt=Math.max(0,...this.pending().map(op=>op.at));}catch{}
 }
 pending(){const rows=[];for(let i=0;i<this.storage.length;i++){const key=this.storage.key(i);if(key?.startsWith(opPrefix)){const value=this.storage.getItem(key);if(value)rows.push(JSON.parse(value));}}return rows.sort((a,b)=>a.at-b.at||a.id.localeCompare(b.id));}
 projected(){const rows=new Map(this.items.map(r=>[r.key,r]));for(const op of this.pending())for(const key of profileTargets(op))if(key.startsWith('state#'))rows.set(key,mutateProfileItem(rows.get(key),op,key));return [...rows.values()];}
 preferences(device){return preferencesFromItems(this.projected(),device);}
 enqueue(value){const op={...value,id:crypto.randomUUID(),at:this.lastAt=Math.max(Date.now(),(this.lastAt??0)+1)};try{this.storage.setItem(opPrefix+op.id,JSON.stringify(op));}catch{throw Error('This device cannot save more changes. Free browser storage before continuing.');}clearTimeout(this.timer);this.timer=setTimeout(()=>void this.sync(),1200);return op;}
 savePreferences(next){
  const prev=this.previous;
  for(const id of new Set([...prev.favorites,...next.favorites]))if(prev.favorites.includes(id)!==next.favorites.includes(id))this.enqueue({type:'favorite',trackId:id,value:next.favorites.includes(id)});
  const before=new Map(prev.playlists.map(p=>[p.id,p])),after=new Map(next.playlists.map(p=>[p.id,p]));
  for(const p of next.playlists){const old=before.get(p.id),base={type:'playlist',playlistId:p.id};if(!old){this.enqueue({...base,action:'create',name:p.name,trackIds:p.trackIds,requestId:p.requestId??null});continue;}
   if(old.name!==p.name)this.enqueue({...base,action:'rename',name:p.name});
   const added=p.trackIds.filter(id=>!old.trackIds.includes(id)),removed=old.trackIds.filter(id=>!p.trackIds.includes(id));
   if(added.length)this.enqueue({...base,action:'add',trackIds:added});if(removed.length)this.enqueue({...base,action:'remove',trackIds:removed});
   if(JSON.stringify(p.trackIds)!==JSON.stringify([...old.trackIds.filter(id=>!removed.includes(id)),...added]))this.enqueue({...base,action:'order',trackIds:p.trackIds});
  }
  for(const id of before.keys())if(!after.has(id))this.enqueue({type:'playlist',playlistId:id,action:'delete'});
  this.previous=clone(next);
 }
 async api(query='',operations){
  const cloud=serverlessTransport();if(cloud){if(operations&&!cloud.csrf)await cloud.session();const send=()=>cloud.fetchJSON('/api/profile'+query,operations?{method:'POST',headers:{'Content-Type':'application/json','X-Resonant-CSRF':cloud.csrf},body:JSON.stringify({operations})}:{});try{return await send();}catch(error){if(error.status!==403)throw error;await cloud.session();return send();}}
  const response=await this.request('/api/profile'+query,{credentials:'same-origin',cache:'no-store',signal:AbortSignal.timeout(15000),...(operations?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({operations})}:{})});const data=await response.json();if(!response.ok)throw Error(data.error??'Your saves could not sync.');return data;
 }
 async init(){
  if(this.importLegacy&&!this.storage.getItem(migrationKey)){
   for(const id of this.previous.favorites)this.enqueue({type:'favorite',trackId:id,value:true});
   for(const p of this.previous.playlists)this.enqueue({type:'playlist',playlistId:p.id,action:'create',name:p.name,trackIds:p.trackIds,requestId:p.requestId??null});
   let old;try{old=JSON.parse(this.storage.getItem('resonant:playlist-review-v1')??'null');}catch{}
   for(const row of old?.attempts??[]){if(!row.prompt)continue;this.enqueue({type:'prompt',requestId:row.id,requestAt:Date.parse(row.at)||Date.now(),prompt:row.prompt,status:row.error?'failed':row.run?.status==='needs_clarification'?'needs_clarification':'complete',trackIds:(row.run?.result?.matches??[]).map(m=>m.track.track_id),elapsedMs:row.elapsedMs??0,error:row.error??null,estimatorProfile:row.estimatorProfile??'quality'});}
   this.storage.setItem(migrationKey,'yes');
  }
  if(typeof window!=='undefined'){
   window.addEventListener('online',()=>void this.sync());
   document.addEventListener('visibilitychange',()=>{if(!document.hidden)void this.sync();});
   window.addEventListener('storage',event=>{if(event.key?.startsWith(opPrefix)) {clearTimeout(this.timer);this.timer=setTimeout(()=>void this.sync(),1500);}});
  }
  await this.sync();
 }
 async sync(){
  if(this.syncing)return this.syncing;
  let success=false;this.syncing=(async()=>{try{
   for(let pass=0;pass<100;pass++){const pending=this.pending();if(!pending.length)break;const batch=[];for(const op of pending.slice(0,20)){if(new TextEncoder().encode(JSON.stringify({operations:[...batch,op]})).length>60000)break;batch.push(op);}if(!batch.length)throw Error('A saved change is too large to sync.');const result=await this.api('',batch);for(const id of result.saved??[])this.storage.removeItem(opPrefix+id);}
   let cursor='',items=[];do{const page=await this.api('?kind=state'+(cursor?'&cursor='+encodeURIComponent(cursor):''));items.push(...page.items);cursor=page.cursor;}while(cursor);
   this.items=items;this.storage.setItem(cacheKey,JSON.stringify(items));this.previous=clone(this.preferences(this.previous));this.onChange(clone(this.previous));success=true;this.failures=0;
  }catch(error){this.onError('Changes are kept on this device; sync is pending. '+error.message);}finally{this.syncing=null;if(this.pending().length){clearTimeout(this.timer);const delay=success?1200:Math.min(300000,15000*2**Math.min(this.failures=(this.failures??0)+1,5));this.timer=setTimeout(()=>void this.sync(),delay);}}})();return this.syncing;
 }
 async prompts(cursor=''){return this.api('?kind=prompt'+(cursor?'&cursor='+encodeURIComponent(cursor):''));}
 recordPrompt(row){this.enqueue({type:'prompt',...row});}
}
