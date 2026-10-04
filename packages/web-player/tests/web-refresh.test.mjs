import test from 'node:test';
import assert from 'node:assert/strict';
import {uniqueAudioTracks,deduplicateCollection} from '../src/model.js';
import {uniqueMatches,playPlaylistMatch,intentHTML} from '../src/playlistiq.js';
import {bindPlaybackLifecycle} from '../src/playback-lifecycle.js';
import {isIOSWebKit,swipeDirection} from '../src/mobile-player.js';
const a='b23cf7fc573254db349ab179fdcc406c5da159186b04b1fe914ff913d83e4ae2';
const b='4d1b398a896faa64804dea2b7ccdc59ac416be35b23bbe84b90e9f1b42d25e24';
const track=(id,hash=id)=>({id,fileHash:hash,title:'Same title',artist:'Same artist',kind:'cloud',status:'ready'});
const match=id=>({track:{track_id:id,title:id},score:.5,reasons:[],score_contributions:[]});
test('web removes verified identical streams but keeps other recordings and originals',()=>{
 const rows=[track(a),track(b),track('c','c'.repeat(64)),track(a)],snapshot=structuredClone(rows);
 assert.deepEqual(uniqueAudioTracks(rows).map(t=>t.id),[a,'c']);assert.deepEqual(rows,snapshot);
 assert.equal(uniqueAudioTracks(rows.slice(0,2).map(t=>({...t,kind:'local'}))).length,2);
});
test('saved favorites and playlists survive duplicate removal in original order',()=>{
 const prefs={favorites:[b,a,'missing'],playlists:[{id:'p',name:'Mix',trackIds:['c',b,a]}],volume:.4};
 const saved=structuredClone(prefs),out=deduplicateCollection([track(a),track(b),track('c')],prefs);
 assert.deepEqual(out.preferences.favorites,[a,'missing']);assert.deepEqual(out.preferences.playlists[0].trackIds,['c',a]);assert.equal(out.preferences.volume,.4);assert.deepEqual(prefs,saved);
});
test('PlaylistIQ keeps first ranked occurrence and plays each recording once',async()=>{
 const tracks=[track(a),track(b),track('c')],matches=[match(a),match(b),match(a),match('c')];
 assert.deepEqual(uniqueMatches(matches,tracks).map(m=>m.track.track_id),[a,'c']);
 let queue;await playPlaylistMatch({setQueue:(q,i)=>{queue=[q.map(t=>t.id),i];}},tracks,matches,'c');
 assert.deepEqual(queue,[[a,'c'],1]);
 const html=intentHTML({result:{matches}});assert.match(html,/2 matching tracks/);assert.equal((html.match(/data-iq-play=/g)||[]).length,2);
});
test('pagehide preserves queue and URLs; foreground reconciles without forced play',()=>{
 const page=new EventTarget(),document=new EventTarget();document.hidden=true;
 let reconciled=0,cleared=0;const unbind=bindPlaybackLifecycle({reconcile:()=>reconciled++,clear:()=>cleared++},{page,document});
 page.dispatchEvent(new Event('pagehide'));document.dispatchEvent(new Event('visibilitychange'));assert.equal(cleared,0);assert.equal(reconciled,0);
 document.hidden=false;page.dispatchEvent(new Event('pageshow'));document.dispatchEvent(new Event('visibilitychange'));assert.equal(reconciled,2);unbind();page.dispatchEvent(new Event('pageshow'));assert.equal(reconciled,2);
});
test('iOS detection protects native audio, desktop retains spectrum',()=>{
 assert.ok(isIOSWebKit({userAgent:'Mozilla iPhone Safari'}));assert.ok(isIOSWebKit({userAgent:'Macintosh',platform:'MacIntel',maxTouchPoints:5}));
 assert.equal(isIOSWebKit({userAgent:'Macintosh Chrome',platform:'MacIntel',maxTouchPoints:0}),false);
});
test('horizontal swipes change tracks without interpreting taps or vertical scrolling',()=>{
 assert.equal(swipeDirection(-80,10),'next');assert.equal(swipeDirection(80,10),'previous');
 assert.equal(swipeDirection(20,0),null);assert.equal(swipeDirection(60,80),null);
});

test('an old recommendation for a hidden alias resolves to the retained recording',()=>{
 const out=uniqueMatches([match(b),match(a)],[track(a)]);
 assert.deepEqual(out.map(m=>m.track.track_id),[a]);
});
