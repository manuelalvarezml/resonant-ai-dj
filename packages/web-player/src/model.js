export const AUTHORITIES = new Set(['encoded_fact', 'standardized_measurement', 'deterministic_measurement', 'benchmark_estimate', 'user_verified', 'llm_proposal', 'executed_action']);
export const formatTime = value => Number.isFinite(value) && value >= 0 ? `${Math.floor(value / 60)}:${String(Math.floor(value % 60)).padStart(2, '0')}` : '—';
export const escapeHTML = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[c]));
// Audio identity is content, never a title or filename. Stored IDs stay intact for playlists.
export function audioIdentity(track) {
  const hash=track.fileHash??track.features?.sha256;
  return track.kind==='local'&&/^[a-f0-9]{64}$/.test(hash??'')?hash:null;
}
export function analysisQuality(features) {
  if(features?.policy!=='maest-top6-v1')return 0;
  return 1+(features.status==='complete'?1000:0)+(features.status==='complete'&&features.feature_version==='selected-estimators-v3-character120'?2000:0)+(features.genres?.length?100:0)+(features.algorithms??[]).filter(a=>['passed','warning'].includes(a.status)).length;
}
export function uniqueAudioTracks(tracks) {
  const result=[],positions=new Map();
  for(const track of tracks){
    const hash=audioIdentity(track);
    if(!hash||!positions.has(hash)){if(hash)positions.set(hash,result.length);result.push(track);continue;}
    const index=positions.get(hash),prior=result[index];
    if(analysisQuality(track.features)>analysisQuality(prior.features))result[index]=track;
  }
  return result;
}
export function filterTracks(tracks, { search = '', sort = 'recent', favorites, ids } = {}) {
  const terms = search.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
  let result = tracks.filter(t => (!favorites || favorites.includes(t.id)) && (!ids || ids.includes(t.id)) && terms.every(term => `${t.title} ${t.artist} ${t.album ?? ''}`.toLocaleLowerCase().includes(term)));
  if (sort === 'playlist' && ids) return ids.map(id => result.find(t => t.id === id)).filter(Boolean);
  return result.sort((a,b) => (sort === 'title' ? a.title.localeCompare(b.title) : sort === 'artist' ? a.artist.localeCompare(b.artist) : sort === 'duration' ? (a.duration ?? Infinity) - (b.duration ?? Infinity) : b.addedAt - a.addedAt) || a.id.localeCompare(b.id));
}
export function moveItem(items, from, to) {
  if (from < 0 || to < 0 || from >= items.length || to >= items.length) return [...items];
  const copy = [...items]; const [entry] = copy.splice(from, 1); copy.splice(to, 0, entry); return copy;
}
export function shuffled(items, random = Math.random) {
  const copy = [...items];
  for (let i = copy.length - 1; i > 0; i--) { const j = Math.floor(random() * (i + 1)); [copy[i], copy[j]] = [copy[j], copy[i]]; }
  return copy;
}
export function validateTrack(t) {
  if (!t || typeof t.id !== 'string' || !/^[a-zA-Z0-9_-]{1,128}$/.test(t.id) || typeof t.title !== 'string' || !t.title.trim() || t.title.length > 500 || typeof t.artist !== 'string' || t.artist.length > 500 || !['ready','unavailable','processing'].includes(t.status)) throw new Error('The library returned an invalid track.');
  if (t.duration !== null && (!Number.isFinite(t.duration) || t.duration < 0)) throw new Error('The library returned an invalid duration.');
  const evidence = Array.isArray(t.evidence) ? t.evidence.map(e => {
    if (!e || typeof e.field !== 'string' || typeof e.value !== 'string' || typeof e.source !== 'string' || !AUTHORITIES.has(e.authority)) throw new Error('The library returned invalid evidence.');
    return { field: e.field, value: e.value, authority: e.authority, source: e.source };
  }) : [];
  // Select public display fields only; never pass arbitrary service data into local persistence.
  return {id:t.id, fileHash:/^[a-f0-9]{64}$/.test(t.fileHash??'')?t.fileHash:null, title:t.title, artist:t.artist, album:typeof t.album === 'string' ? t.album.slice(0,500) : '', duration:t.duration, status:t.status, addedAt:Number.isFinite(t.addedAt) ? t.addedAt : 0, sourceVersion:typeof t.sourceVersion === 'string' ? t.sourceVersion : t.id, kind:t.kind === 'demo' ? 'demo' : t.kind === 'local' ? 'local' : 'cloud', features:t.features?.policy==='maest-top6-v1'?t.features:null, color:Number.isInteger(t.color) ? Math.abs(t.color)%6 : 0, evidence};
}
export function cleanPreferences(value) {
  const v = value && typeof value === 'object' ? value : {};
  const strings = x => Array.isArray(x) ? [...new Set(x.filter(s => typeof s === 'string' && /^[\w-]{1,128}$/.test(s)))].slice(0,5000) : [];
  return {
    favorites: strings(v.favorites),
    playlists: Array.isArray(v.playlists) ? v.playlists.filter(p => p && typeof p.id === 'string' && /^[\w-]{1,128}$/.test(p.id) && typeof p.name === 'string' && p.name.trim()).slice(0,100).map(p => ({id:p.id, name:p.name.slice(0,80), trackIds:strings(p.trackIds)})) : [],
    volume: Number.isFinite(v.volume) ? Math.min(1, Math.max(0, v.volume)) : 0.65,
    repeat: ['off','all','one'].includes(v.repeat) ? v.repeat : 'off',
    shuffle: v.shuffle === true
  };
}
export function playlistExport(playlist,tracks) {
  return {contract_version:'resonant-player/playlist-export/1',name:playlist.name,track_ids:[...playlist.trackIds],tracks:playlist.trackIds.map(id=>tracks.find(t=>t.id===id)).filter(Boolean).map(({id,title,artist,sourceVersion})=>({id,title,artist,sourceVersion}))};
}
