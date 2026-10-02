import test from 'node:test';
import assert from 'node:assert/strict';
import {fullyAnalyzed,RELEASE_STAGES,releaseFront} from '../src/release-policy.js';
import {publicFeatures} from '../scripts/web-library.mjs';
import {validateTrack} from '../src/model.js';
const complete=()=>({feature_version:'selected-estimators-v3-character120',policy:'maest-top6-v1',status:'complete',algorithms:RELEASE_STAGES.map(algorithm_id=>({algorithm_id,status:'warning',values:algorithm_id==='metadata'?{codec:'mp3'}:{}}))});
test('release admission requires all eleven successful stages, current version and MP3 codec',()=>{
 assert.equal(fullyAnalyzed(complete()),true);
 for(const id of RELEASE_STAGES){const f=complete();f.algorithms.find(a=>a.algorithm_id===id).status='failed';assert.equal(fullyAnalyzed(f),false);}
 const f=complete();f.algorithms.pop();assert.equal(fullyAnalyzed(f),false);
 assert.equal(fullyAnalyzed({...complete(),feature_version:'old'}),false);
 assert.equal(fullyAnalyzed({...complete(),status:'partial'}),false);
 const aac=complete();aac.algorithms[0].values.codec='aac';assert.equal(fullyAnalyzed(aac),false);
});
test('web stays on layout three and retired option two migrates to three',()=>{
 for(const requested of ['studio','radio','radio-wide',null])assert.equal(releaseFront('web',requested),'radio-wide');
 assert.equal(releaseFront('local','studio'),'studio');assert.equal(releaseFront('local','radio'),'radio-wide');
});
test('published features retain display evidence without embeddings or process paths',()=>{
 const f=complete();f.algorithms[1].metrics={source:'/Users/example/private'};f.algorithms[1].values={segments:[{embedding:[1,2],mean:.5}],source:'/private/tmp/audio'};
 const safe=publicFeatures(f);assert.ok(!safe.algorithms[1].metrics);assert.deepEqual(safe.algorithms[1].values,{segments:[{mean:.5}]});
 const track=validateTrack({id:'a',kind:'cloud',title:'Track',artist:'',duration:1,status:'ready',features:safe,fileHash:'a'.repeat(64)});assert.equal(track.features,safe);assert.equal(track.fileHash,'a'.repeat(64));
});
