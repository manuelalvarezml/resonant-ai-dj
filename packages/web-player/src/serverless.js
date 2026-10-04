import {validateTrack} from './model.js';
let active=null;
export const serverlessTransport=()=>active;
export async function configureServerless(config,request=globalThis.fetch.bind(globalThis)){
 const transport=new ServerlessTransport(config,request);await transport.init();active=transport;return transport;
}
export class ServerlessTransport{
 constructor(config,request){this.config=config;this.request=request;this.csrf=null;this.expiresAt=0;this.tracks=new Map();this.pending=new Map();try{this.pending=new Map(JSON.parse(globalThis.sessionStorage?.getItem('resonant:pending-cloud-jobs')??'[]'));}catch{}}
 async fetchJSON(path,options={}){
  const url=new URL(path,this.config.origin);if(url.origin!==this.config.origin||url.username||url.password)throw Error('Invalid library address.');
  const response=await this.request(url,{credentials:'same-origin',cache:'no-store',redirect:'error',...options,signal:options.signal??AbortSignal.timeout(15000)});
  let data;try{data=await response.json();}catch{throw Error('The service response could not be read.');}
  if(!response.ok)throw Object.assign(Error(data.error||(response.status===403||response.status===401?'Your access has expired. Open the sign-in page to continue.':'The service is temporarily unavailable.')),{status:response.status});
  return data;
 }
 async session(){const session=await this.fetchJSON('/api/session');this.csrf=session.csrf;this.expiresAt=session.expiresAt;return session;}
 async refresh(){if(!this.csrf)await this.session();const s=await this.fetchJSON('/api/session/refresh',{method:'POST',headers:{'Content-Type':'application/json','X-Resonant-CSRF':this.csrf},body:'{}'});this.csrf=s.csrf;this.expiresAt=s.expiresAt;}
 async init(){
  this.manifest=await this.fetchJSON('/library/current.json');const m=this.manifest;
  if(m.contract_version!=='resonant-player/static-library/1'||!/^[a-f0-9]{64}$/.test(m.releaseId)||!Array.isArray(m.pages)||!m.pages.length||m.pages.length>200||!Number.isInteger(m.trackCount)||m.trackCount<1||m.trackCount>5000||m.pages.some(p=>!new RegExp('^/library/releases/'+m.releaseId+'/page-[0-9]+\\.json$').test(p)))throw Error('Invalid published library.');
  // Authentication is enforced by CloudFront. An API outage must not prevent
  // loading already-authorized static media/catalogs.
  void this.session().catch(()=>{});
  if(typeof window!=='undefined'){
   this.timer=setInterval(()=>{if(this.expiresAt&&this.expiresAt-Date.now()<300000&&!document.hidden)void this.refresh().catch(()=>{});},60000);
   window.addEventListener('pagehide',()=>clearInterval(this.timer),{once:true});
  }
 }
 async listTracks({signal}={}){
  const tracks=[],seen=new Set();
  for(const path of this.manifest.pages){
   const page=await this.fetchJSON(path,{signal});
   if(page.releaseId!==this.manifest.releaseId||!Array.isArray(page.tracks)||page.tracks.length>25)throw Error('The library changed. Refresh to try again.');
   for(const raw of page.tracks){const t=validateTrack({...raw,kind:'cloud'});if(seen.has(t.id)||!/^[a-f0-9]{64}$/.test(raw.fileHash))throw Error('Invalid library track.');seen.add(t.id);this.tracks.set(t.id,{...t,fileHash:raw.fileHash});tracks.push(t);}
  }
  if(tracks.length!==this.manifest.trackCount)throw Error('The library is incomplete. Refresh to try again.');
  return tracks;
 }
 async resolvePlayback(track){
  const row=this.tracks.get(track.id);if(!row||row.sourceVersion!==track.sourceVersion)throw Error('Track is not in the published library.');
  if(this.expiresAt&&this.expiresAt<Date.now()+10000)await this.refresh();
  return{url:new URL('/media/'+row.fileHash+'.mp3',this.config.origin).href,expiresAt:this.expiresAt||Date.now()+900000,release:()=>{}};
 }
 async mix(){return this.fetchJSON('/library/releases/'+this.manifest.releaseId+'/mix.json');}
 async playlist(body,onProgress=()=>{}){
  await this.session();if(this.expiresAt<Date.now()+60000)await this.refresh();
  const raw=new TextEncoder().encode(JSON.stringify({...body,releaseId:this.manifest.releaseId}));
  const fingerprint=[...new Uint8Array(await crypto.subtle.digest('SHA-256',raw))].map(b=>b.toString(16).padStart(2,'0')).join('');
  const saved=this.pending.get(fingerprint),idempotencyKey=saved?.until>Date.now()?saved.key:crypto.randomUUID();
  this.pending.set(fingerprint,{key:idempotencyKey,until:Date.now()+86400000});
  const persist=()=>{for(const [key,row]of this.pending)if(row.until<=Date.now())this.pending.delete(key);while(this.pending.size>10)this.pending.delete(this.pending.keys().next().value);try{globalThis.sessionStorage?.setItem('resonant:pending-cloud-jobs',JSON.stringify([...this.pending]));}catch{}};
  const clear=()=>{this.pending.delete(fingerprint);persist();};persist();
  const payload={...body,releaseId:this.manifest.releaseId,idempotencyKey};
  // A network retry within this submission must retain its key. Never restart
  // a completed/ambiguous paid attempt with a new key automatically.
  const submit=()=>this.fetchJSON('/api/playlist',{method:'POST',headers:{'Content-Type':'application/json','X-Resonant-CSRF':this.csrf},body:JSON.stringify(payload)});
  let job;try{job=await submit();}catch(error){if(error.name==='TypeError'||error.name==='TimeoutError')job=await submit();else throw error;}
  const deadline=Date.now()+1050000;let polls=0;
  while(Date.now()<deadline){
   if(typeof document!=='undefined'&&document.hidden){await new Promise(r=>setTimeout(r,5000));continue;}
   const state=await this.fetchJSON('/api/jobs/'+encodeURIComponent(job.id));
   if(state.status==='failed'){clear();throw Error(state.error||'Playlist preparation failed.');}
   if(state.status==='complete'){
    const url=new URL(state.resultUrl);if(url.protocol!=='https:'||url.username||url.password||url.origin!==this.manifest.resultOrigin)throw Error('Invalid playlist result address.');
    const r=await this.request(url,{credentials:'omit',redirect:'error',cache:'no-store',signal:AbortSignal.timeout(15000)});if(!r.ok)throw Error('The result download expired. Reload the request status.');
    const bytes=await r.arrayBuffer();if(bytes.byteLength>32*1024*1024)throw Error('Playlist result is too large.');
    const digest=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(b=>b.toString(16).padStart(2,'0')).join('');
    if(digest!==state.resultSha256)throw Error('Playlist result integrity check failed.');
    const result=JSON.parse(new TextDecoder().decode(bytes));clear();return result;
   }
   onProgress(state.message||'Preparing your playlist…');polls++;
   await new Promise(r=>setTimeout(r,(polls<5?2000:5000)+Math.random()*250));
  }
  throw Error('This request took too long. Check again before starting another request.');
 }
}
