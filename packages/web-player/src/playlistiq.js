import {matchExplanationHTML} from './match-explanation.js';
import {escapeHTML as esc} from './model.js';
import {mountPlaylistReview,recordReviewAttempt} from './playlist-review.js';

// Keep a draft while navigating between the library and PlaylistIQ in this session.
const draft={prompt:'',clarifications:[],run:null,busy:false,status:'',estimatorProfile:'quality',candidateScope:'all'};
let refreshCurrent=()=>{};
export async function playPlaylistMatch(player,tracks,matches,id){
 const queue=matches.map(m=>tracks.find(t=>t.id===m.track.track_id)).filter(t=>t?.status==='ready');
 const index=queue.findIndex(t=>t.id===id);
 if(index<0)throw Error('This track is no longer available. Find tracks again to refresh the results.');
 await player.setQueue(queue,index);
}
export function intentHTML(run){
 const plan=run.translation?.plan,matches=run.result?.matches??[];
 const warnings=[...(run.translation?.unresolved??[]),...(run.warnings??[]),...(run.result?.warnings??[])];
 return `<div class="iq-result-heading"><h2>${run.status==='needs_clarification'?'One detail before we start':run.status==='unsupported'?'This request needs a change':`${matches.length} matching tracks`}</h2>${matches.length?'<button data-iq-save class="button primary">Save playlist</button>':''}</div>
 ${run.status==='partial_support'?'<p class="muted">Draft with limited evidence. Review the limitations below.</p>':''}
 ${plan?`<p class="iq-interpretation">${esc(plan.interpretation)}</p>${plan.assumptions.length?`<details><summary>Musical assumptions</summary><ul>${plan.assumptions.map(a=>`<li>${esc(a)}</li>`).join('')}</ul></details>`:''}`:''}
 ${run.status==='needs_clarification'&&plan?.clarification?`<form data-iq-clarification><label for="playlistiq-answer">${esc(plan.clarification)}</label><textarea id="playlistiq-answer" class="text-input" maxlength="1000" required></textarea><button class="button primary" type="submit">Continue</button></form>`:''}
 ${warnings.length?`<details><summary>Evidence and limitations</summary><ul>${[...new Set(warnings)].map(w=>`<li>${esc(w)}</li>`).join('')}</ul></details>`:''}
 <ol class="iq-matches">${matches.map((m,index)=>`<li><button type="button" class="button secondary iq-play" data-iq-play="${esc(m.track.track_id)}" aria-label="Play ${esc(m.track.title)}">▶ Play</button><strong>${esc(m.track.title)}</strong> <span>${esc(m.track.artist??'')}</span><details><summary>Why this track · ${(m.score*100).toFixed(2)} / 100</summary>${matchExplanationHTML(m,run,index)}</details></li>`).join('')}</ol>
 <details><summary>Plan, structured query and score evidence</summary><pre>${esc(JSON.stringify({plan:plan??null,proposed_plan:run.translation?.proposed_plan,prompt_version:run.translation?.prompt_version,prompt_digest:run.translation?.prompt_digest,reasoning_effort:run.translation?.reasoning_effort,query:run.translation?.query,ranking:run.result?.ranking_version,compiler:run.translation?.compiler_version,clarifications:run.translation?.clarifications,matches:matches.map(m=>({id:m.track.track_id,score:m.score,contributions:m.score_contributions}))},null,2))}</pre></details>`;
}
export function mountPlaylistIQ(root,{candidates,total,localJob,onSave,onPlay,notice=()=>{},webEdition=false}){
 root.innerHTML=`<section class="playlistiq-page"><div class="iq-count">${candidates.length} / ${total} tracks analyzed</div><form id="playlistiq-form"><label for="playlistiq-text">What do you want to hear?</label><textarea id="playlistiq-text" class="text-input" maxlength="4000" required placeholder="A picnic with my girlfriend, or a birthday party that gets the room dancing">${esc(draft.prompt)}</textarea><label for="estimator-scope">Candidate set<select id="estimator-scope"><option value="all">All analyzed tracks</option><option value="quality">Specialist tracks only (${candidates.filter(t=>t.features?.quality_status==='complete').length})</option><option value="compared">Compared tracks only (${candidates.filter(t=>t.features?.supervised_status==='complete').length})</option></select></label><label for="estimator-profile">Feature estimators<select id="estimator-profile"><option value="reference">Reference · previous pipeline</option><option value="music2emo">Music2Emo · mood comparison</option><option value="musicnn-dance">MusiCNN · experimental danceability</option><option value="supervised">Both challengers · experimental</option><option value="quality">Quality-selected specialists · default</option></select></label><p class="muted">Selected estimates need compatible coverage for every candidate. ${webEdition?'This shared library is analyzed locally by its owner.':'Analyze Tracks runs the selected pipeline; Details also offers an optional danceability comparison.'} Incomplete coverage retains available reference evidence for everyone.</p><div class="iq-submit"><button class="button primary" type="submit">Find tracks</button><span id="playlistiq-status" role="status"></span></div></form><div id="playlistiq-results"></div><div id="playlist-review"></div></section>`;
 const text=root.querySelector('#playlistiq-text'),result=root.querySelector('#playlistiq-results'),status=root.querySelector('#playlistiq-status');
 const selectedCandidates=()=>draft.candidateScope==='quality'?candidates.filter(t=>t.features?.quality_status==='complete'):draft.candidateScope==='compared'?candidates.filter(t=>t.features?.supervised_status==='complete'):candidates;
 const render=()=>{
  if(!root.isConnected)return;
  text.disabled=draft.busy;root.querySelector('#estimator-scope').disabled=draft.busy;root.querySelector('#estimator-scope').value=draft.candidateScope;root.querySelector('#estimator-profile').disabled=draft.busy;root.querySelector('#estimator-profile').value=draft.estimatorProfile;
  root.querySelector('#playlistiq-form button').disabled=draft.busy||!selectedCandidates().length;
  status.textContent=draft.status;
  result.innerHTML=draft.run?intentHTML(draft.run):'';
  const save=result.querySelector('[data-iq-save]');if(save)save.onclick=()=>onSave(draft.prompt,draft.run.result.matches);
  for(const play of result.querySelectorAll('[data-iq-play]')){play.disabled=typeof onPlay!=='function';play.onclick=()=>Promise.resolve().then(()=>onPlay(play.dataset.iqPlay,draft.run.result.matches)).catch(error=>notice(error.message,true));}
  const clarification=result.querySelector('[data-iq-clarification]');
  if(clarification){clarification.querySelector('button').disabled=draft.busy;clarification.onsubmit=e=>{e.preventDefault();const answer=clarification.querySelector('textarea').value.trim();if(answer)void submit([...draft.clarifications,{question:draft.run.translation.plan.clarification,answer}]);};}
 };
 const review=()=>mountPlaylistReview(root.querySelector('#playlist-review'),text,{onOpen:attempt=>{
  if(draft.busy)return;
  draft.prompt=attempt.prompt;draft.run=attempt.run;draft.estimatorProfile=attempt.estimatorProfile??'reference';draft.candidateScope=attempt.candidateScope??'all';draft.clarifications=attempt.clarifications??[];draft.status='Showing saved results; no new playlist request was sent.';
  text.value=draft.prompt;render();result.scrollIntoView({block:'start',behavior:'smooth'});
 }});
 async function submit(answers){
  if(draft.busy)return;
  const prompt=text.value.trim();if(!prompt)return;
  draft.prompt=prompt;draft.busy=true;draft.status='Interpreting your playlist request…';render();
  const started=performance.now();
  try{
   const run=await localJob('playlist',{prompt,clarifications:answers,estimator_profile:draft.estimatorProfile,tracks:selectedCandidates().map(t=>({id:t.id,sha256:t.features.sha256,title:t.title,artist:t.artist??''}))},null,message=>{draft.status=message;refreshCurrent();});
   draft.run=run;draft.clarifications=answers;draft.status='';
   const recorded=recordReviewAttempt({prompt,clarifications:answers,run,candidates:selectedCandidates(),candidateScope:draft.candidateScope,estimatorProfile:draft.estimatorProfile,elapsedMs:Math.round(performance.now()-started)});
   if(!recorded.saved)notice('Review is held in memory. Export it to preserve this session.',true);
  }catch(error){draft.status=error.message;recordReviewAttempt({prompt,clarifications:answers,error:error.message,candidates:selectedCandidates(),candidateScope:draft.candidateScope,estimatorProfile:draft.estimatorProfile,elapsedMs:Math.round(performance.now()-started)});}
  finally{draft.busy=false;refreshCurrent();}
 }
 root.querySelector('#estimator-scope').onchange=e=>{draft.candidateScope=e.target.value;draft.run=null;draft.status='';render();};
 root.querySelector('#estimator-profile').onchange=e=>{draft.estimatorProfile=e.target.value;draft.run=null;draft.status='';render();};
 text.oninput=()=>{draft.prompt=text.value;draft.run=null;draft.clarifications=[];draft.status='';render();};
 root.querySelector('#playlistiq-form').onsubmit=e=>{e.preventDefault();draft.run=null;draft.clarifications=[];void submit([]);};
 refreshCurrent=()=>{if(text.isConnected){render();review();}};
 refreshCurrent();
}
