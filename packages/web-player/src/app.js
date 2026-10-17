import {artworkThumbnail,artworkDetails,startArtwork} from './artwork.js';
import {serverlessTransport} from './serverless.js';
import {accountStorage,purgeLegacyHostedCaches} from './account-storage.js';
import {showAccount} from './account-view.js';
import {attachProductEvents} from './product-events.js';
import {recordedSpectrum} from './recorded-spectrum.js';
import {freshLibraryOrder} from './discovery.js';
import {UserProfile} from './user-profile.js';
import {attachListeningStats} from './listening-stats.js';
import {characterFeatures,statsHTML,promptHistoryHTML,promptResultsHTML} from './profile-views.js';
import {mountSortMenu} from './sort-menu.js';
import {trackCardHTML,queueHTML,playbackQuip} from './web-presentation.js';
import {releaseFront} from './release-policy.js';
import {guideHTML,mountWebMix,resolveMixPlayback} from './web-edition.js';
import {prepareMp3} from './mp3-import.js';
import {runAnalysisQueue,isStorageFailure} from './analysis-queue.js';
import {mountMixes,disposeMixes} from './mixes.js';
import {recoverAnalyzedTracks} from './recovery.js';
import {emptyFilters,orderFields,trackFacts,filterError,activeFilterCount,queryLibrary} from './library-query.js';
import {mountPlaylistIQ,playPlaylistMatch,setPlaylistIQPrompt} from './playlistiq.js';
import {appStatusHTML} from './app-status.js';
import {genreSummary,featureDetails,featureTable,localJob,cachedFeatures,needsEstimatorUpgrade} from './features.js';
const requestedFront=new URLSearchParams(location.search).get('front');
let front = releaseFront('local',requestedFront);
let disposeWebMix=null;
document.body.classList.toggle('radio-layout',front!=='studio');
import {LocalLibrary,HttpLibrary,validateConfig,fileHash,duplicateMatch} from './adapters.js';
import {Player} from './player.js';
import {filterTracks,formatTime,escapeHTML as esc,cleanPreferences,moveItem,playlistExport,uniqueAudioTracks,deduplicateCollection} from './model.js';
import {icon} from './icons.js';
import {attachSpectrogram} from './spectrogram.js';
import {mountMobilePlayer,isIOSWebKit} from './mobile-player.js';
import {bindPlaybackLifecycle} from './playback-lifecycle.js';

const $ = selector => document.querySelector(selector);
let telemetry, profile, library, player, tracks=[], prefs, config, search='', sort='recent', loading=true, loadError='', busy=false;
let featureColumns=false,libraryOrder=new Map();
let libraryFilters=emptyFilters(),orderDirection='desc',librarySort='recent';
let view=location.hash.slice(1), noticeTimer, activeDialogTrack=null, dialogObjectUrl=null;
const storageKey = () => config.serverless?`resonant:account:v1:${serverlessTransport()?.user?.id}:preferences`:`resonant-player:preferences:1:${config.mode}`;
const button = (action,label,symbol,extra='') => `<button class="icon-button" data-action="${action}" aria-label="${esc(label)}" title="${esc(label)}" ${extra}>${icon(symbol)}</button>`;
const artwork = (track,cls='') => `<span class="artwork color-${track?.color ?? 0} ${cls}" aria-hidden="true"><span>${track ? esc(track.title.slice(0,1).toUpperCase()) : icon('music')}</span></span>`;
function rememberFocus() {
  const active=document.activeElement;
  if(!active?.dataset.action)return ()=>{};
  const parent=active.closest('[id]'),data={...active.dataset};
  return ()=>{if(active.isConnected)return;const root=document.getElementById(parent?.id);const match=[...(root?.querySelectorAll('button[data-action]')??[])].find(el=>Object.entries(data).every(([key,value])=>el.dataset[key]===value));if(match&&!match.disabled)match.focus({preventScroll:true});else root?.querySelector('button:not(:disabled)')?.focus({preventScroll:true});};
}
function notice(message,error=false) {
  if(error)telemetry?.error();
  const node=$('#notice'); if(!node)return; clearTimeout(noticeTimer);node.textContent=message;node.classList.toggle('error',error);node.hidden=false;
  noticeTimer=setTimeout(()=>node.hidden=true,error?14000:5500);
}
function save() { try{profile?.savePreferences(prefs);}catch(e){notice(e.message,true);} if(config.mode==='http'&&config.edition!=='web')return;try {localStorage.setItem(storageKey(),JSON.stringify(prefs));}catch{notice('Your changes could not be saved. Browser storage may be full or disabled.',true);} }
function restore() {if(config.mode==='http'&&config.edition!=='web')return cleanPreferences(null);try{return cleanPreferences(JSON.parse(localStorage.getItem(storageKey())));}catch{return cleanPreferences(null);} }
const find = id => tracks.find(t=>t.id===id);
const playlist = () => prefs.playlists.find(p=>view===`playlist/${p.id}`);
function openLibraryFilters(){
  const pool=tracks.filter(t=>t.kind!=='demo'),facts=pool.map(trackFacts);
  const genres=[...new Set(facts.flatMap(f=>f.genres))].sort();
  const keys=[...new Map(facts.filter(f=>f.key).map(f=>[f.key,f.keyLabel])).entries()].sort((a,b)=>a[0].localeCompare(b[0],undefined,{numeric:true}));
  const f=libraryFilters;
  openDialog('Shape your library',`<form id="library-filter-form" class="library-filter-form"><p class="muted">Shared by Your Library and Analysis. Filters combine; selected genres match any of the top six. Tracks missing a requested feature are excluded.</p><div class="filter-grid"><fieldset><legend>01 / Tempo</legend><div class="bpm-range"><label>From BPM<input name="minBpm" type="number" min="0.01" step="any" placeholder="Any" value="${esc(f.minBpm)}"></label><span>—</span><label>To BPM<input name="maxBpm" type="number" min="0.01" step="any" placeholder="Any" value="${esc(f.maxBpm)}"></label></div></fieldset><fieldset><legend>02 / Harmonic key</legend><label>Key<select name="key"><option value="">Any key</option>${keys.map(([v,label])=>`<option value="${esc(v)}" ${f.key===v?'selected':''}>${esc(label)}</option>`).join('')}</select></label></fieldset><fieldset class="genre-filter"><legend>03 / Genres <span>match any selected</span></legend><input id="genre-filter-search" type="search" placeholder="Find a genre…" aria-label="Find a genre"><div class="genre-filter-list">${genres.map(g=>`<label><input type="checkbox" name="genres" value="${esc(g)}" ${f.genres.includes(g)?'checked':''}><span>${esc(g.replace('---',' / '))}</span></label>`).join('')||'<p>No analyzed genres available yet.</p>'}</div></fieldset><fieldset><legend>04 / Collection</legend><label>Analysis<select name="analysis">${[['','Any status'],['complete','Fully analyzed'],['partial','Partly analyzed'],['none','Not analyzed']].map(([v,l])=>`<option value="${v}" ${f.analysis===v?'selected':''}>${l}</option>`).join('')}</select></label><label class="favorite-filter"><input type="checkbox" name="favorites" ${f.favorites?'checked':''}> Favorites only</label></fieldset></div><p id="filter-feedback" role="status"></p><div class="filter-actions"><button type="button" class="button secondary" id="reset-library-filters">Clear filters</button><button type="submit" class="button primary">Apply filters</button></div></form>`);
  const form=$('#library-filter-form');
  const read=()=>{const d=new FormData(form);return {minBpm:d.get('minBpm').trim(),maxBpm:d.get('maxBpm').trim(),genres:d.getAll('genres'),key:d.get('key'),analysis:d.get('analysis'),favorites:d.has('favorites')};};
  const preview=()=>{const draft=read(),error=filterError(draft);$('#filter-feedback').textContent=error||`${queryLibrary(pool,{filters:draft,favorites:prefs.favorites}).length} / ${pool.length} tracks match these filters`;};
  form.oninput=preview;form.onchange=preview;
  $('#genre-filter-search').oninput=event=>{const q=event.target.value.toLowerCase();form.querySelectorAll('.genre-filter-list label').forEach(l=>l.hidden=!l.textContent.toLowerCase().includes(q));};
  $('#reset-library-filters').onclick=()=>{form.querySelectorAll('input').forEach(i=>{if(i.type==='checkbox')i.checked=false;else i.value='';});form.querySelectorAll('select').forEach(i=>i.value='');form.querySelectorAll('.genre-filter-list label').forEach(l=>l.hidden=false);preview();};
  form.onsubmit=event=>{event.preventDefault();const next=read();if(filterError(next)){preview();return;}libraryFilters=next;closeDialog();renderLibrary();};preview();
}
function displayed() {
  const p=playlist();
  const pool = view==='demo' ? tracks.filter(t=>t.kind==='demo') : ['library','analysis','playlistiq','mixes','status'].includes(view) ? tracks.filter(t=>t.kind!=='demo') : tracks;
  const results=filterTracks(view==='analysis'||config.edition==='web'?uniqueAudioTracks(pool):pool,{search,sort: p && sort==='recent' ? 'playlist' : sort, favorites:view==='favorites'?prefs.favorites:undefined,ids:p?.trackIds});
  return ['library','analysis'].includes(view)?queryLibrary(results,{filters:libraryFilters,sort,direction:orderDirection,favorites:prefs.favorites,randomOrder:libraryOrder}):results;
}
function shell() {
  $('#app').innerHTML=`
  <div class="workspace">
    <aside class="sidebar" aria-label="Main navigation">
      <a class="brand" href="#library"><span class="brand-mark">${icon('brand')}</span>resonant<span class="brand-period">.</span></a>
      <div class="sidebar-label">YOUR SPACE</div>${config.edition==='web'?'<button class="text-button account-button" data-action="account">Account</button>':''}
      <nav id="navigation"></nav>
      <div class="playlist-heading" ${config.edition==='web'?'hidden':''}><span class="sidebar-label">${config.edition==='web'?'PLAYLIST':'PLAYLISTS'}</span>${button('new-playlist','Create playlist','plus')}${config.edition==='web'?button('show-queue','Show queue','queue','class-unused="" aria-controls="queue-panel"'):''}</div>
      <nav id="playlists-nav" aria-label="Playlists"></nav>
      <div class="sidebar-bottom"><div class="front-switch" ${config.edition==='web'?'hidden':''} role="group" aria-label="Front end option"><button data-action="set-front" data-front="studio" aria-pressed="false">Option 1</button><button data-action="set-front" data-front="radio-wide" aria-pressed="false">Option 3</button></div><div class="device-note">${icon('music')}<div><strong>${config.mode==='local'?'Made for your music':'Private library'}</strong><span>${config.mode==='local'?'Saved in this browser':'Connected to your library'}</span></div></div>${config.edition==='web'?'':`<button class="text-button" data-action="about">${icon('info')}Library information</button>`}</div>
    </aside>
    <main id="main" tabindex="-1">
      <header class="topbar"><div class="breadcrumb">Your space <span>/</span> <span id="breadcrumb-current">Library</span></div><div class="topbar-actions">${config.edition==='web'?'<button class="text-button account-button" data-action="account">Account</button>':''}<span class="mode-badge">${config.mode==='local'?'On this device':'Private library'}</span>${button('show-queue','Show queue','queue','aria-controls="queue-panel" aria-expanded="true"')}</div></header>
      <section class="library-content">
        <div class="collection-heading"><div><p class="eyebrow" id="eyebrow">YOUR COLLECTION</p><h1 id="view-title">Your library</h1><p id="view-description" class="muted"></p></div><div class="collection-actions"><button class="button secondary" data-action="recover-batch" id="recover-batch">Restore saved batch</button><button class="button secondary" data-action="add-files" id="add-files">${icon('plus')}Add music</button><button id="analysis-start" class="button secondary analysis-start" data-action="analyze-tracks" hidden>${icon('analyze')}Analyze Tracks</button><button id="convert-m4a" class="button secondary" data-action="convert-m4a" hidden>Convert M4A to MP3</button></div>${config.edition==='web'?'':`<div class="spectrum-modes" role="group" aria-label="Spectrogram view"><button type="button" data-spectrum="isometric" aria-pressed="false">Isometric</button><button type="button" data-spectrum="front" aria-pressed="true">Front</button><button type="button" data-spectrum="mountain" aria-pressed="false">Mountain</button><button type="button" data-spectrum="falling" aria-pressed="false">Falling</button></div>`}<canvas class="spectrum-accent" role="img" aria-label="Live 3D spectrogram: frequency, time and amplitude" width="420" height="360"></canvas></div>
        <div class="analysis-toolbar"><span id="analysis-progress" role="status"></span></div><div class="library-toolbar"><button class="button primary" data-action="play-all" id="play-all">${icon('play')}Play all</button><button class="button secondary" data-action="shuffle-all" id="shuffle-all">${icon('shuffle')}Shuffle</button><button class="button secondary" data-action="toggle-features" id="toggle-features" aria-pressed="false">${icon('columns')}Feature columns</button><div class="search-field">${icon('search')}<input id="search" type="search" placeholder="Search your music" aria-label="Search tracks" autocomplete="off"></div><button class="button secondary" id="library-filter" data-action="library-filter" aria-haspopup="dialog">Filter</button><label class="sort-field"><span class="sr-only">Order by</span><select id="sort">${(config.edition==='web'?[['random','Random order'],...orderFields]:orderFields).map(([value,label])=>`<option value="${value}">${label}</option>`).join('')}</select>${icon('down')}</label><button class="button secondary order-direction" id="order-direction" data-action="order-direction" aria-label="Descending order" title="Descending order">↓</button><button class="icon-button" data-action="collection-options" id="collection-options" aria-label="Playlist options">${icon('more')}</button></div>
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
    ${config.edition==='web'?'<div id="player-actions" class="player-actions"></div>':''}
    <div class="player-tools">${button('mute','Mute','volume','id="mute"')}<input id="volume" type="range" min="0" max="1" step="0.01" value="${prefs.volume}" aria-label="Volume">${button('show-queue','Show queue','queue','aria-controls="queue-panel" aria-expanded="true"')}</div>
  </footer>
  <div id="notice" class="notice" role="status" hidden></div>
  <dialog id="dialog" aria-labelledby="dialog-title"><div class="dialog-heading"><h2 id="dialog-title"></h2>${button('close-dialog','Close dialog','close')}</div><div id="dialog-body"></div></dialog>
  <input id="files" type="file" accept=".mp3,.m4a,audio/mpeg,audio/mp4" multiple hidden>
  <audio id="audio" preload="metadata"></audio>`;
  document.body.classList.toggle('web-edition',config.edition==='web');
  if(config.edition==='web'){document.title='Resonant · Library';mountSortMenu($('#sort'));}
  applyFront();
  const nativeAudio=config.edition==='web'&&(isIOSWebKit()||new URLSearchParams(location.search).get('spectrum')==='recorded');
  attachSpectrogram($('#audio'),$('.spectrum-accent'),config.mode==='local'||config.edition==='web',{fixedMode:config.edition==='web'?'falling':null,webEdition:config.edition==='web',sampleSpectrum:nativeAudio?recordedSpectrum($('#audio')):null});
  $('#add-files').hidden=config.mode!=='local';
  if(innerWidth<1200) document.body.classList.add('queue-hidden');
}
function applyFront() {
  document.body.classList.toggle('radio-wide-layout',front==='radio-wide');
  document.body.classList.toggle('radio-layout',front!=='studio');
  document.querySelectorAll('.front-switch button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.front===front)));
  const workspace=$('.workspace'), transport=$('.player');
  if(!workspace || !transport)return;
  if(front!=='studio'){workspace.insertBefore(transport,$('main'));queueVisibility(false);}
  else {workspace.after(transport);queueVisibility(innerWidth>=1200);}
}
function renderNavigation() {
  const links=[['library',config.edition==='web'?'Library':'Your library','library',tracks.filter(t=>t.kind!=='demo').length],['playlists','Playlists','music',prefs.playlists.length],['analysis','Analysis','library',0],['playlistiq','PlaylistIQ','music',0],['mixes','DJ mixes','music',0],['status',config.edition==='web'?'Inside Resonant':'App status','info',0]];
  if(config.edition==='web')links.sort((a,b)=>['playlistiq','library','playlists','mixes','analysis','status'].indexOf(a[0])-['playlistiq','library','playlists','mixes','analysis','status'].indexOf(b[0]));
  $('#navigation').innerHTML=links.filter(([id])=>config.edition!=='web'||!['analysis','status'].includes(id)).map(([id,label,symbol,count])=>`<a class="nav-link ${view===id?'active':''}" href="#${id}" ${view===id?'aria-current="page"':''}>${icon(symbol)}<span>${label}</span><small>${count}</small></a>`).join('')+(config.edition==='web'?button('show-queue','Show queue','queue',`aria-controls="queue-panel" aria-expanded="${!document.body.classList.contains('queue-hidden')}"`):'');
  $('#playlists-nav').innerHTML=prefs.playlists.length ? prefs.playlists.map(p=>`<a class="nav-link playlist-link ${playlist()?.id===p.id?'active':''}" href="#playlist/${p.id}" ${playlist()?.id===p.id?'aria-current="page"':''}><span class="playlist-symbol">${icon('music')}</span><span>${esc(p.name)}</span></a>`).join('') : '';
}
function renderLibrary() {
  if(config.edition==='web'&&['analysis','status','demo'].includes(view))view='library';
  document.body.dataset.view=view;
  disposeWebMix?.();disposeWebMix=null;
  const restoreFocus=rememberFocus();
  if(view!=='mixes')disposeMixes();
  renderNavigation();
  document.body.classList.toggle('status-view',view==='status');
  document.body.classList.toggle('library-view',view==='library');
  document.body.classList.toggle('analysis-view',view==='analysis');
  document.body.classList.toggle('playlistiq-view',view==='playlistiq');
  $('#analysis-start').hidden=view!=='analysis'||config.edition==='web';
  $('#analysis-start').disabled=busy||analyzing||loading;
  $('#convert-m4a').hidden=view!=='analysis'||config.mode!=='local';
  $('#convert-m4a').disabled=busy||analyzing||loading;
  const filterable=['library','analysis'].includes(view);
  $('#recover-batch').hidden=!filterable||config.mode!=='local';
  $('#recover-batch').disabled=busy||analyzing||loading;
  if(filterable)sort=librarySort;
  $('#library-filter').hidden=$('#order-direction').hidden=!filterable;
  $('#library-filter').textContent=`Filter${activeFilterCount(libraryFilters)?' · '+activeFilterCount(libraryFilters):''}`;
  $('#library-filter').classList.toggle('filters-active',activeFilterCount(libraryFilters)>0);
  $('#order-direction').textContent=orderDirection==='asc'?'↑':'↓';
  $('#order-direction').setAttribute('aria-label',orderDirection==='asc'?'Ascending order; switch to descending':'Descending order; switch to ascending');
  $('#order-direction').title=orderDirection==='asc'?'Ascending':'Descending';
  for(const option of $('#sort').options)option.hidden=!filterable&&!['recent','title','artist','duration'].includes(option.value);
  if(!filterable&&!['recent','title','artist','duration'].includes(sort))sort='recent';
  $('#sort').value=sort;
  const toolbar=$('.library-toolbar');
  if(view==='analysis')$('.collection-heading').insertBefore(toolbar,$('.collection-actions'));
  else $('.library-content').insertBefore(toolbar,$('.track-scroll'));
  const index=view==='playlists';
  if(view==='status'){void renderAppStatus();restoreFocus();return;}
  if(view==='playlistiq'){renderPlaylistIQ();restoreFocus();return;}
  if(view==='mixes'){renderMixes();restoreFocus();return;}
  $('.library-toolbar').hidden=index;
  $('#add-files').hidden=index || view==='analysis' || config.mode!=='local';
  $('.track-scroll').setAttribute('aria-label',index?'Playlists':'Tracks');
  if(index){
    $('#view-title').textContent=$('#breadcrumb-current').textContent='Playlists';
    $('#view-description').textContent='';
    $('#library-state').innerHTML=`<div class="playlist-index"><button class="button secondary" data-action="new-playlist">${icon('plus')}Create playlist</button>${config.edition==='web'?`<a class="nav-link liked-songs" href="#favorites">${icon('heart')}<span>Liked Songs</span><span>${prefs.favorites.length} ${prefs.favorites.length===1?'track':'tracks'}</span></a>`:''}${prefs.playlists.map(p=>`<a class="nav-link" href="#playlist/${p.id}">${icon('music')}<span>${esc(p.name)}</span><span>${p.trackIds.length} ${p.trackIds.length===1?'track':'tracks'}</span></a>`).join('')}</div>`;
    $('#track-table').innerHTML='';
    $('#result-count').textContent=`${prefs.playlists.length} ${prefs.playlists.length===1?'playlist':'playlists'}`;
    restoreFocus();return;
  }
  $('#toggle-features').hidden=view==='analysis'||config.edition==='web';
  $('#toggle-features').setAttribute('aria-pressed',String(featureColumns));
  const p=playlist(), demo=view==='demo';
  const title=p?.name ?? (view==='analysis'?'Analysis':demo?'Demo collection':view==='favorites'?'Liked Songs':config.edition==='web'?'Library':'Your library');
  $('#view-title').textContent=title;$('#breadcrumb-current').textContent=p?'Playlist':demo?'Demo collection':view==='favorites'?'Liked Songs':'Library';
  $('#eyebrow').textContent=p?'YOUR PLAYLIST':demo?'DEMO COLLECTION':view==='favorites'?'FAVORITES':'YOUR COLLECTION';
  $('#view-description').textContent=demo?'Generated demo audio':'';
  $('#collection-options').hidden=!p; $('#sort option[value="recent"]').textContent=p?'Playlist order':'Date added';
  const results=displayed();
  $('#play-all').disabled=$('#shuffle-all').disabled=!results.some(t=>t.status==='ready') || loading;
  $('#result-count').textContent=`${results.length} ${results.length===1?'track':'tracks'}${search||(['library','analysis'].includes(view)&&activeFilterCount(libraryFilters))?' found':''}`;
  $('#library-state').innerHTML=loading?'<div class="empty-state"><span class="spinner"></span><h2>Opening your library</h2></div>':loadError?`<div class="empty-state"><h2>We couldn’t open the library</h2><p>${esc(loadError)}</p><button class="button secondary" data-action="reload">${icon('refresh')}Try again</button></div>`:!results.length?`<div class="empty-state">${icon(search?'search':'music')}<h2>${search||activeFilterCount(libraryFilters)?'No tracks found':p?'Empty playlist':view==='favorites'?'Nothing loved. Yet.':'No tracks'}</h2>${['library','analysis'].includes(view)&&activeFilterCount(libraryFilters)?'<button class="button secondary" data-action="clear-library-filters">Clear filters</button>':search?'<button class="button secondary" data-action="clear-search">Clear search</button>':config.mode==='local'&&!p&&view==='library'?'<button class="button primary" data-action="add-files">Add your music</button>':''}</div>`:'';
  $('#track-table').innerHTML=loading||loadError||!results.length?'':`<table class="tracks"><thead><tr><th class="number">#</th><th>Title</th><th class="album-column">Collection</th><th class="source-column">Source</th><th class="duration-column"><span class="sr-only">Duration</span>${icon('clock')}</th><th><span class="sr-only">Favorite</span></th><th><span class="sr-only">Options</span></th></tr></thead><tbody>${results.map((track,i)=>`<tr data-track-id="${track.id}" class="${player.current?.id===track.id?'current':''}"><td class="number"><button class="row-play" data-action="play-track" data-id="${track.id}" aria-label="Play ${esc(track.title)}" ${track.status!=='ready'?'disabled':''}><span class="row-number">${player.current?.id===track.id&&player.wantPlay?icon('brand'):i+1}</span><span class="row-play-icon">${icon('play')}</span></button></td><td><div class="track-title-cell">${artworkThumbnail(track)}<div class="track-text"><button class="track-title" data-action="play-track" data-id="${track.id}" ${track.status!=='ready'?'disabled':''}>${esc(track.title)}</button><span>${esc(track.artist)}</span>${genreSummary(track)}</div></div></td><td class="album-column">${esc(track.album || '—')}</td><td class="source-column"><span class="source-tag ${track.status==='ready'?'':'unavailable'}">${track.status!=='ready'?esc(track.status):track.kind==='demo'?'Demo audio':track.kind==='local'?'On device':'Cloud'}</span></td><td class="duration-column">${formatTime(track.duration)}</td><td>${button('favorite',`${prefs.favorites.includes(track.id)?'Unfavorite':'Favorite'} ${track.title}`,'heart',`data-id="${track.id}" aria-pressed="${prefs.favorites.includes(track.id)}"`)}</td><td>${button('track-options',`Options for ${track.title}`,'more',`data-id="${track.id}"`)}</td></tr>`).join('')}</tbody></table>`;
  if(config.edition==='web')for(const row of document.querySelectorAll('#track-table tr[data-track-id]')){
    const track=find(row.dataset.trackId),love=row.children[5].querySelector('button').outerHTML,more=row.children[6].querySelector('button').outerHTML;row.innerHTML=`<td colspan="7" class="web-card-cell">${trackCardHTML(track)}<div class="web-track-actions">${more}${love}</div></td>`;
  }
  if(config.edition==='web')$('#track-table thead')?.remove();
  if((featureColumns||view==='analysis')&&!loading&&!loadError&&results.length)$('#track-table').innerHTML=featureTable(results);
  restoreFocus();
}
function renderPlayer() {
  const restoreFocus=rememberFocus();
  const track=player.current, playing=player.wantPlay&&!player.audio.paused;
  $('#player-track').innerHTML=track?`${artworkThumbnail(track)}<div class="track-text"><strong>${esc(track.title)}</strong><span>${esc(track.artist)}</span></div>${button('favorite',`${prefs.favorites.includes(track.id)?'Unfavorite':'Favorite'} ${track.title}`,'heart',`data-id="${track.id}" aria-pressed="${prefs.favorites.includes(track.id)}"`)}`:`${artwork(null)}<div class="track-text"><strong>No track selected</strong></div>`;
  $('#toggle').innerHTML=icon(playing?'pause':'play');$('#toggle').setAttribute('aria-label',playing?'Pause':'Play');$('#toggle').title=playing?'Pause':'Play';
  for(const action of ['toggle','previous','next']) $(`[data-action="${action}"]`).disabled=!track;
  $('#shuffle').setAttribute('aria-pressed',String(player.shuffle));$('#shuffle').setAttribute('aria-label',`Shuffle ${player.shuffle?'on':'off'}`);
  $('#repeat').classList.toggle('selected',player.repeat!=='off');$('#repeat').innerHTML=icon('repeat')+(player.repeat==='one'?'<span class="repeat-one">1</span>':'');$('#repeat').setAttribute('aria-label',`Repeat ${player.repeat}`);$('#repeat').title=`Repeat ${player.repeat}`;
  $('#playback-status').textContent=player.status==='error'?player.error:['loading','buffering'].includes(player.status)?'Getting your track ready…':player.status==='ended'?'End of queue':player.interrupted?'Playback paused. Press Play to continue.':track?.kind==='demo'?'Generated demo audio':'';
  $('#playback-status').classList.toggle('error-text',player.status==='error');
  $('#now-playing').innerHTML=track?`${artwork(track,'now-art')}<p class="now-source">${track.kind==='demo'?'GENERATED DEMO':track.kind==='local'?'FROM YOUR DEVICE':'FROM YOUR LIBRARY'}</p><h3>${esc(track.title)}</h3><p class="muted">${esc(track.artist)}</p><button class="text-button" data-action="track-options" data-id="${track.id}">Track details ${icon('arrow')}</button>`:`<div class="queue-empty-art">${icon('music')}</div>`;
  $('#queue-count').textContent=String(Math.max(0,player.queue.length-player.index-1));
  $('#queue-list').innerHTML=player.queue.length?player.queue.map((t,i)=>`<div class="queue-item ${i===player.index?'active':''}"><button class="queue-track" data-action="queue-play" data-index="${i}" aria-label="Play queued ${esc(t.title)}">${artworkThumbnail(t)}<span class="track-text"><strong>${esc(t.title)}</strong><span>${i===player.index?'Now playing':esc(t.artist)}</span></span></button><div class="queue-item-actions">${button('queue-up',`Move ${t.title} up`,'up',`data-index="${i}" ${i===0?'disabled':''}`)}${button('queue-down',`Move ${t.title} down`,'down',`data-index="${i}" ${i===player.queue.length-1?'disabled':''}`)}${button('queue-remove',`Remove ${t.title} from queue`,'close',`data-index="${i}"`)}</div></div>`).join(''):'';
  if(config.edition==='web'){
    $('#now-playing').innerHTML='';$('#queue-list').innerHTML=queueHTML(player);
    $('#playback-status').textContent=playbackQuip(player);
    $('.player').dataset.state=player.status;$('.player').dataset.interrupted=String(!!player.interrupted);
    $('#player-actions').innerHTML=`<button data-action="favorite" data-id="${esc(track?.id??'')}" aria-label="${prefs.favorites.includes(track?.id)?'Remove love':'Love'}" title="${prefs.favorites.includes(track?.id)?'Remove love':'Love'}" aria-pressed="${prefs.favorites.includes(track?.id)}" ${!track||track.kind==='mix'?'disabled':''}>${icon('heart')}</button><button aria-label="Add to playlist" title="Add to playlist" data-action="add-playing-to-playlist" ${!track||track.kind==='mix'?'disabled':''}>${icon('plus')}</button>`;
  }
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
  navigator.mediaSession.playbackState=player.status==='playing'&&!player.audio.paused?'playing':player.current?'paused':'none';
}
function openDialog(title,html) {
  if(dialogObjectUrl){URL.revokeObjectURL(dialogObjectUrl);dialogObjectUrl=null;}
  $('#dialog-title').textContent=title;$('#dialog-body').innerHTML=html;
  if(!$('#dialog').open)$('#dialog').showModal();
  $('#dialog-body input')?.focus();
}
function closeDialog() {historyView++;$('#dialog').close();$('#dialog-body').replaceChildren();document.activeElement?.blur();activeDialogTrack=null;if(dialogObjectUrl){URL.revokeObjectURL(dialogObjectUrl);dialogObjectUrl=null;}}
function playlistPicker(id){
 const t=find(id);if(!t)return;activeDialogTrack=id;
 openDialog('Add to playlist',`<p>${esc(t.title)}</p><div class="playlist-picker">${prefs.playlists.map(p=>`<button class="picker-row" data-action="add-to-playlist" data-id="${esc(p.id)}" ${p.trackIds.includes(id)?'disabled':''}>${icon(p.trackIds.includes(id)?'check':'plus')}${esc(p.name)}</button>`).join('')}<button class="picker-row" data-action="new-playlist-with-track">${icon('plus')}New playlist</button></div>`);
}
let historyRows=[],historyView=0;
function historyTracks(row){
 $('#dialog-title').textContent='Your prompt';$('#dialog-body').innerHTML=promptResultsHTML(row,tracks);
 $('#history-back').onclick=()=>void showPromptHistory();
 for(const b of document.querySelectorAll('[data-history-track]'))b.onclick=()=>{const queue=row.trackIds.map(find).filter(t=>t?.status==='ready'),index=queue.findIndex(t=>t.id===b.dataset.historyTrack);if(index>=0){player.shuffle=false;prefs.shuffle=false;save();void player.setQueue(queue,index,{source:'playlistiq',requestId:row.id});}};
}
async function showPromptHistory(){
 const version=++historyView;openDialog('Your prompts','<p>Opening the musical paper trail…</p>');historyRows=[];
 const page=async cursor=>{try{const result=await profile.prompts(cursor);historyRows.push(...result.items);if(!$('#dialog').open||version!==historyView)return;$('#dialog-body').innerHTML=promptHistoryHTML(historyRows,profile.projected())+(result.cursor?'<button class="button secondary" id="more-prompts">Earlier prompts</button>':'');$('#more-prompts')?.addEventListener('click',()=>void page(result.cursor));
  for(const b of document.querySelectorAll('[data-prompt-reuse]'))b.onclick=()=>{const r=historyRows.find(r=>r.id===b.dataset.promptReuse);if(setPlaylistIQPrompt(r.prompt)===false){notice('Wait for the current playlist request to finish.');return;}closeDialog();view='playlistiq';location.hash=view;renderLibrary();};
  for(const b of document.querySelectorAll('[data-prompt-open]'))b.onclick=()=>{historyView++;historyTracks(historyRows.find(r=>r.id===b.dataset.promptOpen));};
 }catch(e){$('#dialog-body').textContent=e.message;}};await profile.sync();await page('');
}
const playbackContext=()=>({source:playlist()?'playlist':'library',...(playlist()?{playlistId:playlist().id,requestId:playlist().requestId??null}:{})});
function trackOptions(id) {
  const t=find(id);if(!t)return;activeDialogTrack=id;
  if(config.edition==='web'){openDialog(t.title,`<p class="muted">${esc(t.artist)}</p>${artworkDetails(t)}${characterFeatures(t)}<div class="dialog-actions"><button class="button secondary" data-action="pick-playlist" data-id="${id}">${icon('plus')}Add to playlist</button></div>${playlist()?.trackIds.includes(id)?`<button class="text-button" data-action="remove-from-playlist" data-id="${id}">Remove from this playlist</button>`:''}`);return;}
  openDialog(t.title,`<div class="dialog-track">${artwork(t)}<div><strong>${esc(t.artist)}</strong><p>${formatTime(t.duration)} · ${t.kind==='demo'?'Generated demo audio':t.kind==='local'?'Saved on this device':'Private cloud track'}</p></div></div><div class="dialog-actions"><button class="button secondary" data-action="play-next" data-id="${id}" ${t.status!=='ready'?'disabled':''}>${icon('next')}Play next</button><button class="button secondary" data-action="enqueue" data-id="${id}" ${t.status!=='ready'?'disabled':''}>${icon('queue')}Add to queue</button></div>${t.kind==='local'?`<button class="button secondary" data-action="analyze-one" data-id="${id}">${t.features?(needsEstimatorUpgrade(t)?'Upgrade / retry analysis':'Check analysis'):'Analyze track'}</button><button class="button secondary" data-action="compare-estimators" data-id="${id}">${t.features?.supervised_status==='complete'?'Check danceability experiment':'Compare MusiCNN danceability'}</button><p class="muted">Analyze track runs all selected estimators, retaining EffNet and Music2Emo mood scores for comparison. The optional danceability experiment adds MusiCNN; EffNet remains selected.</p>${genreSummary(t)}${featureDetails(t)}`:config.edition==='web'?featureDetails(t):''}${artworkDetails(t)}<h3>Add to a playlist</h3><div class="playlist-picker">${prefs.playlists.map(p=>`<button class="picker-row" data-action="add-to-playlist" data-id="${p.id}" ${p.trackIds.includes(id)?'disabled':''}>${icon(p.trackIds.includes(id)?'check':'plus')}${esc(p.name)}</button>`).join('')}<button class="picker-row" data-action="new-playlist-with-track">${icon('plus')}New playlist</button></div>${playlist()?.trackIds.includes(id)?`<button class="text-button danger" data-action="remove-from-playlist" data-id="${id}">Remove from this playlist</button>`:''}<details class="evidence"><summary>Metadata & provenance</summary><p>Musical descriptors are unknown unless supplied with evidence. No genre, mood or energy is inferred from a title.</p>${t.evidence.length?t.evidence.map(e=>`<div class="evidence-item"><strong>${esc(e.field)}</strong><span>${esc(e.value)}</span><small>${esc(e.authority)} · ${esc(e.source)}</small></div>`).join(''):'<p>No descriptor evidence was supplied.</p>'}<small>Source version: ${esc(t.sourceVersion)}</small></details>${t.kind==='local'?`<button class="text-button danger" data-action="confirm-remove" data-id="${id}">${icon('trash')}Remove from this browser</button>`:''}`);
}
function playlistForm(trackId=null,edit=false) {
  const p=edit?playlist():null;
  openDialog(edit?'Rename playlist':'A new place for your music',`<form id="playlist-form"><label class="form-label" for="playlist-name">Playlist name</label><input class="text-input" id="playlist-name" name="name" required maxlength="80" placeholder="Late night selections" value="${esc(p?.name??'')}"><p class="muted">${config.edition==='web'?'Saved privately to your account.':config.mode==='local'?'Saved on this browser. Export a copy to keep it.':'Kept for this session.'}</p><button class="button primary" type="submit">${edit?'Save name':'Create playlist'}</button></form>`);
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
let analyzing=false;
function featureProgress(text){const e=$('#analysis-progress');if(e)e.textContent=text;}
async function analyzeTracks(ids=null,supervised=false,specialists=false){
  if(busy){notice('Finish the import review before starting analysis.');return;}
  if(config.mode!=='local'){notice('Analysis is available in the local player service.',true);return;}
  if(analyzing){notice('Analysis is already running.');return;}
  const selected=uniqueAudioTracks(tracks.filter(t=>t.kind==='local'&&(!ids||ids.includes(t.id)))).filter(t=>ids||needsEstimatorUpgrade(t));
  if(!selected.length){notice('Add music first, or all loaded tracks are already analyzed.');return;}
  analyzing=true;renderLibrary();const errors=[];let paused=false;
  try{const result=await runAnalysisQueue(selected,async(t,i)=>{
    featureProgress(`Analyzing ${i+1}/${selected.length}: ${t.title}`);
    const audio=await library.read('audio',t.id);if(!audio)throw Error('Stored audio is missing. Add the file again.');
      const features=await localJob('analyze',audio,audio.name||t.title+'.wav',message=>featureProgress(`${i+1}/${selected.length} · ${t.title} · ${message}`),{supervised,specialists});
      const updated=await library.saveFeatures(t.id,features);tracks=tracks.map(x=>x.id===t.id?updated:x);
      if(features.status!=='complete'||(supervised&&features.supervised_status!=='complete')||(specialists&&features.quality_status!=='complete'))errors.push(`${t.title}: ${[...features.algorithms.filter(a=>a.status==='failed').map(a=>a.error||a.algorithm_id),...(features.upgrade_failures??[]).map(a=>a.error||a.algorithm_id)].join('; ')}`);
      renderLibrary();
  });paused=result.paused;errors.push(...result.errors.map(({item,error})=>item.title+': '+error.message));
  }finally{analyzing=false;renderLibrary();featureProgress(paused?'Analysis paused. Reload to reconnect storage; remaining tracks were not attempted.':errors.length?`Analysis finished with ${errors.length} incomplete tracks.`:'Analysis complete. Ready for PlaylistIQ.');}
  if(errors.length)openDialog(paused?'Analysis paused':'Some features need attention',`<p>${paused?'Browser storage could not reconnect. Remaining tracks were not attempted. Reload the player and retry; completed server analysis remains cached.':'Successful features are saved. Retry missing features from a track’s options.'}</p><ul>${errors.map(e=>`<li>${esc(e)}</li>`).join('')}</ul>`);
}
async function renderAppStatus(){
  $('.library-toolbar').hidden=true;$('#add-files').hidden=true;
  $('#view-title').textContent=$('#breadcrumb-current').textContent='App status';
  $('#view-description').textContent='';$('#eyebrow').textContent='CURRENT CHECKPOINT';
  $('.track-scroll').setAttribute('aria-label',config.edition==='web'?'Inside Resonant':'App status');
  $('#track-table').innerHTML='';$('#result-count').textContent='';
  if(config.edition==='web'){$('#view-title').textContent=$('#breadcrumb-current').textContent='Inside Resonant';$('#library-state').innerHTML=guideHTML();return;}
  $('#library-state').innerHTML='<p class="muted">Loading app status…</p>';
  try{
    const response=await fetch(new URL('../app-status.json',import.meta.url),{cache:'no-store'});
    if(!response.ok)throw Error('Could not load the maintained app status. Reload to retry.');
    const data=await response.json();if(view!=='status')return;
    $('#library-state').innerHTML=appStatusHTML(data,tracks,prefs.playlists.length);
  }catch(error){if(view==='status')$('#library-state').textContent=error.message;}
}
function playlistIQForm(){location.hash='playlistiq';view='playlistiq';renderLibrary();}
function renderMixes(){
  $('.library-toolbar').hidden=true;$('#add-files').hidden=true;
  $('#view-title').textContent=$('#breadcrumb-current').textContent='DJ mixes';
  $('#eyebrow').textContent='MAKE IT FLOW';$('#view-description').textContent='';
  $('.track-scroll').setAttribute('aria-label','DJ mixes');
  $('#track-table').innerHTML='';$('#result-count').textContent='';
  if(config.edition==='web'){void mountWebMix($('#library-state'),{player}).then(dispose=>{if(view==='mixes')disposeWebMix=dispose;else dispose?.();});return;}
  mountMixes($('#library-state'),{mainAudio:player.audio,pauseMain:()=>{if(player.wantPlay)player.toggle();}});
}
function renderPlaylistIQ(){
  $('.track-scroll').setAttribute('aria-label','PlaylistIQ results');
  $('.library-toolbar').hidden=true;$('#add-files').hidden=true;
  $('#view-title').textContent=$('#breadcrumb-current').textContent='PlaylistIQ';
  $('#eyebrow').textContent='YOUR NEXT PLAYLIST';$('#view-description').textContent='';
  $('#track-table').innerHTML='';$('#result-count').textContent='';
  const pool=uniqueAudioTracks(tracks.filter(t=>t.kind==='local'||config.edition==='web'));
  const candidates=pool.filter(t=>t.features?.genres?.length);
  const total=pool.length;
  mountPlaylistIQ($('#library-state'),{candidates,total,localJob,notice,webEdition:config.edition==='web',onHistory:()=>void showPromptHistory(),onStats:()=>openDialog('Your listening habits',statsHTML(profile.projected(),tracks)),onRecordPrompt:row=>profile?.recordPrompt(row),onPlay:(id,matches,run)=>playPlaylistMatch(player,tracks,matches,id,{source:'playlistiq',requestId:run?.userRequestId??null}),onSave:(text,matches,run)=>{
    if(prefs.playlists.length>=100){notice('Playlist limit reached.',true);return;}
    const p={id:crypto.randomUUID(),name:text.trim().slice(0,80)||'PlaylistIQ',...(run?.userRequestId?{requestId:run.userRequestId}:{}),trackIds:matches.map(m=>m.track.track_id).filter(id=>find(id))};
    prefs.playlists.push(p);save();location.hash='playlist/'+p.id;view='playlist/'+p.id;renderLibrary();
  }});
}
async function importFiles(files) {
  if(busy||config.mode!=='local')return;
  if(analyzing){notice('Wait for analysis to finish before importing or replacing tracks.');return;}
  busy=true;$('#add-files').disabled=true;let count=0,errors=[],duplicates=[];
  try {
    if(files.length>500)throw new Error('Add at most 500 files at a time.');
    notice('Checking the library for duplicates…');
    const index=await library.duplicateIndex();
    for(const [i,incoming] of [...files].entries()) {
      notice(`Preparing ${i+1} of ${files.length}: ${incoming.name}`);
      try {
        const file=await prepareMp3(incoming);
        const hash=await fileHash(file),match=duplicateMatch(index,file,hash);
        if(match){duplicates.push({file,hash,match,artworkSource:incoming});continue;}
        const t=await library.importFile(file,{hash,artworkSource:incoming});tracks.push(t);index.push({id:t.id,title:t.title,name:file.name,hash});count++;
      }catch(error){errors.push(`${incoming.name}: ${error.message}`);if(isStorageFailure(error))break;}
    }
    if(count){view='library';location.hash=view;search='';$('#search').value='';renderLibrary();}
    if(duplicates.length)await reviewDuplicates(duplicates,count,errors);
    else if(errors.length)openDialog('Import summary',`<p>${count} tracks added.</p><ul>${errors.map(e=>`<li>${esc(e)}</li>`).join('')}</ul>`);
    else notice(`${count} tracks added.`);
    const restored=await library.restoreCachedFeatures(hash=>cachedFeatures(hash));
    if(restored){tracks=await library.listTracks();renderLibrary();notice(`Restored saved analysis for ${restored} tracks. No new analysis needed.`);}
  }catch(error){notice(error.message,true);}finally{busy=false;$('#add-files').disabled=false;$('#files').value='';renderLibrary();}
}
async function convertExistingM4a(){
  if(busy||analyzing||config.mode!=='local')return;
  busy=true;renderLibrary();let converted=0,unsupported=0;const errors=[];
  try{
    const candidates=tracks.filter(t=>t.kind==='local');
    for(const [i,t] of candidates.entries()){
      featureProgress(`Checking audio ${i+1}/${candidates.length}: ${t.title}`);
      try{
        const original=await library.read('audio',t.id);
        if(!original)throw Error('Stored audio is missing.');
        if(/\.mp3$/i.test(original.name))continue;
        if(!/\.m4a$/i.test(original.name)){unsupported++;continue;}
        featureProgress(`Converting to MP3: ${t.title}`);
        const file=await prepareMp3(original);
        const updated=await library.replaceAudioWithMp3(t.id,file,t.fileHash||await fileHash(original));
        tracks=tracks.map(x=>x.id===t.id?updated:x);
        const wasCurrent=player.current?.id===t.id;
        player.queue=player.queue.map(x=>x.id===t.id?updated:x);
        if(wasCurrent)await player.load(0,false);
        converted++;
      }catch(error){errors.push(`${t.title}: ${error.message}`);if(isStorageFailure(error))break;}
    }
  }finally{busy=false;renderLibrary();}
  featureProgress(`${converted} tracks converted to MP3. Run Analyze Tracks for fresh analysis.`);
  openDialog('MP3 conversion',`<p>${converted} tracks converted. Playlist references are preserved. Original files on disk are untouched, and original browser audio and analysis are backed up. Converted tracks need fresh analysis.</p><p class="muted">MP3 conversion is lossy. ${unsupported} files skipped because they are neither MP3 nor M4A.</p>${errors.length?`<ul>${errors.map(e=>`<li>${esc(e)}</li>`).join('')}</ul>`:''}`);
}
function reviewDuplicates(items,count,errors){
 return new Promise(resolve=>{
  openDialog('Review duplicate tracks',`<p>${count} new tracks added. Review ${items.length} duplicate files before adding them.</p><p class="muted">Replace keeps playlist references. Changed audio needs fresh analysis. Closing this review omits pending duplicates.</p><form id="duplicate-form"><div class="duplicate-list">${items.map((d,i)=>`<div class="duplicate-row"><div><strong>${esc(d.file.name)}</strong><p class="muted">${d.hash===d.match.hash?'Identical file':'Matching filename'} · ${esc(d.match.title)}</p></div><label><span class="sr-only">Action for ${esc(d.file.name)}</span><select name="duplicate-${i}"><option value="omit">Omit</option><option value="both">Keep both</option><option value="replace">Replace</option></select></label></div>`).join('')}</div>${errors.length?`<ul>${errors.map(e=>`<li>${esc(e)}</li>`).join('')}</ul>`:''}<p id="duplicate-status" role="status"></p><button class="button primary" type="submit">Apply choices</button></form>`);
  const dialog=$('#dialog');let applying=false;
  const closed=()=>{if(!applying){dialog.removeEventListener('close',closed);resolve();}};
  dialog.addEventListener('close',closed);
  $('#duplicate-form').onsubmit=async event=>{
    event.preventDefault();if(applying)return;applying=true;
    const form=event.currentTarget,choices=new FormData(form);form.querySelector('button').disabled=true;
    const failures=[];let added=0,replaced=0,omitted=0;
    for(const [i,d] of items.entries()){
      const choice=choices.get('duplicate-'+i);if(choice==='omit'){omitted++;continue;}
      try{
        const t=await library.importFile(d.file,{hash:d.hash,replaceId:choice==='replace'?d.match.id:null,artworkSource:d.artworkSource});
        if(choice==='replace'){
          tracks=tracks.map(x=>x.id===t.id?t:x);
          const wasCurrent=player.current?.id===t.id;
          player.queue=player.queue.map(x=>x.id===t.id?t:x);
          if(wasCurrent)await player.load(0,false);
          replaced++;
        }else{tracks.push(t);added++;}
      }catch(e){failures.push(d.file.name+': '+e.message);}
    }
    dialog.removeEventListener('close',closed);closeDialog();renderLibrary();renderPlayer();
    const summary=`${count+added} added · ${replaced} replaced · ${omitted} omitted`;
    if(failures.length)openDialog('Import summary',`<p>${summary}</p><ul>${failures.map(e=>`<li>${esc(e)}</li>`).join('')}</ul>`);else notice(summary);
    resolve();
  };
 });
}

async function loadLibrary() {
  loading=true;loadError='';renderLibrary();
  try{tracks=await library.listTracks();if(config.edition==='web'){const collection=deduplicateCollection(tracks,prefs);tracks=collection.tracks;prefs=collection.preferences;save();}const restored=config.mode==='local'?await library.restoreCachedFeatures(hash=>cachedFeatures(hash)):0;if(restored){tracks=await library.listTracks();notice(`Restored saved analysis for ${restored} track${restored===1?'':'s'}.`);}}catch(error){loadError=error.message;}
  loading=false;renderLibrary();
}
let queueAnimation=null;
function queueVisibility(visible) {
 const panel=$('#queue-panel'),wasOpen=!document.body.classList.contains('queue-hidden');queueAnimation?.cancel();queueAnimation=null;
 document.querySelectorAll('[aria-controls="queue-panel"]').forEach(b=>b.setAttribute('aria-expanded',String(visible)));
 const animated=config?.edition==='web'&&!matchMedia('(prefers-reduced-motion: reduce)').matches;
 if(visible){document.body.classList.remove('queue-hidden');panel.style.transform='';panel.getBoundingClientRect();if(animated&&!wasOpen)queueAnimation=panel.animate([{transform:'translate3d(0,100dvh,0)'},{transform:'translate3d(0,0,0)'}],{duration:780,easing:'cubic-bezier(.32,.72,0,1)'});if(innerWidth<1200)panel.querySelector('button')?.focus();}
 else if(animated&&wasOpen){const start=getComputedStyle(panel).transform;queueAnimation=panel.animate([{transform:start==='none'?'translate3d(0,0,0)':start},{transform:'translate3d(0,100dvh,0)'}],{duration:660,easing:'cubic-bezier(.4,0,.2,1)',fill:'forwards'});queueAnimation.finished.then(()=>{document.body.classList.add('queue-hidden');panel.style.transform='';queueAnimation?.cancel();queueAnimation=null;}).catch(()=>{});}
 else {document.body.classList.add('queue-hidden');panel.style.transform='';}
}
async function action(action,el) {
  const id=el.dataset?.id, index=Number(el.dataset?.index), t=find(id);
  switch(action) {
    case 'recover-batch':{
      if(busy||analyzing||config.mode!=='local')break;
      busy=true;el.disabled=true;$('#add-files').disabled=true;
      try{
        const summary=await recoverAnalyzedTracks(library,message=>notice(message));
        if(config.serverless){purgeLegacyHostedCaches(localStorage);prefs=restore();window.addEventListener('storage',e=>{if(e.key==='resonant:account-change'){player?.clear();location.replace('/login/index.html');}});window.addEventListener('pageshow',e=>{if(e.persisted)location.reload();});}
    tracks=await library.listTracks();search='';$('#search').value='';libraryFilters=emptyFilters();
        const message=`${summary.added} tracks restored · ${summary.omitted} already in your library · saved analysis reused where available`;
        if(summary.errors.length)openDialog('Recovery summary',`<p>${esc(message)}</p><ul>${summary.errors.map(e=>`<li>${esc(e)}</li>`).join('')}</ul>`);
        else notice(message);
      }catch(error){notice(error.message,true);}
      finally{busy=false;$('#add-files').disabled=false;renderLibrary();}break;
    }
    case 'convert-m4a':await convertExistingM4a();break;
    case 'analyze-tracks':await analyzeTracks();break;
    case 'library-filter':openLibraryFilters();break;
    case 'clear-library-filters':libraryFilters=emptyFilters();renderLibrary();break;
    case 'order-direction':orderDirection=orderDirection==='asc'?'desc':'asc';renderLibrary();break;
    case 'quality-estimators':closeDialog();await analyzeTracks([id],false,true);break;
    case 'compare-estimators':closeDialog();await analyzeTracks([id],true);break;
    case 'analyze-one':closeDialog();await analyzeTracks([id]);break;
    case 'playlistiq':playlistIQForm();break;
    case 'toggle-features':featureColumns=!featureColumns;renderLibrary();break;
    case 'set-front':{front=releaseFront(config.edition,el.dataset.front);const url=new URL(location.href);if(front!=='studio')url.searchParams.set('front',front);else url.searchParams.delete('front');history.replaceState(null,'',url);applyFront();if($('#dialog').open)closeDialog();break;}
    case 'add-files':$('#files').click();break;
    case 'reload':await loadLibrary();break;
    case 'play-all':{const list=displayed().filter(t=>t.status==='ready');if(list.length)await player.setQueue(list,0,playbackContext());break;}
    case 'shuffle-all':{const list=displayed().filter(t=>t.status==='ready');if(list.length){player.shuffle=true;prefs.shuffle=true;save();await player.setQueue(list,Math.floor(Math.random()*list.length),playbackContext());}break;}
    case 'play-track':{const list=displayed().filter(t=>t.status==='ready');const at=list.findIndex(t=>t.id===id);if(at>=0)await player.setQueue(list,at,playbackContext());break;}
    case 'toggle':await player.toggle();break;
    case 'previous':await player.previous();break;
    case 'next':await player.next();break;
    case 'shuffle':player.toggleShuffle();prefs.shuffle=player.shuffle;save();break;
    case 'repeat':player.repeat=['off','all','one'][(['off','all','one'].indexOf(player.repeat)+1)%3];prefs.repeat=player.repeat;save();player.emit();break;
    case 'mute':player.audio.muted=!player.audio.muted;$('#mute').innerHTML=icon(player.audio.muted?'mute':'volume');$('#mute').setAttribute('aria-label',player.audio.muted?'Unmute':'Mute');break;
    case 'pick-playlist':playlistPicker(id);break;
    case 'add-playing-to-playlist':playlistPicker(player.current?.id);break;
    case 'prompt-history':await showPromptHistory();break;
    case 'listening-stats':openDialog('Your listening habits',statsHTML(profile.projected(),tracks));break;
    case 'export-listening':{let cursor='',prompts=[];do{const page=await profile.prompts(cursor);prompts.push(...page.items);cursor=page.cursor;}while(cursor);const data={exportedAt:new Date().toISOString(),profile:profile.projected(),prompts};const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const link=document.createElement('a');link.href=url;link.download='resonant-listening-history.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),60000);break;}
    case 'favorite':{if(!t)break;prefs.favorites=prefs.favorites.includes(id)?prefs.favorites.filter(i=>i!==id):[...prefs.favorites,id];save();renderLibrary();renderPlayer();if($('#dialog').open&&activeDialogTrack===id)trackOptions(id);break;}
    case 'show-queue':queueVisibility(document.body.classList.contains('queue-hidden'));break;
    case 'hide-queue':queueVisibility(false);[...document.querySelectorAll('[data-action="show-queue"]')].find(b=>b.getClientRects().length)?.focus();break;
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
    case 'add-to-playlist':{const p=prefs.playlists.find(p=>p.id===id);if(p&&activeDialogTrack&&!p.trackIds.includes(activeDialogTrack)){p.trackIds.push(activeDialogTrack);save();renderLibrary();playlistPicker(activeDialogTrack);notice(`Added to ${p.name}.`);}break;}
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
    case 'account':await showAccount({cloud:serverlessTransport(),profile,player,openDialog});break;
    case 'about':openDialog('Library information',`<h3>Front end</h3><div class="dialog-actions" ${config.edition==='web'?'hidden':''}><button class="button ${front==='studio'?'primary':'secondary'}" data-action="set-front" data-front="studio">01 / Studio</button><button class="button ${front==='radio-wide'?'primary':'secondary'}" data-action="set-front" data-front="radio-wide">03 / Visualization</button></div><p>${config.mode==='local'?'Music you add is copied into this browser’s storage. Analysis sends a temporary copy to the local service on this computer. Audio is not sent to a cloud provider. Your original files stay untouched.':'Tracks are loaded from the configured private library service.'}</p><p>${config.mode==='local'?'Playlists, favorites and volume are saved in this browser. Clearing site data removes them. Browser storage is not a backup of your originals.':'Playlists and favorites are saved in this browser. Everyone can explore the same published collection.'}</p><h3>Keyboard shortcuts</h3><dl class="shortcuts"><dt>Space</dt><dd>Play / pause</dd><dt>← / →</dt><dd>Seek 5 seconds</dd><dt>M</dt><dd>Mute / unmute</dd><dt>/</dt><dd>Search your music</dd></dl><p class="muted">${config.mode==='local'?'The demo collection contains six generated tone studies with fictional titles. Cloud hosting, uploads and account sync are not connected.':'Analysis and library updates are managed locally by the owner.'}</p>`);break;
  }
}
async function boot() {
  try {
    const response=await fetch(new URL('../config.json',import.meta.url),{cache:'no-store',signal:AbortSignal.timeout(15000)});if(!response.ok)throw new Error('Player configuration could not be loaded.');
    config=validateConfig(await response.json());if(config.edition==='web'){sort=librarySort='random';orderDirection='asc';}front=releaseFront(config.edition,requestedFront);prefs=config.serverless?cleanPreferences(null):restore();
    library=config.mode==='local'?new LocalLibrary():new HttpLibrary(config);
    let initError;try{await library.init();}catch(error){if(config.mode!=='local')throw error;initError=error.message;}
    if(config.serverless){purgeLegacyHostedCaches(localStorage);prefs=restore();window.addEventListener('storage',e=>{if(e.key==='resonant:account-change'){player?.clear();location.replace('/login/index.html');}});window.addEventListener('pageshow',e=>{if(e.persisted)location.reload();});}
    tracks=await library.listTracks();if(config.edition==='web'){const collection=deduplicateCollection(tracks,prefs);tracks=collection.tracks;prefs=collection.preferences;save();}const restored=config.mode==='local'?await library.restoreCachedFeatures(hash=>cachedFeatures(hash)):0;if(restored)tracks=await library.listTracks();loading=false;
    if(config.edition==='web'){let prior='';try{prior=localStorage.getItem('resonant:discovery:first')??'';}catch{}libraryOrder=freshLibraryOrder(tracks,prior);try{localStorage.setItem('resonant:discovery:first',[...libraryOrder.keys()][0]??'');}catch{}}
    if(!view)view=config.mode==='local'&&!tracks.some(t=>t.kind==='local')?'demo':'library';
    if(!['demo','library','favorites','playlists','analysis','playlistiq','mixes','status'].includes(view)&&!prefs.playlists.some(p=>view===`playlist/${p.id}`))view='library';
    if(config.mode!=='local'&&view==='demo')view='library';
    shell();player=new Player($('#audio'),(track,options)=>track.kind==='mix'?resolveMixPlayback(track):library.resolvePlayback(track,options));player.repeat=prefs.repeat;player.shuffle=prefs.shuffle;player.audio.volume=prefs.volume;
    renderLibrary();renderPlayer();queueVisibility(!document.body.classList.contains('queue-hidden'));
    const stopArtwork=startArtwork({library,getTracks:()=>tracks,enabled:!config.serverless||Boolean(config.artwork),delivery:config.artwork});
    window.addEventListener('pagehide',stopArtwork,{once:true});
    if(initError)notice(initError,true);else if(restored)notice(`Restored saved analysis for ${restored} track${restored===1?'':'s'}.`);
    player.addEventListener('change',renderPlayer);player.addEventListener('progress',updateProgress);
    document.addEventListener('click',event=>{const el=event.target.closest('[data-action]');if(el&&!el.disabled)action(el.dataset.action,el).catch(error=>notice(error.message,true));});
    $('#search').addEventListener('input',event=>{search=event.target.value;renderLibrary();});
    $('#sort').addEventListener('change',event=>{sort=event.target.value;if(['library','analysis'].includes(view))librarySort=sort;orderDirection=sort==='recent'?'desc':'asc';renderLibrary();});
    $('#seek').addEventListener('input',event=>player.seek(Number(event.target.value)));
    $('#volume').addEventListener('input',event=>{player.audio.volume=Number(event.target.value);prefs.volume=player.audio.volume;save();});
    $('#files').addEventListener('change',event=>importFiles(event.target.files));
    $('#dialog').addEventListener('close',()=>{if(dialogObjectUrl){URL.revokeObjectURL(dialogObjectUrl);dialogObjectUrl=null;}});
    document.addEventListener('pointerdown',event=>{if(config.edition==='web'&&!document.body.classList.contains('queue-hidden')&&!event.target.closest('#queue-panel,[data-action=show-queue]'))queueVisibility(false);});
    window.addEventListener('hashchange',()=>{queueVisibility(false);view=location.hash.slice(1)||'library';if(!['library','favorites','demo','playlists','analysis','playlistiq','mixes','status'].includes(view)&&!prefs.playlists.some(p=>view===`playlist/${p.id}`))view='library';if(config.mode==='http'&&view==='demo')view='library';search='';$('#search').value='';renderLibrary();});
    matchMedia('(max-width:1199px)').addEventListener('change',event=>queueVisibility(front==='studio'&&!event.matches));
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
    if(config.edition==='web'){
      bindPlaybackLifecycle(player);mountMobilePlayer(player,{nativeAudio:isIOSWebKit()||new URLSearchParams(location.search).get('spectrum')==='recorded',closeQueue:()=>queueVisibility(false)});
      profile=new UserProfile({...(config.serverless?{storage:accountStorage(localStorage,serverlessTransport().user.id),importLegacy:false}:{}),preferences:prefs,onError:message=>notice(message,true),onChange:next=>{const changed=JSON.stringify([prefs.favorites,prefs.playlists])!==JSON.stringify([next.favorites,next.playlists]);prefs={...prefs,favorites:next.favorites,playlists:next.playlists};try{localStorage.setItem(storageKey(),JSON.stringify(prefs));}catch{}if(changed){renderNavigation();if(!['playlistiq','mixes'].includes(view))renderLibrary();renderPlayer();}}});
      attachListeningStats(player,profile);if(config.serverless)telemetry=attachProductEvents(serverlessTransport());void profile.init().catch(e=>notice(e.message,true));
    }
    else window.addEventListener('pagehide',()=>player.clear());
  }catch(error){$('#app').innerHTML=`<main class="fatal"><span class="brand-mark">${icon('brand')}</span><h1>The library couldn’t open</h1><p>${esc(error.message)}</p><button id="retry-boot" class="button primary">Try again</button></main>`;$('#retry-boot').onclick=()=>location.reload();}
}
boot();
