import test from 'node:test';
import assert from 'node:assert/strict';
import {advanceSpectrumFrame} from '../src/spectrum-timing.js';

function frames(hz,interval,seconds=10){
 let last=0,count=0;
 for(let n=1;n<=hz*seconds;n++){
  const next=advanceSpectrumFrame(last,n*1000/hz,interval);
  if(next!==null){last=next;count++;}
 }
 return count;
}
test('30 Hz Safari callbacks retain 30 fps painting and 20 Hz history',()=>{
 assert.equal(frames(30,1000/30),300);
 assert.equal(frames(30,50),200);
});
test('60/120 Hz callbacks use the same time window and reduced-motion rate',()=>{
 for(const hz of [60,120]){
  assert.equal(frames(hz,1000/30),300);
  assert.equal(frames(hz,50),200);
  assert.equal(frames(hz,200),50);
 }
});
test('a late callback skips missed frames without a catch-up burst',()=>{
 const next=advanceSpectrumFrame(0,10017,1000/30);
 assert.ok(next<=10017&&10017-next<1000/30);
 assert.equal(advanceSpectrumFrame(next,10018,1000/30),null);
});
