import {escapeHTML as esc} from './model.js';

// Artwork is a display sidecar, never part of feature/ranking or audio records.
let records={},catalog=()=>[],storedHandler=()=>{},imageBase='/api/artwork/images/';
export function artworkDelivery(value){
 if(!value||!/^\/library\/artwork\/releases\/[a-f0-9]{64}\/manifest\.json$/.test(value.manifestURL??'')||value.imageBase!=='/library/artwork/images/')throw Error('Invalid artwork delivery configuration.');
 return {manifestURL:value.manifestURL,imageBase:value.imageBase};
}
export function notifyStoredArtwork(track){
 // Storage has committed. Never await artwork on the import/playback/analysis path.
 setTimeout(()=>storedHandler(track),0);
}
export function artworkThumbnail(track){
 const id=track?.id??track?.track_id??'';
 return `<span class="album-thumbnail" data-artwork-track="${esc(id)}" aria-hidden="true" title="Artwork unavailable"><span>♪</span></span>`;
}
export function matchingArtwork(track,manifest){
 const record=manifest?.[track?.id];
 return record&&record.source_version===track.sourceVersion?record:null;
}
export function artworkDetails(track){
 const record=matchingArtwork(track,records);
 if(!record)return '<p class="muted">Album artwork: not resolved.</p>';
 const link=record.provider==='musicbrainz-caa'&&/^[a-f0-9-]{36}$/.test(record.release_group??'')?` · <a href="https://musicbrainz.org/release-group/${esc(record.release_group)}" target="_blank" rel="noopener noreferrer">MusicBrainz / Cover Art Archive</a>`:'';
 return `<p class="muted">Album artwork: ${esc(record.status)} · ${esc(record.provider??record.reason??'placeholder')} · confidence: ${esc(record.confidence)}${link}</p>`;
}
export function hydrateArtwork(root=document){
 const byId=new Map();for(const t of catalog()){byId.set(t.id,t);if(t.fileHash)byId.set(t.fileHash,t);}
 for(const node of root.querySelectorAll('[data-artwork-track]')){
  const track=byId.get(node.dataset.artworkTrack),record=matchingArtwork(track,records),file=record?.thumbnail?.file;
  const valid=record?.status==='ready'&&/^[a-f0-9]{64}\.jpg$/.test(file??'');
  const key=valid?file:'placeholder';if(node.dataset.artworkRendered===key)continue;
  node.dataset.artworkRendered=key;node.replaceChildren();
  const fallback=document.createElement('span');fallback.textContent='♪';node.append(fallback);
  node.title=valid?(record.provider==='embedded'?'Embedded album artwork':'Cover Art Archive / MusicBrainz · exact artist and album match'):'Artwork unavailable';
  if(valid){const image=document.createElement('img');image.alt='';image.width=36;image.height=36;image.loading='lazy';image.decoding='async';image.src=imageBase+file;image.onerror=()=>image.remove();node.append(image);}
 }
}
export function startArtwork({library,getTracks,enabled=true,delivery=null,request=fetch}){
 catalog=getTracks;
 const hosted=delivery?artworkDelivery(delivery):null;
 imageBase=hosted?.imageBase??'/api/artwork/images/';
 const observer=new MutationObserver(()=>hydrateArtwork());observer.observe(document.body,{childList:true,subtree:true});
 // Hosted delivery is a signed static sidecar. It never enables the local intake API.
 if(!enabled)return()=>observer.disconnect();
 let stopped=false,refreshing=false,queue=Promise.resolve();const pending=new Set();
 const refresh=async()=>{if(stopped||refreshing)return;refreshing=true;try{const response=await request(hosted?.manifestURL??'/api/artwork/manifest',{signal:AbortSignal.timeout(10000)});if(response.ok){const data=await response.json();if(data.contract_version==='resonant/artwork/1'){records=data.tracks??{};hydrateArtwork();}}}catch{}finally{refreshing=false;}};
 const enqueue=track=>{
  const key=track.id+':'+track.sourceVersion;
  if(hosted||stopped||track.kind!=='local'||pending.has(key)||matchingArtwork(track,records))return;
  pending.add(key);
  queue=queue.then(async()=>{
   if(stopped||track.kind!=='local'||matchingArtwork(track,records))return;
   const current=await library.read('tracks',track.id);if(current?.sourceVersion!==track.sourceVersion)return;
   const file=await library.read('audio','artwork-source:'+track.id)??await library.read('audio',track.id);if(!(file instanceof Blob))return;
   const params=new URLSearchParams({id:track.id,version:track.sourceVersion,artist:track.artist,album:track.album});
   const response=await request('/api/artwork/stored?'+params,{method:'POST',headers:{'X-Resonant-Local':'1','Content-Type':'application/octet-stream'},body:file,signal:AbortSignal.timeout(120000)});
   if(response.ok)await refresh();
  }).catch(()=>{}).finally(()=>pending.delete(key));
 };
 storedHandler=enqueue;
 void refresh().then(()=>{if(library.mode==='local')for(const track of getTracks())enqueue(track);});
 const timer=setInterval(()=>{void refresh().then(()=>{if(library.mode==='local')for(const track of getTracks())enqueue(track);});},30000);
 return()=>{stopped=true;clearInterval(timer);observer.disconnect();storedHandler=()=>{};};
}
