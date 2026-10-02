import test from 'node:test';
import assert from 'node:assert/strict';
import {intentHTML,playPlaylistMatch} from '../src/playlistiq.js';
import {validatePlaylistRequest} from '../scripts/local-features.mjs';
import {reviewPrompts,recordReviewAttempt} from '../src/playlist-review.js';
const request=()=>({prompt:'Music for my mom',tracks:[{id:'t1',sha256:'a'.repeat(64),title:'Test',artist:''}],clarifications:[{question:'Her taste?',answer:'Rock'}]});
test('playlist bridge accepts bounded clarification and rejects malformed or excessive input',()=>{
 assert.equal(validatePlaylistRequest(request()).clarifications[0].answer,'Rock');
 for(const patch of [{clarifications:Array(4).fill(request().clarifications[0])},{clarifications:[{question:'?',answer:' '}]},{clarifications:[{question:'?',answer:'a'.repeat(1001)}]},{prompt:' '},{tracks:[]},{secret:'unexpected'}])assert.throws(()=>validatePlaylistRequest({...request(),...patch}));
});
test('clarification presentation is escaped and does not offer an empty playlist',()=>{
 const html=intentHTML({status:'needs_clarification',translation:{plan:{interpretation:'<script>bad</script>',assumptions:['No taste assumed'],clarification:'What mood?'},query:{}},result:null});
 assert.match(html,/data-iq-clarification/);assert.match(html,/&lt;script&gt;/);assert.doesNotMatch(html,/data-iq-save/);
});
test('draft presentation exposes interpretation, query, contributions and save',()=>{
 const html=intentHTML({status:'partial_support',translation:{plan:{interpretation:'A gentle mix',assumptions:[]},query:{preferences:[]}},result:{ranking_version:'maest-intent-v1',matches:[{track:{track_id:'1',title:'A&B'},score:.5,reasons:['Estimated fit'],score_contributions:[{contribution:.5}]}]}});
 assert.match(html,/data-iq-save/);assert.match(html,/A&amp;B/);assert.match(html,/maest-intent-v1/);assert.match(html,/contribution/);
 assert.match(html,/data-iq-play="1"/);assert.match(html,/aria-label="Play A&amp;B"/);
});
test('a PlaylistIQ match starts the main player at the selected ranked result',async()=>{
 const tracks=[{id:'a',status:'ready'},{id:'b',status:'ready'},{id:'c',status:'unavailable'}];
 const matches=['b','missing','c','a'].map(id=>({track:{track_id:id}}));let played;
 const player={async setQueue(queue,index){played={ids:queue.map(t=>t.id),index};}};
 await playPlaylistMatch(player,tracks,matches,'a');
 assert.deepEqual(played,{ids:['b','a'],index:1});
 await assert.rejects(playPlaylistMatch(player,tracks,matches,'missing'),/no longer available/);
});
test('stable benchmark IDs preserve V0 and creative cases before appended scenes',()=>{
 assert.equal(reviewPrompts.length,24);assert.equal(reviewPrompts[0].id,'P01');assert.equal(reviewPrompts[9].id,'P10');
 assert.match(reviewPrompts[13].prompt,/mom/);assert.match(reviewPrompts[14].prompt,/rock or pop/);
});
test('exported Python benchmark matches the listening lab exactly',async()=>{
 const {readFile}=await import('node:fs/promises');
 const suite=JSON.parse(await readFile(new URL('../../prompt-to-playlist/docs/evaluations/iteration1-prompts.json',import.meta.url),'utf8'));
 assert.deepEqual(suite.cases,reviewPrompts.slice(0,20));
});
