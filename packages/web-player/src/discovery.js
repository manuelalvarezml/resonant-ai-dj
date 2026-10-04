import {shuffled} from './model.js';
// One permutation per page load: filtering and player updates never reshuffle it.
export function freshLibraryOrder(tracks,previousFirst='',random=Math.random){
 const rows=shuffled(tracks,random);if(rows.length>1&&rows[0].id===previousFirst)[rows[0],rows[1]]=[rows[1],rows[0]];
 return new Map(rows.map((track,index)=>[track.id,index]));
}
export const promptStyles=[
 {style:'Scene',examples:['A picnic with my girlfriend on a sunny afternoon','A birthday party that gets the room dancing','Dinner on a rooftop as the city lights come on','A tiny house party that accidentally becomes a big one','A beach evening after everyone else has gone home']},
 {style:'Activity',examples:['Music for cooking something ambitious and probably burning it','Help me focus on writing without sending me to sleep','A steady groove for a long walk across the city','Something buoyant for cleaning the apartment','Music for stretching after a demanding day']},
 {style:'Feeling',examples:['I want to feel hopeful without anything too sugary','Give me something tender for a slightly heavy evening','Confident, playful music for getting ready to go out','Let me sit with a little melancholy, but keep it warm','I need a reset: calm at first, then a little brighter']},
 {style:'Texture',examples:['Warm bass, soft percussion and plenty of breathing room','Give me crisp drums and a loose, swinging groove','Airy textures, gentle vocals and understated rhythm','Percussive tracks with broken beats and very little singing','Something gritty, bass-heavy and rhythmically restless']},
 {style:'Genre',examples:['Deep house for an unhurried Sunday afternoon','Relaxed jazz with a warm, intimate feel','Left-field electronic music with an inviting groove','Soulful tracks with a little funk in their step','House and disco for people who claim they never dance']},
 {style:'Specific brief',examples:['House around 120–128 BPM, warm and mostly instrumental','Keep it below 110 BPM with gentle energy and few vocals','Give me punchy electronic tracks around 130 BPM','A relaxed selection with vocals, without aggressive sounds','Danceable music with a steady pulse and no frantic tempos']},
 {style:'Journey',examples:['Start mellow and gradually bring the room to life','From intimate dinner music to a small kitchen dance floor','Give me an arc from dreamy to driving, then ease back down','Begin with a loose groove and finish with a little more bite','A late-night journey that gets softer as it goes']},
 {style:'Minimal',examples:['Warm. Loose. A little funky.','Quiet confidence, low lights.','Broken beats. Deep bass.','Sunshine and a steady groove.','Tender vocals, unhurried rhythm.']},
 {style:'Poetic',examples:['The city at blue hour, with nowhere urgent to be','Sunlight through the blinds on a very slow morning','A small dance floor at the end of a long corridor','Rain on the windows, something warm in my hands','That last golden hour before a good day disappears']},
 {style:'Conversational',examples:['I have friends over; make it interesting without taking over','I want to dance, but I am not ready for peak-time energy','Surprise me with something warm that I might overlook','Give me a little attitude, but please spare me the chaos','I like a good groove more than a big drop tonight']}
];
export const promptExamples=promptStyles.flatMap((group,g)=>group.examples.map((text,i)=>({id:`${g}-${i}`,style:group.style,text})));
export function choosePromptPair(previous=[],random=Math.random){
 const pool=shuffled(promptExamples.filter(p=>!previous.slice(0,2).includes(p.id)),random),first=pool[0],second=pool.find(p=>p.style!==first.style);return[first,second];
}
let sessionPair;
export function sessionPromptPlaceholder(storage=globalThis.localStorage){
 if(!sessionPair){let previous=[];try{previous=JSON.parse(storage.getItem('resonant:discovery:prompts')??'[]');if(!Array.isArray(previous))previous=[];}catch{}
  sessionPair=choosePromptPair(previous);try{storage.setItem('resonant:discovery:prompts',JSON.stringify(sessionPair.map(p=>p.id)));}catch{}
 }
 return sessionPair.map(p=>p.text).join(', or ')+'…';
}
