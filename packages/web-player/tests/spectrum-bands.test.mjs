import test from 'node:test';
import assert from 'node:assert/strict';
import {spectrumBands} from '../src/spectrum-bands.js';
test('bass columns interpolate between bins instead of repeating squared shelves',()=>{
 const bins=Float32Array.from({length:4096},(_,i)=>-80+i*.1);
 const row=spectrumBands(bins,48000,8192);
 for(let x=0;x<10;x++){
  const hz=40*450**(x/95),expected=(-80+hz*8192/48000*.1+90)/90;
  assert.ok(Math.abs(row[x]-expected)<1e-6);
  if(x)assert.ok(row[x]>row[x-1]);
 }
});
test('silence stays finite and broad bands preserve a narrow spectral peak',()=>{
 const bins=new Float32Array(4096).fill(-Infinity);
 assert.ok(spectrumBands(bins,48000,8192).every(v=>v===0));
 const x=70,center=40*450**(x/95)*8192/48000;
 bins[Math.round(center)]=-18;
 assert.ok(Math.abs(spectrumBands(bins,48000,8192)[x]-.8)<1e-6);
});

test('dual FFT display selects bass below 350 Hz and coarse bins above',async()=>{
 const {splitSpectrumBands}=await import('../src/spectrum-bands.js');
 const row=splitSpectrumBands(new Float32Array(4096).fill(-18),new Float32Array(1024).fill(-72),48000);
 for(let x=0;x<row.length;x++)assert.ok(Math.abs(row[x]-(40*450**(x/95)<350?.8:.2))<1e-6);
});
