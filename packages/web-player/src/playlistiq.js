import {mountEstimatorMenu} from './estimator-menu.js';
import {promptSnapshot} from './prompt-snapshot.js';
import {sessionPromptPlaceholder} from './discovery.js';
import {webIntentHTML,jobQuip} from './web-presentation.js';
import {canonicalAudioHash} from './recording-identity.js';
import {matchExplanationHTML} from './match-explanation.js';
import {escapeHTML as esc,uniqueAudioTracks,audioIdentity} from './model.js';
import {mountPlaylistReview,recordReviewAttempt} from './playlist-review.js';

// Keep a draft while navigating between the library and PlaylistIQ in this session.
const draft={prompt:'',clarifications:[],run:null,busy:false,status:'',estimatorProfile:'quality',candidateScope:'all'};
let refreshCurrent=()=>{};
export function setPlaylistIQPrompt(prompt){if(draft.busy)return false;draft.prompt=prompt;draft.run=null;draft.clarifications=[];draft.status='';return true;}
export function uniqueMatches(matches,tracks=[]){
 const byId=new Map(tracks.map(t=>[t.id,t])),byHash=new Map(tracks.map(t=>[audioIdentity(t),t])),seen=new Set(),result=[];
 for(const match of matches){
  const id=match.track.track_id,track=byId.get(id)||byHash.get(canonicalAudioHash(id)),key=track?audioIdentity(track)||id:canonicalAudioHash(id);
  if(seen.has(key))continue;seen.add(key);
  result.push(track&&track.id!==id?{...match,track:{...match.track,track_id:track.id}}:match);
 }
 return result;
}
export async function playPlaylistMatch(player,tracks,matches,id,context=null){
 const queue=uniqueMatches(matches,tracks).map(m=>tracks.find(t=>t.id===m.track.track_id)).filter(t=>t?.status==='ready');
 const index=queue.findIndex(t=>t.id===id);
 if(index<0)throw Error('This track is no longer available. Find tracks again to refresh the results.');
 await player.setQueue(queue,index,context);
}
export function intentHTML(run){
 const plan=run.translation?.plan,matches=uniqueMatches(run.result?.matches??[]);
 const warnings=[...(run.translation?.unresolved??[]),...(run.warnings??[]),...(run.result?.warnings??[])];
 return `<div class="iq-result-heading"><h2>${run.status==='needs_clarification'?'One detail before we start':run.status==='unsupported'?'This request needs a change':`${matches.length} matching tracks`}</h2>${matches.length?'<button data-iq-save class="button primary">Save playlist</button>':''}</div>
 ${run.status==='partial_support'?'<p class="muted">Draft with limited evidence. Review the limitations below.</p>':''}
 ${plan?`<p class="iq-interpretation">${esc(plan.interpretation)}</p>${plan.assumptions.length?`<details><summary>Musical assumptions</summary><ul>${plan.assumptions.map(a=>`<li>${esc(a)}</li>`).join('')}</ul></details>`:''}`:''}
 ${run.status==='needs_clarification'&&plan?.clarification?`<form data-iq-clarification><label for="playlistiq-answer">${esc(plan.clarification)}</label><textarea id="playlistiq-answer" class="text-input" maxlength="1000" required></textarea><button class="button primary" type="submit">Continue</button></form>`:''}
 ${warnings.length?`<details><summary>Evidence and limitations</summary><ul>${[...new Set(warnings)].map(w=>`<li>${esc(w)}</li>`).join('')}</ul></details>`:''}
 <ol class="iq-matches">${matches.map((m,index)=>`<li><button type="button" class="button secondary iq-play" data-iq-play="${esc(m.track.track_id)}" aria-label="Play ${esc(m.track.title)}">▶ Play</button><strong>${esc(m.track.title)}</strong> <span>${esc(m.track.artist??'')}</span><details><summary>Why this track · ${(m.score*100).toFixed(2)} / 100</summary>${matchExplanationHTML(m,run,index)}</details></li>`).join('')}</ol>
 <details><summary>Plan, structured query and score evidence</summary><pre>${esc(JSON.stringify({plan:plan??null,proposed_plan:run.translation?.proposed_plan,prompt_version:run.translation?.prompt_version,prompt_digest:run.translation?.prompt_digest,reasoning_effort:run.translation?.reasoning_effort,query:run.translation?.query,ranking:run.result?.ranking_version,compiler:run.translation?.compiler_version,clarifications:run.translation?.clarifications,matches:matches.map(m=>({id:m.track.track_id,score:m.score,contributions:m.score_contributions}))},null,2))}</pre></details>`;
}
export function mountPlaylistIQ(root,{candidates,total,localJob,onSave,onPlay,notice=()=>{},webEdition=false,onRecordPrompt=()=>{},onHistory=()=>{},onStats=()=>{}}){
 candidates=uniqueAudioTracks(candidates);
 if(webEdition)draft.candidateScope='all';
 root.innerHTML=`<section class="playlistiq-page ${webEdition?'iq-web':''}">${webEdition?'':`<div class="iq-count">${candidates.length} / ${total} tracks analyzed</div>`}<form id="playlistiq-form"><label for="playlistiq-text">What do you want to hear?</label><textarea id="playlistiq-text" class="text-input" maxlength="4000" required placeholder="${esc(webEdition?sessionPromptPlaceholder():'A picnic with my girlfriend, or a birthday party that gets the room dancing')}">${esc(draft.prompt)}</textarea>${webEdition?'<p class="iq-invitation">Or surprise us. We’ve heard worse.</p>':''}${webEdition?'':`<label for="estimator-scope">Candidate set<select id="estimator-scope"><option value="all">All analyzed tracks</option><option value="quality">Specialist tracks only (${candidates.filter(t=>t.features?.quality_status==='complete').length})</option><option value="compared">Compared tracks only (${candidates.filter(t=>t.features?.supervised_status==='complete').length})</option></select></label>`}${webEdition?'<details class="iq-estimator"><summary>Estimators</summary>':''}<label for="estimator-profile">Feature estimators<select id="estimator-profile"><option value="reference">Reference · previous pipeline</option><option value="music2emo">Music2Emo · mood comparison</option><option value="musicnn-dance">MusiCNN · experimental danceability</option><option value="supervised">Both challengers · experimental</option><option value="quality">Quality-selected specialists · default</option></select></label>${webEdition?'</details>':''}${webEdition?'':`<p class="muted">Selected estimates need compatible coverage for every candidate. ${webEdition?'This shared library is analyzed locally by its owner.':'Analyze Tracks runs the selected pipeline; Details also offers an optional danceability comparison.'} Incomplete coverage retains available reference evidence for everyone.</p>`}<div class="iq-submit"><button class="button primary" type="submit">Find tracks</button><span id="playlistiq-status" role="status"></span></div></form><div id="playlistiq-results"></div>${webEdition?'':'<div id="playlist-review"></div>'}</section>`;
 if(webEdition){const settings=mountEstimatorMenu(root.querySelector('.iq-estimator')),links=document.createElement('footer');links.className='profile-links';links.innerHTML='<button type="button" data-history>Your prompts</button><button type="button" data-stats>Listening habits</button>';links.querySelector('[data-history]').onclick=onHistory;links.querySelector('[data-stats]').onclick=onStats;links.append(settings);root.querySelector('.iq-web').append(links);}

 const text=root.querySelector('#playlistiq-text'),result=root.querySelector('#playlistiq-results'),status=root.querySelector('#playlistiq-status');
 const selectedCandidates=()=>draft.candidateScope==='quality'?candidates.filter(t=>t.features?.quality_status==='complete'):draft.candidateScope==='compared'?candidates.filter(t=>t.features?.supervised_status==='complete'):candidates;
 const render=()=>{
  if(!root.isConnected)return;
  text.disabled=draft.busy;const scope=root.querySelector('#estimator-scope');if(scope){scope.disabled=draft.busy;scope.value=draft.candidateScope;}root.querySelector('#estimator-profile').disabled=draft.busy;root.querySelector('#estimator-profile').value=draft.estimatorProfile;
  root.querySelector('#playlistiq-form button').disabled=draft.busy||!selectedCandidates().length;
  status.textContent=webEdition&&draft.busy?jobQuip(draft.status):draft.status;
  const run=draft.run?.result?{...draft.run,result:{...draft.run.result,matches:uniqueMatches(draft.run.result.matches,candidates)}}:draft.run;
  result.innerHTML=run?(webEdition?webIntentHTML(run):intentHTML(run)):'';
  const save=result.querySelector('[data-iq-save]');if(save)save.onclick=()=>onSave(draft.prompt,run.result.matches,run);
  for(const play of result.querySelectorAll('[data-iq-play]')){play.disabled=typeof onPlay!=='function';play.onclick=()=>Promise.resolve().then(()=>onPlay(play.dataset.iqPlay,run.result.matches,run)).catch(error=>notice(error.message,true));}
  const clarification=result.querySelector('[data-iq-clarification]');
  if(clarification){clarification.querySelector('button').disabled=draft.busy;clarification.onsubmit=e=>{e.preventDefault();const answer=clarification.querySelector('textarea').value.trim();if(answer)void submit([...draft.clarifications,{question:draft.run.translation.plan.clarification,answer}]);};}
 };
 const review=()=>!webEdition&&mountPlaylistReview(root.querySelector('#playlist-review'),text,{onOpen:attempt=>{
  if(draft.busy)return;
  draft.prompt=attempt.prompt;draft.run=attempt.run;draft.estimatorProfile=attempt.estimatorProfile??'reference';draft.candidateScope=attempt.candidateScope??'all';draft.clarifications=attempt.clarifications??[];draft.status='Showing saved results; no new playlist request was sent.';
  text.value=draft.prompt;render();result.scrollIntoView({block:'start',behavior:'smooth'});
 }});
 async function submit(answers){
  if(draft.busy)return;
  const prompt=text.value.trim();if(!prompt)return;
  const requestId=crypto.randomUUID(),requestAt=Date.now(),record={requestId,requestAt,prompt,clarifications:answers,estimatorProfile:draft.estimatorProfile};
  try{if(webEdition)onRecordPrompt({...record,status:'requested',trackIds:[]});}catch(e){notice(e.message,true);return;}
  draft.prompt=prompt;draft.busy=true;draft.status='Interpreting your playlist request…';render();
  const started=performance.now();
  try{
   const run=await localJob('playlist',{prompt,clarifications:answers,estimator_profile:draft.estimatorProfile,tracks:selectedCandidates().map(t=>({id:t.id,sha256:t.features.sha256,title:t.title,artist:t.artist??''}))},null,message=>{draft.status=message;refreshCurrent();});
   draft.run={...run,userRequestId:requestId};draft.clarifications=answers;draft.status='';
   if(webEdition)try{onRecordPrompt({...record,status:['needs_clarification','unsupported','partial_support'].includes(run.status)?run.status:'complete',trackIds:uniqueMatches(run.result?.matches??[],candidates).map(m=>m.track.track_id),elapsedMs:Math.round(performance.now()-started),snapshot:promptSnapshot(run,uniqueMatches(run.result?.matches??[],candidates))});}catch(e){notice(e.message,true);}
   const recorded=recordReviewAttempt({prompt,clarifications:answers,run,candidates:selectedCandidates(),candidateScope:draft.candidateScope,estimatorProfile:draft.estimatorProfile,elapsedMs:Math.round(performance.now()-started)});
   if(!recorded.saved)notice('Review is held in memory. Export it to preserve this session.',true);
  }catch(error){draft.status=error.message;if(webEdition)try{onRecordPrompt({...record,status:'failed',trackIds:[],error:error.message,elapsedMs:Math.round(performance.now()-started)});}catch(e){notice(e.message,true);}recordReviewAttempt({prompt,clarifications:answers,error:error.message,candidates:selectedCandidates(),candidateScope:draft.candidateScope,estimatorProfile:draft.estimatorProfile,elapsedMs:Math.round(performance.now()-started)});}
  finally{draft.busy=false;refreshCurrent();}
 }
 if(root.querySelector('#estimator-scope'))root.querySelector('#estimator-scope').onchange=e=>{draft.candidateScope=e.target.value;draft.run=null;draft.status='';render();};
 root.querySelector('#estimator-profile').onchange=e=>{draft.estimatorProfile=e.target.value;draft.run=null;draft.status='';render();};
 text.oninput=()=>{draft.prompt=text.value;draft.run=null;draft.clarifications=[];draft.status='';render();};
 root.querySelector('#playlistiq-form').onsubmit=e=>{e.preventDefault();draft.run=null;draft.clarifications=[];void submit([]);};
 refreshCurrent=()=>{if(text.isConnected){render();review();}};
 refreshCurrent();
}
