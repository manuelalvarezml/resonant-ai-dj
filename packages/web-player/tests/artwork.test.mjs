import test from 'node:test';
import assert from 'node:assert/strict';
import {artworkThumbnail,matchingArtwork,notifyStoredArtwork,artworkDelivery} from '../src/artwork.js';
import {trackCardHTML,webIntentHTML} from '../src/web-presentation.js';
import {promptResultsHTML} from '../src/profile-views.js';

test('artwork is version-bound and stale source replacements retain placeholders',()=>{
 const track={id:'a',sourceVersion:'v2'},records={a:{source_version:'v1',status:'ready'}};
 assert.equal(matchingArtwork(track,records),null);
 records.a.source_version='v2';assert.equal(matchingArtwork(track,records),records.a);
});
test('thumbnail identifiers escape markup and do not trust remote image URLs',()=>{
 const html=artworkThumbnail({id:'"><script>',artwork:{url:'https://evil.test/track'}});
 assert.ok(html.includes('&quot;&gt;&lt;script&gt;'));assert.ok(!html.includes('<script>'));assert.ok(!html.includes('evil.test'));
});
test('library and fresh/saved playlist results place compact artwork before the title',()=>{
 const t={id:'a',title:'Song',artist:'Artist',status:'ready'};
 const outputs=[trackCardHTML(t),webIntentHTML({result:{matches:[{track:{track_id:'a',title:'Song'},score:1}]}}),promptResultsHTML({prompt:'Music',trackIds:['a']},[t])];
 for(const html of outputs){assert.ok(html.indexOf('album-thumbnail')<html.indexOf('<strong'));assert.ok(!html.includes('now-art'));}
});
test('stored artwork notification returns immediately without starting audio analysis',()=>{
 assert.equal(notifyStoredArtwork({id:'a'}),undefined);
});

test('hosted artwork only accepts the protected immutable library namespace',()=>{
 const value={manifestURL:'/library/artwork/releases/'+'a'.repeat(64)+'/manifest.json',imageBase:'/library/artwork/images/'};
 assert.deepEqual(artworkDelivery(value),value);
 for(const manifestURL of ['https://evil.test/manifest.json','/api/artwork/manifest','/library/artwork/releases/../manifest.json'])assert.throws(()=>artworkDelivery({...value,manifestURL}));
 assert.throws(()=>artworkDelivery({...value,imageBase:'https://evil.test/'}));
});
