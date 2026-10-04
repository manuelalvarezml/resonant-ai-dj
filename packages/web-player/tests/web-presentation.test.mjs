import test from 'node:test';
import assert from 'node:assert/strict';
import {trackFacts,trackCardHTML,upcomingQueue,webIntentHTML,conciseMatchHTML,planSummaryRows,playbackQuip} from '../src/web-presentation.js';
import {adjacentTrack,shouldDismiss} from '../src/mobile-player.js';
import {spectrumBands} from '../src/spectrum-bands.js';
const track={id:'a',title:'A & B',artist:'Artist',status:'ready',features:{genres:['One','Two','Three','Four'].map(genre=>({genre})),algorithms:[{algorithm_id:'rhythm',values:{bpm:122.3}},{algorithm_id:'key_sheetsage2',values:{standard_key:'A minor'}},{algorithm_id:'semantic_audio',values:{descriptors:{soft:{label:'Soft',mean:.2},bright:{label:'Bright',mean:.7}}}}]}};
const run={status:'complete',translation:{request_text:'Jazz at home',plan:{interpretation:'Easy jazz for an evening at home',occasion:'Evening',activity:'Reading',assumptions:['Low energy suits this reading.']},query:{}},result:{matches:[{track:{track_id:'a',title:'A & B',artist:'Artist'},score:.6,score_contributions:[{tags:['mood:relaxed'],direction:'increase',utility:.8,weight:.75,contribution:.6,source:'technical:private_source_tag'}]}]}};
test('cards retain the best character label, selected key and three genres without status or scores',()=>{
 assert.deepEqual(trackFacts(track),['122 BPM','A minor','Bright']);const html=trackCardHTML(track);
 assert.match(html,/data-action="play-track"/);assert.match(html,/A &amp; B/);assert.doesNotMatch(html,/Four|Analyzed|cosine|0.7/);assert.equal((html.match(/<button/g)||[]).length,1);
});
test('queue starts at current occurrence and keeps action indexes from the original queue',()=>{
 const player={queue:[{id:'old'},track,{id:'next'}],index:1};
 assert.deepEqual(upcomingQueue(player).map(x=>[x.track.id,x.index,x.current]),[['a',1,true],['next',2,false]]);
});
test('swipe preview respects queue edges and repeat-all',()=>{
 const p={queue:[track,{id:'b'}],index:0,repeat:'off'};assert.equal(adjacentTrack(p,'previous'),null);assert.equal(adjacentTrack(p,'next').id,'b');
 p.repeat='all';assert.equal(adjacentTrack(p,'previous').id,'b');p.index=1;assert.equal(adjacentTrack(p,'next').id,'a');
});
test('dismissal allows deliberate pull or quick flick, rejects taps and short slow drags',()=>{
 assert.ok(shouldDismiss(120,500));assert.ok(shouldDismiss(50,60));assert.equal(shouldDismiss(10,10),false);assert.equal(shouldDismiss(50,500),false);
});
test('web explanation keeps two paragraphs, scene fields and exact points without diagnostic tags',()=>{
 const html=conciseMatchHTML(run.result.matches[0],run);assert.equal((html.match(/<p>/g)||[]).length,2);assert.match(html,/Occasion/);assert.match(html,/Reading/);assert.match(html,/60.0/);assert.doesNotMatch(html,/private_source_tag|<pre>|Evidence source/);
 const full=webIntentHTML(run);assert.ok(full.indexOf('Musical assumptions')>full.indexOf('Why this track'));assert.doesNotMatch(full,/data-iq-play[^>]*>▶|<pre>/);assert.ok(planSummaryRows(run).length<=10);
});
test('humorous status retains actionable error information',()=>{assert.match(playbackQuip({status:'error',error:'Press Play to try again.'}),/Press Play/);assert.match(playbackQuip({interrupted:true}),/Press Play/);});
test('web spectrum extends to 20 Hz and 20 kHz without changing default sampling',()=>{
 const bins=Float32Array.from({length:4096},(_,i)=>-80+i*.001),web=spectrumBands(bins,48000,8192,96,20,20000),local=spectrumBands(bins,48000,8192);
 assert.ok(web[0]<local[0]);assert.ok(web.at(-1)>local.at(-1));assert.ok(web.every(Number.isFinite));
});

test('human plan preserves exclusions and ordering within ten facts; limitations retain the reason',()=>{
 const full={...run,status:'partial_support',translation:{plan:{...run.translation.plan,recipient:'Me',emotional_goal:'Focus',musical_description:'Soft jazz',avoid_descriptions:['Sharp, abrasive textures'],evidence_gaps:[{explanation:'Lyrics have not been assessed.'}]}},result:{...run.result,query:{required_tags:['genre:jazz'],any_tag_groups:[['genre:soul','genre:funk']],preferences:[{tag:'mood:relaxed'}],min_bpm:70,max_bpm:110,excluded_tags:['mood:aggressive'],order:'bpm_ascending'}}};
 const rows=planSummaryRows(full);assert.equal(rows.length,10);assert.ok(rows.find(([k,v])=>k==='Avoid'&&v.includes('Sharp, abrasive')));assert.ok(rows.find(([k,v])=>k==='Order'&&v==='Slowest first'));assert.match(webIntentHTML(full),/Lyrics have not been assessed/);
});
