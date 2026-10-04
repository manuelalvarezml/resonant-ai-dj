import {escapeHTML as esc} from './model.js';
import {descriptorName} from './match-explanation.js';
const pct=n=>Number.isFinite(n)?(n*100).toFixed(1):'—';
const values=(t,id)=>t.features?.algorithms?.find(a=>a.algorithm_id===id&&a.status!=='failed')?.values??{};
export function trackFacts(track){
 const bpm=values(track,'rhythm').bpm,key=values(track,'key_sheetsage2').standard_key??values(track,'key').standard_key;
 const character=Object.entries(values(track,'semantic_audio').descriptors??{}).filter(([,v])=>Number.isFinite(v.mean)).sort((a,b)=>b[1].mean-a[1].mean)[0];
 return [Number.isFinite(bpm)?`${Math.round(bpm)} BPM`:'Tempo unavailable',key||'Key unavailable',character?(character[1].label??character[0].replaceAll('_',' ')):'Character unavailable'];
}
export function trackCardHTML(track){
 return `<button class="web-track-card" data-action="play-track" data-id="${esc(track.id)}" aria-label="Play ${esc(track.title)}" ${track.status!=='ready'?'disabled':''}><strong class="track-title">${esc(track.title)}</strong><span class="track-artist">${esc(track.artist)}</span><span class="web-track-facts"><span class="web-genres">${(track.features?.genres??[]).slice(0,3).map(g=>`<span>${esc(g.genre.replace('---',' / '))}</span>`).join('')}</span><span class="web-measures">${trackFacts(track).map(v=>`<span>${esc(v)}</span>`).join('')}</span></span></button>`;
}
export function upcomingQueue(player){return player.queue.slice(Math.max(0,player.index)).map((track,n)=>({track,index:Math.max(0,player.index)+n,current:Math.max(0,player.index)+n===player.index}));}
export function queueHTML(player){return upcomingQueue(player).map(({track,index,current})=>`<div class="queue-item ${current?'active':''}"><button class="queue-track" data-action="queue-play" data-index="${index}" aria-label="${current?'Playing':'Play queued'} ${esc(track.title)}" ${current?'aria-current="true"':''}><span class="track-text"><strong>${esc(track.title)}</strong><span>${esc(track.artist)}</span></span></button></div>`).join('')||'<p class="muted">An empty queue. Very avant-garde.</p>';}
export function playbackQuip(player){
 if(player.status==='error')return `Plot twist: ${player.error}`;
 if(player.seeking||player.audio?.seeking)return '';
 if(player.status==='paused'&&!player.manualPause&&!player.interrupted)return '';
 if(player.interrupted)return 'Reality interrupted. Press Play to escape again.';
 return {loading:'Convincing the next track to make an entrance…',buffering:'A dramatic pause. Blame the connection.',ended:'The queue has left the building.',paused:'A moment of silence. By request.'}[player.status]??'';
}
export function jobQuip(message){
 if(!message)return '';
 if(/queue|waiting/i.test(message))return 'Your playlist is in line. No guest-list privileges.';
 if(/rank|match|scor/i.test(message))return 'Judging the tracks. Quietly, but thoroughly.';
 if(/load|warm|start/i.test(message))return 'Waking up the DJ. Apparently coffee takes a minute.';
 if(/interpret|plan|translat/i.test(message))return 'Turning your very specific vibe into music…';
 return 'Auditioning the library. Some tracks will take this personally.';
}
const contextRows=plan=>[['Occasion',plan?.occasion],['Activity',plan?.activity],['For',plan?.recipient],['Emotional aim',plan?.emotional_goal]].filter(([,v])=>typeof v==='string'&&v.trim());
const listRows=rows=>`<dl class="human-facts">${rows.map(([k,v])=>`<div><dt>${esc(k)}</dt><dd>${esc(v)}</dd></div>`).join('')}</dl>`;
const contributionName=c=>(c.tags??[]).map(t=>`${c.direction==='decrease'?'less emphasis on ':''}${descriptorName(t)}`).join(' or ')||'Musical character';
export function conciseMatchHTML(match,run){
 const plan=run.translation?.plan,contributions=(match.score_contributions??[]).filter(c=>Number.isFinite(c.contribution)).sort((a,b)=>b.contribution-a.contribution);
 const strongest=contributions.filter(c=>c.contribution>0).slice(0,2);
 const first=plan?.interpretation||'This track fits the musical preferences recorded for your request.';
 const second=strongest.length?`Its strongest matches are ${strongest.map(contributionName).join(' and ')}. These contribute ${pct(strongest.reduce((s,c)=>s+c.contribution,0))} points. The score describes musical fit, not a guarantee that the track suits your moment.`:'It passes the requested filters, but no weighted musical-fit breakdown is available. Give it a listen and judge the connection yourself.';
 return `<div class="human-match"><p>${esc(first)}</p><p>${esc(second)}</p>${listRows(contextRows(plan))}${contributions.length?`<table class="human-scores"><caption>How the score adds up</caption><thead><tr><th>Quality</th><th>Fit</th><th>Weight</th><th>Points</th></tr></thead><tbody>${contributions.map(c=>`<tr><td>${esc(contributionName(c))}${c.score_kind==='relative_similarity'?' <small>(relative match)</small>':''}</td><td>${pct(c.utility)}</td><td>${pct(c.weight)}%</td><td>${pct(c.contribution)}</td></tr>`).join('')}</tbody><tfoot><tr><th colspan="3">Total / 100</th><td>${pct(match.score)}</td></tr></tfoot></table>`:''}</div>`;
}
export function planSummaryRows(run){
 const query=run.result?.query??run.translation?.query??{},plan=run.translation?.plan;
 return [['Interpretation',plan?.interpretation],['Context',contextRows(plan).map(([key,value])=>`${key}: ${value}`).join(' · ')],['Musical character',query.semantic?.description??plan?.musical_description],['Required styles',(query.required_tags??[]).map(descriptorName).join(', ')],['Alternatives',(query.any_tag_groups??[]).map(g=>g.map(descriptorName).join(' or ')).join('; ')],['Preferences',(query.preferences??[]).map(p=>`${p.direction==='decrease'?'Less ':''}${descriptorName(p.tag)}`).join(', ')],['Tempo',query.min_bpm!=null||query.max_bpm!=null?`${query.min_bpm??'Any'}–${query.max_bpm??'any'} BPM`:null],['Avoid',[...(query.excluded_tags??[]).map(descriptorName),...(plan?.avoid_descriptions??[])].join(', ')],['Order',query.order?.startsWith('bpm')?(query.order==='bpm_ascending'?'Slowest first':'Fastest first'):'Best musical fit'],['Tracks',String(run.result?.matches?.length??0)]].filter(([,v])=>v!=null&&String(v).trim()).slice(0,10);
}
export function webIntentHTML(run){
 const matches=run.result?.matches??[],plan=run.translation?.plan;
 const warnings=[...(run.translation?.unresolved??[]),...(run.warnings??[]),...(run.result?.warnings??[])];
 // Technical diagnostics stay in the saved result; the listening UI gives their practical implication.
 const gaps=[...new Set((plan?.evidence_gaps??[]).map(g=>g.explanation).filter(Boolean))];
 const limits=warnings.some(w=>/no usable|incomplete|retained|missing|unsupported/i.test(w))?'Some requested qualities could not be judged consistently across the library. Available musical evidence was used; listen to check the fit.':'Musical qualities are estimates. A high match score does not guarantee the right track for your occasion.';
 return `<div class="iq-result-heading"><h2>${run.status==='needs_clarification'?'One detail before we start':run.status==='unsupported'?'This request needs a change':`${matches.length} matching tracks`}</h2>${matches.length?'<button data-iq-save class="button primary">Save playlist</button>':''}</div>${run.status==='partial_support'?'<p class="muted">Some preferences could only be partly assessed. See the limitations below.</p>':''}${plan?.interpretation?`<p class="iq-interpretation">${esc(plan.interpretation)}</p>`:''}${run.status==='needs_clarification'&&plan?.clarification?`<form data-iq-clarification><label for="playlistiq-answer">${esc(plan.clarification)}</label><textarea id="playlistiq-answer" class="text-input" maxlength="1000" required></textarea><button class="button primary" type="submit">Continue</button></form>`:''}<ol class="iq-matches">${matches.map(m=>`<li><button class="iq-match-track" data-iq-play="${esc(m.track.track_id)}" aria-label="Play ${esc(m.track.title)}"><strong>${esc(m.track.title)}</strong><span>${esc(m.track.artist??'')}</span></button><details><summary>Why this track · ${pct(m.score)} / 100</summary>${conciseMatchHTML(m,run)}</details></li>`).join('')}</ol><div class="iq-footnotes">${plan?.assumptions?.length?`<details><summary>Musical assumptions</summary><ul>${plan.assumptions.map(a=>`<li>${esc(a)}</li>`).join('')}</ul></details>`:''}<details><summary>Evidence and limitations</summary><p>${esc(limits)}</p>${gaps.length?`<ul>${gaps.map(g=>`<li>${esc(g)}</li>`).join('')}</ul>`:''}</details><details><summary>The plan, in plain language</summary>${listRows(planSummaryRows(run))}</details></div>`;
}
