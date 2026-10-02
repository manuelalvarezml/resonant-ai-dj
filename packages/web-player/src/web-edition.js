import {escapeHTML as esc,formatTime} from './model.js';
export const guideHTML=()=>`<div class="web-guide"><article><h2>Inside Resonant</h2><p>A shared music collection, ready to explore. Every included track has completed the current audio analysis pipeline.</p></article><article><h2>How to use</h2><p>Browse, filter and play the library. In PlaylistIQ, describe a moment or a mood, then play the matches or save a playlist.</p></article><article><h2>What works today</h2><p>Music playback, audio features, prompt-based playlists and one DJ mix example. Everyone explores the same library; your saved playlists and favorites stay in this browser.</p></article><article><h2>What’s next</h2><p>Better mood matching, smoother playlist flow and more DJ mix controls.</p></article></div>`;
export async function mountWebMix(root,{pauseMain,mainAudio}){
 root.innerHTML='<p>Loading the mix…</p>';
 const response=await fetch('/api/web/mix');if(!response.ok){root.textContent='The mix is unavailable.';return;}
 const m=await response.json();if(!root.isConnected)return;
 root.innerHTML=`<section class="mix-workspace"><h2>${esc(m.title)}</h2><p>${m.tracks.map(esc).join(' → ')} · ${formatTime(m.duration_s)}</p><audio controls preload="metadata" src="${esc(m.url)}" aria-label="DJ mix playback"></audio><div class="web-guide"><article><h3>Listen for the transitions</h3>${m.transitions.map((t,i)=>`<p><strong>${formatTime(t.start_s)}–${formatTime(t.end_s)}</strong> · Transition ${i+1}: ${esc(m.tracks[i])} → ${esc(m.tracks[i+1])}</p>`).join('')}<p>Each blend lasts about 29 seconds, with a bass handoff at its midpoint.</p></article></div></section>`;
 const audio=root.querySelector('audio');audio.addEventListener('play',pauseMain);const stop=()=>audio.pause();mainAudio.addEventListener('play',stop);
 return ()=>{audio.pause();audio.removeAttribute('src');audio.load();mainAudio.removeEventListener('play',stop);};
}
