import {escapeHTML as esc} from './model.js';
export const GENRE_POLICY='maest-top6-v1';
export const FEATURE_VERSION='selected-estimators-v3-character120';
export function needsEstimatorUpgrade(track){return track.features?.feature_version!==FEATURE_VERSION||track.features?.status!=='complete';}
export function genreSummary(track){const f=track.features;if(!f)return '';const g=f.genres??[];return `<div class="genre-summary">${g.slice(0,3).map(x=>`<span>${esc(x.genre.replace('---',' / '))}</span>`).join('')}${g.length>3?`<details><summary>All ${g.length} genres</summary>${g.slice(3).map(x=>`<span>${esc(x.genre.replace('---',' / '))}</span>`).join('')}</details>`:''}<small>${f.status==='complete'?(needsEstimatorUpgrade(track)?'Analyzed · estimator upgrade available':'Analyzed'):'Partly analyzed — retry available'}</small></div>`;}
export async function cachedFeatures(hash,request=globalThis.fetch){
 if(!/^[a-f0-9]{64}$/.test(hash))return null;
 const response=await request('/api/local/features/'+hash,{headers:{'X-Resonant-Local':'1'},cache:'no-store'});
 if(response.status===404)return null;
 let body;try{body=await response.json();}catch{throw Error('Saved analysis could not be read.');}
 const value=body?.result;
 if(!response.ok||!value||value.sha256!==hash||value.policy!==GENRE_POLICY||!['complete','partial'].includes(value.status)||!Array.isArray(value.algorithms)||!Array.isArray(value.genres)||value.genres.length>6)throw Error(body?.error||'Saved analysis is invalid.');
 return value;
}
export async function localJob(action,body,filename,onProgress=()=>{},options={}){
 const response=await fetch(`/api/local/${action}${filename?'?filename='+encodeURIComponent(filename)+(options.supervised?'&supervised=1':'')+(options.specialists?'&specialists=1':''):''}`,{method:'POST',headers:{'X-Resonant-Local':'1','Content-Type':action==='analyze'?'application/octet-stream':'application/json'},body:action==='analyze'?body:JSON.stringify(body)});
 let job;try{job=await response.json()}catch{throw Error('Restart the local player server to enable analysis and PlaylistIQ.');}
 if(!response.ok)throw Error(job.error||'The local service is unavailable.');
 for(;;){const r=await fetch('/api/local/jobs/'+encodeURIComponent(job.id),{cache:'no-store'});const state=await r.json();if(!r.ok||state.status==='failed')throw Error(state.error||'Local processing failed.');if(state.status==='complete')return state.result;onProgress(state.message);await new Promise(resolve=>setTimeout(resolve,1000));}
}
export function featureDetails(track){
 const f=track.features;if(!f)return '';
 const values=id=>f.algorithms?.find(a=>a.algorithm_id===id&&a.status!=='failed')?.values??{};
 const rhythm=values('rhythm'),key=values('key'),loud=values('loudness'),energy=values('emotion_music2emo').arousal_mean!=null?values('emotion_music2emo'):values('energy'),semantic=values('semantic_audio');
 const rows=[['Tempo',rhythm.bpm!=null?Number(rhythm.bpm).toFixed(1)+' BPM':null],['Reference key',key.standard_key?key.standard_key+' · '+key.camelot:null],['Loudness',loud.integrated_lufs!=null?loud.integrated_lufs+' LUFS':null],['Arousal',energy.arousal_mean!=null?Number(energy.arousal_mean).toFixed(2)+' / 9 (raw estimate)':null]];
 rows.push(['Valence',(energy.valence_mean??energy.valence_mean_deferred)!=null?Number(energy.valence_mean??energy.valence_mean_deferred).toFixed(2)+' / 9 (raw estimate)':null],['Key strength',Number.isFinite(key.strength)?key.strength.toFixed(3)+' (uncalibrated)':null]);
 if(rhythm.tempo_candidates_bpm)rows.push(['Tempo hypotheses',rhythm.tempo_candidates_bpm.map(x=>x.toFixed(1)).join(' / ')+' BPM; half/double-time alternatives, not confirmed tempi']);
 if(semantic.segments?.length){rows.push(['Semantic coverage',`${semantic.sampled_seconds?.toFixed(1)} seconds sampled across ${semantic.segments.length} windows; ${semantic.duration_s?.toFixed(1)} seconds total`]);rows.push(['Character bank',`${semantic.descriptor_bank_version??'legacy'} · ${Object.keys(semantic.descriptors??{}).length} descriptions`]);for(const [label,v] of Object.entries(semantic.descriptors??{}).sort((a,b)=>b[1].mean-a[1].mean))rows.push(['Character / '+(v.dimension?v.dimension.replaceAll('_',' ')+' / ':'')+(v.label??label),`${v.mean.toFixed(3)} cosine (range ${v.min.toFixed(3)}–${v.max.toFixed(3)}); not a probability`]);}
 for(const stage of ['emotion_music2emo','danceability_musicnn']){const v=values(stage);if(v.segments?.length){rows.push([stage+' / coverage',`${v.sampled_seconds.toFixed(1)} / ${v.duration_s.toFixed(1)} seconds (${(100*v.coverage_fraction).toFixed(1)}%); ${stage==='emotion_music2emo'?'selected':'experimental'}`],['Estimator identity',v.model_id]);if(v.valence_mean!=null)rows.push(['Music2Emo valence',v.valence_mean.toFixed(3)+' raw / 9'],['Music2Emo arousal',v.arousal_mean.toFixed(3)+' raw / 9']);for(const [label,score] of Object.entries(v.scores??{}))rows.push([stage+' / '+label,(score*100).toFixed(2)+' / 100 support']);for(const seg of v.segments)rows.push([stage+' / excerpt',`${seg.start_s.toFixed(1)}–${seg.end_s.toFixed(1)} s; ${seg.valence!=null?'valence '+seg.valence.toFixed(3)+', arousal '+seg.arousal.toFixed(3):'danceable '+(100*seg.scores.danceable).toFixed(2)+' / 100 support'}`]);}}
 for(const stage of ['vocal_musicnn','aggression_vggish','instrument_passt']){const v=values(stage);if(v.segments?.length){rows.push([stage+' / coverage',`${v.sampled_seconds.toFixed(1)} / ${v.duration_s.toFixed(1)} seconds sampled`],['Estimator identity',v.model_id]);for(const [label,score] of Object.entries(v.scores??{}))rows.push([stage+' / '+label,(score*100).toFixed(2)+' / 100 support']);}}
 const expertKey=values('key_sheetsage2');if(expertKey.standard_key){rows.push(['SheetSage2 key',expertKey.standard_key],['Key estimator identity',expertKey.model_id]);for(const [start,end,key] of expertKey.key_intervals??[])rows.push(['Key interval',`${start.toFixed(1)}–${end.toFixed(1)} s: ${key}`]);}
 for(const [name,head] of Object.entries(values('semantic').heads??{}))for(const [label,score] of Object.entries(head.scores??{}))rows.push([name+' / '+label,(Number(score)*100).toFixed(1)+' / 100 model support']);
 return `<details class="evidence"><summary>Audio features</summary><p>Genre matching uses the six ranked MAEST candidates. Tempo, key and classifier scores are estimates. Voice support is not the percentage of time with vocals. Theme tags are not all emotions; semantic cosines are not probabilities.</p>${rows.filter(r=>r[1]!=null).map(([label,value])=>`<div class="evidence-item"><strong>${esc(label)}</strong><span>${esc(value)}</span></div>`).join('')}<p>All 519 genre probabilities are retained. No listening-review overrides are applied.</p></details>`;
}

export function featureTable(tracks){
 const columns=['Track','Analysis','Genres · top six','BPM','Key · selected','LUFS','Arousal','Happy','Sad','Relaxed','Aggressive · reference','Danceable','Vocal · selected','Instrumental · selected','Valence','Mood / themes · EffNet','Instruments','Musical character','Mood / themes · Music2Emo','MusiCNN dance · experimental','Selected specialists','Missing features'];
 const number=(v,suffix='')=>Number.isFinite(v)?v.toFixed(1)+suffix:'—';
 const percent=v=>Number.isFinite(v)?(v*100).toFixed(1)+'%':'—';
 return `<table class="feature-table"><thead><tr>${columns.map(c=>`<th scope="col">${c}</th>`).join('')}</tr></thead><tbody>${tracks.map(t=>{
  const f=t.features,values=id=>f?.algorithms?.find(a=>a.algorithm_id===id&&a.status!=='failed')?.values??{};
  const heads=values('semantic').heads??{},score=(h,l)=>percent(heads[h]?.scores?.[l]);
  const genres=(f?.genres??[]).map(g=>`${esc(g.genre.replace('---',' / '))} <span class="muted">${percent(g.probability)}</span>`).join('<br>');
  const topHead=name=>Object.entries(heads[name]?.scores??{}).sort((a,b)=>b[1]-a[1]).slice(0,4).map(([label,v])=>`${esc(label)} ${percent(v)} support`).join('<br>')||'—';
  const character=characterSummary(values('semantic_audio'));
  const failed=f?.algorithms?.filter(a=>a.status==='failed').map(a=>a.algorithm_id+': '+(a.error||'Unavailable')).join('; ');
  const cells=[f?.status==='complete'?'Analyzed':f?'Partial':'Not analyzed',genres||'—',number(values('rhythm').bpm),esc(values('key_sheetsage2').standard_key??values('key').standard_key??'—')+(values('key_sheetsage2').standard_key?' <small>SheetSage2</small>':''),number(values('loudness').integrated_lufs),number(values('emotion_music2emo').arousal_mean??values('energy').arousal_mean,' / 9'),...['happy','sad','relaxed','aggressive'].map(m=>score('mood_'+m,m)),score('danceability','danceable'),...['voice','instrumental'].map(k=>values('vocal_musicnn').scores?.[k]!=null?percent(values('vocal_musicnn').scores[k])+' <small>MusiCNN</small>':score('vocal_profile',k)),number(values('emotion_music2emo').valence_mean??values('energy').valence_mean??values('energy').valence_mean_deferred,' / 9'),topHead('mood_theme'),topHead('instruments'),character,supervisedSummary(values('emotion_music2emo')),supervisedSummary(values('danceability_musicnn')),['vocal_musicnn','aggression_vggish','instrument_passt'].map(stage=>{const v=values(stage);return v.scores?esc(stage)+': '+Object.entries(v.scores).sort((a,b)=>b[1]-a[1]).slice(0,3).map(([k,x])=>esc(k)+' '+percent(x)+' support').join(', '):'';}).filter(Boolean).concat(values('key_sheetsage2').standard_key?['SheetSage2: '+esc(values('key_sheetsage2').standard_key)]:[]).join('<br>')||'Not run',esc(failed||f?.upgrade_failures?.map(x=>x.algorithm_id+': '+x.error).join('; ')||'—')];
  return `<tr data-track-id="${esc(t.id)}"><th scope="row"><button class="track-title" data-action="play-track" data-id="${esc(t.id)}">${esc(t.title)}</button><button class="text-button" data-action="track-options" data-id="${esc(t.id)}">Details</button></th>${cells.map(c=>`<td>${c}</td>`).join('')}</tr>`;
 }).join('')}</tbody></table>`;
}

export function supervisedSummary(v){
 if(!v?.segments?.length)return 'Not compared';
 const coverage=`${v.sampled_seconds.toFixed(0)} seconds analyzed · ${(100*v.coverage_fraction).toFixed(0)}% sampled`;
 if(v.kind==='music2emo')return `V ${v.valence_mean.toFixed(2)} / A ${v.arousal_mean.toFixed(2)} · raw 1–9<br>${coverage}<br>${Object.entries(v.scores).sort((a,b)=>b[1]-a[1]).slice(0,3).map(([k,x])=>esc(k)+' '+(100*x).toFixed(1)+' / 100 support').join('<br>')}`;
 return `${(100*v.scores.danceable).toFixed(1)} / 100 support<br>${coverage}`;
}


export function characterSummary(semantic){
 const entries=Object.entries(semantic.descriptors??{}).sort((a,b)=>b[1].mean-a[1].mean);
 if(!entries.length)return 'Analysis needed';
 const describe=([id,v])=>`${esc(v.label??id)} ${Number(v.mean).toFixed(3)} cosine`;
 if(!entries.some(([,v])=>v.dimension))return entries.slice(0,4).map(describe).join('<br>')+'<br><small>Previous bank · refresh available</small>';
 const dimensions=[['emotion','Emotion'],['groove','Groove'],['texture','Texture'],['intensity','Intensity'],['space_arrangement','Arrangement']];
 return dimensions.map(([id,label])=>{
  const top=entries.filter(([,v])=>v.dimension===id).slice(0,2);
  return top.length?`<strong>${label}</strong>: ${top.map(describe).join('; ')}`:'';
 }).filter(Boolean).join('<br>')+'<br><small>Strongest relative matches · 120 descriptions; uncalibrated</small>';
}
