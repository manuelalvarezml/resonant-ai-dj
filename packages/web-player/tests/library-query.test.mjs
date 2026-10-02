import test from 'node:test';
import assert from 'node:assert/strict';
import {queryLibrary,emptyFilters,filterError} from '../src/library-query.js';
const track=(id,bpm,key,genres,status='complete')=>({id,title:id,artist:'Artist',addedAt:1,features:{status,genres:genres.map(genre=>({genre})),algorithms:[{algorithm_id:'rhythm',status:'passed',values:{bpm}},{algorithm_id:'key',status:'passed',values:{camelot:key}}]}});
const tracks=[track('a',120,'2A',['House','Techno']),track('b',128,'10A',['Disco']),track('c',132,'2A',['House'],'partial'),{id:'d',title:'d',artist:'Unknown',addedAt:2}];
test('BPM bounds are inclusive, combine with key/OR genres, and exclude missing evidence',()=>{
 const filters={...emptyFilters(),minBpm:'120',maxBpm:'128',genres:['House','Disco']};
 assert.deepEqual(queryLibrary(tracks,{filters,sort:'bpm',direction:'asc'}).map(t=>t.id),['a','b']);
 assert.deepEqual(queryLibrary(tracks,{filters:{...filters,key:'2A'}}).map(t=>t.id),['a']);
 assert.ok(filterError({...filters,minBpm:'140'}));assert.ok(filterError({...filters,minBpm:'NaN'}));
});
test('numeric key order, descending BPM and missing-last ordering preserve source list',()=>{
 assert.deepEqual(queryLibrary(tracks,{sort:'bpm',direction:'desc'}).map(t=>t.id),['c','b','a','d']);
 assert.deepEqual(queryLibrary(tracks,{sort:'key',direction:'asc'}).map(t=>t.id),['a','c','b','d']);
 assert.deepEqual(tracks.map(t=>t.id),['a','b','c','d']);
});
test('status, favorites and top-six policy do not promote failed or seventh-genre evidence',()=>{
 assert.deepEqual(queryLibrary(tracks,{filters:{...emptyFilters(),analysis:'none'}}).map(t=>t.id),['d']);
 assert.deepEqual(queryLibrary(tracks,{filters:{...emptyFilters(),favorites:true},favorites:['b']}).map(t=>t.id),['b']);
 const t=track('x',120,'1A',['a','b','c','d','e','f','seventh']);t.features.algorithms[0].status='failed';
 assert.equal(queryLibrary([t],{filters:{...emptyFilters(),minBpm:'100'}}).length,0);
 assert.equal(queryLibrary([t],{filters:{...emptyFilters(),genres:['seventh']}}).length,0);
});
test('selected SheetSage2 key drives browsing while failed specialist evidence falls back',()=>{
 const t=track('selected',120,'1A',['House']);
 const expert={algorithm_id:'key_sheetsage2',status:'warning',values:{standard_key:'C minor',camelot:'5A'}};
 t.features.algorithms.push(expert);
 assert.equal(queryLibrary([t],{filters:{...emptyFilters(),key:'5A'}}).length,1);
 assert.equal(queryLibrary([t],{filters:{...emptyFilters(),key:'1A'}}).length,0);
 expert.status='failed';
 assert.equal(queryLibrary([t],{filters:{...emptyFilters(),key:'1A'}}).length,1);
});
