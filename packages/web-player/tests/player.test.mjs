import test from 'node:test';
import assert from 'node:assert/strict';
import {Player} from '../src/player.js';
class AudioFake extends EventTarget {
  src='';currentTime=0;duration=120;readyState=0;paused=true;
  pause(){this.paused=true;this.dispatchEvent(new Event('pause'));}
  removeAttribute(){this.src='';this.currentTime=0;this.readyState=0;}
  load(){if(this.src){this.readyState=1;this.dispatchEvent(new Event('loadedmetadata'));}}
  async play(){this.paused=false;this.dispatchEvent(new Event('playing'));}
}
const track=id=>({id,title:id,status:'ready',duration:120});
const deferred=()=>{let resolve;return {promise:new Promise(r=>resolve=r),resolve};};
const tick=()=>new Promise(resolve=>setImmediate(resolve));
const session=(id,release=()=>{})=>({url:`blob:${id}`,expiresAt:null,release});
function fixture(resolver=async t=>session(t.id)){const audio=new AudioFake();return {audio,p:new Player(audio,resolver)};}
test('last selected track wins when resolution completes out of order',async()=>{
  const first=deferred(),second=deferred();let released=false;
  const {p,audio}=fixture(t=>t.id==='a'?first.promise:second.promise);
  const a=p.setQueue([track('a')]),b=p.setQueue([track('b')]);
  second.resolve(session('b'));await b;first.resolve(session('a',()=>released=true));await a;
  assert.equal(audio.src,'blob:b');assert.equal(p.current.id,'b');assert.ok(released);
});
test('pause during loading prevents late autoplay',async()=>{
  const wait=deferred();const {p,audio}=fixture(()=>wait.promise);const loading=p.setQueue([track('a')]);p.toggle();wait.resolve(session('a'));await loading;
  assert.equal(p.status,'paused');assert.equal(audio.paused,true);assert.equal(p.wantPlay,false);
});
test('clear releases a late session and cancels stale seek',async()=>{
  const wait=deferred(),calls=[];let released=false;
  const {p}=fixture((t,o)=>{calls.push([t.id,o.position]);return t.id==='a'?wait.promise:Promise.resolve(session(t.id));});
  const loading=p.setQueue([track('a')]);p.seek(45);p.clear();p.enqueue(track('b'));await p.toggle();wait.resolve(session('a',()=>released=true));await loading;
  assert.deepEqual(calls,[['a',0],['b',0]]);assert.ok(released);assert.equal(p.current.id,'b');
});
test('removing current track while paused keeps replacement paused',async()=>{
  const {p,audio}=fixture();await p.setQueue(['a','b'].map(track));p.toggle();await p.remove(0);
  assert.equal(p.current.id,'b');assert.equal(p.wantPlay,false);assert.equal(audio.paused,true);
});
test('queue reordering keeps the exact occurrence current, even with duplicates',async()=>{
  const {p}=fixture();await p.setQueue(['a','b','a','c'].map(track),2);p.move(2,0);assert.equal(p.index,0);p.move(3,0);assert.equal(p.index,1);await p.remove(0);assert.equal(p.index,0);assert.equal(p.current.id,'a');
});
test('removing final entry clears playback and source capability',async()=>{
  let released=false;const {p,audio}=fixture(async()=>session('a',()=>released=true));await p.setQueue([track('a')]);await p.remove(0);
  assert.equal(p.current,null);assert.equal(p.status,'idle');assert.equal(audio.src,'');assert.ok(released);
});
test('next, previous and end behavior respect repeat modes',async()=>{
  const {p,audio}=fixture();await p.setQueue(['a','b'].map(track));await p.next();assert.equal(p.current.id,'b');audio.currentTime=10;p.previous();assert.equal(audio.currentTime,0);await p.previous();assert.equal(p.current.id,'a');
  p.repeat='one';await p.next(true);assert.equal(p.current.id,'a');await p.next();assert.equal(p.current.id,'b');p.repeat='all';await p.next(true);assert.equal(p.current.id,'a');p.repeat='off';await p.next();await p.next(true);assert.equal(p.status,'ended');assert.equal(p.wantPlay,false);
});
test('shuffle preserves current and all queue members',async()=>{const {p}=fixture();await p.setQueue(['a','b','c','d'].map(track),1);p.toggleShuffle();assert.equal(p.index,1);assert.equal(p.current.id,'b');assert.deepEqual(p.queue.map(t=>t.id).sort(),['a','b','c','d']);});
test('expired capability renewal resumes position and consecutive failures are bounded',async()=>{
  let calls=0;const {p,audio}=fixture(async()=>({...session(String(++calls)),expiresAt:Date.now()-1}));await p.setQueue([track('a')]);audio.currentTime=37;
  await p.mediaError();assert.equal(calls,2);assert.equal(audio.currentTime,37);await p.mediaError();assert.equal(calls,2);assert.equal(p.status,'error');
});
test('successful playback progress resets renewal budget for later expiry',async()=>{
  let calls=0;const {p,audio}=fixture(async()=>({...session(String(++calls)),expiresAt:Date.now()-1}));await p.setQueue([track('a')]);audio.currentTime=10;await p.mediaError();audio.currentTime=12;audio.dispatchEvent(new Event('timeupdate'));await p.mediaError();assert.equal(calls,3);assert.equal(audio.currentTime,12);
});
test('expired seek while paused does not autoplay',async()=>{
  const {p,audio}=fixture(async()=>({...session('a'),expiresAt:Date.now()-1}));await p.setQueue([track('a')]);p.toggle();await p.seek(30);assert.equal(audio.currentTime,30);assert.equal(audio.paused,true);
});
test('play rejection becomes actionable error, and retry works',async()=>{
  const {p,audio}=fixture();audio.play=async()=>{throw Object.assign(new Error('blocked'),{name:'NotAllowedError'});};await p.setQueue([track('a')]);assert.equal(p.status,'error');assert.match(p.error,/Press Play/);audio.play=AudioFake.prototype.play;await p.toggle();assert.equal(p.status,'playing');
});
test('seek clamps negative and beyond-end positions',async()=>{const {p,audio}=fixture();await p.setQueue([track('a')]);p.seek(-5);assert.equal(audio.currentTime,0);p.seek(999);assert.equal(audio.currentTime,120);});
test('resolver errors do not advance queue or invent successful playback',async()=>{const {p}=fixture(async()=>{throw new Error('Unavailable');});await p.setQueue(['a','b'].map(track));assert.equal(p.current.id,'a');assert.equal(p.wantPlay,false);assert.equal(p.status,'error');});
test('late play rejection after a newer selection cannot damage current state',async()=>{
  const {p,audio}=fixture();const pending=deferred();audio.play=()=>pending.promise;const old=p.setQueue([track('a')]);await tick();audio.play=AudioFake.prototype.play;await p.setQueue([track('b')]);pending.resolve();await old;assert.equal(p.current.id,'b');assert.equal(p.status,'playing');
});

test('native interruption clears play intent and allows explicit resume',async()=>{
 const {p,audio}=fixture();await p.setQueue([track('a')]);audio.pause();
 assert.equal(p.status,'paused');assert.equal(p.wantPlay,false);assert.equal(p.interrupted,true);
 await p.toggle();assert.equal(p.status,'playing');assert.equal(p.interrupted,false);
});
test('loading a replacement does not treat its internal pause as interruption',async()=>{
 const {p}=fixture();await p.setQueue(['a','b'].map(track));await p.next();
 assert.equal(p.current.id,'b');assert.equal(p.status,'playing');assert.equal(p.interrupted,false);
});
test('returning from suspension reconciles a missing pause event without autoplay',async()=>{
 const {p,audio}=fixture();await p.setQueue([track('a')]);audio.paused=true;p.reconcile();
 assert.equal(p.wantPlay,false);assert.equal(p.status,'paused');assert.equal(p.interrupted,true);assert.equal(audio.src,'blob:a');
});
test('native ended advances the same element, and swipe previous does not restart current',async()=>{
 const {p,audio}=fixture();await p.setQueue(['a','b'].map(track));audio.dispatchEvent(new Event('ended'));await tick();
 assert.equal(p.current.id,'b');assert.equal(p.audio,audio);assert.equal(p.status,'playing');audio.currentTime=40;
 await p.previous(false);assert.equal(p.current.id,'a');assert.equal(p.status,'playing');
});

test('a queued old pause event cannot undo newly playing media',async()=>{
 const {p,audio}=fixture();await p.setQueue([track('a')]);audio.dispatchEvent(new Event('pause'));
 assert.equal(audio.paused,false);assert.equal(p.status,'playing');assert.equal(p.wantPlay,true);
});
test('seeking preserves playback intent and never creates a manual pause',async()=>{const{p,audio}=fixture();await p.setQueue([track('a')]);p.seek(45);audio.seeking=true;audio.dispatchEvent(new Event('seeking'));audio.dispatchEvent(new Event('waiting'));assert.equal(p.wantPlay,true);assert.equal(p.manualPause,false);assert.equal(p.seeking,true);audio.seeking=false;audio.dispatchEvent(new Event('seeked'));audio.dispatchEvent(new Event('playing'));assert.equal(p.seeking,false);assert.equal(p.status,'playing');assert.equal(audio.currentTime,45);p.toggle();assert.equal(p.manualPause,true);p.seek(60);assert.equal(p.wantPlay,false);assert.equal(audio.paused,true);});
test('seeking to the current position cannot leave a permanent seek state',async()=>{const{p,audio}=fixture();await p.setQueue([track('a')]);p.seek(audio.currentTime);assert.equal(p.seeking,false);});
