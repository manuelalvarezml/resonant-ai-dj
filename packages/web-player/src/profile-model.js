// One shared listener. Pure mutations are reused by local and cloud persistence.
export const PROFILE_KEY='PROFILE#OWNER';
const validId=s=>typeof s==='string'&&/^[\w-]{1,128}$/.test(s);
const fail=message=>{throw Object.assign(Error(message),{status:400});};
export function validateProfileOperation(op,members){
 if(!op||!(typeof op.id==='string'&&/^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/.test(op.id))||!Number.isSafeInteger(op.at)||op.at<0)fail('Invalid save operation.');
 const track=id=>{if(!validId(id)||(members&&!members.has(id)&&id!=='mix-house-example'))fail('Unknown track.');};
 if(op.type==='favorite'){track(op.trackId);if(typeof op.value!=='boolean')fail('Invalid love value.');}
 else if(op.type==='playlist'){
  if(!validId(op.playlistId)||!['create','rename','add','remove','order','delete'].includes(op.action))fail('Invalid playlist change.');
  if(['create','rename'].includes(op.action)&&(typeof op.name!=='string'||!op.name.trim()||op.name.length>80))fail('Name your playlist (80 characters maximum).');
  if(['add','remove','order'].includes(op.action)&&!Array.isArray(op.trackIds))fail('Missing playlist tracks.');
  if(op.trackIds!=null){if(!Array.isArray(op.trackIds)||op.trackIds.length>1000)fail('A playlist can hold up to 1,000 tracks.');op.trackIds.forEach(track);}
  if(op.requestId!=null&&!validId(op.requestId))fail('Invalid prompt reference.');
 }else if(op.type==='prompt'){
  if(!validId(op.requestId)||!Number.isSafeInteger(op.requestAt)||op.requestAt<0||typeof op.prompt!=='string'||!op.prompt.trim()||op.prompt.length>4000||!['requested','complete','failed','needs_clarification','unsupported','partial_support'].includes(op.status))fail('Invalid prompt history entry.');
  if(op.trackIds!=null){if(!Array.isArray(op.trackIds)||op.trackIds.length>100)fail('Too many results.');op.trackIds.forEach(track);}
  if(op.snapshot!=null){
   const snap=op.snapshot;
   if(!snap||typeof snap.interpretation!=='string'||snap.interpretation.length>2000||!snap.context||typeof snap.context!=='object'||Array.isArray(snap.context)||Object.keys(snap.context).some(k=>!['occasion','activity','recipient','emotional_goal'].includes(k))||Object.values(snap.context).some(v=>typeof v!=='string'||v.length>500)||!Array.isArray(snap.matches)||snap.matches.length>100||new TextEncoder().encode(JSON.stringify(snap)).length>45000)fail('Invalid saved explanations.');
   for(const m of snap.matches){track(m.id);if(!Number.isFinite(m.score)||!Array.isArray(m.reasons)||m.reasons.length>5||m.reasons.some(r=>typeof r.label!=='string'||r.label.length>180||!['fit','weight','points'].every(k=>Number.isFinite(r[k]))))fail('Invalid saved match.');}
  }
  if(op.clarifications!=null&&(!Array.isArray(op.clarifications)||op.clarifications.length>3||op.clarifications.some(a=>!a||typeof a.question!=='string'||a.question.length>1000||typeof a.answer!=='string'||a.answer.length>1000)))fail('Invalid clarification history.');
 }else if(op.type==='listen'){
  track(op.trackId);if(!Number.isFinite(op.seconds)||op.seconds<0||op.seconds>300)fail('Invalid listening duration.');
  for(const key of ['starts','qualified','completed','skipped'])if(![0,1,undefined].includes(op[key]))fail('Invalid listening count.');
  if(op.requestId!=null&&!validId(op.requestId))fail('Invalid request reference.');
  if(op.playlistId!=null&&!validId(op.playlistId))fail('Invalid playlist reference.');
 }else fail('Unknown save operation.');
 return op;
}
export function profileTargets(op){
 if(op.type==='favorite')return ['state#favorite#'+op.trackId];
 if(op.type==='playlist')return ['state#playlist#'+op.playlistId];
 if(op.type==='prompt')return ['prompt#'+String(op.requestAt).padStart(13,'0')+'#'+op.requestId];
 return ['state#track#'+op.trackId,...(op.requestId?['state#request#'+op.requestId]:[]),...(op.playlistId?['state#collection#'+op.playlistId]:[])];
}
export function mutateProfileItem(previous,op,key){
 const old=previous??{},base={...old,key,updatedAt:op.at};
 if(op.type==='favorite')return {...base,kind:'favorite',trackId:op.trackId,loved:op.value};
 if(op.type==='playlist'){
  if(old.deleted&&op.action!=='create')return old;
  const row={...base,kind:'playlist',id:op.playlistId,name:old.name??'Playlist',trackIds:old.trackIds??[]};
  if(op.action==='create'){if(old.id)return old;Object.assign(row,{name:op.name,trackIds:[...new Set(op.trackIds??[])],requestId:op.requestId??null});}
  if(op.action==='rename')row.name=op.name;
  if(op.action==='delete')row.deleted=true;
  if(op.action==='add')row.trackIds=[...new Set([...row.trackIds,...op.trackIds])];
  if(op.action==='remove')row.trackIds=row.trackIds.filter(id=>!op.trackIds.includes(id));
  if(op.action==='order')row.trackIds=[...op.trackIds.filter(id=>row.trackIds.includes(id)),...row.trackIds.filter(id=>!op.trackIds.includes(id))];
  if(row.trackIds.length>1000)fail('A playlist can hold up to 1,000 tracks.');
  return row;
 }
 if(op.type==='prompt')return {...base,kind:'prompt',id:op.requestId,at:op.requestAt,prompt:op.prompt,status:op.status,snapshot:op.snapshot??old.snapshot??null,trackIds:op.trackIds??old.trackIds??[],elapsedMs:Math.max(0,Math.min(op.elapsedMs??0,3600000)),error:typeof op.error==='string'?op.error.slice(0,1000):null,estimatorProfile:typeof op.estimatorProfile==='string'?op.estimatorProfile.slice(0,40):null,clarifications:op.clarifications?.map(({question,answer})=>({question,answer}))??old.clarifications??[]};
 const row={...base,kind:key.startsWith('state#track#')?'track-stats':key.startsWith('state#request#')?'request-stats':'playlist-stats',id:op.trackId,seconds:(old.seconds??0)+op.seconds};
 for(const field of ['starts','qualified','completed','skipped'])row[field]=(old[field]??0)+(op[field]??0);
 if(row.kind!=='track-stats'){row.id=key.split('#').at(-1);row.heardTrackIds=[...new Set([...(old.heardTrackIds??[]),...(op.seconds>0?[op.trackId]:[])])];row.qualifiedTrackIds=[...new Set([...(old.qualifiedTrackIds??[]),...(op.qualified?[op.trackId]:[])])];}
 return row;
}
export function preferencesFromItems(items,device={}){
 return {...device,favorites:items.filter(r=>r.kind==='favorite'&&r.loved).map(r=>r.trackId),playlists:items.filter(r=>r.kind==='playlist'&&!r.deleted).map(({id,name,trackIds,requestId})=>({id,name,trackIds,...(requestId?{requestId}:{})}))};
}
