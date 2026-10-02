import test from 'node:test';import assert from 'node:assert/strict';
import {genreSummary,cachedFeatures} from '../src/features.js';import {allowedLocalRequest,validCachedFeatures} from '../scripts/local-features.mjs';
test('genre display separates first three from expandable remainder and escapes labels',()=>{const html=genreSummary({features:{status:'complete',genres:Array.from({length:6},(_,i)=>({genre:'Electronic---<Style '+i+'>'}))}});assert.match(html,/All 6 genres/);assert.equal((html.split('<details>')[0].match(/<span>/g)||[]).length,3);assert.ok(!html.includes('<Style'));});
test('local mutations reject foreign origins, hosts and missing request marker',()=>{const headers={host:'127.0.0.1:4173',origin:'http://127.0.0.1:4173','x-resonant-local':'1'};assert.equal(allowedLocalRequest({headers},4173),true);for(const patch of [{origin:'https://evil.example'},{host:'evil.example'},{'x-resonant-local':undefined}])assert.equal(allowedLocalRequest({headers:{...headers,...patch}},4173),false);});

test('saved analysis lookup accepts only matching bounded MAEST records',async()=>{const hash='a'.repeat(64),value={sha256:hash,policy:'maest-top6-v1',status:'complete',algorithms:[],genres:[]};assert.equal(validCachedFeatures(value,hash),true);assert.equal(validCachedFeatures({...value,sha256:'b'.repeat(64)},hash),false);let request;const result=await cachedFeatures(hash,async(url,options)=>{request={url,options};return {ok:true,status:200,json:async()=>({result:value})};});assert.equal(result,value);assert.equal(request.url,'/api/local/features/'+hash);assert.equal(request.options.headers['X-Resonant-Local'],'1');assert.equal(await cachedFeatures(hash,async()=>({ok:false,status:404,json:async()=>({})})),null);await assert.rejects(cachedFeatures(hash,async()=>({ok:true,status:200,json:async()=>({result:{...value,policy:'other'}})})),/invalid/);});

test('feature table distinguishes unknown values from zero and escapes track data',async()=>{const {featureTable}=await import('../src/features.js');const html=featureTable([{id:'a',title:'<song>',features:{status:'partial',genres:[],algorithms:[{algorithm_id:'semantic',status:'warning',values:{heads:{mood_happy:{scores:{happy:0}}}}},{algorithm_id:'rhythm',status:'failed',error:'No <beats>'}]}}]);assert.match(html,/0.0%/);assert.match(html,/Partial/);assert.match(html,/No &lt;beats&gt;/);assert.match(html,/&lt;song&gt;/);assert.ok(!html.includes('<song>'));assert.match(html,/scope="col"/);});

test('experimental outputs expose raw units and coverage while missing stages stay unestimated',async()=>{
 const {supervisedSummary,featureDetails}=await import('../src/features.js');
 assert.equal(supervisedSummary({}),'Not compared');
 const v={kind:'music2emo',sampled_seconds:30,duration_s:100,coverage_fraction:.3,valence_mean:7,arousal_mean:5,scores:{'<label>':.6},model_id:'test',segments:[{start_s:10,end_s:40,valence:7,arousal:5}]};
 assert.match(supervisedSummary(v),/30% sampled/);assert.match(supervisedSummary(v),/raw 1–9/);assert.match(supervisedSummary(v),/&lt;label&gt;/);
 const html=featureDetails({features:{algorithms:[{algorithm_id:'emotion_music2emo',status:'warning',values:v}]}});
 assert.match(html,/10.0–40.0/);assert.match(html,/7.000 raw \/ 9/);
});
test('estimator selection is an explicit bounded playlist request field',async()=>{
 const {validatePlaylistRequest}=await import('../scripts/local-features.mjs');
 const v={prompt:'Dance',tracks:[{id:'a',title:'A',artist:'',sha256:'a'.repeat(64)}]};
 for(const estimator_profile of ['reference','music2emo','musicnn-dance','supervised'])assert.equal(validatePlaylistRequest({...v,estimator_profile}).estimator_profile,estimator_profile);
 assert.throws(()=>validatePlaylistRequest({...v,estimator_profile:'automatic-best'}));
});
test('selected specialist details preserve names, coverage and independent key evidence',async()=>{
 const {featureDetails,featureTable}=await import('../src/features.js');
 const track={id:'one',title:'One',features:{status:'complete',genres:[],algorithms:[
  {algorithm_id:'instrument_passt',status:'warning',values:{model_id:'pinned',sampled_seconds:90,duration_s:300,scores:{banjo:.7,'<unsafe>':.1},segments:[{start_s:0,end_s:10}]}},
  {algorithm_id:'key_sheetsage2',status:'warning',values:{model_id:'key-pinned',standard_key:'C:maj',key_intervals:[[0,300,'C:maj']]}}
 ]}};
 const details=featureDetails(track);assert.match(details,/90.0 \/ 300.0 seconds sampled/);assert.match(details,/&lt;unsafe&gt;/);assert.match(details,/0.0–300.0 s: C:maj/);
 assert.match(featureTable([track]),/Selected specialists/);assert.match(featureTable([track]),/banjo 70.0% support/);
 const {validatePlaylistRequest}=await import('../scripts/local-features.mjs');
 assert.equal(validatePlaylistRequest({prompt:'Banjo music',estimator_profile:'quality',tracks:[{id:'one',title:'One',artist:'',sha256:'a'.repeat(64)}]}).estimator_profile,'quality');
});
