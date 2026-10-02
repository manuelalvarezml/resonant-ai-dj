export const emptyFilters=()=>({minBpm:'',maxBpm:'',genres:[],key:'',analysis:'',favorites:false});
export const orderFields=[['recent','Date added'],['title','Title'],['artist','Artist'],['duration','Duration'],['bpm','BPM'],['key','Key · Camelot'],['genre','Top genre'],['loudness','Loudness · LUFS'],['energy','Arousal']];
export function trackFacts(t){
 const value=id=>t.features?.algorithms?.find(a=>a.algorithm_id===id&&a.status!=='failed')?.values??{};
 const key=value('key_sheetsage2').standard_key?value('key_sheetsage2'):value('key');
 return {bpm:value('rhythm').bpm,key:key.camelot||key.standard_key||null,keyLabel:[key.camelot,key.standard_key].filter(Boolean).join(' · '),genres:(t.features?.genres??[]).slice(0,6).map(g=>g.genre),loudness:value('loudness').integrated_lufs,energy:value('emotion_music2emo').arousal_mean??value('energy').arousal_mean,analysis:t.features?(t.features.status==='complete'?'complete':'partial'):'none'};
}
export function filterError(f){
 for(const v of [f.minBpm,f.maxBpm])if(v!==''&&(!Number.isFinite(Number(v))||Number(v)<=0))return 'Enter a BPM greater than zero.';
 return f.minBpm!==''&&f.maxBpm!==''&&Number(f.minBpm)>Number(f.maxBpm)?'Minimum BPM must be no higher than maximum BPM.':'';
}
export function activeFilterCount(f){return Number(f.minBpm!==''||f.maxBpm!=='')+Number(f.genres.length>0)+Number(!!f.key)+Number(!!f.analysis)+Number(f.favorites);}
export function queryLibrary(tracks,{filters=emptyFilters(),sort='recent',direction='desc',favorites=[]}={}){
 if(filterError(filters))return [];
 const rows=tracks.map(t=>({t,f:trackFacts(t)})).filter(({t,f})=>
  (filters.minBpm===''||(Number.isFinite(f.bpm)&&f.bpm>=Number(filters.minBpm)))&&
  (filters.maxBpm===''||(Number.isFinite(f.bpm)&&f.bpm<=Number(filters.maxBpm)))&&
  (!filters.genres.length||filters.genres.some(g=>f.genres.includes(g)))&&
  (!filters.key||f.key===filters.key)&&(!filters.analysis||f.analysis===filters.analysis)&&(!filters.favorites||favorites.includes(t.id)));
 const value=({t,f})=>sort==='recent'?t.addedAt:['title','artist','duration'].includes(sort)?t[sort]:sort==='genre'?f.genres[0]:f[sort];
 const missing=v=>v==null||v===''||(typeof v==='number'&&!Number.isFinite(v));
 rows.sort((a,b)=>{const av=value(a),bv=value(b);if(missing(av)!==missing(bv))return missing(av)?1:-1;
 const diff=missing(av)?0:typeof av==='number'&&typeof bv==='number'?av-bv:String(av).localeCompare(String(bv),undefined,{numeric:true,sensitivity:'base'});
 return diff*(direction==='desc'?-1:1)||a.t.title.localeCompare(b.t.title)||a.t.id.localeCompare(b.t.id);});
 return rows.map(r=>r.t);
}
