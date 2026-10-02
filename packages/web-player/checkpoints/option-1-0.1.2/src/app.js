import {LocalLibrary,HttpLibrary,validateConfig} from './adapters.js';
import {Player} from './player.js';
import {filterTracks,formatTime,escapeHTML as esc,cleanPreferences,moveItem,playlistExport} from './model.js';
import {icon} from './icons.js';

const $ = selector => document.querySelector(selector);
let library, player, tracks=[], prefs, config, search='', sort='recent', loading=true, loadError='', busy=false;
let view=location.hash.slice(1), noticeTimer, activeDialogTrack=null, dialogObjectUrl=null;
const storageKey = () => `resonant-player:preferences:1:${config.mode}`;
const button = (action,label,symbol,extra='') => `<button class="icon-button" data-action="${action}" aria-label="${esc(label)}" title="${esc(label)}" ${extra}>${icon(symbol)}</button>`;
const artwork = (track,cls='') => `<span class="artwork color-${track?.color ?? 0} ${cls}" aria-hidden="true"><span>${track ? esc(track.title.slice(0,1).toUpperCase()) : icon('music')}</span></span>`;
function rememberFocus() {
  const active=document.activeElement;
  if(!active?.dataset.action)return ()=>{};
  const parent=active.closest('[id]'),data={...active.dataset};
  return ()=>{if(active.isConnected)return;const root=document.getElementById(parent?.id);const match=[...(root?.querySelectorAll('button[data-action]')??[])].find(el=>Object.entries(data).every(([key,value])=>el.dataset[key]===value));if(match&&!match.disabled)match.focus({preventScroll:true});else root?.querySelector('button:not(:disabled)')?.focus({preventScroll:true});};
}
function notice(message,error=false) {
  const node=$('#notice'); if(!node)return; clearTimeout(noticeTimer);node.textContent=message;node.classList.toggle('error',error);node.hidden=false;
  noticeTimer=setTimeout(()=>node.hidden=true,error?14000:5500);
}
function save() { if(config.mode==='http')return;try {localStorage.setItem(storageKey(),JSON.stringify(prefs));}catch{notice('Your changes could not be saved. Browser storage may be full or disabled.',true);} }
function restore() {if(config.mode==='http')return cleanPreferences(null);try{return cleanPreferences(JSON.parse(localStorage.getItem(storageKey())));}catch{return cleanPreferences(null);} }
const find = id => tracks.find(t=>t.id===id);
const playlist = () => prefs.playlists.find(p=>view===`playlist/${p.id}`);
function displayed() {
  const p=playlist();
  const pool = view==='demo' ? tracks.filter(t=>t.kind==='demo') : view==='library' ? tracks.filter(t=>t.kind!=='demo') : tracks;
  return filterTracks(pool,{search,sort: p && sort==='recent' ? 'playlist' : sort, favorites:view==='favorites'?prefs.favorites:undefined,ids:p?.trackIds});
}
function shell() {
  $('#app').innerHTML=`
  <div class="workspace">
    <aside class="sidebar" aria-label="Main navigation">
      <a class="brand" href="#library"><span class="brand-mark">${icon('brand')}</span>resonant<span class="brand-period">.</span></a>
      <div class="sidebar-label">YOUR SPACE</div>
      <nav id="navigation"></nav>
      <div class="playlist-heading"><span class="sidebar-label">PLAYLISTS</span>${button('new-playlist','Create playlist','plus')}</div>
      <nav id="playlists-nav" aria-label="Playlists"></nav>
      <div class="sidebar-bottom"><div class="device-note">${icon('music')}<div><strong>${config.mode==='local'?'Made for your music':'Private library'}</strong><span>${config.mode==='local'?'Saved in this browser':'Connected to your library'}</span></div></div><button class="text-button" data-action="about">${icon('info')}Library information</button></div>
    </aside>
    <main id="main" tabindex="-1">
      <header class="topbar"><div class="breadcrumb">Your space <span>/</span> <span id="breadcrumb-current">Library</span></div><div class="topbar-actions"><span class="mode-badge">${config.mode==='local'?'On this device':'Private library'}</span>${button('show-queue','Show queue','queue','aria-controls="queue-panel" aria-expanded="true"')}</div></header>
      <section class="library-content">
        <div class="collection-heading"><div><p class="eyebrow" id="eyebrow">YOUR COLLECTION</p><h1 id="view-title">Your library</h1><p id="view-description" class="muted"></p></div><button class="button secondary" data-action="add-files" id="add-files">${icon('plus')}Add music</button></div>
        <div class="library-toolbar"><button class="button primary" data-action="play-all" id="play-all">${icon('play')}Play all</button><button class="button secondary" data-action="shuffle-all" id="shuffle-all">${icon('shuffle')}Shuffle</button><div class="search-field">${icon('search')}<input id="search" type="search" placeholder="Search your music" aria-label="Search tracks" autocomplete="off"></div><label class="sort-field"><span class="sr-only">Sort tracks</span><select id="sort"><option value="recent">Recently added</option><option value="title">Title A–Z</option><option value="artist">Artist A–Z</option><option value="duration">Duration</option></select>${icon('down')}</label><button class="icon-button" data-action="collection-options" id="collection-options" aria-label="Playlist options">${icon('more')}</button></div>
        <div class="track-scroll" role="region" aria-label="Tracks" tabindex="0"><div id="library-state" aria-live="polite"></div>
        <div id="track-table"></div></div>
        <div class="collection-footer"><span id="result-count"></span></div>
      </section>
    </main>
    <aside class="queue-panel" id="queue-panel" aria-label="Playback queue">
      <div class="queue-heading"><h2>Listening now</h2>${button('hide-queue','Hide queue','close')}</div>
      <div id="now-playing"></div>
      <div class="up-next-heading"><h3>Next up <span id="queue-count">0</span></h3><button class="text-button" data-action="clear-queue">Clear</button></div>
      <div id="queue-list"></div>
    </aside>
  </div>
  <footer class="player" aria-label="Audio player">
    <div id="player-track" class="player-track"></div>
    <div class="player-center"><div class="transport">${button('shuffle','Shuffle off','shuffle','id="shuffle" aria-pressed="false"')}${button('previous','Previous track','previous')}${button('toggle','Play','play','id="toggle" class-unused=""')}${button('next','Next track','next')}${button('repeat','Repeat off','repeat','id="repeat"')}</div><div class="timeline"><span id="elapsed">0:00</span><input id="seek" type="range" aria-label="Seek playback" min="0" max="1" step="0.1" value="0" disabled><span id="duration">0:00</span></div><div id="playback-status" role="status"></div></div>
    <div class="player-tools">${button('mute','Mute','volume','id="mute"')}<input id="volume" type="range" min="0" max="1" step="0.01" value="${prefs.volume}" aria-label="Volume">${button('show-queue','Show queue','queue','aria-controls="queue-panel" aria-expanded="true"')}</div>
  </footer>
  <div id="notice" class="notice" role="status" hidden></div>
  <dialog id="dialog" aria-labelledby="dialog-title"><div class="dialog-heading"><h2 id="dialog-title"></h2>${button('close-dialog','Close dialog','close')}</div><div id="dialog-body"></div></dialog>
  <input id="files" type="file" accept="audio/*,.mp3,.m4a,.aac,.ogg,.oga,.opus,.wav,.flac,.aif,.aiff" multiple hidden>
  <audio id="audio" preload="metadata"></audio>`;
  $('#add-files').hidden=config.mode!=='local';
  if(innerWidth<1200) document.body.classList.add('queue-hidden');
}
function renderNavigation() {
  const links=[['library','Your library','library',tracks.filter(t=>t.kind!=='demo').length],['favorites','Favorites','heart',prefs.favorites.length]];
  if(config.mode==='local') links.push(['demo','Demo collection','music',6]);
  $('#navigation').innerHTML=links.map(([id,label,symbol,count])=>`<a class="nav-link ${view===id?'active':''}" href="#${id}" ${view===id?'aria-current="page"':''}>${icon(symbol)}<span>${label}</span><small>${count}</small></a>`).join('');
  $('#playlists-nav').innerHTML=prefs.playlists.length ? prefs.playlists.map(p=>`<a class="nav-link playlist-link ${playlist()?.id===p.id?'active':''}" href="#playlist/${p.id}" ${playlist()?.id===p.id?'aria-current="page"':''}><span class="playlist-symbol">${icon('music')}</span><span>${esc(p.name)}</span></a>`).join('') : '';
}
function renderLibrary() {
  const restoreFocus=rememberFocus();
  renderNavigation();
  const p=playlist(), demo=view==='demo';
  const title=p?.name ?? (demo?'Demo collection':view==='favorites'?'Favorites':'Your library');
  $('#view-title').textContent=title;$('#breadcrumb-current').textContent=p?'Playlist':demo?'Demo collection':view==='favorites'?'Favorites':'Library';
  $('#eyebrow').textContent=p?'YOUR PLAYLIST':demo?'DEMO COLLECTION':view==='favorites'?'FAVORITES':'YOUR COLLECTION';
  $('#view-description').textContent=demo?'Generated demo audio':'';
  $('#collection-options').hidden=!p; $('#sort option[value="recent"]').textContent=p?'Playlist order':'Recently added';
  const results=displayed();
  $('#play-all').disabled=$('#shuffle-all').disabled=!results.some(t=>t.status==='ready') || loading;
  $('#result-count').textContent=`${results.length} ${results.length===1?'track':'tracks'}${search?' found':''}`;
  $('#library-state').innerHTML=loading?'<div class="empty-state"><span class="spinner"></span><h2>Opening your library</h2></div>':loadError?`<div class="empty-state"><h2>We couldn’t open the library</h2><p>${esc(loadError)}</p><button class="button secondary" data-action="reload">${icon('refresh')}Try again</button></div>`:!results.length?`<div class="empty-state">${icon(search?'search':'music')}<h2>${search?'No tracks found':p?'Empty playlist':view==='favorites'?'No favorites':'No tracks'}</h2>${search?'<button class="button secondary" data-action="clear-search">Clear search</button>':config.mode==='local'&&!p&&view==='library'?'<button class="button primary" data-action="add-files">Add your music</button>':''}</div>`:'';
  $('#track-table').innerHTML=loading||loadError||!results.length?'':`<table class="tracks"><thead><tr><th class="number">#</th><th>Title</th><th class="album-column">Collection</th><th class="source-column">Source</th><th class="duration-column"><span class="sr-only">Duration</span>${icon('clock')}</th><th><span class="sr-only">Favorite</span></th><th><span class="sr-only">Options</span></th></tr></thead><tbody>${results.map((track,i)=>`<tr data-track-id="${track.id}" class="${player.current?.id===track.id?'current':''}"><td class="number"><button class="row-play" data-action="play-track" data-id="${track.id}" aria-label="Play ${esc(track.title)}" ${track.status!=='ready'?'disabled':''}><span class="row-number">${player.current?.id===track.id&&player.wantPlay?icon('brand'):i+1}</span><span class="row-play-icon">${icon('play')}</span></button></td><td><div class="track-title-cell">${artwork(track)}<div class="track-text"><button class="track-title" data-action="play-track" data-id="${track.id}" ${track.status!=='ready'?'disabled':''}>${esc(track.title)}</button><span>${esc(track.artist)}</span></div></div></td><td class="album-column">${esc(track.album || '—')}</td><td class="source-column"><span class="source-tag ${track.status==='ready'?'':'unavailable'}">${track.status!=='ready'?esc(track.status):track.kind==='demo'?'Demo audio':track.kind==='local'?'On device':'Cloud'}</span></td><td class="duration-column">${formatTime(track.duration)}</td><td>${button('favorite',`${prefs.favorites.includes(track.id)?'Unfavorite':'Favorite'} ${track.title}`,'heart',`data-id="${track.id}" aria-pressed="${prefs.favorites.includes(track.id)}"`)}</td><td>${button('track-options',`Options for ${track.title}`,'more',`data-id="${track.id}"`)}</td></tr>`).join('')}</tbody></table>`;
  restoreFocus();
}
function renderPlayer() {
  const restoreFocus=rememberFocus();
  const track=player.current, playing=player.wantPlay;
  $('#player-track').innerHTML=track?`${artwork(track)}<div class="track-text"><strong>${esc(track.title)}</strong><span>${esc(track.artist)}</span></div>${button('favorite',`${prefs.favorites.includes(track.id)?'Unfavorite':'Favorite'} ${track.title}`,'heart',`data-id="${track.id}" aria-pressed="${prefs.favorites.includes(track.id)}"`)}`:`${artwork(null)}<div class="track-text"><strong>No track selected</strong></div>`;
  $('#toggle').innerHTML=icon(playing?'pause':'play');$('#toggle').setAttribute('aria-label',playing?'Pause':'Play');$('#toggle').title=playing?'Pause':'Play';
  for(const action of ['toggle','previous','next']) $(`[data-action="${action}"]`).disabled=!track;
  $('#shuffle').setAttribute('aria-pressed',String(player.shuffle));$('#shuffle').setAttribute('aria-label',`Shuffle ${player.shuffle?'on':'off'}`);
  $('#repeat').classList.toggle('selected',player.repeat!=='off');$('#repeat').innerHTML=icon('repeat')+(player.repeat==='one'?'<span class="repeat-one">1</span>':'');$('#repeat').setAttribute('aria-label',`Repeat ${player.repeat}`);$('#repeat').title=`Repeat ${player.repeat}`;
  $('#playback-status').textContent=player.status==='error'?player.error:['loading','buffering'].includes(player.status)?'Getting your track ready…':player.status==='ended'?'End of queue':track?.kind==='demo'?'Generated demo audio':'';
  $('#playback-status').classList.toggle('error-text',player.status==='error');
  $('#now-playing').innerHTML=track?`${artwork(track,'now-art')}<p class="now-source">${track.kind==='demo'?'GENERATED DEMO':track.kind==='local'?'FROM YOUR DEVICE':'FROM YOUR LIBRARY'}</p><h3>${esc(track.title)}</h3><p class="muted">${esc(track.artist)}</p><button class="text-button" data-action="track-options" data-id="${track.id}">Track details ${icon('arrow')}</button>`:`<div class="queue-empty-art">${icon('music')}</div>`;
  $('#queue-count').textContent=String(Math.max(0,player.queue.length-player.index-1));
  $('#queue-list').innerHTML=player.queue.length?player.queue.map((t,i)=>`<div class="queue-item ${i===player.index?'active':''}"><button class="queue-track" data-action="queue-play" data-index="${i}" aria-label="Play queued ${esc(t.title)}">${artwork(t)}<span class="track-text"><strong>${esc(t.title)}</strong><span>${i===player.index?'Now playing':esc(t.artist)}</span></span></button><div class="queue-item-actions">${button('queue-up',`Move ${t.title} up`,'up',`data-index="${i}" ${i===0?'disabled':''}`)}${button('queue-down',`Move ${t.title} down`,'down',`data-index="${i}" ${i===player.queue.length-1?'disabled':''}`)}${button('queue-remove',`Remove ${t.title} from queue`,'close',`data-index="${i}"`)}</div></div>`).join(''):'';
  document.querySelectorAll('tr[data-track-id]').forEach(row=>row.classList.toggle('current',row.dataset.trackId===track?.id));
  updateProgress();updateMediaSession();
  restoreFocus();
}
function updateProgress() {
  const audio=player.audio, duration=Number.isFinite(audio.duration)?audio.duration:player.current?.duration ?? 0;
  const seek=$('#seek');seek.max=duration||1;seek.value=audio.currentTime||0;seek.disabled=!player.current||!duration;
  seek.setAttribute('aria-valuetext',`${formatTime(audio.currentTime||0)} of ${formatTime(duration)}`);
  $('#elapsed').textContent=formatTime(audio.currentTime||0);$('#duration').textContent=formatTime(duration);
  seek.style.setProperty('--progress',`${duration?(audio.currentTime||0)/duration*100:0}%`);
  if('mediaSession' in navigator && Number.isFinite(audio.duration) && audio.duration>0) try{navigator.mediaSession.setPositionState({duration:audio.duration,playbackRate:1,position:Math.min(audio.currentTime,audio.duration)});}catch{}
}
function updateMediaSession() {
  if(!('mediaSession' in navigator))return;
  if(player.current && 'MediaMetadata' in window) navigator.mediaSession.metadata=new MediaMetadata({title:player.current.title,artist:player.current.artist,album:player.current.album});
  else navigator.mediaSession.metadata=null;
  navigator.mediaSession.playbackState=player.wantPlay?'playing':player.current?'paused':'none';
}
function openDialog(title,html) {
  if(dialogObjectUrl){URL.revokeObjectURL(dialogObjectUrl);dialogObjectUrl=null;}
  $('#dialog-title').textContent=title;$('#dialog-body').innerHTML=html;
  if(!$('#dialog').open)$('#dialog').showModal();
  $('#dialog-body input')?.focus();
}
function closeDialog() {$('#dialog').close();activeDialogTrack=null;if(dialogObjectUrl){URL.revokeObjectURL(dialogObjectUrl);dialogObjectUrl=null;}}
function trackOptions(id) {
  const t=find(id);if(!t)return;activeDialogTrack=id;
  openDialog(t.title,`<div class="dialog-track">${artwork(t)}<div><strong>${esc(t.artist)}</strong><p>${formatTime(t.duration)} · ${t.kind==='demo'?'Generated demo audio':t.kind==='local'?'Saved on this device':'Private cloud track'}</p></div></div><div class="dialog-actions"><button class="button secondary" data-action="play-next" data-id="${id}" ${t.status!=='ready'?'disabled':''}>${icon('next')}Play next</button><button class="button secondary" data-action="enqueue" data-id="${id}" ${t.status!=='ready'?'disabled':''}>${icon('queue')}Add to queue</button></div><h3>Add to a playlist</h3><div class="playlist-picker">${prefs.playlists.map(p=>`<button class="picker-row" data-action="add-to-playlist" data-id="${p.id}" ${p.trackIds.includes(id)?'disabled':''}>${icon(p.trackIds.includes(id)?'check':'plus')}${esc(p.name)}</button>`).join('')}<button class="picker-row" data-action="new-playlist-with-track">${icon('plus')}New playlist</button></div>${playlist()?.trackIds.includes(id)?`<button class="text-button danger" data-action="remove-from-playlist" data-id="${id}">Remove from this playlist</button>`:''}<details class="evidence"><summary>Metadata & provenance</summary><p>Musical descriptors are unknown unless supplied with evidence. No genre, mood or energy is inferred from a title.</p>${t.evidence.length?t.evidence.map(e=>`<div class="evidence-item"><strong>${esc(e.field)}</strong><span>${esc(e.value)}</span><small>${esc(e.authority)} · ${esc(e.source)}</small></div>`).join(''):'<p>No descriptor evidence was supplied.</p>'}<small>Source version: ${esc(t.sourceVersion)}</small></details>${t.kind==='local'?`<button class="text-button danger" data-action="confirm-remove" data-id="${id}">${icon('trash')}Remove from this browser</button>`:''}`);
}
function playlistForm(trackId=null,edit=false) {
  const p=edit?playlist():null;
  openDialog(edit?'Rename playlist':'A new place for your music',`<form id="playlist-form"><label class="form-label" for="playlist-name">Playlist name</label><input class="text-input" id="playlist-name" name="name" required maxlength="80" placeholder="Late night selections" value="${esc(p?.name??'')}"><p class="muted">${config.mode==='local'?'Saved on this browser.':'Kept for this session.'} Export a copy to keep it.</p><button class="button primary" type="submit">${edit?'Save name':'Create playlist'}</button></form>`);
  $('#playlist-form').onsubmit=event=>{event.preventDefault();const name=$('#playlist-name').value.trim();if(!name)return;
    if(p)p.name=name;else{if(prefs.playlists.length>=100){notice('You can save up to 100 playlists in this browser.',true);return;}const created={id:crypto.randomUUID(),name,trackIds:trackId?[trackId]:[]};prefs.playlists.push(created);view=`playlist/${created.id}`;location.hash=view;}
    save();closeDialog();renderLibrary();notice(p?'Playlist renamed.':'Playlist created.');};
}
function showCollectionOptions() {
  const p=playlist();if(!p)return;
  openDialog(p.name,`<div class="dialog-actions"><button class="button secondary" data-action="rename-playlist">Rename</button><button class="button secondary" data-action="export-playlist">${icon('download')}Export playlist</button></div><h3>Track order</h3><div class="playlist-order">${p.trackIds.map((id,i)=>{const t=find(id);return `<div class="order-row"><span>${esc(t?.title??'Unavailable track')}</span>${button('playlist-up',`Move ${t?.title??'track'} up`,'up',`data-index="${i}" ${i===0?'disabled':''}`)}${button('playlist-down',`Move ${t?.title??'track'} down`,'down',`data-index="${i}" ${i===p.trackIds.length-1?'disabled':''}`)}</div>`;}).join('')||'<p class="muted">No tracks yet.</p>'}</div><button class="text-button danger" data-action="confirm-delete-playlist">${icon('trash')}Delete playlist</button>`);
}
function downloadJSON(value,name) {
  const json=JSON.stringify(value,null,2),url=URL.createObjectURL(new Blob([json],{type:'application/json'}));
  openDialog('Export playlist',`<p>Save a list of your tracks. Audio files are not included. You can also select and copy the JSON below.</p><textarea class="export-json" aria-label="Playlist JSON" readonly>${esc(json)}</textarea><a class="button primary" href="${esc(url)}" download="${esc(name)}">${icon('download')}Download JSON</a>`);
  dialogObjectUrl=url;
}
async function importFiles(files) {
  if(busy||config.mode!=='local')return;busy=true;$('#add-files').disabled=true;let count=0,errors=[];
  try {
    if(files.length>500)throw new Error('Add at most 500 files at a time.');
    for(const [i,file] of [...files].entries()) {notice(`Adding ${i+1} of ${files.length}: ${file.name}`);try{const t=await library.importFile(file);tracks.push(t);count++;}catch(error){errors.push(`${file.name}: ${error.message}`);}}
    if(count){view='library';location.hash=view;search='';$('#search').value='';renderLibrary();}
    if(errors.length)openDialog('Some files couldn’t be added',`<p>${count} ${count===1?'track was':'tracks were'} saved. ${errors.length} couldn’t be added.</p><ul class="import-errors">${errors.map(e=>`<li>${esc(e)}</li>`).join('')}</ul>`);
    notice(`${count} ${count===1?'track':'tracks'} added to this browser.${errors.length?` ${errors.length} failed.`:''}`,errors.length>0);
  }catch(error){notice(error.message,true);}finally{busy=false;$('#add-files').disabled=false;$('#files').value='';}
}
async function loadLibrary() {
  loading=true;loadError='';renderLibrary();
  try{tracks=await library.listTracks();}catch(error){loadError=error.message;}
  loading=false;renderLibrary();
}
function queueVisibility(visible) {document.body.classList.toggle('queue-hidden',!visible);document.querySelectorAll('[aria-controls="queue-panel"]').forEach(b=>b.setAttribute('aria-expanded',String(visible)));if(visible&&innerWidth<1200)$('#queue-panel button')?.focus();}
async function action(action,el) {
  const id=el.dataset?.id, index=Number(el.dataset?.index), t=find(id);
  switch(action) {
    case 'add-files':$('#files').click();break;
    case 'reload':await loadLibrary();break;
    case 'play-all':{const list=displayed().filter(t=>t.status==='ready');if(list.length)await player.setQueue(list);break;}
    case 'shuffle-all':{const list=displayed().filter(t=>t.status==='ready');if(list.length){player.shuffle=true;prefs.shuffle=true;save();await player.setQueue(list,Math.floor(Math.random()*list.length));}break;}
    case 'play-track':{const list=displayed().filter(t=>t.status==='ready');const at=list.findIndex(t=>t.id===id);if(at>=0)await player.setQueue(list,at);break;}
    case 'toggle':await player.toggle();break;
    case 'previous':await player.previous();break;
    case 'next':await player.next();break;
    case 'shuffle':player.toggleShuffle();prefs.shuffle=player.shuffle;save();break;
    case 'repeat':player.repeat=['off','all','one'][(['off','all','one'].indexOf(player.repeat)+1)%3];prefs.repeat=player.repeat;save();player.emit();break;
    case 'mute':player.audio.muted=!player.audio.muted;$('#mute').innerHTML=icon(player.audio.muted?'mute':'volume');$('#mute').setAttribute('aria-label',player.audio.muted?'Unmute':'Mute');break;
    case 'favorite':{if(!t)break;prefs.favorites=prefs.favorites.includes(id)?prefs.favorites.filter(i=>i!==id):[...prefs.favorites,id];save();renderLibrary();renderPlayer();break;}
    case 'show-queue':queueVisibility(document.body.classList.contains('queue-hidden'));break;
    case 'hide-queue':queueVisibility(false);$('.topbar [data-action="show-queue"]').focus();break;
    case 'clear-queue':player.clear();break;
    case 'queue-play':player.index=index;await player.load();break;
    case 'queue-up':player.move(index,index-1);break;
    case 'queue-down':player.move(index,index+1);break;
    case 'queue-remove':await player.remove(index);break;
    case 'track-options':trackOptions(id);break;
    case 'close-dialog':closeDialog();break;
    case 'play-next':if(t){player.enqueue(t,true);closeDialog();notice('Added next in your queue.');}break;
    case 'enqueue':if(t){player.enqueue(t);closeDialog();notice('Added to your queue.');}break;
    case 'new-playlist':playlistForm();break;
    case 'new-playlist-with-track':playlistForm(activeDialogTrack);break;
    case 'add-to-playlist':{const p=prefs.playlists.find(p=>p.id===id);if(p&&activeDialogTrack&&!p.trackIds.includes(activeDialogTrack)){p.trackIds.push(activeDialogTrack);save();renderLibrary();trackOptions(activeDialogTrack);notice(`Added to ${p.name}.`);}break;}
    case 'remove-from-playlist':{const p=playlist();if(p){p.trackIds=p.trackIds.filter(i=>i!==id);save();closeDialog();renderLibrary();}break;}
    case 'collection-options':showCollectionOptions();break;
    case 'rename-playlist':playlistForm(null,true);break;
    case 'playlist-up':case 'playlist-down':{const p=playlist();if(p){p.trackIds=moveItem(p.trackIds,index,index+(action==='playlist-up'?-1:1));save();renderLibrary();showCollectionOptions();}break;}
    case 'export-playlist':{const p=playlist();if(p)downloadJSON(playlistExport(p,tracks),'resonant-playlist.json');break;}
    case 'confirm-delete-playlist':openDialog('Delete this playlist?',`<p>This removes the playlist. Your tracks stay in the library.</p><button class="button danger-button" data-action="delete-playlist">Delete playlist</button>`);break;
    case 'delete-playlist':{const p=playlist();if(p){prefs.playlists=prefs.playlists.filter(x=>x.id!==p.id);save();closeDialog();view='library';location.hash=view;renderLibrary();}break;}
    case 'confirm-remove':openDialog('Remove this track?',`<p>The browser’s saved copy will be removed. The original file on your device stays untouched.</p><button class="button danger-button" data-action="remove-track" data-id="${id}">Remove track</button>`);break;
    case 'remove-track':if(t?.kind==='local') {await library.removeTrack(id);if(player.current?.id===id)player.clear();else for(let i=player.queue.length-1;i>=0;i--)if(player.queue[i].id===id)await player.remove(i);tracks=tracks.filter(t=>t.id!==id);prefs.favorites=prefs.favorites.filter(i=>i!==id);prefs.playlists.forEach(p=>p.trackIds=p.trackIds.filter(i=>i!==id));save();closeDialog();renderLibrary();notice('Removed from this browser.');}break;
    case 'clear-search':search='';$('#search').value='';renderLibrary();$('#search').focus();break;
    case 'about':openDialog('Your library, your space',`<p>${config.mode==='local'?'Music you add is copied into this browser’s storage. Nothing is uploaded. Your original files stay untouched.':'Tracks are loaded from the configured private library service.'}</p><p>${config.mode==='local'?'Playlists, favorites and volume are saved in this browser. Clearing site data removes them. Browser storage is not a backup of your originals.':'Playlists and favorites last for this session only. Export playlists you want to keep. Account synchronization is not connected.'}</p><h3>Keyboard shortcuts</h3><dl class="shortcuts"><dt>Space</dt><dd>Play / pause</dd><dt>← / →</dt><dd>Seek 5 seconds</dd><dt>M</dt><dd>Mute / unmute</dd><dt>/</dt><dd>Search your music</dd></dl><p class="muted">${config.mode==='local'?'The demo collection contains six generated tone studies with fictional titles. Cloud hosting, uploads and account sync are not connected.':'Reloading clears this session’s playlists and favorites.'}</p>`);break;
  }
}
async function boot() {
  try {
    const response=await fetch(new URL('../config.json',import.meta.url),{cache:'no-store',signal:AbortSignal.timeout(15000)});if(!response.ok)throw new Error('Player configuration could not be loaded.');
    config=validateConfig(await response.json());prefs=restore();
    library=config.mode==='local'?new LocalLibrary():new HttpLibrary(config);
    let initError;try{await library.init();}catch(error){if(config.mode!=='local')throw error;initError=error.message;}
    tracks=await library.listTracks();loading=false;
    if(!view)view=config.mode==='local'&&!tracks.some(t=>t.kind==='local')?'demo':'library';
    if(!['demo','library','favorites'].includes(view)&&!prefs.playlists.some(p=>view===`playlist/${p.id}`))view='library';
    if(config.mode!=='local'&&view==='demo')view='library';
    shell();player=new Player($('#audio'),(track,options)=>library.resolvePlayback(track,options));player.repeat=prefs.repeat;player.shuffle=prefs.shuffle;player.audio.volume=prefs.volume;
    renderLibrary();renderPlayer();queueVisibility(!document.body.classList.contains('queue-hidden'));
    if(initError)notice(initError,true);
    player.addEventListener('change',renderPlayer);player.addEventListener('progress',updateProgress);
    document.addEventListener('click',event=>{const el=event.target.closest('[data-action]');if(el&&!el.disabled)action(el.dataset.action,el).catch(error=>notice(error.message,true));});
    $('#search').addEventListener('input',event=>{search=event.target.value;renderLibrary();});
    $('#sort').addEventListener('change',event=>{sort=event.target.value;renderLibrary();});
    $('#seek').addEventListener('input',event=>player.seek(Number(event.target.value)));
    $('#volume').addEventListener('input',event=>{player.audio.volume=Number(event.target.value);prefs.volume=player.audio.volume;save();});
    $('#files').addEventListener('change',event=>importFiles(event.target.files));
    $('#dialog').addEventListener('close',()=>{if(dialogObjectUrl){URL.revokeObjectURL(dialogObjectUrl);dialogObjectUrl=null;}});
    window.addEventListener('hashchange',()=>{view=location.hash.slice(1)||'library';if(!['library','favorites','demo'].includes(view)&&!prefs.playlists.some(p=>view===`playlist/${p.id}`))view='library';if(config.mode==='http'&&view==='demo')view='library';search='';$('#search').value='';sort='recent';$('#sort').value='recent';renderLibrary();});
    matchMedia('(max-width:1199px)').addEventListener('change',event=>queueVisibility(!event.matches));
    document.addEventListener('keydown',event=>{
      if(event.key==='Escape'&&!$('#dialog').open){queueVisibility(false);return;}
      if(event.ctrlKey||event.metaKey||event.altKey||event.target.closest('input,textarea,select,button,[contenteditable="true"]')||$('#dialog').open)return;
      if(event.key===' '){event.preventDefault();player.toggle();}else if(event.key==='ArrowRight'){event.preventDefault();player.seek(player.audio.currentTime+5);}else if(event.key==='ArrowLeft'){event.preventDefault();player.seek(player.audio.currentTime-5);}else if(event.key.toLowerCase()==='m')action('mute',{});else if(event.key==='/'){event.preventDefault();$('#search').focus();}
    });
    document.addEventListener('dragover',event=>{if([...event.dataTransfer.types].includes('Files')){event.preventDefault();document.body.classList.add('dragging');}});
    document.addEventListener('dragleave',event=>{if(!event.relatedTarget)document.body.classList.remove('dragging');});
    document.addEventListener('drop',event=>{event.preventDefault();document.body.classList.remove('dragging');if(event.dataTransfer.files.length)importFiles(event.dataTransfer.files);});
    window.addEventListener('offline',()=>notice(config.mode==='local'?'You’re offline. Saved local music is still available.':'You’re offline. Cloud playback may stop; reconnect and retry.'));
    if('mediaSession' in navigator)for(const [name,handler] of Object.entries({play:()=>{if(!player.wantPlay)player.toggle();},pause:()=>{if(player.wantPlay)player.toggle();},nexttrack:()=>player.next(),previoustrack:()=>player.previous(),seekto:event=>player.seek(event.seekTime),seekbackward:event=>player.seek(player.audio.currentTime-(event.seekOffset??10)),seekforward:event=>player.seek(player.audio.currentTime+(event.seekOffset??10))}))try{navigator.mediaSession.setActionHandler(name,handler);}catch{}
    window.addEventListener('pagehide',()=>player.clear());
  }catch(error){$('#app').innerHTML=`<main class="fatal"><span class="brand-mark">${icon('brand')}</span><h1>The library couldn’t open</h1><p>${esc(error.message)}</p><button id="retry-boot" class="button primary">Try again</button></main>`;$('#retry-boot').onclick=()=>location.reload();}
}
boot();
