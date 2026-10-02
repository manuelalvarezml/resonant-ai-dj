import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {matchExplanationHTML} from '../src/match-explanation.js';
import {intentHTML} from '../src/playlistiq.js';
const c=(patch={})=>({tags:['mood:relaxed'],direction:'increase',origin:'inferred',group:'preference',evidence_value:.8,utility:.8,weight:.35,contribution:.28,source:'discogs-effnet/relaxed',...patch});
const m=(contributions)=>({track:{track_id:'one',title:'Title',bpm:{value:125}},score:contributions.reduce((s,c)=>s+c.contribution,0),score_contributions:contributions,reasons:['original <note>']});
const r=(query={})=>({translation:{query},result:{ranking_version:'maest-intent-v1',eligible_count:12,query}});
test('plain-language explanation reconciles genre and preference points with score and rank',()=>{
 const contributions=[c({tags:['genre:house'],group:'genre',origin:'explicit',evidence_value:.6,utility:.6,weight:.65,contribution:.39,source:'maest-top6-v1 [Electronic---House]' }),c()];
 const html=matchExplanationHTML(m(contributions),r({required_tags:['genre:house'],preferences:[{tag:'mood:relaxed',direction:'increase',importance:'primary',source_span:'a quiet picnic'}]}),1);
 for(const text of ['Musical fit: 67.00 / 100','39.00 + 28.00 = 67.00','60.00% fit × 65.00% weight','80.00% fit × 35.00% weight','Shown at #2 among 12','Inferred from your request','Required genre match','Electronic / House','not a 67.00% chance','original &lt;note&gt;'])assert.ok(html.includes(text),text);
 assert.match(html,/largest unused share.*house style/);
});
test('asking for less reverses known evidence, while unknown evidence never earns credit',()=>{
 const low=c({tags:['mood:aggressive'],direction:'decrease',evidence_value:.2,utility:.8,weight:.5,contribution:.4});
 const unknown=c({tags:['vocals:vocal'],direction:'decrease',evidence_value:null,utility:0,weight:.5,contribution:0,source:null});
 const html=matchExplanationHTML(m([low,unknown]),r(),0);
 assert.match(html,/100 − 20.00 = 80.00/);assert.match(html,/40.00 \+ 0.00 = 40.00/);
 assert.match(html,/Evidence is missing for vocals/);assert.match(html,/earns zero points, including when.*asks for less/);
 const zero=matchExplanationHTML(m([c({...low,evidence_value:0,utility:1,weight:1,contribution:1})]),r());
 assert.match(zero,/100 − 0.00 = 100.00/);assert.doesNotMatch(zero,/Evidence is missing/);
});
test('tempo ordering, genre alternatives and filters are separate from score',()=>{
 const html=matchExplanationHTML(m([c({tags:['genre:rock','genre:pop'],group:'genre',origin:'explicit',weight:1,contribution:.8,source:'maest-top6-v1 [Rock---Garage Rock]'})]),r({order:'bpm_ascending',min_bpm:120,max_bpm:130,any_tag_groups:[['genre:rock','genre:pop']],genre_scope:'taxonomy'}),2);
 assert.match(html,/ordered by tempo, slowest first/);assert.match(html,/125.0 BPM/);assert.match(html,/Tempo filtering adds no score points/);assert.match(html,/best-supported alternative/);assert.match(html,/strongest matching style/);
});
test('zero-score and historical runs do not fabricate weighted explanations',()=>{
 const html=matchExplanationHTML(m([]),r(),0);assert.match(html,/eligible tracks tie/);assert.doesNotMatch(html,/How the score adds up/);
 const old=matchExplanationHTML({...m([]),score:.5},{result:{ranking_version:'tag-coverage-v1'}},0);
 assert.match(old,/Recorded score: 0.500/);assert.doesNotMatch(old,/eligible tracks tie/);
});
test('unscored catalog preferences, energy mapping and untrusted source text remain explicit',()=>{
 const html=matchExplanationHTML(m([c({tags:['energy:low'],source:'deam-arousal-linear-preference-v1-unvalidated',weight:1,contribution:.8})]),r({preferences:[{tag:'energy:low',direction:'increase',source_span:'<script>quiet</script>'},{tag:'mood:happy',direction:'increase'}]}));
 assert.match(html,/Not scored here: a happy mood/);assert.match(html,/arousal estimate on a 1–9 scale/);assert.ok(!html.includes('<script>'));assert.match(html,/&lt;script&gt;/);
});
test('recorded engine fixture reconciles every explanation and renders through PlaylistIQ',async()=>{
 const fixture=JSON.parse(await readFile(new URL('./browser/playlistiq-data.json',import.meta.url),'utf8')).matched;
 for(const match of fixture.result.matches){
  const sum=match.score_contributions.reduce((s,c)=>s+c.contribution,0);assert.ok(Math.abs(sum-match.score)<.000001);
  const html=matchExplanationHTML(match,fixture,0);assert.match(html,/How the score adds up/);assert.ok(html.includes((match.score*100).toFixed(2)+' / 100'));
 }
 assert.match(intentHTML(fixture),/iq-match-story/);
});

test('rounded component totals use an approximation sign instead of a false equality',()=>{
 const parts=[c({weight:.5,utility:.666666,contribution:.333333}),c({weight:.5,utility:.666666,contribution:.333333})];
 assert.match(matchExplanationHTML(m(parts),r()),/33.33 \+ 33.33 ≈ 66.67/);
});
