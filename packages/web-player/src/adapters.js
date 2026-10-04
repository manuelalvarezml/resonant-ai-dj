import {configureServerless} from './serverless.js';
import {readAudioTags,featureTags,applyAudioTags} from './audio-tags.js';
import { demoTracks, createDemoAudio } from './demo.js';
import { validateTrack,analysisQuality } from './model.js';

export class LocalLibrary {
  mode = 'local';
  async init() {
    if(this.opening)return this.opening;
    this.opening=new Promise((resolve,reject)=>{
      let settled=false;
      const finish=(error,db)=>{if(settled){db?.close();return;}settled=true;clearTimeout(timer);if(error)reject(error);else resolve(db);};
      const timer=setTimeout(()=>finish(new Error('Browser storage did not reopen. Close other player tabs and reload.')),8000);
      let request;try{request=indexedDB.open('resonant-library-v1',1);}catch(error){finish(error);return;}
      request.onupgradeneeded=()=>{request.result.createObjectStore('tracks',{keyPath:'id'});request.result.createObjectStore('audio');};
      request.onsuccess=()=>finish(null,request.result);
      request.onerror=()=>finish(request.error||new Error('Browser storage is unavailable.'));
      request.onblocked=()=>finish(new Error('Browser storage is blocked. Close other player tabs and reload.'));
    }).then(db=>{
      this.db=db;
      db.onversionchange=()=>{db.close();if(this.db===db)this.db=null;};
      db.onclose=()=>{if(this.db===db)this.db=null;};
    }).finally(()=>{this.opening=null;});
    return this.opening;
  }
  async withDatabase(operation){
    for(let attempt=0;attempt<2;attempt++){
      try{if(!this.db)await this.init();return await operation(this.db);}
      catch(error){
        const closed=error?.name==='InvalidStateError'||error?.name==='AbortError'||/connection is closing|database.*closed/i.test(error?.message??'');
        if(attempt===0&&closed){try{this.db?.close();}catch{}this.db=null;continue;}
        if(error?.code==='LIBRARY_TRACK_CHANGED')throw error;
        const failure=new Error('Browser storage is unavailable. The batch is paused; completed analysis remains cached on this computer. Reload the player to reconnect. '+(error?.message??''));
        failure.code='LIBRARY_STORAGE_UNAVAILABLE';failure.cause=error;throw failure;
      }
    }
  }
  async listTracks() {
    if (!this.db) return [...demoTracks];
    const saved = await this.read('tracks');
    for(let i=0;i<saved.length;i++){
      const track=saved[i];
      if(track.tagReadVersion!==1||!/^[a-f0-9]{64}$/.test(track.fileHash??'')){
        const file=await this.read('audio',track.id);
        const tags={...featureTags(track),...(file?await readAudioTags(file).catch(()=>({})): {})};
        saved[i]={...applyAudioTags(track,tags),tagReadVersion:1,fileHash:track.fileHash||(file?await fileHash(file):null)};
        await new Promise((resolve,reject)=>{const tx=this.db.transaction('tracks','readwrite');tx.objectStore('tracks').put(saved[i]);tx.oncomplete=resolve;tx.onerror=tx.onabort=()=>reject(new Error('Could not save track tags.'));});
      }
    }
    return [...saved.map(validateTrack), ...demoTracks];
  }
  read(store,id) {
    return this.withDatabase(db=>new Promise((resolve,reject)=>{
      const tx=db.transaction(store,'readonly');let value;
      const request=tx.objectStore(store)[id?'get':'getAll'](id);
      request.onsuccess=()=>{value=request.result;};
      request.onerror=()=>reject(request.error||new Error('Could not read browser storage.'));
      tx.oncomplete=()=>resolve(value);tx.onabort=tx.onerror=()=>reject(tx.error||new Error('Could not read browser storage.'));
    }));
  }
  async duplicateIndex() {
    const result=[];
    for(const track of await this.read('tracks')){
      const file=await this.read('audio',track.id);if(!file)continue;
      result.push({id:track.id,title:track.title,name:file.name||track.title,hash:track.fileHash||track.features?.sha256||await fileHash(file)});
    }
    return result;
  }
  async importFile(file,{replaceId=null,hash=null}={}) {
    if (!this.db) throw new Error('Browser storage is unavailable. Allow site storage, then reload.');
    if (!/\.(mp3|m4a|aac|ogg|oga|opus|wav|flac|aif|aiff)$/i.test(file.name)) throw new Error('Choose an MP3, M4A, AAC, Ogg, WAV, FLAC or AIFF audio file.');
    if (!file.size || file.size > 512*1024*1024) throw new Error('Each audio file must be between 1 byte and 512 MB.');
    const duration = await probeAudio(file);
    hash=hash||await fileHash(file);
    const previous=replaceId?await this.read('tracks',replaceId):null;
    if(replaceId&&!previous)throw new Error('The original track is no longer available.');
    const id = replaceId||crypto.randomUUID();
    let track = {id, sourceVersion:id, title:file.name.replace(/\.[^.]+$/,''), artist:'Unknown artist', album:'Local files', duration, addedAt:Date.now(), status:'ready', kind:'local', color:Math.floor(Math.random()*6), evidence:[{field:'Title',value:'Display name from selected filename; embedded tags not imported',authority:'encoded_fact',source:'browser-file/1'},{field:'Duration',value:`${duration.toFixed(3)} seconds`,authority:'deterministic_measurement',source:'HTMLMediaElement metadata'}]};
    if(previous){
      track.addedAt=previous.addedAt;track.color=previous.color;
      if(previous.features?.sha256===hash)track.features=previous.features;
      track.sourceVersion=crypto.randomUUID();
    }
    track={...applyAudioTags(track,await readAudioTags(file).catch(()=>({}))),tagReadVersion:1};
    track.fileHash=hash;
    await new Promise((resolve,reject) => {
      const tx = this.db.transaction(['tracks','audio'],'readwrite');
      tx.objectStore('tracks').put(track); tx.objectStore('audio').put(file,id);
      tx.oncomplete = resolve; tx.onabort = tx.onerror = () => reject(new Error('Could not save this file. Browser storage may be full or disabled. Free space and try again.'));
    });
    return track;
  }
  async saveFeatures(id,features) {
    const track=await this.read('tracks',id);if(!track)throw new Error('Track was removed during analysis.');
    await this.withDatabase(db=>new Promise((resolve,reject)=>{
      const tx=db.transaction('tracks','readwrite'),store=tx.objectStore('tracks'),request=store.get(id);
      // Recheck identity inside the write transaction: another tab may have converted the track.
      request.onsuccess=()=>{
        const current=request.result;
        if(!current||(current.fileHash&&features.sha256&&current.fileHash!==features.sha256)){
          const error=new Error('Track audio changed during analysis; retry the current audio.');error.code='LIBRARY_TRACK_CHANGED';reject(error);tx.abort();return;
        }
        current.features=features;Object.assign(current,applyAudioTags(current,{...featureTags(current),...current.embeddedTags}));Object.assign(track,current);store.put(current);
      };
      tx.oncomplete=resolve;tx.onerror=tx.onabort=()=>reject(tx.error||new Error('Could not save audio features.'));
    }));
    return validateTrack(track);
  }
  async replaceAudioWithMp3(id,file,expectedHash){
    if(!/\.mp3$/i.test(file.name))throw Error('Converted audio must be MP3.');
    const hash=await fileHash(file),duration=await probeAudio(file);let updated;
    await this.withDatabase(db=>new Promise((resolve,reject)=>{
      const tx=db.transaction(['tracks','audio'],'readwrite'),tracks=tx.objectStore('tracks'),audio=tx.objectStore('audio');
      const tr=tracks.get(id),ar=audio.get(id);let pending=2;
      const ready=()=>{if(--pending)return;
        const current=tr.result,original=ar.result;
        if(!current||!original||current.fileHash!==expectedHash){const e=new Error('Track changed during conversion; original audio was kept.');e.code='LIBRARY_TRACK_CHANGED';reject(e);tx.abort();return;}
        // Backup and replacement commit together; no database schema migration is needed.
        audio.put({audio:original,track:current},'conversion-backup:'+id+':'+expectedHash);
        updated={...current,fileHash:hash,sourceVersion:crypto.randomUUID(),duration,features:null,
          conversion:{originalHash:expectedHash,originalName:original.name,profile:'ffmpeg-libmp3lame-vbr2'},
          evidence:[...current.evidence,{field:'Audio conversion',value:'M4A to MP3; original browser audio backed up',authority:'executed_action',source:'ffmpeg-libmp3lame-vbr2'}]};
        audio.put(file,id);tracks.put(updated);
      };
      tr.onsuccess=ar.onsuccess=ready;
      tx.oncomplete=resolve;tx.onerror=tx.onabort=()=>reject(tx.error||new Error('Could not save conversion; original audio was kept.'));
    }));
    return validateTrack(updated);
  }
  async restoreCachedFeatures(resolve) {
    if(!this.db||typeof resolve!=='function')return 0;
    let restored=0;
    for(const saved of await this.read('tracks')){
      if(saved.kind!=='local'||(saved.features?.policy==='maest-top6-v1'&&saved.features.status==='complete'&&saved.features.feature_version==='selected-estimators-v3-character120'&&saved.features.supervised_status==='complete'&&saved.features.quality_status==='complete'))continue;
      let hash=/^[a-f0-9]{64}$/.test(saved.fileHash??'')?saved.fileHash:null;
      if(!hash){const audio=await this.read('audio',saved.id);if(audio instanceof Blob)hash=await fileHash(audio);}
      if(!hash)continue;
      let features;try{features=await resolve(hash);}catch{continue;}
      if(!features||features.sha256!==hash||analysisQuality(features)<=analysisQuality(saved.features))continue;
      const current=await this.read('tracks',saved.id);if(!current)continue;
      current.fileHash=hash;current.features=features;
      Object.assign(current,applyAudioTags(current,{...featureTags(current),...current.embeddedTags}));
      await new Promise((accept,reject)=>{const tx=this.db.transaction('tracks','readwrite');tx.objectStore('tracks').put(current);tx.oncomplete=accept;tx.onerror=tx.onabort=()=>reject(new Error('Could not restore saved audio features.'));});
      restored++;
    }
    return restored;
  }
  async removeTrack(id) {
    if (id.startsWith('demo-')) throw new Error('Demo tracks cannot be removed.');
    await new Promise((resolve,reject) => {
      const tx = this.db.transaction(['tracks','audio'],'readwrite'); tx.objectStore('tracks').delete(id); tx.objectStore('audio').delete(id);
      tx.oncomplete = resolve; tx.onerror = tx.onabort = () => reject(new Error('The track could not be removed.'));
    });
  }
  async resolvePlayback(track,{signal} = {}) {
    if (track.status !== 'ready') throw new Error('This track is not available for playback yet.');
    const blob = track.kind === 'demo' ? createDemoAudio(Number(track.id.split('-')[1])-1) : await this.read('audio',track.id);
    signal?.throwIfAborted();
    if (!(blob instanceof Blob)) throw new Error('The saved audio is missing. Remove this entry and add the original file again.');
    const url = URL.createObjectURL(blob);
    return {url, expiresAt:null, release:() => URL.revokeObjectURL(url)};
  }
}

export function probeAudio(file) {
  return new Promise((resolve,reject) => {
    const audio = document.createElement('audio'), url = URL.createObjectURL(file);
    const finish = (error) => { clearTimeout(timeout); audio.removeAttribute('src'); audio.load(); URL.revokeObjectURL(url); if(error) reject(error); };
    const timeout = setTimeout(() => finish(new Error('Audio metadata took too long to load. Try a browser-compatible MP3 or WAV.')),12000);
    audio.preload = 'metadata';
    audio.onloadedmetadata = () => {
      const duration = audio.duration;
      if (!Number.isFinite(duration) || duration <= 0) return finish(new Error('This file has no usable audio duration.'));
      audio.onloadedmetadata = audio.onerror = null; finish(); resolve(duration);
    };
    audio.onerror = () => { audio.onerror = null; finish(new Error('This browser cannot read the audio file. Try an MP3 or WAV version.')); };
    audio.src = url;
  });
}

export function validateConfig(value, locationHref = globalThis.location?.href ?? 'http://localhost/') {
  if (value?.contract_version !== 'resonant-player/config/1' || !['local','http'].includes(value.mode)) throw new Error('The player configuration is invalid.');
  const base = new URL(value.apiBase ?? '/api/', locationHref), origin = new URL(locationHref).origin;
  if (base.origin !== origin || base.username || base.password || base.search || base.hash || !base.pathname.endsWith('/')) throw new Error('The API must use a same-origin path ending in /.');
  const mediaOrigins = value.mediaOrigins ?? [];
  if (!Array.isArray(mediaOrigins) || mediaOrigins.some(s => {try {const u = new URL(s); return u.protocol !== 'https:' || u.origin !== s;} catch {return true;}})) throw new Error('Media origins must be explicit HTTPS origins.');
  if(value.serverless===true&&(value.mode!=='http'||value.edition!=='web'))throw new Error('Serverless transport requires the web edition.');
  return {edition:value.edition==='web'?'web':'local',mode:value.mode, apiBase:base.href, mediaOrigins, origin,...(value.serverless===true?{serverless:true}:{})};
}

export class HttpLibrary {
  mode = 'http';
  constructor(config, request = (...args)=>globalThis.fetch(...args)) { this.config=config; this.request=request; }
  async init() {if(this.config.serverless)this.cloud=await configureServerless(this.config,this.request);}
  async json(path,options={}) {
    const controller=new AbortController(),cancel=()=>controller.abort(options.signal.reason);
    if(options.signal?.aborted)cancel();else options.signal?.addEventListener('abort',cancel,{once:true});
    const timeout=setTimeout(()=>controller.abort(),15000);
    try {
      let response;
      try { response = await this.request(new URL(path,this.config.apiBase),{...options,signal:controller.signal, credentials:'same-origin', cache:'no-store', redirect:'error', headers:{'Content-Type':'application/json',...options.headers}}); }
      catch(error) { if (options.signal?.aborted || (error.name==='AbortError'&&!controller.signal.aborted)) throw error; throw new Error(controller.signal.aborted?'The library service took too long. Retry when your connection is ready.':'The library service cannot be reached. Check your connection and retry.'); }
      if (!response.ok) throw new Error(response.status === 401 || response.status === 403 ? 'Your session has expired or access was denied. Sign in through your hosting service, then retry.' : response.status === 404 ? 'This track is no longer available.' : response.status === 429 ? 'The service is busy. Wait a moment, then retry.' : 'The library service could not complete the request. Try again.');
      try { return await response.json(); } catch { throw new Error('The library service returned an unreadable response.'); }
    } finally {clearTimeout(timeout);options.signal?.removeEventListener('abort',cancel);}
  }
  async listTracks({signal}={}) {
    if(this.cloud)return this.cloud.listTracks({signal});
    const tracks = [], seen = new Set(), cursors = new Set(); let cursor, revision;
    for(let page=0;page<50;page++) {
      const data = await this.json(`v1/tracks?limit=100${cursor ? `&cursor=${encodeURIComponent(cursor)}` : ''}`,{signal});
      if (data.contract_version !== 'resonant-player/library/1' || !Array.isArray(data.tracks) || data.tracks.length>100 || typeof data.revision !== 'string') throw new Error('The library contract is invalid.');
      if (revision && revision !== data.revision) throw new Error('The library changed while loading. Refresh to try again.');
      revision = data.revision;
      for(const raw of data.tracks) { const t = validateTrack({...raw,kind:'cloud'}); if(seen.has(t.id)) throw new Error('The library returned duplicate track identifiers.'); seen.add(t.id); tracks.push(t); }
      if(data.next_cursor == null) return tracks;
      if(typeof data.next_cursor !== 'string' || !data.next_cursor || data.next_cursor.length>1024 || cursors.has(data.next_cursor)) throw new Error('The library returned an invalid page cursor.');
      cursor=data.next_cursor; cursors.add(cursor);
    }
    throw new Error('This library exceeds the supported 5,000-track browsing limit.');
  }
  async resolvePlayback(track,{position=0,signal}={}) {
    if(this.cloud)return this.cloud.resolvePlayback(track,{position,signal});
    const data = await this.json('v1/playback-sessions',{method:'POST',signal,body:JSON.stringify({contract_version:'resonant-player/playback-request/1',track_id:track.id,source_version:track.sourceVersion,position_seconds:position})});
    let url;
    try {url=new URL(data.url);} catch {throw new Error('The service returned an invalid playback session.');}
    const expiry=Date.parse(data.expires_at);
    if(data.contract_version !== 'resonant-player/playback-session/1' || data.track_id !== track.id || data.source_version !== track.sourceVersion || !Number.isFinite(expiry) || expiry < Date.now()+5000 || ![this.config.origin,...this.config.mediaOrigins].includes(url.origin) || url.username || url.password || url.hash || (url.protocol !== 'https:' && url.origin !== this.config.origin)) throw new Error('The service returned an invalid playback session.');
    return {url:url.href,expiresAt:expiry,release:()=>{}};
  }
}

export async function fileHash(file){return [...new Uint8Array(await crypto.subtle.digest('SHA-256',await file.arrayBuffer()))].map(b=>b.toString(16).padStart(2,'0')).join('');}
export function duplicateMatch(index,file,hash){return index.find(t=>t.hash===hash)||index.find(t=>t.name.normalize('NFC').toLocaleLowerCase()===file.name.normalize('NFC').toLocaleLowerCase());}
