import {escapeHTML as esc} from './model.js';
export const reviewPrompts=[
 ['Sparse','House.','Does one word produce a useful interpretation without inventing extra constraints?'],
 ['Simple','Give me 8 house tracks.','Check requested count and genre relevance; fewer is valid if the catalog cannot supply eight.'],
 ['Broad genre','Give me 6 rock tracks.','Check broad rock coverage across subgenres.'],
 ['Mood only','Something relaxed and happy for a slow Sunday afternoon.','Check whether mood stays a preference and the context is interpreted sensibly.'],
 ['Hard bounds','Give me 8 house tracks between 120 and 128 BPM.','Every returned tempo should respect the bounds; inspect empty or short results.'],
 ['Several preferences','Give me 6 reggaeton tracks, preferably energetic and danceable.','Check genre eligibility separately from the strength of energy/danceability ranking.'],
 ['Negative constraint','Give me 6 house tracks, but no techno.','Check exclusion handling and explanations; unknown negative evidence may legitimately restrict results.'],
 ['Casual Spanish','Ponme unas 8 canciones de reggaetón para bailar, alegres pero no demasiado agresivas.','Check language, quantity, mood and negative preference interpretation.'],
 ['Contradictory','Give me 10 tracks that are below 100 BPM and above 130 BPM at the same time.','Should explain the contradiction or ask for clarification, never silently ignore one bound.'],
 ['Out of scope','Make a 30-minute journey from ambient into peak-time techno, with smooth harmonic transitions and no repeated artists.','Check honest handling of duration, sequencing, harmonic mixing and artist-diversity requests that are not fully supported.']
,['Picnic','Playlist for a picnic with my girlfriend.','Soft relaxed context; no invented genre, BPM or personal taste.']
 ,['Night party','Playlist for my birthday party in the night to make the room dance.','Prioritize danceability and energy, without invented BPM bounds.']
 ,['Heartbreak','Heartbroken music after a breakup.','Sad acoustic mood; do not promise breakup lyrics.']
 ,['Recipient','Music for my mom.','Ask one useful taste/mood question; no demographic stereotype.']
 ,['Alternatives','Give me 8 rock or pop tracks.','One OR genre group, not both genres required on each track.']
 ,['Lower intensity','Something relaxed, less aggressive, for reading.','Decrease aggression; unknown evidence must not count as low aggression.']
 ,['Lyrics','Only songs with lyrics about breaking up.','Unsupported explicit lyric requirement blocks retrieval.']
 ,['Spanish context','Música para un picnic tranquilo con mi novia.','A soft contextual interpretation in Spanish.']
 ,['Explicit ordering','Give me 5 house tracks from 120 to 130 BPM, ordered by increasing BPM.','Preserve genre, count, bounds and requested tempo ordering.']
 ,['Optional unknown','Relaxed music, preferably familiar favorites.','Disclose missing familiarity evidence; a supported draft may still be offered.']
,['Calm beach','Un día en la playa, tranquilo y con una sensación de aire libre.','Separate calmness and scene fit; compare the same candidate set across profiles.']
 ,['Energetic beach','Música alegre y movida para una fiesta en la playa.','Beach is not always calm; evaluate arousal, movement and suitability separately.']
 ,['Intimate evening','Música para una noche íntima y romántica en el sofá después de una cita.','Quiet intimacy is not guaranteed by low arousal alone.']
 ,['Celebration','Joyful music for a celebration with friends.','Joy and communal celebration do not automatically mean maximum danceability.']
].map(([kind,prompt,check],i)=>({id:`P${String(i+1).padStart(2,'0')}`,kind,prompt,check}));
const key='resonant:playlist-review-v1';
let session;
function state(){
 if(!session){try{const value=JSON.parse(localStorage.getItem(key)||'null');session=value?.version===1&&Array.isArray(value.attempts)?value:null;}catch{}session??={version:1,attempts:[]};}
 return session;
}
function persist(){try{localStorage.setItem(key,JSON.stringify(state()));return true;}catch{return false;}}
export function recordReviewAttempt({prompt,clarifications=[],run,error,candidates,elapsedMs,estimatorProfile='reference',candidateScope='all'}){
 const entry={id:crypto.randomUUID(),at:new Date().toISOString(),benchmarkVersion:'playlistiq-iteration1-v1',estimatorProfile,candidateScope,clarifications,testId:reviewPrompts.find(p=>p.prompt===prompt)?.id??'custom',prompt,elapsedMs,catalog:candidates.map(t=>({id:t.id,sha256:t.features.sha256,title:t.title,artist:t.artist})),run:run??null,error:error??null,verdict:'',notes:''};
 state().attempts.push(entry);return {entry,saved:persist()};
}
export function mountPlaylistReview(root,textarea,{onOpen}={}){
 const data=state();
 root.innerHTML=`<details class="iq-review"><summary>PlaylistIQ listening lab <span>${reviewPrompts.length} prompt tests · ${data.attempts.filter(a=>a.verdict).length} reviewed attempts</span></summary><p>Load a prompt, then press Find tracks. Each attempt keeps its query, candidates, result and timing. Listen through a saved playlist and record what fits, what does not, and what is missing.</p><div class="review-prompts">${reviewPrompts.map(p=>`<article><span>${p.id} / ${esc(p.kind)}</span><p>${esc(p.prompt)}</p><small>${esc(p.check)}</small><button class="button secondary" type="button" data-review-prompt="${p.id}" ${textarea.disabled?'disabled':''}>Use prompt</button></article>`).join('')}</div><h3>Review notebook</h3><p>Repeated tests are kept separately. Notes save in this browser; export them for our milestone review.</p><div class="review-attempts">${data.attempts.map(a=>`<details><summary>${esc(a.testId)} · ${esc(a.prompt)} · ${a.error?'Error':`${a.run?.result?.matches?.length??0} matches`}</summary>${a.run&&onOpen?`<button type="button" class="button secondary" data-review-open="${esc(a.id)}">View these results</button>`:''}<label>Verdict<select data-review-id="${esc(a.id)}" data-field="verdict">${[['','Not reviewed'],['good','Good'],['mixed','Mixed'],['poor','Poor'],['expected-limit','Expected limitation']].map(([v,l])=>`<option value="${v}" ${a.verdict===v?'selected':''}>${l}</option>`).join('')}</select></label><label>Listening notes<textarea data-review-id="${esc(a.id)}" data-field="notes" placeholder="Which tracks fit or miss? What did you expect? Was the interpretation right?">${esc(a.notes)}</textarea></label><details><summary>Captured result and interpretation</summary><pre>${esc(JSON.stringify(a.error??a.run,null,2))}</pre></details></details>`).join('')||'<p>No attempts recorded yet.</p>'}</div><p class="review-save-status" role="status"></p><button class="button secondary" type="button" data-review-export>Export review JSON</button><div class="review-export"></div></details>`;
 root.querySelectorAll('[data-review-open]').forEach(b=>b.onclick=()=>{const attempt=data.attempts.find(a=>a.id===b.dataset.reviewOpen);if(attempt?.run&&!textarea.disabled)onOpen(attempt);});
 root.querySelectorAll('[data-review-prompt]').forEach(b=>b.onclick=()=>{if(textarea.disabled)return;textarea.value=reviewPrompts.find(p=>p.id===b.dataset.reviewPrompt).prompt;textarea.dispatchEvent(new Event('input',{bubbles:true}));textarea.focus();});
 root.querySelectorAll('[data-review-id]').forEach(el=>el.oninput=()=>{const a=data.attempts.find(a=>a.id===el.dataset.reviewId);a[el.dataset.field]=el.value;root.querySelector('.review-save-status').textContent=persist()?'Saved in this browser.':'Browser storage is full or unavailable. Export now to preserve this session.';});
 let url;
 root.querySelector('[data-review-export]').onclick=()=>{
  if(url)URL.revokeObjectURL(url);
  const json=JSON.stringify({...data,exportedAt:new Date().toISOString(),testSuite:reviewPrompts},null,2);
  url=URL.createObjectURL(new Blob([json],{type:'application/json'}));
  root.querySelector('.review-export').innerHTML=`<p>Your file is ready. Click Download JSON. If downloading fails, copy the complete text below.</p><a class="button primary" download="playlistiq-iteration1-review.json" href="${url}">Download JSON</a><textarea readonly aria-label="Review JSON">${esc(json)}</textarea>`;
 };
}
