import test from 'node:test';import assert from 'node:assert/strict';import {randomUUID} from 'node:crypto';
import {decodeSpectrum,spectrumAt} from '../src/recorded-spectrum.js';
import {promptSnapshot} from '../src/prompt-snapshot.js';
import {validateProfileOperation,mutateProfileItem,profileTargets} from '../src/profile-model.js';
import {promptHistoryHTML,promptResultsHTML} from '../src/profile-views.js';
test('recorded spectrum follows measured frames and seeks instead of song progress',()=>{
 const bytes=new Uint8Array(96*3);bytes[2]=255;bytes[96+80]=255;bytes[192+12]=255;
 const data=decodeSpectrum({schema:'resonant-spectrum/1',columns:96,fps:10,frames:3,data:Buffer.from(bytes).toString('base64')});
 assert.equal(spectrumAt(data,.1)[2],1);assert.equal(spectrumAt(data,.2)[2],0);assert.equal(spectrumAt(data,.2)[80],1);assert.equal(spectrumAt(data,999)[12],1);assert.equal(spectrumAt(data,.1)[80],0);
 assert.throws(()=>decodeSpectrum({...data,frames:4}),/Incomplete/);
});
test('prompt explanations survive requested-to-complete mutation and render safely',()=>{
 const run={translation:{plan:{interpretation:'<script>hello</script>',occasion:'Dinner',activity:'Talking'}},result:{matches:[]}},matches=[{track:{track_id:'track-a'},score:.8,score_contributions:[{tags:['mood_happy'],utility:.7,weight:.5,contribution:.35}]}];
 const snapshot=promptSnapshot(run,matches),op={id:randomUUID(),at:2,type:'prompt',requestId:'request',requestAt:1,prompt:'Dinner',status:'complete',trackIds:['track-a'],snapshot};
 validateProfileOperation(op,new Set(['track-a']));const row=mutateProfileItem(null,op,profileTargets(op)[0]);assert.equal(row.snapshot.context.activity,'Talking');
 const html=promptResultsHTML(row,[{id:'track-a',title:'Track',artist:'Artist'}]);assert.match(html,/data-history-track="track-a"/);assert.match(html,/&lt;script&gt;/);assert.doesNotMatch(html,/<script>/);
 assert.match(promptHistoryHTML([row],[]),/data-prompt-open="request"/);
 assert.throws(()=>validateProfileOperation({...op,snapshot:{...snapshot,matches:[{...snapshot.matches[0],id:'foreign'}]}},new Set(['track-a'])),/Unknown track/);
});
test('old prompt tracks remain visible without inventing missing explanations',()=>{
 const html=promptResultsHTML({id:'old',prompt:'Music',trackIds:['a']},[{id:'a',title:'A',artist:'B'}]);assert.match(html,/data-history-track="a"/);assert.match(html,/weren’t stored/);
});
