import {mountPlaylistIQ} from '/src/playlistiq.js';
import {demoTracks,createDemoAudio} from '/src/demo.js';
import {Player} from '/src/player.js';
const data=await (await fetch('/__iq-qa-data.json')).json();
const candidates=demoTracks.slice(0,2).map(t=>({...t,features:{sha256:'a'.repeat(64)}}));
const audio=document.querySelector('#qa-audio');
const player=new Player(audio,async track=>{const url=URL.createObjectURL(createDemoAudio(Number(track.id.split('-')[1])-1));return {url,release:()=>URL.revokeObjectURL(url)}});
player.addEventListener('change',()=>document.querySelector('#play-state').textContent=player.status+' '+(player.current?.title??''));
function renderSaved(){const saved=JSON.parse(localStorage.getItem('iq-qa-playlist')||'null');if(!saved)return;const root=document.querySelector('#saved');root.replaceChildren();const text=document.createElement('p');text.textContent='Saved '+saved.trackIds.length+' tracks: '+saved.name;const play=document.createElement('button');play.textContent='Play saved QA playlist';play.className='button primary';play.onclick=()=>player.setQueue(saved.trackIds.map(id=>candidates.find(t=>t.id===id)));root.append(text,play);}
mountPlaylistIQ(document.querySelector('#qa-root'),{candidates,total:2,localJob:async(action,request)=>{localStorage.setItem('iq-qa-request',JSON.stringify(request));return request.clarifications.length?data.matched:data.question},onSave:(name,matches)=>{localStorage.setItem('iq-qa-playlist',JSON.stringify({name,trackIds:matches.map(m=>m.track.track_id)}));renderSaved()}});renderSaved();
