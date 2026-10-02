import test from 'node:test';
import assert from 'node:assert/strict';
import {promptConnectionHTML} from '../src/prompt-connection.js';
import {matchExplanationHTML} from '../src/match-explanation.js';
const part=(tag,direction='increase',origin='inferred')=>({tags:[tag],direction,origin,evidence_value:.8,utility:.8,weight:1,contribution:.8,group:'preference'});
const result=parts=>({track:{title:'Example',track_id:'one'},score:.8,score_contributions:parts,reasons:[]});
const run=(request_text='un dia en la playa',interpretation='Un día tranquilo, alegre y relajado en la playa.')=>({translation:{request_text,plan:{interpretation,occasion:'día de playa',activity:null,recipient:null,emotional_goal:'relajado',assumptions:['I assumed a calm outing.']}},result:{ranking_version:'maest-intent-v1',query:{}}});
test('scene explanation connects original prompt and planner interpretation to scored musical roles',()=>{
 const html=promptConnectionHTML(result([part('mood:relaxed'),part('mood:happy')]),run());
 assert.match(html,/You asked for “un dia en la playa”/);assert.match(html,/The planner read this as/);assert.match(html,/moment feel unhurried/);assert.match(html,/cheerful tone/);assert.match(html,/inferred this preference/);assert.match(html,/does not directly measure that kind of scene fit/);
 assert.doesNotMatch(html,/perfect beach track|sounds of waves|Grecia/);
});
test('energetic beach interpretation is explained without imposing calm as a beach stereotype',()=>{
 const html=promptConnectionHTML(result([part('energy:high','increase','explicit'),part('danceability:danceable','increase','explicit')]),run('playa con mucha energía para bailar','Una tarde enérgica para bailar.'));
 assert.match(html,/sense of momentum/);assert.match(html,/rhythmic reason to move/);assert.doesNotMatch(html,/earned credit for a relaxed mood|inferred this preference|The assumption to check/);
});
test('a date prompt is grounded in its own plan and does not infer intimacy from mood scores',()=>{
 const html=promptConnectionHTML(result([part('energy:low')]),run('After dessert on the sofa with my date','A quiet evening after dinner.'));
 assert.match(html,/After dessert on the sofa with my date/);assert.match(html,/without demanding constant attention/);assert.doesNotMatch(html,/will create chemistry|romantic vocals|sensual timbre/);
});
test('unknown, zero and unsupported scores cannot supply scene evidence; missing history is honest',()=>{
 const track=result([{...part('mood:relaxed'),evidence_value:null,contribution:0},{...part('mood:happy'),contribution:0}]);
 assert.match(promptConnectionHTML(track,run()),/does not contain enough scored/);assert.doesNotMatch(promptConnectionHTML(track,run()),/earned credit for/);
 assert.equal(promptConnectionHTML(track,{}),'');
 assert.match(promptConnectionHTML(result([part('genre:house')]),run('House','House tracks')),/Style evidence alone/);
});
test('scene content is escaped, decreasing preferences have the right role, and scoring remains present',()=>{
 const input=run('<img src=x onerror=alert(1)>','<script>scene</script>');
 const html=matchExplanationHTML(result([part('energy:high','decrease')]),input,0);
 assert.match(html,/How it connects to your prompt/);assert.match(html,/less high-energy intensity/);assert.match(html,/pushing the moment toward sustained intensity/);assert.match(html,/What drove its score/);assert.match(html,/How the score adds up/);
 assert.doesNotMatch(html,/<script>|<img/);assert.match(html,/&lt;script&gt;/);
});
