import { demoTracks, createDemoAudio } from './demo.js';
import { validateTrack } from './model.js';

export class LocalLibrary {
  mode = 'local';
  async init() {
    this.db = await new Promise((resolve,reject) => {
      const request = indexedDB.open('resonant-library-v1',1);
      request.onupgradeneeded = () => { request.result.createObjectStore('tracks',{keyPath:'id'}); request.result.createObjectStore('audio'); };
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(new Error('Browser storage is unavailable. Allow site storage and reload to save your music.'));
      request.onblocked = () => reject(new Error('Close other Resonant tabs, then reload to open your library.'));
    });
    this.db.onversionchange = () => this.db.close();
  }
  async listTracks() {
    if (!this.db) return [...demoTracks];
    const saved = await this.read('tracks');
    return [...saved.map(validateTrack), ...demoTracks];
  }
  read(store,id) {
    return new Promise((resolve,reject) => {
      const request = this.db.transaction(store,'readonly').objectStore(store)[id ? 'get' : 'getAll'](id);
      request.onsuccess = () => resolve(request.result); request.onerror = () => reject(new Error('Could not read browser storage.'));
    });
  }
  async importFile(file) {
    if (!this.db) throw new Error('Browser storage is unavailable. Allow site storage, then reload.');
    if (!/\.(mp3|m4a|aac|ogg|oga|opus|wav|flac|aif|aiff)$/i.test(file.name)) throw new Error('Choose an MP3, M4A, AAC, Ogg, WAV, FLAC or AIFF audio file.');
    if (!file.size || file.size > 512*1024*1024) throw new Error('Each audio file must be between 1 byte and 512 MB.');
    const duration = await probeAudio(file);
    const id = crypto.randomUUID();
    const track = {id, sourceVersion:id, title:file.name.replace(/\.[^.]+$/,''), artist:'Unknown artist', album:'Local files', duration, addedAt:Date.now(), status:'ready', kind:'local', color:Math.floor(Math.random()*6), evidence:[{field:'Title',value:'Display name from selected filename; embedded tags not imported',authority:'encoded_fact',source:'browser-file/1'},{field:'Duration',value:`${duration.toFixed(3)} seconds`,authority:'deterministic_measurement',source:'HTMLMediaElement metadata'}]};
    await new Promise((resolve,reject) => {
      const tx = this.db.transaction(['tracks','audio'],'readwrite');
      tx.objectStore('tracks').put(track); tx.objectStore('audio').put(file,id);
      tx.oncomplete = resolve; tx.onabort = tx.onerror = () => reject(new Error('Could not save this file. Browser storage may be full or disabled. Free space and try again.'));
    });
    return track;
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
  return {mode:value.mode, apiBase:base.href, mediaOrigins, origin};
}

export class HttpLibrary {
  mode = 'http';
  constructor(config, request = globalThis.fetch) { this.config=config; this.request=request; }
  async init() {}
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
    const data = await this.json('v1/playback-sessions',{method:'POST',signal,body:JSON.stringify({contract_version:'resonant-player/playback-request/1',track_id:track.id,source_version:track.sourceVersion,position_seconds:position})});
    let url;
    try {url=new URL(data.url);} catch {throw new Error('The service returned an invalid playback session.');}
    const expiry=Date.parse(data.expires_at);
    if(data.contract_version !== 'resonant-player/playback-session/1' || data.track_id !== track.id || data.source_version !== track.sourceVersion || !Number.isFinite(expiry) || expiry < Date.now()+5000 || ![this.config.origin,...this.config.mediaOrigins].includes(url.origin) || url.username || url.password || url.hash || (url.protocol !== 'https:' && url.origin !== this.config.origin)) throw new Error('The service returned an invalid playback session.');
    return {url:url.href,expiresAt:expiry,release:()=>{}};
  }
}
