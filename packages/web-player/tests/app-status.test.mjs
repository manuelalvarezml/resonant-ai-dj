import test from 'node:test';
import assert from 'node:assert/strict';
import {appStatusHTML} from '../src/app-status.js';

test('status counts local analysis separately from demos and escapes maintained content',()=>{
 const html=appStatusHTML({updated:'2026-09-15',summary:'<script>bad()</script>',sections:[{title:'Models & matching',ordered:true,items:['<img onerror=x>']}]},[
 {kind:'local',features:{status:'complete'}},{kind:'local',features:{status:'partial'}},{kind:'local'},{kind:'demo',features:{status:'complete'}}
 ],2);
 assert.match(html,/<strong>3<\/strong><span>Loaded tracks/);
 assert.match(html,/<strong>1<\/strong><span>Fully analyzed/);
 assert.match(html,/<strong>1<\/strong><span>Partial analysis/);
 assert.match(html,/<strong>2<\/strong><span>Saved playlists/);
 assert.ok(!html.includes('<script>'));
 assert.match(html,/&lt;img onerror=x&gt;/);
 assert.match(html,/<ol>/);
});
