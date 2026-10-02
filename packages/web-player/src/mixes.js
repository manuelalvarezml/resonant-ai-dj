import {escapeHTML as esc,formatTime} from './model.js';
import {canStreamMix,streamMix} from './mix-stream.js';
let currentId=null,disposeCurrent=null;
const terminal=job=>['complete','failed','cancelled'].includes(job.status);
async function api(path='',options={}){const response=await fetch('/api/mixes'+path,{...options,headers:{'Content-Type':'application/json','X-Resonant-Local':'1',...options.headers}});const value=await response.json();if(!response.ok)throw Error(value.error||'Mix request failed');return value;}
export function disposeMixes(){disposeCurrent?.();disposeCurrent=null;}
export function mountMixes(root,{pauseMain=()=>{},mainAudio}={}){
 disposeMixes();let closed=false,pollTimer,stopStream=null,playingId=null,lastJob=null,startedAt=0;
 root.innerHTML=`<section class="mix-workspace"><p>Render a saved DJ mix and listen while it is being prepared. Your original audio stays on this Mac.</p>
 <form id="mix-form"><label for="mix-plan">Mix plan</label><select id="mix-plan"><option>Loading saved plans…</option></select><button class="button primary" id="mix-render" type="submit">Render mix</button></form>
 <details><summary>Use a custom manual plan</summary><p>Choose a MixPlan JSON referencing tracks in the existing DJ analysis collection.</p><input id="mix-import" type="file" accept=".json,application/json" aria-label="Import a manual mix plan"></details>
 <p id="mix-status" role="status" aria-live="polite">Loading…</p><div class="mix-controls"><button class="button secondary" id="mix-preview" disabled>Listen now</button><button class="button secondary" id="mix-cancel" hidden>Cancel render</button></div>
 <audio id="mix-audio" hidden controls preload="metadata" aria-label="DJ mix playback"></audio><p id="mix-playback-status" role="status"></p><div id="mix-downloads"></div><p id="mix-timing" class="muted"></p>
 <h3>Recent mixes</h3><div id="mix-recent"></div></section>`;
 const $=s=>root.querySelector(s),audio=$('#mix-audio');
 const stop=()=>{stopStream?.();stopStream=null;audio.pause();audio.removeAttribute('src');audio.load();playingId=null;};
 const pauseMix=()=>audio.pause();mainAudio?.addEventListener('play',pauseMix);
 disposeCurrent=()=>{closed=true;clearTimeout(pollTimer);mainAudio?.removeEventListener('play',pauseMix);stop();};
 audio.addEventListener('play',pauseMain);
 audio.addEventListener('playing',()=>{$('#mix-playback-status').textContent='Playing';if(startedAt){$('#mix-timing').textContent+=` · Browser start ${(performance.now()-startedAt).toFixed(0)} ms`;startedAt=0;}});
 audio.addEventListener('pause',()=>{$('#mix-playback-status').textContent='Paused';});
 audio.addEventListener('ended',()=>{$('#mix-playback-status').textContent='Finished';});
 audio.addEventListener('waiting',()=>{$('#mix-playback-status').textContent='Buffering…';});
 audio.addEventListener('seeking',()=>{
  if(lastJob?.status!=='complete'||!stopStream)return;
  const position=audio.currentTime;
  for(let i=0;i<audio.buffered.length;i++)if(position>=audio.buffered.start(i)&&position<audio.buffered.end(i))return;
  const wanted=!audio.paused,endStream=stopStream;stopStream=null;
  setTimeout(()=>{if(closed)return;endStream();audio.src=`/api/mixes/${lastJob.id}/audio`;
  audio.addEventListener('loadedmetadata',()=>{audio.currentTime=Math.min(position,audio.duration);if(wanted)void audio.play().catch(()=>{});},{once:true});audio.load();},0);
 });
 audio.addEventListener('error',()=>{$('#mix-playback-status').textContent='Could not play this mix. Use Listen now to retry.';playingId=null;});
 function show(job){
  lastJob=job;$('#mix-status').textContent=job.error||job.message||(job.status==='complete'?'Mix and listening copy are ready.':job.status);
  $('#mix-render').disabled=!terminal(job);$('#mix-cancel').hidden=terminal(job);
  $('#mix-preview').disabled=!(job.status==='complete'||job.playable&&canStreamMix());
  if(job.playable&&!canStreamMix()&&job.status!=='complete')$('#mix-status').textContent+=' This browser can play the completed file when ready.';
  if(job.status==='failed'||job.status==='cancelled')stop();
  $('#mix-timing').textContent=[job.duration_s?`Mix ${formatTime(job.duration_s)}`:'',job.cache_hit?'Verified cache reused':'',job.first_fragment_s?`First stream data ${job.first_fragment_s.toFixed(2)} s`:'',job.render_wall_s?`Render ${job.render_wall_s.toFixed(2)} s`:'',job.request_wall_s?`With verification ${job.request_wall_s.toFixed(2)} s`:''].filter(Boolean).join(' · ');
  if(job.status==='complete'){
   $('#mix-downloads').innerHTML=`<a class="button secondary" href="/api/mixes/${job.id}/master" download="resonant-mix.wav">Download lossless mix</a> <a class="button secondary" href="/api/mixes/${job.id}/audio" download="resonant-mix.m4a">Download listening copy</a>`;

  }else $('#mix-downloads').innerHTML='';
 }
 async function poll(){if(closed||!currentId)return;try{const id=currentId,job=await api('/'+id);if(closed||id!==currentId)return;show(job);if(!terminal(job))pollTimer=setTimeout(poll,350);else void recent();}catch(e){if(!closed){$('#mix-status').textContent=e.message;$('#mix-render').disabled=false;}}}
 async function start(payload){stop();lastJob=null;$('#mix-preview').disabled=true;$('#mix-downloads').innerHTML='';$('#mix-timing').textContent='';clearTimeout(pollTimer);$('#mix-render').disabled=true;$('#mix-status').textContent='Checking the mix plan…';try{const value=await api('',{method:'POST',body:JSON.stringify(payload)});if(closed)return;currentId=value.id;void poll();}catch(e){if(!closed){$('#mix-status').textContent=e.message;$('#mix-render').disabled=false;}}}
 async function recent(){try{const data=await api();if(closed)return;$('#mix-recent').innerHTML=data.recent.map(j=>`<button class="button secondary" data-mix-id="${esc(j.id)}">${esc(j.plan_id)} · ${formatTime(j.duration_s)}</button>`).join('')||'<p class="muted">Your completed mixes will appear here.</p>';return data;}catch(e){if(!closed)$('#mix-status').textContent=e.message;}}
 $('#mix-form').addEventListener('submit',e=>{e.preventDefault();void start({planId:$('#mix-plan').value});});
 $('#mix-import').addEventListener('change',async e=>{const f=e.target.files?.[0];if(!f)return;try{if(f.size>1024*1024)throw Error('Plan must be smaller than 1 MB.');void start({plan:JSON.parse(await f.text())});}catch(error){$('#mix-status').textContent=error.message;}e.target.value='';});
 $('#mix-cancel').addEventListener('click',async()=>{try{show(await api('/'+currentId+'/cancel',{method:'POST'}));}catch(e){$('#mix-status').textContent=e.message;}});
 $('#mix-preview').addEventListener('click',()=>{
  const job=lastJob;if(!job)return;stop();pauseMain();playingId=job.id;audio.hidden=false;startedAt=performance.now();
  if(job.status==='complete'){audio.src=`/api/mixes/${job.id}/audio`;audio.load();void audio.play().catch(()=>{$('#mix-playback-status').textContent='Press Play in the audio controls.';});}
  else{stopStream=streamMix(audio,`/api/mixes/${job.id}/live`,{duration:job.duration_s,onReady:()=>{void audio.play().catch(()=>{$('#mix-playback-status').textContent='Press Play in the audio controls.';});},onError:e=>{$('#mix-playback-status').textContent=e.message+' Retry Listen now or wait for completion.';}});void audio.play().catch(()=>{});}
 });
 $('#mix-recent').addEventListener('click',e=>{const id=e.target.closest('[data-mix-id]')?.dataset.mixId;if(id){stop();clearTimeout(pollTimer);currentId=id;void poll();}});
 void (async()=>{const data=await recent();if(!data||closed)return;$('#mix-plan').innerHTML=data.plans.map(p=>`<option value="${esc(p.id)}" ${p.id.includes('v2')?'selected':''}>${esc(p.title)} · ${formatTime(p.duration_s)}</option>`).join('');if(!data.plans.length)$('#mix-render').disabled=true;if(data.active)currentId=data.active.id;if(currentId)void poll();else $('#mix-status').textContent='Choose a saved plan, then render your mix.';})();
}
