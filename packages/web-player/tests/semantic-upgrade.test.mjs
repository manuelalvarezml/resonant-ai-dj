import test from 'node:test';
import assert from 'node:assert/strict';
import {needsEstimatorUpgrade,featureDetails,featureTable} from '../src/features.js';
import {matchExplanationHTML} from '../src/match-explanation.js';

test('old completed analysis is visibly upgradeable without deleting it',()=>{
 assert.equal(needsEstimatorUpgrade({features:{status:'complete'}}),true);
 assert.equal(needsEstimatorUpgrade({features:{status:'complete',feature_version:'selected-estimators-v3-character120'}}),false);
 assert.equal(needsEstimatorUpgrade({features:{status:'partial',feature_version:'selected-estimators-v3-character120'}}),true);
});
test('cosines are shown separately from classifier support and retain sampling limits',()=>{
 const track={id:'one',title:'One',features:{algorithms:[{algorithm_id:'semantic_audio',status:'warning',values:{duration_s:200,sampled_seconds:30,segments:[{},{},{}],descriptors:{dreamy:{mean:.24,min:.2,max:.3}}}},{algorithm_id:'semantic',status:'warning',values:{heads:{mood_theme:{scores:{romantic:.2}},instruments:{scores:{piano:.6}}}}}]}};
 const details=featureDetails(track);
 assert.match(details,/0.240 cosine/);assert.match(details,/30.0 seconds sampled/);assert.match(details,/20.0 \/ 100 model support/);assert.match(details,/not a probability/);
 assert.match(featureTable([track]),/Mood \/ themes/);assert.match(featureTable([track]),/piano 60.0% support/);
});
test('hybrid explanations reconcile points without calling cosines probabilities',()=>{
 const c={tags:['semantic:scene'],group:'semantic',direction:'increase',origin:'inferred',evidence_value:.23,utility:.75,weight:.3,contribution:.225,score_kind:'relative_similarity',detail:'mean cosine 0.2300; sampled range 0.1–0.4'};
 const match={track:{track_id:'one'},score:.225,score_contributions:[c],reasons:[]};
 const run={translation:{request_text:'un día en la playa'},result:{ranking_version:'hybrid-semantic-v1',eligible_count:2,query:{semantic:{description:'Airy <script> music'}}}};
 const html=matchExplanationHTML(match,run,0);
 assert.match(html,/22.50 \/ 100/);assert.match(html,/75.00 \/ 100 relative rank/);assert.match(html,/mean cosine 0.2300/);assert.match(html,/not mean the track has that mood/);assert.doesNotMatch(html,/evidence value is 23.00\/100/);assert.doesNotMatch(html,/<script>/);
});

test('main columns prefer selected values while retaining previous mood evidence',()=>{
 const track={id:'one',title:'One',features:{algorithms:[
 {algorithm_id:'energy',status:'warning',values:{arousal_mean:2,valence_mean:2}},
 {algorithm_id:'emotion_music2emo',status:'warning',values:{arousal_mean:7,valence_mean:6}},
 {algorithm_id:'vocal_musicnn',status:'warning',values:{scores:{voice:.9,instrumental:.1}}},
 {algorithm_id:'semantic',status:'warning',values:{heads:{mood_theme:{scores:{calm:.7}},vocal_profile:{scores:{voice:.2,instrumental:.8}}}}}
 ]}};
 const html=featureTable([track]);
 assert.match(html,/7.0 \/ 9/);assert.match(html,/6.0 \/ 9/);assert.match(html,/90.0% <small>MusiCNN/);
 assert.match(html,/calm 70.0% support/);assert.match(html,/Mood \/ themes · Music2Emo/);
});

test('new character bank presents separate dimensions and preserves cosine meaning',()=>{
 const values={descriptors:{melancholic:{label:'melancholic',dimension:'emotion',mean:.14},bouncy:{label:'bouncy',dimension:'groove',mean:.3},shimmering:{label:'shimmering',dimension:'texture',mean:.2},calm:{label:'calm',dimension:'intensity',mean:.15},sparse:{label:'sparse',dimension:'space_arrangement',mean:.12}}};
 const html=featureTable([{id:'test',title:'Test',features:{algorithms:[{algorithm_id:'semantic_audio',status:'warning',values}]}}]);
 for(const label of ['Emotion','Groove','Texture','Intensity','Arrangement'])assert.match(html,new RegExp(label));
 assert.match(html,/melancholic 0.140 cosine/);assert.match(html,/120 descriptions; uncalibrated/);
});
