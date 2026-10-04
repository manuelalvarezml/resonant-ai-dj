import {serverlessTransport} from './serverless.js';
import {escapeHTML as esc,formatTime} from './model.js';
export const guideHTML=()=>`<div class="web-guide"><article><h2>Inside Resonant</h2><p>A shared music collection, ready to explore. Every included track has completed the current audio analysis pipeline.</p></article><article><h2>How to use</h2><p>Browse, filter and play the library. In PlaylistIQ, describe a moment or a mood, then play the matches or save a playlist.</p></article><article><h2>What works today</h2><p>Music playback, audio features, prompt-based playlists and one DJ mix example. Everyone explores the same library; your saved playlists and favorites stay in this browser.</p></article><article><h2>What’s next</h2><p>Better mood matching, smoother playlist flow and more DJ mix controls.</p></article></div>`;
export const mixTrackDetails=[{title:'My Paradise - Edit',artist:'The Trip'},{title:'Rock The House (Original Mix)',artist:'Demi Riquísimo, The Trip (UK)'},{title:'Triple Funk',artist:'Lemon8'}];
export async function resolveMixPlayback(track){
 const cloud=serverlessTransport();if(cloud?.expiresAt&&cloud.expiresAt<Date.now()+10000)await cloud.refresh();
 const url=new URL(track.mixUrl,location.origin);
 if(url.origin!==location.origin||!(url.pathname==='/api/web/mix/audio'||/^\/media\/mix-[a-f0-9]{64}\.m4a$/.test(url.pathname)))throw Error('Invalid mix audio address.');
 return{url:url.href,expiresAt:cloud?.expiresAt||null,release:()=>{}};
}
export async function mountWebMix(root,{player}){
 root.innerHTML='<p>Loading the mix…</p>';
 let m;try{if(serverlessTransport())m=await serverlessTransport().mix();else{const response=await fetch('/api/web/mix');if(!response.ok)throw Error('Unavailable');m=await response.json();}}catch{root.textContent='The mix is unavailable.';return;}
 if(!root.isConnected)return;
 const track={id:'mix-house-example',sourceVersion:'mix-house-example',title:m.title,artist:'Resonant · DJ mix',duration:m.duration_s,status:'ready',kind:'mix',mixUrl:m.url,color:0};
 root.innerHTML=`<section class="mix-workspace"><h2>${esc(m.title)}</h2><ol class="mix-tracks numbered-editorial">${mixTrackDetails.map(t=>`<li><div><strong>${esc(t.title)}</strong><span>${esc(t.artist)}</span></div></li>`).join('')}</ol><button class="button primary mix-main-play" type="button">Play mix <span>${formatTime(m.duration_s)}</span></button><div class="mix-transitions"><h3>Transitions:</h3><ol class="numbered-editorial">${m.transitions.map(t=>`<li><button class="transition-link" type="button" data-transition="${Number(t.start_s)}">${formatTime(t.start_s)}</button></li>`).join('')}</ol><p>Each blend lasts about 30 seconds.</p><p class="mix-message" role="status"></p></div></section>`;
 const play=async position=>{try{if(player.current?.id!==track.id){player.queue=[track];player.index=0;player.listeningContext={source:'mix'};await player.load(position);}else{player.seek(position);if(!player.wantPlay)await player.toggle();}}catch(e){root.querySelector('.mix-message').textContent=e.message;}};
 root.querySelector('.mix-main-play').onclick=()=>void play(0);
 for(const button of root.querySelectorAll('[data-transition]'))button.onclick=()=>void play(Number(button.dataset.transition));
 // Navigation does not interrupt a mix: the main player owns its lifetime.
 return ()=>{};
}
