import test from 'node:test';
import assert from 'node:assert/strict';
import {readAudioTags,applyAudioTags,featureTags} from '../src/audio-tags.js';
test('ID3v2 UTF-8 tags and untagged files',async()=>{
 const text=new TextEncoder().encode('Song é');
 const frame=new Uint8Array(11+text.length);frame.set(new TextEncoder().encode('TIT2'));frame[7]=text.length+1;frame[10]=3;frame.set(text,11);
 const bytes=new Uint8Array(10+frame.length);bytes.set([73,68,51,4,0,0,0,0,0,frame.length]);bytes.set(frame,10);
 assert.deepEqual(await readAudioTags(new Blob([bytes])),{title:'Song é'});
 assert.deepEqual(await readAudioTags(new Blob(['no tags'])),{});
});
test('ID3v1 and analysis tags retain field provenance without guessing missing fields',async()=>{
 const bytes=new Uint8Array(128);bytes.set(new TextEncoder().encode('TAGTitle'));bytes.set(new TextEncoder().encode('Artist'),33);
 assert.deepEqual(await readAudioTags(new Blob([bytes])),{title:'Title',artist:'Artist'});
 const track={title:'filename',artist:'Unknown artist',features:{algorithms:[{algorithm_id:'metadata',status:'passed',values:{encoded_tags:{TITLE:' Tagged ',ARTIST:'Name'}}}]}};
 const next=applyAudioTags(track,featureTags(track));
 assert.equal(next.title,'Tagged');assert.equal(next.artist,'Name');assert.equal(track.title,'filename');assert.equal(next.evidence.length,2);
 assert.equal(applyAudioTags(track,{}).artist,'Unknown artist');
});
